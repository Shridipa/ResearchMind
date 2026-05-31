# LLM Provider Issues - Fixes Applied

## Issues Fixed

### 1. **OpenRouter Streaming Error (ERR_ABORTED)**
**Problem:** The chat endpoint was returning `net::ERR_ABORTED` errors when attempting to stream responses.

**Root Causes Identified:**
- No timeout configuration on OpenRouter client
- Insufficient error handling in streaming
- Fallback model list was not optimized
- Missing logging for debugging

**Fixes Applied:**

#### A. Added Timeout Configuration
- **File:** `backend/app/llm/openrouter_provider.py`
- Set 60-second timeout on both sync and async OpenAI clients
- Prevents indefinite hangs on API calls

```python
self.sync_client = OpenAI(
    base_url=settings.openrouter_base_url, 
    api_key=api_key,
    timeout=60.0  # 60 second timeout
)
```

#### B. Improved Error Handling in Streaming
- **File:** `backend/app/llm/openrouter_provider.py`
- Added try-catch for individual chunks
- Better error logging with stack traces
- More informative retry messages

```python
async for chunk in response:
    try:
        content = None
        if chunk.choices and chunk.choices[0].delta:
            content = chunk.choices[0].delta.get("content")
        if content:
            yield content
    except Exception as chunk_error:
        logger.warning(f"Error processing chunk: {chunk_error}")
        continue
```

#### C. Enhanced Chat Route Error Handling
- **File:** `backend/app/api/v1/routes/chat.py`
- Wrapped streaming in proper event generator
- Added error event emission
- Better exception logging

```python
async def event_generator():
    try:
        async for event in rag_service.answer_question_stream(request):
            yield event
    except Exception as e:
        logger.error(f"Error in chat stream: {e}", exc_info=True)
        yield {"event": "error", "data": f"Error: {str(e)}"}

return EventSourceResponse(event_generator())
```

#### D. Optimized Model Fallback Chain
- **File:** `backend/.env`
- Changed primary model from `deepseek/deepseek-v4-flash:free` to `openrouter/auto`
- Reordered fallback models for better availability:
  1. `openrouter/auto` (automatically selects best available)
  2. `qwen/qwen-2.5-72b-instruct:free` (high quality, reliable)
  3. `google/gemini-2.0-flash-exp:free` (fast)
  4. `deepseek/deepseek-v4-flash:free` (fallback)

#### E. Added Detailed Logging
- Provider initialization logs model configuration
- Each streaming attempt is logged
- Fallback triggers are logged
- Chunk processing errors are captured

---

## Configuration Changes

### Updated `.env` Settings

```ini
# Primary model changed from deepseek to openrouter/auto
OPENROUTER_MODEL=openrouter/auto

# Improved fallback chain
OPENROUTER_FALLBACK_MODELS=qwen/qwen-2.5-72b-instruct:free,google/gemini-2.0-flash-exp:free,deepseek/deepseek-v4-flash:free
```

---

## Testing the Fixes

### To verify fixes are working:

1. **Check logs during startup:**
   ```
   INFO:     Application startup complete.
   INFO: app.llm.openrouter_provider OpenRouter provider initialized with primary model: openrouter/auto
   INFO: app.llm.openrouter_provider Fallback models: [...]
   ```

2. **Send a chat message and monitor logs:**
   - Should see: `Attempting OpenRouter streaming with model: openrouter/auto`
   - Should see: `Successfully completed streaming with openrouter/auto`
   - If first model fails, should see: `OpenRouter streaming model failed; falling back to next model`

3. **Frontend should receive proper responses:**
   - Messages should stream in real-time
   - Metadata event shows sources
   - Content events show answer chunks
   - Grounding stats show validation results

---

## Improvements Made

| Issue | Before | After |
|-------|--------|-------|
| Timeout | None (indefinite) | 60 seconds |
| Error Handling | Minimal | Comprehensive with logging |
| Fallback Chain | Static list | Prioritized by availability |
| Logging | Basic | Detailed per attempt |
| Model Selection | Fixed | Auto-selection + fallbacks |
| Chunk Error Handling | Fails entire stream | Skips bad chunk, continues |
| API Route Error Handling | Raw exceptions | Wrapped with error events |

---

## Files Modified

1. `backend/app/llm/openrouter_provider.py` - Added timeout, improved streaming error handling, added logging
2. `backend/app/api/v1/routes/chat.py` - Added event generator wrapper with error handling
3. `backend/.env` - Updated model configuration and fallback chain

---

## Next Steps

1. **Restart the backend server:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **Test the chat endpoint:**
   - Upload a PDF (if not already done)
   - Ask a research question
   - Monitor backend logs for debug info
   - Response should stream without ERR_ABORTED errors

3. **Monitor for any remaining issues:**
   - Check if timeout needs adjustment (current: 60s)
   - Verify fallback models are being used if primary fails
   - Monitor error rates in logs

---

## If Issues Persist

### Debugging Steps

1. **Check backend logs for specific OpenRouter errors:**
   - Rate limiting (429 errors)
   - Authentication (401/403 errors)
   - Model not found (404 errors)
   - Timeout exceeded (504/timeout errors)

2. **Try switching to a mock provider temporarily:**
   ```bash
   LLM_PROVIDER=mock
   ```

3. **Try OpenAI provider if you have an API key:**
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your-key
   ```

4. **Check API account status:**
   - Visit https://openrouter.ai/account
   - Verify credits/subscription status
   - Check rate limits

