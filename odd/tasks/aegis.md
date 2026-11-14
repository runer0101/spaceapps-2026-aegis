# AEGIS — Crew Health Sentinel

NASA Space Apps Challenge 2026 · challenge *Create Health Monitoring Software for Astronauts on Space Missions* (Human Exploration · Software · Space Exploration, Intermediate, CSA). Event window: 14–16 November 2026. Feature branch: `feature/aegis`.

Deliverable: a browser demo that simulates mission scenarios, streams crew health telemetry over a bus, renders the crew and ship in 3D, and raises explainable, source-cited alerts.

## Specs

S1 — Multi-scenario simulation with many variables. The product runs several "what could happen in space" scenarios, not one.
Verbatim: «ban hacer barios esenario queremos hacer simulaciones de que puede pasr en el espacio y hay muchas bariables con modelo 3d con los esenarios»

S2 — 3D scenario viewer. Scenarios are rendered with a 3D model, wired to the telemetry bus so the renderer is replaceable.
Verbatim (sketch): «Unity 3D», «C#», «Telemetría → 3D».
Decision of record: delivered viewer runs in the browser; Unity may attach to the same stream later.

S3 — Telemetry bus between app and hardware.
Verbatim (sketch): «App ⇄ MQTT».
Verbatim decision: «Todo simulado, MQTT opcional».

S4 — Dashboard with live visualization.
Verbatim (sketch): «Dashboard», «Visual».

S5 — AI module.
Verbatim (sketch): «IA».

S6 — Star scenario: solar storm during a Mars transit, radiation-driven.
Verbatim decision: «Tormenta solar en misión a Marte (radiación)».

S7 — Stack: Python for data, JavaScript for the app. No Rust.
Verbatim decision: «Sin Rust: Python para datos, JS para la app».

S8 — Out of scope: the power subsystem. No AC/DC, no 220 V, no RC/`Ceq` circuit modelling.
Verbatim: «eso de ac dc es de otro tema no es relevante para el proyecto todo lo demas si»

S9 — Crew health is the challenge subject: astronauts track and act on their own health status on long missions. Thresholds must cite a public source; no invented physiology.

## Tasks

| ID | Spec | Route | What completes it |
| --- | --- | --- | --- |
| T1 | S1, S6, S9 | inline | Repo scaffold, sample data contract, feature doc |
| T2 | S6, S9 | inline | Real DONKI SEP + OSDR study data, verified against known values |
| T3 | S1, S6, S9 | inline | Scenario engine: Mars transit timeline, radiation dose, physiology model |
| T4 | S3, S4 | inline | Telemetry server: SSE stream, scenario control, MQTT-compatible payload |
| T5 | S4, S5 | delegate | Dashboard: live charts, explainable alerts, AI summary with declared limits |
| T6 | S2 | delegate | 3D viewer: ship and astronaut, state by colour, driven by the same stream |
| T7 | all | inline | README, license, verification script, video script, impact sentence |

## Log

L1 (user, verbatim): «hola estamos en hackaton este es tema que haremos bre preparando https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/»

L2 (user, verbatim, with sketch `/home/runer/Downloads/080a2760-33f6-4688-b28a-2dbbd91d41b6.jpeg`): «ban hacer barios esenario queremos hacer simulaciones de que puede pasr en el espacio y hay muchas bariables con modelo 3d con los esenarios»

L3 (user, verbatim, decisions): «eso de ac dc es de otro tema no es relevante para el proyecto todo lo demas si» · «Todo simulado, MQTT opcional» · «Tormenta solar en misión a Marte (radiación)» · «Sin Rust: Python para datos, JS para la app»

L4 (evidence, verified 2026-11-14 from this machine): DONKI SEP returns real events — 27 in 2024-05-01..2024-06-30 (the May 2024 storm series), 13 in 2025-01-01..2025-03-01, 11 in 2026-08-06..2026-10-04. OSDR returns 54 studies for "bone loss" (19 ALSDA with DXA/micro-CT/histomorphometry). NTRS search API returns results. PDS MSL RAD index exceeded a 30 s timeout and is treated as unavailable.
