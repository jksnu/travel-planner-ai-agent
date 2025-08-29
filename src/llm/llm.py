from huggingface_hub import InferenceClient
import os

HUGGINGFACE_API_TOKEN = os.getenv("HF_API_TOKEN")
LLM_MODEL = os.getenv("HF_MODEL_ID") #    mistralai/Mixtral-8x7B-Instruct-v0.1

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
    "Content-Type": "application/json"
}

def build_client() -> InferenceClient:
    return InferenceClient(
        model=LLM_MODEL,
        token=HUGGINGFACE_API_TOKEN,
        timeout=300
    )

def query_llm(messages: list[dict]) -> str|None:
    try:
        client = build_client()
        result = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=500
        )
        text = result.choices[0].message.content
        
        return text    
    except Exception as e:
        print(f"Error querying LLM: {e}")
        return "Error querying LLM"