
from ollama import chat

MODEL_NAME = "llama3.2"

try:
    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": "In one sentence, explain how to troubleshoot Wi-Fi."
            }
        ],
        options={"temperature": 0.2},
    )

    print("Ollama connection: SUCCESS")
    print("Model:", MODEL_NAME)
    print("Response:", response.message.content)

except Exception as error:
    print("Ollama connection: FAILED")
    print("Error:", error)
