# 🚀 5-Day AI Agents Intensive Course with Google (Google ADK)

This repository accompanies the **5-Day AI Agents Intensive Course with Google**, a hands-on, online program created by Google’s ML researchers and engineers.

## 📚 About this course

Welcome to our 5-Day AI Agents Intensive Course with Google!

This 5-day online course was crafted by Google’s ML researchers and engineers to help developers explore the foundations and practical applications of AI agents. You’ll learn the core components – models, tools, orchestration, memory, and evaluation. Finally, you’ll discover how agents move beyond LLM prototypes to become production-ready systems.

Each day blends conceptual deep dives with hands-on examples, codelabs, and live discussions. By the end, you’ll be ready to build, evaluate, and deploy agents that solve real-world problems.

This course is also a **Kaggle initiative**. You can find the official course page and resources here:

> https://www.kaggle.com/learn-guide/5-day-agents

All live sessions are available in the following YouTube playlist:

> https://www.youtube.com/playlist?list=PLqFaTIg4myu9r7uRoNfbJhHUbLp-1t1YE

Each `dayXX-*` folder in this repo represents an incremental content block, with examples ranging from a simple agent to agents with persistent state, tools, and context compaction.

## 📁 Repository structure

- **day01-agentic/**  
  Basic agent concepts and event flow with ADK.

- **day02-tools_agent/**  
  Introduction to tools invoked by the agent, including examples of:
  - Simple tools (e.g., utility calls);  
  - Tools with *human-in-the-loop* (you approve/provide answers for the agent).

- **day03-memory_agent/**  
  Focus on session state, persistence, and agent memory patterns:
  - **3_1_simple_stateful_agent/** – agent with in-memory sessions, showing how context is kept across turns while the process is running.
  - **3_2_session_as_tool_agent/** – tools that read/write `ToolContext.state`, storing user/session data.
  - **3_3_sqlite_stateful_agent/** – agent using `DatabaseSessionService` (SQLite) to persist events and resume sessions.
  - **3_4_ingest_memory_agent/** – demonstrates ingesting session information into `MemoryService` so it can be reused beyond a single conversation.
  - **3_5_proactive_load_memory_agent/** – uses `preload_memory` to proactively retrieve memories before responding.
  - **3_6_reactive_load_memory_agent/** – uses `load_memory` to reactively fetch relevant memories when needed.
  - **3_8_auto_save_memory_agent/** – shows how to automatically save sessions to `MemoryService` and later search those memories.

- **day04-quality_agent/**  
  Agent quality, observability, and evaluation:
  - **4_1_basic_log_agent/** – agent with basic logging and a research-paper search flow, used to demonstrate type errors and debugging via logs.
  - **4_2_plugins_hook_agent/** – adds plugins (callbacks) to count invocations and record events for observability.
  - **4_3_evaluation_agent/** – interactive evaluation examples in the ADK Web UI, with `*.evalset.json` generated from real sessions.
  - **4_4_system_evaluation_agent/** – systematic evaluation via CLI using `adk eval`, with `test_config.json` and `integration.evalset.json`.
  - **4_5_user_simulation_agent/** – home-automation agent used to demonstrate *User Simulation* with `conversation_scenarios.json`, `session_input.json`, and metric configuration in `eval_config_user_sim.json`.

## 🧠 Key concepts covered

- **🤖 Runner and Agents**  
  Use of `LlmAgent`, `Runner`, and `App` to define flows, the application root, and agent composition.

- **🧰 Tools**  
  How to expose Python functions as tools to the model (`tools=[...]`), and how the ADK routes the model’s `function_call` to those functions.

- **💾 Sessions and persistence**  
  - In-memory sessions (`InMemorySessionService`);  
  - Persistent sessions with `DatabaseSessionService` using SQLite (`my_agent_data.db`);  
  - Inspecting events and content stored in the database.

- **🗂️ State in Tools**  
  - Using `ToolContext.state` and prefixes (e.g., `user:name`, `user:country`) to differentiate scopes and let the agent retrieve user information in future turns.

- **🧹 Context compaction (Events Compaction)**  
  Configuring `EventsCompactionConfig` to summarize/compact older events after a certain number of interactions, keeping useful context without exceeding model context limits.

## 🗄️ Database files

Some examples use SQLite (typically files like `my_agent_data.db` inside the day folders).  
They are created and managed by the example scripts and can be safely removed if you want to start from scratch – the scripts will recreate the database as needed.

> **Tip:** if you want a clean state, simply delete the `*.db` files inside `day03-session/**` before running the examples again.

## 🎓 Capstone (Final Project)

At the end of the course, you can build a **capstone project** that integrates several concepts:

- Orchestrating multiple agents (for example: researcher, writer, evaluator).
- Combining external tools (APIs), session state, and context compaction.
- Persisting logs, sessions, and results in a database.

A possible repository for this capstone (fictional link) could be:

> https://github.com/rc-ventura/5-day-ai-agents-intensive-course-with-google/tree/master/capstone

There you could organize a more complete agent, for example: an assistant that researches, plans, and executes study or software-development tasks using the ADK.

## ▶️ How to run the examples

1. Create and activate a virtual environment (or use your Conda environment).  
2. Install the required dependencies for the Google ADK and Gemini client (as described in the course).  
3. Configure your environment variables (e.g., Gemini API key) via `.env`.  
4. Change into the folder of the example you want to run and execute:

```bash
python agent.py
```

Each subfolder contains an `agent.py` with a specific flow, commented step by step.

### Day 4 – Evaluation (CLI)

In addition to running `python agent.py`, Day 4 also includes evaluation flows
using the `adk eval` CLI.

From the repository root:

```bash
cd day04-quality_agent
```

- **System evaluation (4_4_system_evaluation_agent)**

  ```bash
  adk eval \
    4_4_system_evaluation_agent \
    4_4_system_evaluation_agent/integration.evalset.json \
    --config_file_path=4_4_system_evaluation_agent/test_config.json \
    --print_detailed_results
  ```

- **User Simulation evaluation (4_5_user_simulation_agent)**

  1. Create the EvalSet (once):

     ```bash
     adk eval_set create \
       4_5_user_simulation_agent \
       user_sim_eval_set
     ```

  2. Add conversation scenarios as eval cases:

     ```bash
     adk eval_set add_eval_case \
       4_5_user_simulation_agent \
       user_sim_eval_set \
       --scenarios_file 4_5_user_simulation_agent/conversation_scenarios.json \
       --session_input_file 4_5_user_simulation_agent/session_input.json
     ```

  3. Run the evaluation with user simulation:

     ```bash
     adk eval \
       4_5_user_simulation_agent \
       --config_file_path 4_5_user_simulation_agent/eval_config_user_sim.json \
       user_sim_eval_set \
       --print_detailed_results
     ```
