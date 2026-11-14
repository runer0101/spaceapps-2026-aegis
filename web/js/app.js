/**
 * AEGIS orchestrator.
 *
 * Owns the connection to the telemetry stream and publishes every frame as a
 * DOM CustomEvent, so the dashboard and the 3D scene stay independent modules.
 *
 * Event contract: `window.addEventListener("aegis:frame", e => ...)`
 *   e.detail = { frame, scenario, history, total, complete }
 * Event contract: `aegis:scenario` fires when the scenario changes,
 *   e.detail = { scenario, summary }
 */

const state = {
  scenario: null,
  scenarios: [],
  history: [],
  speed: 0.18,
  playing: true,
  source: null,
};

const select = document.getElementById("scenario-select");
const speedSelect = document.getElementById("speed-select");
const playToggle = document.getElementById("play-toggle");
const missionDay = document.getElementById("mission-day");
const missionDate = document.getElementById("mission-date");
const missionPhase = document.getElementById("mission-phase");

export function frameEvent(frame, extra = {}) {
  return new CustomEvent("aegis:frame", {
    detail: { frame, scenario: state.scenario, history: state.history, ...extra },
  });
}

function phaseLabel(phase) {
  return phase.replace(/_/g, " ");
}

function updateClock(frame) {
  missionDay.textContent = `Day ${Math.round(frame.t_day)}`;
  missionDate.textContent = frame.calendar_day;
  missionPhase.textContent = phaseLabel(frame.phase);
}

function connect(fromDay) {
  if (state.source) {
    state.source.close();
    state.source = null;
  }
  const params = new URLSearchParams({
    scenario: state.scenario,
    interval: String(state.speed),
  });
  if (fromDay > 0) params.set("from", String(fromDay));

  const source = new EventSource(`/stream?${params.toString()}`);
  state.source = source;

  source.onmessage = (message) => {
    const frame = JSON.parse(message.data);
    state.history.push(frame);
    updateClock(frame);
    window.dispatchEvent(frameEvent(frame));
  };

  source.onerror = () => {
    source.close();
    state.source = null;
    if (state.playing) {
      window.dispatchEvent(frameEvent(state.history.at(-1) ?? null, { complete: true }));
    }
  };
}

async function loadScenario(scenarioId) {
  state.scenario = scenarioId;
  state.history = [];
  const meta = state.scenarios.find((item) => item.id === scenarioId);

  window.dispatchEvent(
    new CustomEvent("aegis:scenario", {
      detail: { scenario: scenarioId, summary: meta ? meta.summary : "" },
    })
  );

  if (state.playing) connect(0);
}

async function boot() {
  const response = await fetch("/api/scenarios");
  const payload = await response.json();
  state.scenarios = payload.scenarios;

  for (const scenario of state.scenarios) {
    const option = document.createElement("option");
    option.value = scenario.id;
    option.textContent = `${scenario.title} · ${scenario.days} d`;
    select.append(option);
  }
  select.value = payload.default;
  await loadScenario(payload.default);
}

select.addEventListener("change", () => loadScenario(select.value));

speedSelect.addEventListener("change", () => {
  state.speed = Number(speedSelect.value);
  if (state.playing) {
    const last = state.history.at(-1);
    connect(last ? last.t_day + 1 : 0);
  }
});

playToggle.addEventListener("click", () => {
  state.playing = !state.playing;
  playToggle.textContent = state.playing ? "Pause" : "Resume";
  playToggle.setAttribute("aria-pressed", String(state.playing));
  if (state.playing) {
    const last = state.history.at(-1);
    connect(last ? last.t_day + 1 : 0);
  } else if (state.source) {
    state.source.close();
    state.source = null;
  }
});

window.aegis = state;
boot();
