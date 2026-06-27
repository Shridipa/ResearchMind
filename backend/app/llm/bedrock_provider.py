import json
import logging
from typing import AsyncGenerator
import asyncio

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None  # type: ignore
try:
    from botocore.exceptions import ClientError
except ImportError:  # pragma: no cover
    ClientError = Exception  # type: ignore
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.llm.base_provider import LLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

# Basic cost estimation mapping per 1k tokens (input, output) in USD
COST_ESTIMATION = {
    "anthropic.claude-3-sonnet-20240229-v1:0": (0.003, 0.015),
    "anthropic.claude-3-haiku-20240307-v1:0": (0.00025, 0.00125),
    "amazon.titan-text-premier-v1:0": (0.0005, 0.0015),
    "amazon.nova-pro-v1:0": (0.0008, 0.0032), 
}

class RateLimitError(Exception):
    pass

class BedrockLLM(LLMProvider):
    """AWS Bedrock integration with Claude, Titan, and Nova support."""
    
    def __init__(self):
        self.region = settings.aws_region_name
        if boto3 is None:
            self.client = None  # type: ignore
        else:
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
        self._semaphore = asyncio.Semaphore(10) # Basic rate limiting

    def _estimate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        rates = COST_ESTIMATION.get(model_id, (0, 0))
        return (input_tokens / 1000.0) * rates[0] + (output_tokens / 1000.0) * rates[1]

    def _prepare_payload(self, system_prompt: str, user_prompt: str, model_id: str) -> tuple[str, dict]:
        if "claude" in model_id.lower():
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}]
            }
            return model_id, body
        elif "titan" in model_id.lower():
            body = {
                "inputText": f"{system_prompt}\n\n{user_prompt}",
                "textGenerationConfig": {"maxTokenCount": 4096}
            }
            return model_id, body
        elif "nova" in model_id.lower():
            # Approximating Nova message format based on latest AWS docs
            body = {
                "system": [{"text": system_prompt}],
                "messages": [{"role": "user", "content": [{"text": user_prompt}]}],
                "inferenceConfig": {"maxTokens": 4096}
            }
            return model_id, body
        else:
            raise ValueError(f"Unsupported Bedrock model family: {model_id}")

    @retry(
        retry=retry_if_exception_type((ClientError, RateLimitError)),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60)
    )
    async def _invoke_model_async(self, model_id: str, body: dict) -> str:
        async with self._semaphore:
            # We use asyncio.to_thread because boto3 is synchronous
            if self.client is None:
                raise ImportError("boto3 is not installed. Bedrock provider is unavailable.")
            try:
                response = await asyncio.to_thread(
                    self.client.invoke_model,
                    modelId=model_id,
                    body=json.dumps(body),
                    accept="application/json",
                    contentType="application/json"
                )

                response_body = json.loads(response.get('body').read())

                # Token tracking & Cost Estimation
                input_tokens = 0
                output_tokens = 0

                # Parse response based on model
                if "claude" in model_id.lower():
                    result = response_body.get("content", [{}])[0].get("text", "")
                    input_tokens = response_body.get("usage", {}).get("input_tokens", 0)
                    output_tokens = response_body.get("usage", {}).get("output_tokens", 0)
                elif "titan" in model_id.lower():
                    result = response_body.get("results", [{}])[0].get("outputText", "")
                    input_tokens = response_body.get("inputTextTokenCount", 0)
                    output_tokens = response_body.get("results", [{}])[0].get("tokenCount", 0)
                elif "nova" in model_id.lower():
                    result = response_body.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "")
                    input_tokens = response_body.get("usage", {}).get("inputTokens", 0)
                    output_tokens = response_body.get("usage", {}).get("outputTokens", 0)
                else:
                    result = str(response_body)

                cost = self._estimate_cost(model_id, input_tokens, output_tokens)
                logger.info(f"[Bedrock] Model: {model_id} | In: {input_tokens} | Out: {output_tokens} | Cost: ${cost:.6f}")

                return result
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ThrottlingException':
                    logger.warning("Bedrock rate limit exceeded. Retrying…")
                    raise RateLimitError("Rate limit exceeded")
                raise
                raise

    def generate(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        model_id = model or settings.bedrock_default_model
        _, body = self._prepare_payload(system_prompt, user_prompt, model_id)
        # We need to run the async method synchronously
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self._invoke_model_async(model_id, body))

    async def generate_stream(
        self, system_prompt: str, user_prompt: str, model: str | None = None
    ) -> AsyncGenerator[str, None]:
        model_id = model or settings.bedrock_default_model
        _, body = self._prepare_payload(system_prompt, user_prompt, model_id)
        
        async with self._semaphore:
            if self.client is None:
                raise ImportError("boto3 is not installed. Bedrock provider is unavailable.")
            try:
                response = await asyncio.to_thread(
                    self.client.invoke_model_with_response_stream,
                    modelId=model_id,
                    body=json.dumps(body),
                    accept="application/json",
                    contentType="application/json"
                )

                stream = response.get('body')
                if not stream:
                    yield "Error: Empty stream"
                    return

                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_obj = json.loads(chunk.get('bytes').decode())

                        # Streaming response parsing depends heavily on model
                        if "claude" in model_id.lower():
                            if chunk_obj['type'] == 'content_block_delta':
                                yield chunk_obj['delta'].get('text', '')
                        elif "titan" in model_id.lower():
                            yield chunk_obj.get('outputText', '')
                        elif "nova" in model_id.lower():
                            yield chunk_obj.get('contentBlockDelta', {}).get('delta', {}).get('text', '')
                # Note: Streaming cost tracking is more complex as it requires accumulating tokens over stream chunks
            except ClientError as e:
                logger.error(f"Bedrock streaming error: {e}")
                yield f"Error: {e}"
