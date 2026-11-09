
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def get_llm_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    return Groq(api_key=api_key)


def call_llm(system_prompt, user_prompt):
    client = get_llm_client()

    model_name = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=700
    )

    return response.choices[0].message.content or ""
