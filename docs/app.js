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

  function readOptionalPreviewValue(name) {
    const directValue = window[name];
    if (typeof directValue === "string" && directValue.trim()) {
      return directValue.trim();
    }
    try {
      const storedValue = window.localStorage && window.localStorage.getItem(name);
      return typeof storedValue === "string" ? storedValue.trim() : "";
    } catch (error) {
      return "";
    }
  }

  function authorizationValue() {
    const header = readOptionalPreviewValue("SAEE_PREVIEW_AUTHORIZATION");
    if (header) {
      return header.startsWith("Bearer ") ? header : `Bearer ${header}`;
    }
    const token = readOptionalPreviewValue("SAEE_PREVIEW_TOKEN");
    if (!token) {
      return "";
    }
    return token.startsWith("Bearer ") ? token : `Bearer ${token}`;
  }

  function requestHeaders() {
    const headers = { "Content-Type": "application/json" };
    const authorization = authorizationValue();
    const role = readOptionalPreviewValue("SAEE_PREVIEW_ROLE");
    const tenantId = readOptionalPreviewValue("SAEE_PREVIEW_TENANT_ID");
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
    return {
      experiment_id: "landing-demo-battle",
      agents: [
        {
          agent_id: "agent-a",
          config: { policy: "aggressive experimental risky unguarded fragile" },
          type: "llm"
        },
        {
          agent_id: "agent-b",
          config: { workflow: "guarded stable monitor retry bounded safe" },
          type: "workflow"
        },
        {
          agent_id: "agent-c",
          config: "rule:conservative bounded retry",
          type: "rule"
        }
      ],
      environment: {
        scenario_type: "landing_demo_competition",
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

  function renderResult(result) {
    const decision = result.decision_result || {};
    const items = decision.ranking || [];
    const recommended = decision.recommended_agent || result.recommended_agent || "unavailable";
    const score = Number(decision.confidence_score || result.confidence_score || 0);

    recommendedAgent.textContent = recommended;
    confidence.textContent = `Confidence ${score.toFixed(6)}`;
    winnerMark.textContent = recommended.split("-").pop().slice(0, 1).toUpperCase();
    hint.textContent = "SAEE returned a deterministic deployment recommendation from the local decision engine.";
    output.hidden = false;

    renderList(ranking, items, (element, item) => {
      const span = document.createElement("span");
      span.textContent = `#${item.rank} ${item.agent_id}`;
      const strong = document.createElement("strong");
      strong.textContent = Number(item.score).toFixed(6);
      element.appendChild(span);
      element.appendChild(strong);
    });

    const summary = decision.failure_modes_summary || {};
    const failureItems = Object.entries(summary).map(([agentId, modes]) => ({
      agentId,
      modes: modes.length ? modes.join(", ") : "none"
    }));
    renderList(failures, failureItems, (element, item) => {
      const span = document.createElement("span");
      span.textContent = item.agentId;
      const strong = document.createElement("strong");
      strong.textContent = item.modes;
      element.appendChild(span);
      element.appendChild(strong);
    });
  }

  function renderError(error) {
    output.hidden = true;
    hint.textContent = `Backend unavailable: ${error.message}. Start the local API with python3 -m uvicorn saee_backend.main:app --reload --port 8000.`;
  }

  async function runDemoBattle() {
    button.disabled = true;
    setStatus("Running", "running");
    hint.textContent = "Running SAEE Evaluation...";
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
      setStatus("Decision ready", "ready");
    } catch (error) {
      renderError(error);
      setStatus("Backend offline", "error");
    } finally {
      button.disabled = false;
    }
  }

  if (button) {
    button.addEventListener("click", runDemoBattle);
  }
})();
