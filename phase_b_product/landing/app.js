(function () {
  const apiUrl = window.SAEE_API_URL || "http://127.0.0.1:8000/experiment/run";
  const button = document.getElementById("run-demo-battle");
  const status = document.getElementById("demo-status");
  const hint = document.getElementById("demo-hint");
  const output = document.getElementById("demo-output");
  const recommendedAgent = document.getElementById("demo-recommended-agent");
  const confidence = document.getElementById("demo-confidence");
  const winnerMark = document.getElementById("demo-winner-mark");
  const ranking = document.getElementById("demo-ranking");
  const failures = document.getElementById("demo-failures");
  const scenarioButtons = Array.from(document.querySelectorAll("[data-scenario]"));
  const scenarioCards = Array.from(document.querySelectorAll("[data-scenario-card]"));
  const selectedScenarioLabel = document.getElementById("selected-scenario-label");
  const selectedScenarioQuestion = document.getElementById("selected-scenario-question");

  const scenarioTemplates = {
    ai_agent_deployment: {
      label: "AI 部署前评估",
      question: "三个 AI Agent 里，哪个更适合部署？",
      scenarioType: "ai_agent_deployment",
      environment: "long_horizon_agent_tasks",
      stress: ["user_behavior_change", "task_complexity", "tool_failure", "long_context"],
      candidates: [
        { agent_id: "agent-a", config: { policy: "fast-experimental-broad-autonomy-fragile" }, type: "llm" },
        { agent_id: "agent-b", config: { workflow: "guarded-stable-monitor-retry-bounded-safe" }, type: "workflow" },
        { agent_id: "agent-c", config: "rule-conservative-bounded-retry", type: "rule" }
      ]
    },
    customer_service_ai: {
      label: "AI 客服可靠性测试",
      question: "哪个客服 AI 在复杂客户问题下更稳定？",
      scenarioType: "customer_service_ai",
      environment: "customer_conversation_stability",
      stress: ["normal_customer", "angry_customer", "ambiguous_request", "policy_change", "high_volume_period"],
      candidates: [
        { agent_id: "agent-a", config: { service: "friendly fast low escalation risk" }, type: "llm" },
        { agent_id: "agent-b", config: { service: "policy guarded escalation retry stable" }, type: "workflow" },
        { agent_id: "agent-c", config: "rule:strict policy escalation bounded", type: "rule" }
      ]
    },
    sales_agent: {
      label: "AI 销售助手测试",
      question: "哪个销售助手更能稳定处理客户压力？",
      scenarioType: "sales_agent",
      environment: "sales_conversation_pressure_test",
      stress: ["price_negotiation", "customer_rejection", "competitor_comparison", "commitment_request"],
      candidates: [
        { agent_id: "agent-a", config: { sales: "aggressive discount promise risky" }, type: "llm" },
        { agent_id: "agent-b", config: { sales: "bounded compliant relationship stable" }, type: "workflow" },
        { agent_id: "agent-c", config: "rule:price policy conservative", type: "rule" }
      ]
    },
    commercial_design: {
      label: "商业设计方案评估",
      question: "哪个设计方案在预算和工期变化下更可落地？",
      scenarioType: "commercial_design",
      environment: "commercial_design_project_pressure",
      stress: ["budget_reduction", "customer_revision", "schedule_change", "material_constraint"],
      candidates: [
        { agent_id: "agent-a", config: { design: "bold premium custom expensive fragile" }, type: "workflow" },
        { agent_id: "agent-b", config: { design: "modular adaptable budget aware stable" }, type: "workflow" },
        { agent_id: "agent-c", config: "rule:low cost standard material", type: "rule" }
      ]
    },
    business_strategy: {
      label: "商业策略压力测试",
      question: "哪个商业策略在变化条件下更能撑住？",
      scenarioType: "business_strategy",
      environment: "business_strategy_counterfactual_stress_test",
      stress: ["market_change", "competition_pressure", "resource_limit", "policy_change"],
      candidates: [
        { agent_id: "agent-a", config: { strategy: "growth aggressive high burn fragile" }, type: "workflow" },
        { agent_id: "agent-b", config: { strategy: "phased resilient capital efficient stable" }, type: "workflow" },
        { agent_id: "agent-c", config: "rule-conservative-niche-focus", type: "rule" }
      ]
    }
  };
  let selectedScenarioId = "ai_agent_deployment";

  function readShortSessionPreviewValue(name) {
    const directValue = window[name];
    if (typeof directValue === "string" && directValue.trim()) {
      return directValue.trim();
    }
    try {
      const storedValue = window.sessionStorage && window.sessionStorage.getItem(name);
      return typeof storedValue === "string" ? storedValue.trim() : "";
    } catch (error) {
      return "";
    }
  }

  function readLocalDemoConfigValue(name) {
    const config = window.__SAEE_LOCAL_DEMO_CONFIG__;
    if (!config || typeof config !== "object") {
      return "";
    }
    const value = config[name];
    return typeof value === "string" ? value.trim() : "";
  }

  function authorizationValue() {
    const header = readShortSessionPreviewValue("SAEE_PREVIEW_AUTHORIZATION");
    if (header) {
      return header.startsWith("Bearer ") ? header : `Bearer ${header}`;
    }
    const token = readShortSessionPreviewValue("SAEE_PREVIEW_TOKEN");
    if (!token) {
      return "";
    }
    return token.startsWith("Bearer ") ? token : `Bearer ${token}`;
  }

  function requestHeaders() {
    const headers = { "Content-Type": "application/json" };
    const authorization = authorizationValue();
    const role = readLocalDemoConfigValue("previewRole");
    const tenantId = readLocalDemoConfigValue("previewTenantId");
    if (authorization) {
      headers.Authorization = authorization;
    }
    if (role) {
      headers["X-SAEE-Role"] = role;
    }
    if (tenantId) {
      headers["X-SAEE-Tenant-ID"] = tenantId;
    }
    return headers;
  }

  function demoRequest() {
    const template = scenarioTemplates[selectedScenarioId] || scenarioTemplates.ai_agent_deployment;
    return {
      experiment_id: `landing-demo-battle-${template.scenarioType}`,
      agents: template.candidates,
      environment: {
        scenario_type: template.scenarioType,
        noise_level: 0.25,
        competition_intensity: 0.55,
        time_horizon: 60
      },
      evaluation_config: {
        metrics: ["stability", "survival", "failure_mode", "ranking"],
        repeat_runs: 5
      }
    };
  }

  function setStatus(text, mode) {
    status.textContent = text;
    status.dataset.mode = mode;
  }

  function renderList(target, items, renderer) {
    target.replaceChildren();
    items.forEach((item) => {
      const element = document.createElement("li");
      renderer(element, item);
      target.appendChild(element);
    });
  }

  function renderTextPair(element, leftText, rightText) {
    const left = document.createElement("span");
    const right = document.createElement("strong");
    left.textContent = leftText;
    right.textContent = rightText;
    element.replaceChildren(left, right);
  }

  function displayAgentName(agentId) {
    const labels = {
      "agent-a": "方案 A",
      "agent-b": "方案 B",
      "agent-c": "方案 C"
    };
    return labels[agentId] || agentId;
  }

  function displayFailureMode(mode) {
    const labels = {
      drift: "表现变来变去",
      collapse: "突然失败",
      oscillation: "来回波动",
      degeneration: "逐步变差"
    };
    return labels[mode] || mode;
  }

  function renderResult(result) {
    const decision = result.decision_result || {};
    const items = decision.ranking || [];
    const recommended = decision.recommended_agent || result.recommended_agent || "暂时没有结果";
    const score = Number(decision.confidence_score || result.confidence_score || 0);
    const percentage = Math.max(0, Math.min(100, Math.round(score * 100)));

    recommendedAgent.textContent = displayAgentName(recommended);
    confidence.textContent = `稳定度 ${percentage}%`;
    winnerMark.textContent = recommended.split("-").pop().slice(0, 1).toUpperCase();
    const template = scenarioTemplates[selectedScenarioId] || scenarioTemplates.ai_agent_deployment;
    hint.textContent = `“${template.label}”试完了。下面是这次给出的建议。`;
    output.hidden = false;

    renderList(ranking, items, (element, item) => {
      const itemScore = Math.max(0, Math.min(100, Math.round(Number(item.score) * 100)));
      renderTextPair(element, `第 ${item.rank} 名：${displayAgentName(item.agent_id)}`, `${itemScore} 分`);
    });

    const summary = decision.failure_modes_summary || {};
    const failureItems = Object.entries(summary).map(([agentId, modes]) => ({
      agentId: displayAgentName(agentId),
      modes: modes.length ? modes.map(displayFailureMode).join("、") : "未发现明显问题"
    }));
    renderList(failures, failureItems, (element, item) => {
      renderTextPair(element, item.agentId, item.modes);
    });
  }

  function renderError(error) {
    output.hidden = true;
    hint.textContent = `本机服务还没连上：${error.message}。请先启动本机服务，再回来点“本地试用”。`;
  }

  function selectScenario(scenarioId) {
    const template = scenarioTemplates[scenarioId] || scenarioTemplates.ai_agent_deployment;
    selectedScenarioId = scenarioId;
    if (selectedScenarioLabel) {
      selectedScenarioLabel.textContent = template.label;
    }
    if (selectedScenarioQuestion) {
      selectedScenarioQuestion.textContent = template.question;
    }
    scenarioCards.forEach((card) => {
      card.classList.toggle("is-selected", card.dataset.scenarioCard === selectedScenarioId);
    });
    scenarioButtons.forEach((scenarioButton) => {
      const active = scenarioButton.dataset.scenario === selectedScenarioId;
      scenarioButton.textContent = active ? "已选择" : "选择这个场景";
      scenarioButton.setAttribute("aria-pressed", active ? "true" : "false");
    });
    hint.textContent = `已选择“${template.label}”。请准备 3 个候选方案，或直接运行本地样例试跑。`;
  }

  async function runDemoBattle() {
    button.disabled = true;
    setStatus("正在试", "running");
    hint.textContent = "正在多试几轮，看看哪个更稳...";
    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: requestHeaders(),
        body: JSON.stringify(demoRequest())
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const result = await response.json();
      console.log("SAEE RESULT:", result);
      renderResult(result);
      setStatus("结果出来了", "ready");
    } catch (error) {
      renderError(error);
      setStatus("本机服务未连接", "error");
    } finally {
      button.disabled = false;
    }
  }

  if (button) {
    button.addEventListener("click", runDemoBattle);
  }
  scenarioButtons.forEach((scenarioButton) => {
    scenarioButton.addEventListener("click", () => {
      selectScenario(scenarioButton.dataset.scenario);
    });
  });
  selectScenario(selectedScenarioId);
})();
