(() => {
  const statusScenarios = [
    {
      text: "Scenario: a client requests an existing academy file with GET.",
      answer: "200",
      note: "The path is allowed and the file exists."
    },
    {
      text: "Scenario: a decoded URL path contains ../ traversal.",
      answer: "400",
      note: "Traversal is rejected as a bad request."
    },
    {
      text: "Scenario: the path starts with /private.",
      answer: "403",
      note: "The syntax is valid, but the directory root is blocked."
    },
    {
      text: "Scenario: the path is /public/missing.html.",
      answer: "404",
      note: "The directory is allowed, but the file is not present."
    },
    {
      text: "Scenario: the request method is POST.",
      answer: "405",
      note: "Only GET is supported for static file serving."
    }
  ];

  function setupThemeToggle() {
    const root = document.documentElement;
    const toggle = document.querySelector("[data-theme-toggle]");
    const label = document.querySelector("[data-theme-label]");
    const icon = document.querySelector("[data-theme-icon]");

    const savedTheme = localStorage.getItem("cna-theme");
    const initialTheme = savedTheme || "dark";

    applyTheme(initialTheme);

    if (!toggle) {
      return;
    }

    toggle.addEventListener("click", () => {
      const currentTheme = root.dataset.theme === "dark" ? "dark" : "light";
      const nextTheme = currentTheme === "dark" ? "light" : "dark";

      applyTheme(nextTheme);
      localStorage.setItem("cna-theme", nextTheme);
    });

    function applyTheme(theme) {
      const normalizedTheme = theme === "light" ? "light" : "dark";
      root.dataset.theme = normalizedTheme;

      if (label) {
        label.textContent = normalizedTheme === "dark" ? "Dark" : "Light";
      }

      if (icon) {
        icon.textContent = normalizedTheme === "dark" ? "☾" : "☀";
      }

      if (toggle) {
        toggle.setAttribute(
          "aria-label",
          normalizedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"
        );
      }
    }
  }

  function ready(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback);
    } else {
      callback();
    }
  }

  ready(() => {
    setupThemeToggle();
    setupConcurrencySimulator();
    setupStatusGame();
  });

  function setupConcurrencySimulator() {
    const root = document.querySelector("[data-concurrency-simulator]");
    if (!root) {
      return;
    }

    const countInput = root.querySelector("[data-client-count]");
    const countOutput = root.querySelector("[data-client-output]");
    const startButton = root.querySelector("[data-start-sim]");
    const resetButton = root.querySelector("[data-reset-sim]");
    const clientList = root.querySelector("[data-client-list]");
    const laneList = root.querySelector("[data-lane-list]");
    const threadList = root.querySelector("[data-thread-list]");
    const responseList = root.querySelector("[data-response-list]");
    const activeCount = root.querySelector("[data-active-count]");
    const completeCount = root.querySelector("[data-complete-count]");
    const message = root.querySelector("[data-sim-message]");
    const explanation = root.querySelector("[data-sim-explanation]");
    let timers = [];
    let completed = 0;

    function clearTimers() {
      timers.forEach((timer) => window.clearTimeout(timer));
      timers = [];
    }

    function setMessage(text) {
      message.textContent = text;
    }

    function updateCounts(total) {
      activeCount.textContent = `${Math.max(total - completed, 0)} active`;
      completeCount.textContent = `${completed} complete`;
    }

    function makeNode(tagName, className, text) {
      const node = document.createElement(tagName);
      node.className = className;
      node.textContent = text;
      return node;
    }

    function resetSimulation() {
      clearTimers();
      completed = 0;
      const total = Number(countInput.value);
      countOutput.value = String(total);
      clientList.replaceChildren();
      laneList.replaceChildren();
      threadList.replaceChildren();
      responseList.replaceChildren();

      for (let index = 1; index <= total; index += 1) {
        clientList.append(makeNode("div", "client-node", `Client ${index}`));
        laneList.append(makeNode("div", "connection-lane", "waiting"));
        threadList.append(makeNode("div", "thread-node", "idle"));
        responseList.append(makeNode("div", "response-node", "pending"));
      }

      updateCounts(total);
      setMessage("Ready to accept client connections.");

      if (explanation) {
        explanation.hidden = true;
        explanation.classList.remove("is-visible");
      }

      root.classList.remove("is-running");
    }

    function schedule(callback, delay) {
      const timer = window.setTimeout(callback, delay);
      timers.push(timer);
    }

    function startSimulation() {
      resetSimulation();

      const total = Number(countInput.value);
      const clients = [...clientList.children];
      const lanes = [...laneList.children];
      const threads = [...threadList.children];
      const responses = [...responseList.children];

      root.classList.add("is-running");
      setMessage("Clients are opening TCP connections.");

      clients.forEach((client, index) => {
        const start = index * 140;

        schedule(() => {
          client.classList.add("active");
          client.textContent = `Client ${index + 1}: TCP`;
          lanes[index].classList.add("tcp");
          lanes[index].textContent = "TCP connection";
        }, start);

        schedule(() => {
          lanes[index].classList.add("request");
          lanes[index].textContent = "HTTP request";
          threads[index].classList.add("busy");
          threads[index].textContent = `Thread ${index + 1}`;
          setMessage("The server assigns one thread per accepted connection.");
        }, start + 420);

        schedule(() => {
          lanes[index].classList.add("response");
          responses[index].classList.add("done");
          responses[index].textContent = "HTTP/1.0 200 OK";
          threads[index].classList.remove("busy");
          threads[index].classList.add("done");
          clients[index].classList.add("done");

          completed += 1;
          updateCounts(total);

          if (completed === total) {
            root.classList.remove("is-running");
            setMessage("All responses returned. Each connection is closed.");

            if (explanation) {
              explanation.hidden = false;
              window.requestAnimationFrame(() => {
                explanation.classList.add("is-visible");
              });
            }
          }
        }, start + 900 + (index % 4) * 120);
      });
    }

    countInput.addEventListener("input", resetSimulation);
    startButton.addEventListener("click", startSimulation);
    resetButton.addEventListener("click", resetSimulation);

    resetSimulation();
  }

  function setupStatusGame() {
    const root = document.querySelector("[data-status-game]");
    if (!root) {
      return;
    }

    const scenarioText = document.querySelector("#scenario-text");
    const result = document.querySelector("#status-result");
    const nextButton = root.querySelector("[data-next-scenario]");
    const answerButtons = [...root.querySelectorAll("[data-answer]")];
    let scenarioIndex = 0;
    let score = 0;
    let attempts = 0;

    function renderScenario() {
      const scenario = statusScenarios[scenarioIndex];
      scenarioText.textContent = scenario.text;

      answerButtons.forEach((button) => {
        button.disabled = false;
        button.classList.remove("correct", "wrong");
      });
    }

    answerButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const scenario = statusScenarios[scenarioIndex];
        attempts += 1;

        if (button.dataset.answer === scenario.answer) {
          score += 1;
          button.classList.add("correct");
          result.textContent = `Correct. ${scenario.note} Score: ${score} / ${attempts}`;
        } else {
          button.classList.add("wrong");
          result.textContent = `Not this one. ${scenario.note} Score: ${score} / ${attempts}`;
        }

        answerButtons.forEach((choice) => {
          choice.disabled = true;

          if (choice.dataset.answer === scenario.answer) {
            choice.classList.add("correct");
          }
        });
      });
    });

    nextButton.addEventListener("click", () => {
      scenarioIndex = (scenarioIndex + 1) % statusScenarios.length;
      renderScenario();
    });

    renderScenario();
  }
})();