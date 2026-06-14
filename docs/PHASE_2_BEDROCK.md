# Phase 2: AWS Bedrock Integration Architecture

## Architecture Overview

The Bedrock Service Layer acts as an enterprise-grade LLM provider abstraction, connecting our AI Operations Platform to Amazon Web Services' Foundation Models.

### Core Capabilities:

1.  **Provider Support**:
    *   **Claude 3**: Handled via `anthropic_version` specific payloads. High-reasoning tasks.
    *   **Titan**: Amazon's native models, supporting `inputText` format. Good for embeddings (future) and simple generative tasks.
    *   **Nova**: Next-generation models, handled via the new `inferenceConfig` schema.

2.  **Enterprise Features**:
    *   **Retry Handling**: Implemented using `tenacity` (`@retry`). It exponentially backs off upon encountering `ClientError` (specifically `ThrottlingException` and `RateLimitError`).
    *   **Rate Limiting**: An `asyncio.Semaphore` ensures we do not flood the Bedrock API with more than 10 concurrent requests per worker, preventing immediate throttling.
    *   **Token Tracking & Cost Estimation**: Each response parses the specific token counts from the Bedrock response body (`usage.input_tokens`, etc.) and calculates USD costs using a predefined `COST_ESTIMATION` matrix.
    *   **Streaming Responses**: The `invoke_model_with_response_stream` API is fully supported, parsing model-specific streaming chunk deltas.

### Design Decisions:

*   **Abstraction Layer**: `BedrockLLM` inherits from our `LLMProvider` base class. This allows the rest of the application (e.g., Agents) to remain entirely agnostic of the underlying model. We can swap between OpenAI, Gemini, OpenRouter, and Bedrock just by changing the `LLM_PROVIDER` environment variable.
*   **Asynchronous Execution**: Although `boto3` is synchronous, we use `asyncio.to_thread` to ensure we do not block the main FastAPI event loop, retaining high concurrency for the platform.
