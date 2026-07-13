#!/usr/bin/env python3
"""Validate the SAEE MVP landing page product surface."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_LANDING_PAGE_SMOKE: FAIL: {message}")


def require_file(relpath: str) -> Path:
    path = ROOT / relpath
    if not path.is_file():
        fail(f"missing {relpath}")
    return path


def require_tokens(relpath: str, tokens: list[str]) -> None:
    text = require_file(relpath).read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        fail(f"{relpath} missing tokens: {', '.join(missing)}")


def main() -> None:
    html_path = require_file("phase_b_product/landing/index.html")
    commercial_path = require_file("phase_b_product/landing/commercial-readiness.html")
    css_path = require_file("phase_b_product/landing/styles.css")
    app_path = require_file("phase_b_product/landing/app.js")
    readme_path = require_file("phase_b_product/landing/README.md")
    image_path = require_file("phase_b_product/landing/assets/saee-interface-operation-demo.gif")
    generator_path = require_file("scripts/generate_saee_landing_workbench_gif.py")
    gate_path = require_file("docs/strategy/SAEE_MVP_LANDING_PAGE_RECOMMENDATION_GATE.md")

    html = html_path.read_text(encoding="utf-8")
    commercial = commercial_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    app = app_path.read_text(encoding="utf-8")
    readme = readme_path.read_text(encoding="utf-8")
    generator = generator_path.read_text(encoding="utf-8")
    gate = gate_path.read_text(encoding="utf-8")

    if image_path.stat().st_size < 100_000:
        fail("landing image asset is unexpectedly small")

    forbidden_html_tokens = [
        "data:image",
        "saee_v1_0",
        "kernel/runtime.py",
        "selection_engine",
        "mutation_engine",
        "lineage_engine",
        "fitness_engine",
    ]
    found_forbidden = [token for token in forbidden_html_tokens if token in html]
    if found_forbidden:
        fail("landing HTML contains forbidden tokens: " + ", ".join(found_forbidden))
    forbidden_contact_tokens = [
        "hello@example.com",
        "mailto:",
    ]
    found_contact_tokens = [token for token in forbidden_contact_tokens if token in html]
    if found_contact_tokens:
        fail("landing HTML contains unconfigured contact tokens: " + ", ".join(found_contact_tokens))

    required_html_tokens = [
        "assets/saee-interface-operation-demo.gif",
        "workbench-cn-v4-20260708",
        "styles.css?v=linklings-reference-cn-v25-20260709",
        "SAEE 中文工作台动图",
        "app.js",
        "run-demo-battle",
        "demo-output",
        "SAEE 是本地运行的 AI 方案试跑工具。",
        "让多个 AI 方案",
        "先跑一遍，再决定用谁",
        "本地试用",
        "本地运行 · 不上传数据",
        "该选谁",
        "哪里会出错",
        "现在能不能用",
        "怎么试一下",
        "多个 AI 助手 / 工作流 / 策略对比",
        "trial-access-status",
        "commercial-readiness.html",
        "commercial-readiness-link",
        "查看商用准备度",
        "离正式商用，还差真实证据。",
        "在自己电脑上试",
        "online-experience.html",
        "线上体验",
        "先看线上体验",
        "线上体验版只用样例数据，不上传你的资料，不代表正式上线。",
        "本页面不发邮件",
    ]
    missing_html = [token for token in required_html_tokens if token not in html]
    if missing_html:
        fail("landing HTML missing tokens: " + ", ".join(missing_html))

    required_commercial_tokens = [
        "SAEE 商用准备度",
        "styles.css?v=service-simple-cn-v20-20260709",
        "现在可以本地试，但还不能正式商用。",
        "暂不允许上线。",
        "上线前事项仍未补齐",
        "本地预览已补齐",
        "64 个推荐值已按人工确认写入本地预览，但还没有导入正式表格，也没有把任何事项标记完成。",
        "可直接通过的事项",
        "现在没有任何事项可以直接通过，也不能声称客户已验证。",
        "先做安全预检。",
        "现在 64 条本地预览已经补齐。下一步只能先做安全预检和导入审批",
        "先看开始页，再看行动板。",
        "phase_b_product/commercial_readiness/commercial_readiness_begin_here/commercial_readiness_begin_here.html",
        "如果你是在 <code>127.0.0.1:8765</code> 看到这个页面",
        "python3 -m http.server 8876 --bind 127.0.0.1",
        "http://127.0.0.1:8876/phase_b_product/commercial_readiness/commercial_readiness_begin_here/commercial_readiness_begin_here.html",
        "这个地址只在你启动本机服务后可用",
        "它不会联网，也不会导入或写入任何商用证据。",
        "打开完整开始页",
        "如果想先看完整商用准备总览",
        "http://127.0.0.1:8876/phase_b_product/commercial_readiness/commercial_readiness_dashboard/commercial_readiness_dashboard.html",
        "总览页只读显示 24 个上线前事项、149 个所需证据项和 112 个仍缺生产证据，不授权上线。",
        "打开商用准备总览",
        "phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.html",
        "9 个事项可进入人工审查",
        "15 个事项仍受外部依赖阻塞",
        "不导入、不发布、不把任何事项标记为已完成。",
        "打开 64 行本地预览",
        "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_all_confirmed_values_import_preview.local.csv",
        "python3 scripts/saee_commercial_sprint_remaining_human_confirmed_values_smoke.py",
        "python3 scripts/mainline_guard.py",
        "再跑主线守卫",
        "不收集客户资料。",
        "不导入工作簿，不把事项标记为已完成。",
        "不声称生产可用、客户已验证或产品已发布。",
        "不暴露私有核心，不修改运行时、后端、内核或接口结构。",
    ]
    missing_commercial = [
        token for token in required_commercial_tokens if token not in commercial
    ]
    if missing_commercial:
        fail(
            "landing commercial-readiness.html missing tokens: "
            + ", ".join(missing_commercial)
        )
    forbidden_commercial_tokens = [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "mailto:",
        "还在 hold",
        "生产 blocker",
        "可关闭 blocker",
        "关闭 blocker",
        "当前商用证据 sprint",
        "再跑 dry-run",
        "API schema",
        "saee_v1_0",
        "selection_engine",
        "mutation_engine",
        "lineage_engine",
        "fitness_engine",
    ]
    found_commercial_forbidden = [
        token for token in forbidden_commercial_tokens if token in commercial
    ]
    if found_commercial_forbidden:
        fail(
            "landing commercial-readiness.html contains forbidden tokens: "
            + ", ".join(found_commercial_forbidden)
        )

    required_css_tokens = [
        "--palette-name: linklings-reference-cn-v25;",
        "--bg: #f5f7fb;",
        "--text: #111827;",
        "--blue: #2563eb;",
        "--blue-dark: #10213d;",
        "--blue-soft: #eef4ff;",
        "background: var(--blue);",
        "linear-gradient(135deg, #10213d 0%, #2563eb 100%)",
        "animation: visual-float 8s ease-in-out infinite;",
        ".hero-content > *",
        "animation: none;",
        ".hero-section",
        ".hero-visual",
        ".value-grid",
        ".workflow-list",
        ".demo-result-panel",
        ".demo-ranking",
        "@media (max-width: 640px)",
    ]
    missing_css = [token for token in required_css_tokens if token not in css]
    if missing_css:
        fail("landing CSS missing tokens: " + ", ".join(missing_css))

    required_app_tokens = [
        "http://127.0.0.1:8000/experiment/run",
        "landing-demo-battle",
        "decision_result",
        "recommended_agent",
        "confidence_score",
        "failure_modes_summary",
        "正在多试几轮，看看哪个更稳",
    ]
    missing_app = [token for token in required_app_tokens if token not in app]
    if missing_app:
        fail("landing app.js missing tokens: " + ", ".join(missing_app))

    required_generator_tokens = [
        "SAEE_LANDING_WORKBENCH_GIF: PASS",
        "SAEE 工作台",
        "稳定性对比",
        "推荐结果",
        "部署建议",
    ]
    missing_generator = [token for token in required_generator_tokens if token not in generator]
    if missing_generator:
        fail("landing workbench GIF generator missing tokens: " + ", ".join(missing_generator))

    required_boundary_tokens = [
        "local_static_page: true",
        "graphite_teal_palette_v0_2: false",
        "clean_cobalt_white_palette_v0_3: false",
        "soft_openai_green_palette_v0_4: false",
        "clean_blue_white_palette_v0_5: false",
        "warm_graphite_sage_palette_v0_6: false",
        "clean_mono_blue_palette_v0_7: false",
        "openai_sage_palette_v0_8: false",
        "warm_neutral_palette_v0_9: false",
        "clean_cloud_indigo_palette_v1_0: false",
        "openai_warm_sage_palette_v1_1: false",
        "openai_neutral_sage_palette_v1_2: false",
        "openai_soft_graphite_blue_palette_v1_3: false",
        "openai_warm_graphite_sage_palette_v1_4: false",
        "openai_clean_graphite_mint_palette_v1_5: false",
        "clean_ink_blue_palette_v1_6: false",
        "soft_graphite_teal_palette_v1_7: false",
        "calm_open_blue_palette_v1_8: false",
        "openai_soft_sage_palette_v1_9: false",
        "openai_mono_mint_palette_v2_0: false",
        "openai_clean_blue_palette_v2_1: false",
        "openai_graphite_sage_palette_v2_2: false",
        "openai_mono_cobalt_palette_v2_3: false",
        "openai_warm_sage_graphite_palette_v2_4: false",
        "openai_clean_slate_blue_palette_v2_5: false",
        "openai_soft_graphite_mint_palette_v2_6: false",
        "openai_clean_blue_mono_palette_v3_1: false",
        "openai_warm_graphite_jade_palette_v3_2: false",
        "openai_clean_mist_green_palette_v4_0: false",
        "openai_porcelain_indigo_palette_v4_1: false",
        "openai_warm_ink_sage_palette_v4_2: false",
        "openai_clean_ink_blue_palette_v4_3: false",
        "openai_soft_indigo_ink_palette_v4_4: false",
        "openai_warm_ink_jade_palette_v4_5: false",
        "openai_clean_neutral_mint_palette_v5_0: false",
        "openai_luminous_blue_palette_v5_1: false",
        "openai_calm_prism_palette_v5_2: false",
        "openai_clean_cobalt_palette_v5_3: false",
        "saee_calm_blue_palette_v7: false",
        "single_primary_blue_black_palette: false",
        "openai_soft_graphite_mint_palette_v8: false",
        "single_primary_graphite_mint_palette: false",
        "openai_clean_warm_gray_teal_palette_v9: false",
        "single_primary_graphite_palette: false",
        "openai_clean_cool_blue_palette_v10: false",
        "single_primary_cool_blue_palette: false",
        "openai_warm_graphite_sage_palette_v11: false",
        "openai_quiet_graphite_jade_palette_v13: false",
        "openai_clean_ink_blue_palette_v14: false",
        "openai_soft_ink_green_palette_v15: false",
        "openai_clean_graphite_blue_palette_v16: false",
        "ordinary_user_chinese_copy_v3: true",
        "linklings_service_cn_v18_palette: false",
        "linklings_service_blue_cn_v22_palette: false",
        "linklings_openai_service_cn_v23_palette: false",
        "linklings_reference_cn_v24_palette: true",
        "linklings_like_service_page_structure: true",
        "openai_soft_graphite_sage_palette_v17: false",
        "single_primary_sage_graphite_palette: false",
        "single_primary_graphite_jade_palette: false",
        "single_primary_ink_blue_palette: false",
        "single_primary_ink_green_palette: false",
        "single_primary_graphite_blue_palette: false",
        "toned_down_hero_workbench_animation: true",
        "soft_graphite_sage_demo_visual: false",
        "linklings_like_chinese_workbench_visual: true",
        "commercial_readiness_landing_page_v0_1: true",
        "source_commercial_readiness_landing_page: phase_b_product/landing/commercial-readiness.html",
        "commercial_readiness_landing_page_points_to_begin_here: true",
        "commercial_readiness_landing_page_points_to_human_action_board: true",
        "commercial_readiness_landing_page_local_root_bridge: true",
        "commercial_readiness_landing_page_local_root_bridge_external_calls: false",
        "commercial_readiness_landing_page_local_root_bridge_writes_files: false",
        "commercial_readiness_landing_page_local_root_bridge_imports_evidence: false",
        "commercial_readiness_landing_page_local_root_bridge_closes_blockers: false",
        "commercial_readiness_local_root_bridge_command: python3 -m http.server 8876 --bind 127.0.0.1",
        "commercial_readiness_begin_here_local_url: http://127.0.0.1:8876/phase_b_product/commercial_readiness/commercial_readiness_begin_here/commercial_readiness_begin_here.html",
        "commercial_readiness_dashboard_local_url: http://127.0.0.1:8876/phase_b_product/commercial_readiness/commercial_readiness_dashboard/commercial_readiness_dashboard.html",
        "commercial_readiness_landing_page_points_to_dashboard: true",
        "commercial_readiness_dashboard_bridge_external_calls: false",
        "commercial_readiness_dashboard_bridge_writes_files: false",
        "commercial_readiness_dashboard_bridge_imports_evidence: false",
        "commercial_readiness_dashboard_bridge_closes_blockers: false",
        "commercial_readiness_landing_page_authorizes_import: false",
        "commercial_readiness_landing_page_authorizes_blocker_closure: false",
        "commercial_readiness_landing_page_authorizes_launch: false",
        "product_launched: false",
        "public_sdk_release: false",
        "production_deployed: false",
        "customer_contacted: false",
        "private_core_exported: false",
        "implementation_disclosed: false",
    ]
    missing_readme = [token for token in required_boundary_tokens if token not in readme]
    if missing_readme:
        fail("landing README missing boundary tokens: " + ", ".join(missing_readme))
    missing_gate = [token for token in required_boundary_tokens if token not in gate]
    if missing_gate:
        fail("landing gate missing boundary tokens: " + ", ".join(missing_gate))

    print(
        "SAEE_LANDING_PAGE_SMOKE: PASS "
        "static_page=true asset_file_reference=true api_integration_script=true base64_embed=false "
        "product_launched=false implementation_disclosed=false"
    )


if __name__ == "__main__":
    main()
