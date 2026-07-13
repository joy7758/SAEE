"""Storage factory for the SAEE MVP API shell."""

from __future__ import annotations

from saee_backend.config import SETTINGS, SaeeBackendSettings
from saee_backend.storage.memory_db import MemoryExperimentStore
from saee_backend.storage.sqlite_store import SQLiteExperimentStore


def create_experiment_store(settings: SaeeBackendSettings = SETTINGS):
    if settings.storage_backend == "memory":
        return MemoryExperimentStore(
            require_tenant_id=settings.require_tenant_id,
            allowed_tenant_ids=tuple(settings.allowed_tenant_ids),
            require_authorized_context=settings.require_bound_tenant_authorization,
        )
    if settings.storage_backend == "sqlite":
        return SQLiteExperimentStore(
            settings.storage_path,
            require_tenant_id=settings.require_tenant_id,
            allowed_tenant_ids=tuple(settings.allowed_tenant_ids),
            require_authorized_context=settings.require_bound_tenant_authorization,
        )
    raise ValueError(f"Unsupported SAEE_STORAGE_BACKEND: {settings.storage_backend}")
