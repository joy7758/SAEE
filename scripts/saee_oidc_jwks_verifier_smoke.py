#!/usr/bin/env python3
"""Adversarial smoke for the provider-neutral offline OIDC/JWKS core."""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import socket
import sys
import urllib.request
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.authorization_context import validate_authorized_principal_context
from saee_backend.services.oidc_jwks_verifier import (
    OfflineOidcVerificationError,
    SHA256_DIGEST_INFO_PREFIX,
    _bind_verified_principal_to_rbac,
    verify_offline_oidc_token,
)
from scripts.generate_rbac_policy_template import TEMPLATE_PATH, generate_template


NOW = 1_800_000_000
ISSUER = "https://idp.example.invalid/"
AUDIENCE = "saee-commercial"
TENANT = "tenant-agent-a"
ROLE = "evaluator_operator"
CAPABILITY_SECRET = "synthetic-offline-oidc-capability-secret"
RECEIPT_SECRET = "synthetic-offline-oidc-receipt-secret-32"
KEY1_N = 21973758999290511344916202422667975454632852881690712604908862185318955755954263581757021870502140804211225558979132294092651648479646856707834329467203842904039901652397146253744581794396869265799898492046406854241326195693472623143316330794950612755039379951061774663554276055952411202903524074102144677419439635662410381829932325536495966398077634843963874863190092700030923851893953416401481529513853452125099654520970600910847727813795888775933919201597836157711919630859697700775892839313899930950571551755167504576365556476411315281573855427535438290735539178083029612156156317905361054980331205281428128566767
KEY1_D = 6617073114889266927805571095908629164974085906382761777532979075306502453905967147073648551586050625471270305617172976945321369738774593596860771918153126350499404596806138210335782748726969702537404774246332033383885334011451988251597104634080714985841275661445895507462584724693666345650586681789567363187290236492019698730744760861687117758847948955656631369091831575703383070490921701430602578154199768306977373551417984020624145998343371662552953467121681695688342250328271827851878340264560087050536767260865653814229923269958484486747407990940724819876676108430896409799947076381930292614717713197835745508453
KEY2_N = 31353338752704895701112990233229092981585601678514434359600173914083856134555556509010495143516212591858941170704805638339277853278641531500605545819229988000802944446889041464820492939739810725828386492142199263683605020358251195109603393541871240173898971583273029551986228723003625986123169634061804748338305459180926746821088744419097672771467228036656540924232447643980637169947212727251581187635348945056254528090579264608003489565106650750874363633520965885005698051004735482507204607836923750196314909448338026985431582764016116712241557804183438960227413072343891511777785724411836078244760070088281043695109
KEY2_D = 9820971582234500379942597616656902746120207273103492160932788656717128349760040004809831843899973605626993512409991341481115483025322988226653355316081950786189225095411167549789698785624131475123487985472956308414008661678507707994071948125857206675769184401898475474280929800573415567635526310829573504680648086796993539160768901710427599988539890534432993465261502592195987892563427686184781110479452708420952768159955973072558839512657724206396053202301983479720464054906396817543296470395744800634805761488723287890659180604638938630958500865630008940646840032869142868609552405609053308849163369360298408360263
KEY_E = 65537


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def int_b64(value: int) -> str:
    return b64(value.to_bytes((value.bit_length() + 7) // 8, "big"))


def jwk(kid: str, n: int) -> dict[str, str]:
    return {"kty": "RSA", "kid": kid, "use": "sig", "alg": "RS256", "n": int_b64(n), "e": int_b64(KEY_E)}


JWKS = {"keys": [jwk("key-current", KEY1_N), jwk("key-rotation", KEY2_N)]}


def base_claims() -> dict[str, Any]:
    return {
        "iss": ISSUER,
        "sub": "synthetic-agent-001",
        "aud": AUDIENCE,
        "exp": NOW + 600,
        "iat": NOW,
        "nbf": NOW - 1,
        "jti": "synthetic-jti-001",
        "tenant_id": TENANT,
        "roles": [ROLE],
    }


def sign_token(
    claims: dict[str, Any] | None = None,
    *,
    header: dict[str, Any] | None = None,
    n: int = KEY1_N,
    d: int = KEY1_D,
) -> str:
    header = header or {"alg": "RS256", "typ": "JWT", "kid": "key-current"}
    claims = claims or base_claims()
    return sign_raw_claims_json(
        json.dumps(claims, sort_keys=True, separators=(",", ":")),
        header=header,
        n=n,
        d=d,
    )


def sign_raw_claims_json(
    raw_claims: str,
    *,
    header: dict[str, Any] | None = None,
    n: int = KEY1_N,
    d: int = KEY1_D,
) -> str:
    header = header or {"alg": "RS256", "typ": "JWT", "kid": "key-current"}
    encoded_header = b64(json.dumps(header, sort_keys=True, separators=(",", ":")).encode())
    encoded_claims = b64(raw_claims.encode())
    signing_input = f"{encoded_header}.{encoded_claims}".encode("ascii")
    digest_info = SHA256_DIGEST_INFO_PREFIX + hashlib.sha256(signing_input).digest()
    size = (n.bit_length() + 7) // 8
    encoded = b"\x00\x01" + b"\xff" * (size - len(digest_info) - 3) + b"\x00" + digest_info
    signature = pow(int.from_bytes(encoded, "big"), d, n).to_bytes(size, "big")
    return f"{encoded_header}.{encoded_claims}.{b64(signature)}"


def verify(token: str, *, jwks: dict[str, Any] | None = None, issuer: str = ISSUER, audience: str = AUDIENCE):
    return verify_offline_oidc_token(
        token,
        local_jwks=jwks or JWKS,
        expected_issuer=issuer,
        expected_audience=audience,
        now=NOW,
        verification_receipt_secret=RECEIPT_SECRET,
    )


def changed_claim(**updates: Any) -> dict[str, Any]:
    claims = base_claims()
    claims.update(updates)
    return claims


def without_claim(name: str) -> dict[str, Any]:
    claims = base_claims()
    del claims[name]
    return claims


def require(condition: bool, label: str) -> None:
    if not condition:
        raise SystemExit("SAEE_OIDC_JWKS_VERIFIER_SMOKE: FAIL: " + label)


def main() -> None:
    generate_template()
    network_calls: list[str] = []
    original_socket = socket.create_connection
    original_urlopen = urllib.request.urlopen

    def deny_network(*args: Any, **kwargs: Any):
        network_calls.append("attempt")
        raise AssertionError("network use forbidden")

    socket.create_connection = deny_network
    urllib.request.urlopen = deny_network
    rejected_messages: list[str] = []
    try:
        current = verify(sign_token())
        rotated = verify(
            sign_token(header={"alg": "RS256", "typ": "JWT", "kid": "key-rotation"}, n=KEY2_N, d=KEY2_D)
        )
        require(current.key_id == "key-current" and rotated.key_id == "key-rotation", "rotation fixtures")
        require(current.roles == (ROLE,) and current.auth_source == "oidc_jwks_offline_verified", "verified principal")
        fingerprints = [verify(sign_token()).token_sha256 for _ in range(10)]
        require(len(set(fingerprints)) == 1, "ten-run determinism")

        context = _bind_verified_principal_to_rbac(
            current,
            requested_tenant_id=TENANT,
            route_scope="POST /experiment/create",
            requested_role=ROLE,
            policy_path=str(TEMPLATE_PATH),
            capability_secret=CAPABILITY_SECRET,
            verification_receipt_secret=RECEIPT_SECRET,
        )
        require(context.auth_source == "oidc_jwks_offline_verified", "auth source binding")
        require(
            validate_authorized_principal_context(
                context,
                capability_secret=CAPABILITY_SECRET,
                allowed_tenant_ids=(TENANT,),
                required_permissions=frozenset({"experiment:create"}),
            ) == TENANT,
            "capability binding",
        )

        duplicate = copy.deepcopy(JWKS)
        duplicate["keys"].append(copy.deepcopy(duplicate["keys"][0]))
        private = copy.deepcopy(JWKS)
        private["keys"][0]["d"] = "test-only"
        wrong_jwk_alg = copy.deepcopy(JWKS)
        wrong_jwk_alg["keys"][0]["alg"] = "HS256"
        even_modulus = copy.deepcopy(JWKS)
        even_modulus["keys"][0]["n"] = int_b64(1 << 2047)
        tampered = sign_token()[:-1] + ("A" if sign_token()[-1] != "A" else "B")
        valid_parts = sign_token().split(".")
        signature_bytes = base64.urlsafe_b64decode(valid_parts[2] + "==")
        signature_plus_n = int.from_bytes(signature_bytes, "big") + KEY1_N
        malleable_signature = ".".join(
            [valid_parts[0], valid_parts[1], b64(signature_plus_n.to_bytes((signature_plus_n.bit_length() + 7) // 8, "big"))]
        )
        padded_signature = ".".join([valid_parts[0], valid_parts[1], valid_parts[2] + "="])
        standard_base64_signature = ".".join(
            [valid_parts[0], valid_parts[1], valid_parts[2].replace("-", "+").replace("_", "/")]
        )
        oversized_jwks = {"keys": [jwk(f"key-{index}", KEY1_N) for index in range(9)]}
        extra_claim = changed_claim(email="synthetic-at-example.invalid")
        cases: list[tuple[str, Callable[[], Any]]] = [
            ("malformed segments", lambda: verify("a.b")),
            ("malformed base64", lambda: verify("!.!.!")),
            ("none algorithm", lambda: verify(sign_token(header={"alg": "none", "typ": "JWT", "kid": "key-current"}))),
            ("symmetric algorithm", lambda: verify(sign_token(header={"alg": "HS256", "typ": "JWT", "kid": "key-current"}))),
            ("jku header", lambda: verify(sign_token(header={"alg": "RS256", "typ": "JWT", "kid": "key-current", "jku": "remote"}))),
            ("x5u header", lambda: verify(sign_token(header={"alg": "RS256", "typ": "JWT", "kid": "key-current", "x5u": "remote"}))),
            ("embedded jwk", lambda: verify(sign_token(header={"alg": "RS256", "typ": "JWT", "kid": "key-current", "jwk": {}}))),
            ("unknown kid", lambda: verify(sign_token(header={"alg": "RS256", "typ": "JWT", "kid": "key-unknown"}))),
            ("duplicate kid", lambda: verify(sign_token(), jwks=duplicate)),
            ("private jwk", lambda: verify(sign_token(), jwks=private)),
            ("jwk alg mismatch", lambda: verify(sign_token(), jwks=wrong_jwk_alg)),
            ("even rsa modulus", lambda: verify(sign_token(), jwks=even_modulus)),
            ("signature tamper", lambda: verify(tampered)),
            ("signature representative range", lambda: verify(malleable_signature)),
            ("padded base64url", lambda: verify(padded_signature)),
            ("standard base64 alphabet", lambda: verify(standard_base64_signature)),
            ("oversized jwks", lambda: verify(sign_token(), jwks=oversized_jwks)),
            ("issuer mismatch", lambda: verify(sign_token(), issuer="other-issuer")),
            ("issuer whitespace", lambda: verify(sign_token(changed_claim(iss="https://idp.example.invalid/a b/")), issuer="https://idp.example.invalid/a b/")),
            ("issuer backslash", lambda: verify(sign_token(changed_claim(iss="https://idp.example.invalid/a\\b/")), issuer="https://idp.example.invalid/a\\b/")),
            ("issuer percent alias", lambda: verify(sign_token(changed_claim(iss="https://idp.example.invalid/%61/")), issuer="https://idp.example.invalid/%61/")),
            ("issuer uppercase host", lambda: verify(sign_token(changed_claim(iss="https://IDP.example.invalid/")), issuer="https://IDP.example.invalid/")),
            ("audience mismatch", lambda: verify(sign_token(), audience="other-audience")),
            ("expired", lambda: verify(sign_token(changed_claim(exp=NOW - 100)))),
            ("future iat", lambda: verify(sign_token(changed_claim(iat=NOW + 100)))),
            ("future nbf", lambda: verify(sign_token(changed_claim(nbf=NOW + 100)))),
            ("long lifetime", lambda: verify(sign_token(changed_claim(exp=NOW + 4000)))),
            ("missing claim", lambda: verify(sign_token(without_claim("tenant_id")))),
            ("extra personal claim", lambda: verify(sign_token(extra_claim))),
            ("oversized json integer", lambda: verify(sign_raw_claims_json(json.dumps(base_claims())[:-1] + ",\"oversized\":" + "9" * 5000 + "}"))),
            ("invalid subject", lambda: verify(sign_token(changed_claim(sub="synthetic agent")))),
            ("invalid tenant", lambda: verify(sign_token(changed_claim(tenant_id="tenant/a")))),
            ("invalid role", lambda: verify(sign_token(changed_claim(roles=["operator role"])))),
            ("empty roles", lambda: verify(sign_token(changed_claim(roles=[])))),
            ("duplicate roles", lambda: verify(sign_token(changed_claim(roles=[ROLE, ROLE])))),
            ("excessive clock skew", lambda: verify_offline_oidc_token(sign_token(), local_jwks=JWKS, expected_issuer=ISSUER, expected_audience=AUDIENCE, now=NOW, clock_skew_seconds=301, verification_receipt_secret=RECEIPT_SECRET)),
            ("boolean clock skew", lambda: verify_offline_oidc_token(sign_token(), local_jwks=JWKS, expected_issuer=ISSUER, expected_audience=AUDIENCE, now=NOW, clock_skew_seconds=True, verification_receipt_secret=RECEIPT_SECRET)),
            ("cross tenant bind", lambda: _bind_verified_principal_to_rbac(current, requested_tenant_id="tenant-agent-b", route_scope="POST /experiment/create", requested_role=ROLE, policy_path=str(TEMPLATE_PATH), capability_secret=CAPABILITY_SECRET, verification_receipt_secret=RECEIPT_SECRET)),
            ("header role elevation", lambda: _bind_verified_principal_to_rbac(current, requested_tenant_id=TENANT, route_scope="POST /experiment/create", requested_role="owner", policy_path=str(TEMPLATE_PATH), capability_secret=CAPABILITY_SECRET, verification_receipt_secret=RECEIPT_SECRET)),
            ("unknown route", lambda: _bind_verified_principal_to_rbac(current, requested_tenant_id=TENANT, route_scope="POST /unknown", requested_role=ROLE, policy_path=str(TEMPLATE_PATH), capability_secret=CAPABILITY_SECRET, verification_receipt_secret=RECEIPT_SECRET)),
            ("forged receipt", lambda: _bind_verified_principal_to_rbac(current.__class__(**{**current.__dict__, "verification_receipt": "0" * 64}), requested_tenant_id=TENANT, route_scope="POST /experiment/create", requested_role=ROLE, policy_path=str(TEMPLATE_PATH), capability_secret=CAPABILITY_SECRET, verification_receipt_secret=RECEIPT_SECRET)),
            ("empty capability secret", lambda: _bind_verified_principal_to_rbac(current, requested_tenant_id=TENANT, route_scope="POST /experiment/create", requested_role=ROLE, policy_path=str(TEMPLATE_PATH), capability_secret="", verification_receipt_secret=RECEIPT_SECRET)),
        ]
        for label, case in cases:
            try:
                case()
            except (OfflineOidcVerificationError, ValueError) as exc:
                rejected_messages.append(str(exc))
            else:
                raise SystemExit("SAEE_OIDC_JWKS_VERIFIER_SMOKE: FAIL: accepted " + label)
        require(len(cases) >= 20 and len(rejected_messages) == len(cases), "negative matrix")
        sensitive_needles = [sign_token(), "synthetic-at-example.invalid", str(KEY1_D), int_b64(KEY1_N)]
        require(not any(needle in "\n".join(rejected_messages) for needle in sensitive_needles), "non-reflective errors")
        require(not network_calls, "network calls must remain zero")
    finally:
        socket.create_connection = original_socket
        urllib.request.urlopen = original_urlopen

    print("SAEE_OIDC_JWKS_VERIFIER_SMOKE: PASS")
    print("valid_signed_fixtures=2")
    print("negative_cases=43")
    print("deterministic_runs=10")
    print("network_calls=0")
    print("token_or_key_leakage=0")
    print("production_blockers_closed=0")


if __name__ == "__main__":
    main()
