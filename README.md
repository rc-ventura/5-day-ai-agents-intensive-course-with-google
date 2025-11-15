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

- **day02-tools/**  
  Introduction to tools invoked by the agent, including examples of:
  - Simple tools (e.g., utility calls);  
  - Tools with *human-in-the-loop* (you approve/provide answers for the agent).

- **day03-session/**  
  Focus on session state and persistence with SQLite:
  - **simple_stateful_agent_d03/** – agent with in-memory sessions, showing how context is kept across turns while the process is running.
  - **sqlite_stateful_agent_d03/** – agent using `DatabaseSessionService` (SQLite), persisting events and allowing you to resume sessions after the process ends.
  - **context_compaction_agent_d03/** – similar research agent, but with `EventsCompactionConfig` enabled, demonstrating history compaction (event summarization) to control LLM context size.
  - **session_as_tool_agent_d03/** – example where tools write to and read from `ToolContext.state`, storing user information (name, country, etc.) in the session and showing how the agent can “remember” data between turns.

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

> https://github.com/your-username/ai-agents-capstone

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
