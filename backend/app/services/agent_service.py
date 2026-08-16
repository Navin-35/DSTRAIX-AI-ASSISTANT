import json

from google import genai

from app.core.config import settings
from app.tools.calculator import calculate


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


MODEL_NAME = "gemini-3.6-flash"


calculator_tool = {
    "type": "function",
    "name": "calculate",
    "description": (
        "Calculate mathematical expressions accurately. "
        "Use this tool whenever the user asks for "
        "arithmetic or numerical calculations."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": (
                    "The mathematical expression to calculate. "
                    "Example: 25 * 48 + 100"
                )
            }
        },
        "required": [
            "expression"
        ]
    }
}


TOOLS = [
    calculator_tool
]


def run_agent(message: str) -> str:

    # ------------------------------------------------
    # STEP 1: Ask Gemini whether it needs a tool
    # ------------------------------------------------

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=message,
        tools=TOOLS
    )

    # ------------------------------------------------
    # STEP 2: Check whether Gemini requested a tool
    # ------------------------------------------------

    function_results = []

    for step in interaction.steps:

        if step.type != "function_call":
            continue

        # --------------------------------------------
        # Get requested function
        # --------------------------------------------

        function_name = step.name

        arguments = step.arguments

        # --------------------------------------------
        # Execute our local function
        # --------------------------------------------

        if function_name == "calculate":

            result = calculate(
                arguments["expression"]
            )

        else:

            result = (
                f"Unknown function: {function_name}"
            )

        # --------------------------------------------
        # Prepare function result
        # --------------------------------------------

        function_result = {
            "type": "function_result",
            "name": function_name,
            "call_id": step.id,
            "result": [
                {
                    "type": "text",
                    "text": json.dumps(result)
                }
            ]
        }

        function_results.append(
            function_result
        )

    # ------------------------------------------------
    # STEP 3: If no tool was requested,
    # return normal Gemini response
    # ------------------------------------------------

    if not function_results:

        return interaction.output_text

    # ------------------------------------------------
    # STEP 4: Send tool result back to Gemini
    # ------------------------------------------------

    final_interaction = client.interactions.create(
        model=MODEL_NAME,
        previous_interaction_id=interaction.id,
        input=function_results,
        tools=TOOLS
    )

    # ------------------------------------------------
    # STEP 5: Return final natural-language response
    # ------------------------------------------------

    return final_interaction.output_text