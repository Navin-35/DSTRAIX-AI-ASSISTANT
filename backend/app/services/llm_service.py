from google import genai

from app.core.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


MODEL_NAME = "gemini-3.6-flash"


def generate_response(
    message: str,
    history: list[dict]
) -> str:

    prompt = """
You are DSTRAIX, an intelligent AI assistant.

Your responsibilities:
- Give accurate and useful answers.
- Explain difficult concepts clearly.
- Maintain context throughout the conversation.
- Be concise when a short answer is enough.
- Provide detailed explanations when required.
- Never pretend to know information that you do not know.

Conversation history:
"""

    for item in history:

        role = item["role"]
        content = item["content"]

        prompt += f"\n{role}: {content}"

    prompt += f"""

user: {message}

assistant:
"""

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=prompt
    )

    return interaction.output_text