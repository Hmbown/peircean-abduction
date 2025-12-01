# 🕵️ Peircean Abduction
### A Logic Harness for Abductive Inference

> *"Abduction is the process of forming an explanatory hypothesis. It is the only logical operation which introduces any new idea."*
> — Charles Sanders Peirce

**Peircean Abduction** turns your LLM into a rigorous detective. It forces models to stop guessing and start reasoning.

Most LLMs are great at *deduction* (applying rules) and *induction* (finding patterns), but terrible at **abduction**—the art of explaining *why* something weird just happened. This MCP server fixes that by enforcing a strict, 3-phase logic loop: **Observe → Hypothesize → Evaluate.**

---

## 🛰️ The Case of the "Defunct" Satellite

Imagine you are an intelligence analyst. You receive a disturbing report:

> **Observation:** A "defunct" satellite, claimed by Country A to be space debris, executed a controlled burn 10 seconds before colliding with a space station.
> **Context:** Country A insists it was an accident. Flight logs recovered later show the thrusters fired intentionally.

You feed this into **Peircean Abduction**. It doesn't just summarize the text. It investigates.

### Phase 1: The Observation
The system flags the anomaly: *Debris follows Keplerian orbits. It does not steer.*
**Surprise Score:** 0.99 (Extremely Anomalous)

### Phase 2: The Hypotheses
The model generates competing explanations, not just one answer:

*   **Hypothesis 1 (The Sleeper):** The satellite was a dormant Kinetic Anti-Satellite (ASAT) weapon, activated for a covert strike.
*   **Hypothesis 2 (The Glitch):** An automated "end-of-life" deorbit script triggered erroneously, coincidentally steering it into the target.
*   **Hypothesis 3 (The Frame-Job):** A third-party actor hacked the satellite's command link to frame Country A for an act of war.

### Phase 3: The Verdict (Inference to Best Explanation)
The **Council of Critics** (a simulated debate between a Logician, Empiricist, and Scientist) weighs the evidence.

> **Verdict:** **Hypothesis 1 (The Sleeper)** is the best explanation.
> *Reasoning:* The precision of the burn (steering *into* the target) makes H2 statistically impossible. H3 is plausible but lacks evidence of signal intrusion. H1 explains all facts with the fewest assumptions.

---

## 🚀 Quick Start

### 1. Install
```bash
pip install peircean-abduction
```

### 2. Connect (Claude Desktop / Cursor)
Run the auto-installer to register the MCP server:
```bash
peircean --install
```

### 3. Solve a Mystery
Open Claude and ask:
> "Use the `peircean_observe_anomaly` tool. A satellite just maneuvered before impact. Country A says it was debris. Analyze this."

---

## ✨ Features

*   **🧠 MCP-First Architecture:** Designed to plug directly into Claude Desktop, Cursor, and other agentic IDEs.
*   **⚖️ The Council of Critics:** Every hypothesis is grilled by a panel of simulated experts (Logician, Empiricist, Probability Theorist) before being accepted.
*   **🔌 Provider Agnostic:** Works with **Anthropic**, **OpenAI**, **Gemini**, and **Ollama**.
*   **🔓 No API Key Required:** By default, it generates the *prompts* for you to run. You only need keys if you want it to execute the reasoning loop autonomously.

## 📦 Supported Models

Peircean Abduction is designed to be provider-agnostic and supports the latest models from:

*   **Anthropic** (Claude)
*   **OpenAI** (GPT)
*   **Google DeepMind** (Gemini)
*   **Ollama** (Local models)

## 📚 Documentation

*   [Installation Guide](docs/getting-started/installation.md)
*   [Configuration Guide](docs/guides/configuration.md)
*   [API Reference](docs/api/reference.md)

## 📄 License

MIT License. Use it to solve crimes, debug code, or understand the universe.
