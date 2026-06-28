import litellm
from src.config.settings import settings

# Configure LiteLLM to use the provided OpenAI key
litellm.api_key = settings.OPENAI_API_KEY

async def generate_embedding(text: str) -> list[float]:
    """Generates a dense vector embedding using OpenAI."""
    # For Phase 4 we use a mock embedding if the key is empty, to allow the code to run
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
        return [0.0] * 1536 # Mock 1536-dimensional vector for OpenAI text-embedding-3-small

    try:
        response = await litellm.aembedding(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0]["embedding"]
    except Exception as e:
        print(f"Embedding Error: {e}")
        return [0.0] * 1536

async def stream_chat_response(prompt: str):
    """Streams the LLM response token by token via LiteLLM."""
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
        # Mock streaming response for local dev without a key
        mock_response = "I am a mock response because no OPENAI_API_KEY was provided. "
        for word in mock_response.split():
            yield f"data: {word} \n\n"
        yield "data: [DONE]\n\n"
        return

    messages = [{"role": "user", "content": prompt}]
    
    try:
        response = await litellm.acompletion(
            model="gpt-4o-mini",
            messages=messages,
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield f"data: {chunk.choices[0].delta.content}\n\n"
                
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: Error generating response: {e}\n\n"
        yield "data: [DONE]\n\n"
