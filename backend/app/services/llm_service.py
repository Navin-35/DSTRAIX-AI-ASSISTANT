from google import genai

from app.core.config import settings


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# NORMAL RESPONSE
# ============================================================

def generate_response(
    message: str,
    history: list[dict]
) -> str:

    system_instruction = """
You are DSTRAIX, an intelligent AI assistant.

Your responsibilities:
- Give accurate and useful answers.
- Explain difficult concepts clearly.
- Maintain context throughout the conversation.
- Be concise when a short answer is enough.
- Provide detailed explanations when required.
- Never pretend to know information that you do not know.
"""


    # --------------------------------------------------------
    # Build conversation input
    # --------------------------------------------------------

    input_data = []


    for item in history:

        role = item["role"]

        content = item["content"]


        input_data.append(
            {
                "type": "text",
                "text": f"{role}: {content}"
            }
        )


    # Add current user message

    input_data.append(
        {
            "type": "text",
            "text": f"user: {message}"
        }
    )


    # --------------------------------------------------------
    # Gemini Interaction
    # --------------------------------------------------------

    interaction = client.interactions.create(

        model=MODEL_NAME,

        input=input_data,

        system_instruction=system_instruction
    )


    return (
        interaction.output_text
        or "I couldn't generate a response."
    )


# ============================================================
# STREAMING RESPONSE
# ============================================================

def stream_chat_response(
    message: str,
    history: list[dict]
):

    system_instruction = """
You are DSTRAIX, an intelligent AI assistant.

Your responsibilities:
- Give accurate and useful answers.
- Explain difficult concepts clearly.
- Maintain context throughout the conversation.
- Be concise when a short answer is enough.
- Provide detailed explanations when required.
- Never pretend to know information that you do not know.

When answering:
- Start responding immediately.
- Avoid unnecessary introductions.
- Use clear and natural language.
"""


    # --------------------------------------------------------
    # Build conversation input
    # --------------------------------------------------------

    input_data = []


    for item in history:

        role = item["role"]

        content = item["content"]


        input_data.append(
            {
                "type": "text",
                "text": f"{role}: {content}"
            }
        )


    # Current message

    input_data.append(
        {
            "type": "text",
            "text": f"user: {message}"
        }
    )


    # --------------------------------------------------------
    # Create streaming interaction
    # --------------------------------------------------------

    stream = client.interactions.create(

        model=MODEL_NAME,

        input=input_data,

        system_instruction=system_instruction,

        stream=True
    )


    # --------------------------------------------------------
    # Read streaming events
    # --------------------------------------------------------

    for event in stream:

        if event.event_type != "step.delta":
            continue


        if not event.delta:
            continue


        if getattr(
            event.delta,
            "type",
            None
        ) != "text":

            continue


        text = getattr(
            event.delta,
            "text",
            None
        )


        if text:

            yield text