"""SQLite-backed persistence for the SAEE MVP API shell."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from saee_backend.storage.memory_db import (
    AgentMetricRecord,
    AgentRunRecord,
    ExperimentListRecord,
    ExperimentResult,
)
from saee_backend.storage.serialization import (
    deserialize_experiment_result,
    serialize_experiment_result,
)
from saee_backend.storage.secret_boundary import (
    validate_identifier_not_tenant,
    validate_persistable_experiment_result,
)
from saee_backend.storage.tenant_key import (
    tenant_public_experiment_id,
    tenant_storage_key,
    validate_required_storage_tenant_id,
    validate_storage_tenant_allowlist,
)
from saee_backend.services.authorization_context import (
    AuthorizedPrincipalContext,
    TenantAuthorization,
    tenant_id_from_authorization,
    validate_authorized_principal_context,
)


CREATE_PERMISSIONS = frozenset({"experiment:create"})
RUN_PERMISSIONS = frozenset({"experiment:run"})
READ_PERMISSIONS = frozenset({"experiment:read"})


class SQLiteExperimentStore:
    """Persist public-shell experiment records in a local SQLite database."""

    def __init__(
        self,
        db_path: str | Path,
        *,
        require_tenant_id: bool = False,
        allowed_tenant_ids: tuple[str, ...] = (),
        require_authorized_context: bool = False,
    ) -> None:
        self.db_path = Path(db_path)
        self.require_tenant_id = require_tenant_id
        self.allowed_tenant_ids = validate_storage_tenant_allowlist(
            required=require_tenant_id,
            allowed_tenant_ids=tuple(allowed_tenant_ids),
        )
        self.require_authorized_context = require_authorized_context
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
        self._assert_no_legacy_raw_tenant_keys()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _tenant_id(
        self,
        authorization: TenantAuthorization,
        required_permissions: frozenset[str],
    ) -> str | None:
        if self.require_authorized_context:
            if not isinstance(authorization, AuthorizedPrincipalContext):
                raise ValueError("an authorized principal context is required by storage")
            return validate_authorized_principal_context(
                authorization,
                capability_secret=os.environ.get(
                    "SAEE_PREVIEW_JWT_HS256_SECRET", ""
                ).strip(),
                allowed_tenant_ids=self.allowed_tenant_ids,
                required_permissions=required_permissions,
            )
        return tenant_id_from_authorization(authorization)

    def _key(
        self,
        experiment_id: str,
        tenant_id: TenantAuthorization = None,
        required_permissions: frozenset[str] = READ_PERMISSIONS,
    ) -> str:
        tenant_id = self._tenant_id(tenant_id, required_permissions)
        safe_tenant_id = validate_required_storage_tenant_id(
            tenant_id,
            required=self.require_tenant_id,
            allowed_tenant_ids=self.allowed_tenant_ids,
        )
        return tenant_storage_key(experiment_id, safe_tenant_id)

    def _public_id(self, key: str, tenant_id: str | None = None) -> str | None:
        return tenant_public_experiment_id(key, tenant_id)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    result_json TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _assert_no_legacy_raw_tenant_keys(self) -> None:
        if not self.require_tenant_id:
            return
        with self._connect() as conn:
            rows = conn.execute("SELECT experiment_id FROM experiments").fetchall()
        legacy_present = any(
            str(row[0]).startswith("tenant:")
            and not str(row[0]).startswith("tenant:v1:")
            for row in rows
        )
        if legacy_present:
            raise ValueError(
                "legacy raw tenant storage keys require explicit archive or migration"
            )

    def create(self, experiment_id: str, tenant_id: str | None = None) -> None:
        safe_tenant_id = self._tenant_id(tenant_id, CREATE_PERMISSIONS)
        validate_identifier_not_tenant(experiment_id, safe_tenant_id)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO experiments (experiment_id)
                VALUES (?)
                ON CONFLICT(experiment_id) DO NOTHING
                """,
                (self._key(experiment_id, tenant_id, CREATE_PERMISSIONS),),
            )

    def save(self, result: ExperimentResult, tenant_id: str | None = None) -> None:
        safe_tenant_id = self._tenant_id(tenant_id, RUN_PERMISSIONS)
        validate_persistable_experiment_result(result, tenant_id=safe_tenant_id)
        payload = json.dumps(
            serialize_experiment_result(result),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        key = self._key(result.summary.experiment_id, tenant_id, RUN_PERMISSIONS)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO experiments (experiment_id, result_json, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(experiment_id) DO UPDATE SET
                    result_json = excluded.result_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, payload),
            )

    def exists(self, experiment_id: str, tenant_id: str | None = None) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM experiments WHERE experiment_id = ? LIMIT 1",
                (self._key(experiment_id, tenant_id),),
            ).fetchone()
        return row is not None

    def get(self, experiment_id: str, tenant_id: str | None = None) -> ExperimentResult | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT result_json FROM experiments WHERE experiment_id = ?",
                (self._key(experiment_id, tenant_id),),
            ).fetchone()
        if row is None or row[0] is None:
            return None
        result = deserialize_experiment_result(json.loads(row[0]))
        validate_persistable_experiment_result(
            result,
            tenant_id=self._tenant_id(tenant_id, READ_PERMISSIONS),
        )
        return result

    def get_runs(self, experiment_id: str, tenant_id: str | None = None) -> list[AgentRunRecord]:
        result = self.get(experiment_id, tenant_id)
        return [] if result is None else result.runs

    def get_metrics(
        self, experiment_id: str, tenant_id: str | None = None
    ) -> list[AgentMetricRecord]:
        result = self.get(experiment_id, tenant_id)
        return [] if result is None else result.metrics

    def list(self, tenant_id: str | None = None) -> list[ExperimentListRecord]:
        tenant_id = self._tenant_id(tenant_id, READ_PERMISSIONS)
        safe_tenant_id = validate_required_storage_tenant_id(
            tenant_id,
            required=self.require_tenant_id,
            allowed_tenant_ids=self.allowed_tenant_ids,
        )
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT experiment_id, result_json
                FROM experiments
                ORDER BY updated_at DESC, experiment_id ASC
                """
            ).fetchall()

        records: list[ExperimentListRecord] = []
        for key, result_json in rows:
            public_id = self._public_id(str(key), safe_tenant_id)
            if public_id is None:
                continue
            if result_json is None:
                records.append(ExperimentListRecord(experiment_id=public_id, status="created"))
                continue
            result = deserialize_experiment_result(json.loads(result_json))
            validate_persistable_experiment_result(result, tenant_id=safe_tenant_id)
            records.append(
                ExperimentListRecord(
                    experiment_id=public_id,
                    status=result.summary.status,
                    recommended_agent=result.summary.recommended_agent,
                    confidence_score=result.summary.confidence_score,
                )
            )
        return records
