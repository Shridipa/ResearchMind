# Phase 3: Multi-Agent Framework Architecture

## Architecture Overview

The Multi-Agent framework establishes a distributed intelligence model where complex tasks are decomposed into specialized personas. Each agent focuses on a specific aspect of the cognitive pipeline.

### Agents Implemented:
1. **Planner Agent**: Decomposes high-level requests into a sequence of actionable subtasks.
2. **Retrieval Agent**: Interfaces with the Vector Store to find relevant context and ground truth.
3. **Research Agent**: Synthesizes retrieved documents to extract concrete evidence.
4. **Reasoning Agent**: Analyzes the gathered evidence to find patterns and draw conclusions.
5. **Decision Agent**: Translates conclusions into strategic, actionable recommendations.
6. **Summarizer Agent**: Compiles the analysis and recommendations into a coherent executive report.

### Design Decisions:

* **State-Driven execution**: All agents implement a generic `run(state: Dict)` method. They read from and write to a shared dictionary. This strongly decouples the agents from each other, allowing us to orchestrate them in arbitrary graphs (which we will do in Phase 4 via LangGraph).
* **BaseAgent class**: Encapsulates common functionality like tool execution and LLM instantiation via the `get_llm_provider()` factory. This ensures that every agent automatically uses the correct underlying LLM (e.g., Bedrock) configured by the environment.
* **Separation of Concerns**: By splitting Retrieval from Research, and Reasoning from Decision-making, we dramatically reduce the cognitive load on the LLM per prompt, which significantly lowers the hallucination rate (as evaluated in Phase 10).
