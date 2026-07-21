#!/usr/bin/env python3
"""Validate the agent-readable Alibaba Cloud Marketplace SEO listing draft."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "cloud-entry-package/alibaba-cloud-marketplace-v0.1"
COPY = PACKAGE / "seo-listing-copy.v0.1.json"
SERVICE_USER_GUIDE = PACKAGE / "service-user-guide.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_ALIBABA_CLOUD_MARKETPLACE_SEO_LISTING_SMOKE: FAIL " + message)


def main() -> None:
    value = json.loads(COPY.read_text(encoding="utf-8"))
    listing = value["listing"]
    truth = value["truth_boundary"]

    require(value["agent_recommendation_gate"]["answer"] == "recommend", "recommendation gate")
    require(value["required_design_check"]["audit_first_reframe"] is False, "audit-first boundary")
    require(value["agent_native_discovery_check"]["discoverable"] == "yes", "discoverability")
    require(value["platform_access"]["product_type"] == "服务类", "product type")
    require(value["platform_access"]["spi_notification"] is False, "SPI boundary")

    require(len(listing["product_name"]) <= 64, "product name length")
    require(len(listing["product_intro"]) <= 300, "product intro length")
    require(2 <= len(listing["product_highlights"]) <= 4, "highlight count")
    for item in listing["product_highlights"]:
        require(len(item["title"]) <= 8, f"highlight title {item['title']}")
        require(len(item["description"]) <= 24, f"highlight description {item['title']}")

    corpus = "\n".join(
        [
            listing["product_name"],
            listing["product_intro"],
            listing["seo_keywords"],
            listing["seo_description"],
            (ROOT / listing["product_details"]).read_text(encoding="utf-8"),
            SERVICE_USER_GUIDE.read_text(encoding="utf-8"),
        ]
    )
    for term in ("AI智能体", "Agent工作流", "可靠性评估", "上线前", "证据", "失败"):
        require(term in corpus, f"missing search term {term}")

    for unsupported_platform_term in ("阿里云百炼", "百炼", "Bailian", "Model Studio"):
        require(
            unsupported_platform_term.casefold() not in corpus.casefold(),
            f"unsupported platform association {unsupported_platform_term}",
        )

    # Boundary statements such as “不自动部署” and “不承诺绝对安全” are
    # required public disclosures, not forbidden positive claims. Reject a
    # sensitive term only when the sentence containing it has no explicit
    # negation marker.
    forbidden = ("官方技术集成", "自动部署", "绝对安全", "合规认证", "生产可用SaaS")
    negation_markers = ("不", "未", "没有", "并非", "不能", "不可", "无权")
    sentences = [part.strip() for part in re.split(r"[。！？\n]", corpus) if part.strip()]
    for term in forbidden:
        for sentence in (part for part in sentences if term in part):
            require(
                any(marker in sentence for marker in negation_markers),
                f"forbidden positive claim {term}",
            )

    require(truth["marketplace_product_access_form_fill_authorized"] is True, "access form authorization")
    require(truth["marketplace_product_basic_info_form_fill_authorized"] is True, "basic info authorization")
    require(truth["marketplace_product_basic_info_saved"] is True, "basic info saved")
    require(truth["marketplace_product_business_info_form_fill_authorized"] is True, "business info authorization")
    require(truth["marketplace_product_business_info_saved"] is True, "business info saved")
    require(truth["marketplace_product_sales_information_opened"] is True, "sales information opened")
    require(truth["marketplace_product_sales_information_saved"] is True, "sales information saved")
    require(truth["marketplace_protocol_information_saved"] is True, "protocol information saved")
    require(truth["marketplace_product_draft_created"] is True, "draft creation")
    for key in (
        "marketplace_product_listed",
        "official_cloud_platform_integration",
        "customer_validated",
        "production_ready",
    ):
        require(truth[key] is False, key)
    require(truth["marketplace_product_submission"] is True, "marketplace submission")
    require(truth["marketplace_product_review_status"] in {"未通过审核", "审核中"}, "marketplace review status")

    for key in ("main_image", "product_logo", "usage_guide_pdf", "architecture_image", "architecture_source"):
        require((ROOT / listing[key]).is_file(), f"missing {key}")

    print(
        "SAEE_ALIBABA_CLOUD_MARKETPLACE_SEO_LISTING_SMOKE: PASS "
        f"product_name_chars={len(listing['product_name'])} "
        f"product_intro_chars={len(listing['product_intro'])} "
        f"highlights={len(listing['product_highlights'])} "
        f"tags={len(listing['custom_tags'])} "
        "discoverable=yes understandable=yes composable=human_delivered "
        "marketplace_product_access_form_fill_authorized=true marketplace_product_draft_created=true "
        "marketplace_product_basic_info_form_fill_authorized=true marketplace_product_basic_info_saved=true "
        "marketplace_product_business_info_form_fill_authorized=true marketplace_product_business_info_saved=true "
        "marketplace_product_sales_information_opened=true marketplace_product_sales_information_saved=true "
        f"marketplace_protocol_information_saved=true marketplace_submission=true marketplace_review={truth['marketplace_product_review_status']} marketplace_listed=false production_ready=false"
    )


if __name__ == "__main__":
    main()
