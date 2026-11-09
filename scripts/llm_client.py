
import os
import requests
import json

MODEL = "qwen2.5-coder:3b"
OLLAMA_URL = "http://localhost:11434/api/generate"


def mock_llm(prompt):

    return json.dumps({
        "design": "4-bit synchronous counter",
        "assertions": [
            {
                "name": "counter_reset",
                "code": """
property counter_reset;
    @(posedge clk)
    reset |=> (count == 4'd0);
endproperty

assert property (counter_reset);
"""
            }
        ],
        "assumptions": [
            "Reset is active-high and synchronous."
        ]
    })


def ollama_llm(prompt):

    print("Connecting to Qwen2.5-Coder...")

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1
            }
        },
        timeout=300
    )

    response.raise_for_status()

    return response.json()["response"]


def generate(prompt):

    provider = os.getenv(
        "ASSERTLLM_PROVIDER", "mock"
    ).lower()

    if provider == "mock":
        return mock_llm(prompt)

    elif provider == "ollama":
        return ollama_llm(prompt)

    else:
        raise ValueError("Unknown LLM provider")
