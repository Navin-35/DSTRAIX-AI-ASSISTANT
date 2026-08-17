import json
import re
import time

from google import genai

from app.core.config import settings
from app.tools.calculator import calculate


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


# ============================================================
# MODEL
# ============================================================

AGENT_MODEL = "gemini-3.6-flash"


# ============================================================
# CALCULATOR TOOL DECLARATION
# ============================================================

calculator_tool = {
    "type": "function",
    "name": "calculate",
    "description": (
        "Performs mathematical calculations. "
        "Use this tool when the user asks for "
        "arithmetic or mathematical calculations."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": (
                    "A mathematical expression such as "
                    "25 * 48 or (100 + 50) / 5"
                )
            }
        },
        "required": [
            "expression"
        ]
    }
}


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are DSTRAIX, an intelligent AI assistant.

You can:
- Answer general questions.
- Perform calculations using the calculator tool.
- Explain technical concepts clearly.
- Help users solve problems.

Rules:
1. Give concise and useful answers.
2. Use the calculator tool for mathematical calculations.
3. Never invent calculator results.
4. If the user's request is not mathematical, answer normally.
5. Do not expose internal tool execution details.
"""


# ============================================================
# FAST CALCULATION DETECTION
# ============================================================

def is_calculation_query(message: str) -> bool:
    """
    Detect simple arithmetic queries locally.

    This avoids a Gemini API call for simple calculations.
    """

    text = message.lower().strip()

    calculation_words = [
        "calculate",
        "compute",
        "solve",
        "what is",
        "what's",
        "find",
        "evaluate"
    ]

    has_calculation_word = any(
        word in text
        for word in calculation_words
    )

    # Detect mathematical operators
    has_operator = bool(
        re.search(
            r"[\+\-\*\/\%\^]",
            text
        )
    )

    # Detect at least one number
    has_number = bool(
        re.search(
            r"\d",
            text
        )
    )

    return (
        has_calculation_word
        and has_operator
        and has_number
    )


# ============================================================
# EXTRACT MATHEMATICAL EXPRESSION
# ============================================================

def extract_expression(message: str):
    """
    Extract the mathematical part from a natural-language query.
    """

    text = message.lower()

    replacements = [
        "calculate",
        "compute",
        "solve",
        "what is",
        "what's",
        "evaluate",
        "find",
        "please",
    ]

    for word in replacements:

        text = text.replace(
            word,
            ""
        )

    # Convert common mathematical words
    text = text.replace(
        "×",
        "*"
    )

    text = text.replace(
        "÷",
        "/"
    )

    text = text.replace(
        "^",
        "**"
    )

    text = text.strip()

    # Extract only mathematical characters
    match = re.search(
        r"[\d\.\+\-\*\/\%\(\)\s]+",
        text
    )

    if not match:
        return None

    expression = match.group().strip()

    # Must actually contain an operator
    if not re.search(
        r"[\+\-\*\/\%\(\)]",
        expression
    ):
        return None

    return expression


# ============================================================
# FORMAT CALCULATOR RESULT
# ============================================================

def format_result(result):
    """
    Format calculator output cleanly.
    """

    if isinstance(
        result,
        float
    ) and result.is_integer():

        return str(
            int(result)
        )

    return str(result)


# ============================================================
# FAST LOCAL CALCULATOR
# ============================================================

def fast_calculate(message: str):
    """
    Perform a calculation locally without Gemini.

    Returns:
        str | None
    """

    if not is_calculation_query(message):
        return None

    expression = extract_expression(
        message
    )

    if not expression:
        return None

    try:

        result = calculate(
            expression
        )

        return (
            f"The result is "
            f"{format_result(result)}."
        )

    except Exception as error:

        print(
            f"Local calculator failed: {error}"
        )

        return None


# ============================================================
# EXECUTE GEMINI TOOL
# ============================================================

def execute_tool(
    function_name: str,
    arguments: dict
):
    """
    Execute a requested Gemini function.
    """

    if function_name == "calculate":

        expression = arguments.get(
            "expression"
        )

        if not expression:

            return {
                "error":
                    "No mathematical expression provided."
            }

        try:

            result = calculate(
                expression
            )

            return {
                "expression": expression,
                "result": result
            }

        except Exception as error:

            return {
                "error": str(error)
            }


    return {
        "error":
            f"Unknown function: {function_name}"
    }


# ============================================================
# RUN AGENT
# ============================================================

def run_agent(message: str) -> str:

    start_time = time.perf_counter()

    print(
        "\n======================================"
    )

    print(
        f"DSTRAIX QUERY: {message}"
    )

    print(
        "======================================"
    )


    # ========================================================
    # FAST PATH
    # ========================================================

    fast_result = fast_calculate(
        message
    )

    if fast_result is not None:

        elapsed = (
            time.perf_counter()
            - start_time
        )

        print(
            f"Fast calculator response: "
            f"{elapsed:.3f}s"
        )

        return fast_result


    # ========================================================
    # GEMINI AGENT
    # ========================================================

    print(
        "Sending query to Gemini..."
    )

    gemini_start = time.perf_counter()


    interaction = client.interactions.create(

        model=AGENT_MODEL,

        input=[
            {
                "type": "user_input",

                "content": [
                    {
                        "type": "text",
                        "text": message
                    }
                ]
            }
        ],

        system_instruction=SYSTEM_INSTRUCTION,

        tools=[
            calculator_tool
        ]
    )


    gemini_time = (
        time.perf_counter()
        - gemini_start
    )


    print(
        f"Gemini first response: "
        f"{gemini_time:.3f}s"
    )


    # ========================================================
    # FIND FUNCTION CALLS
    # ========================================================

    function_calls = []

    for step in interaction.steps:

        if step.type == "function_call":

            function_calls.append(
                step
            )


    # ========================================================
    # NO TOOL REQUIRED
    # ========================================================

    if not function_calls:

        elapsed = (
            time.perf_counter()
            - start_time
        )

        print(
            f"Total response time: "
            f"{elapsed:.3f}s"
        )

        return (
            interaction.output_text
            or "I couldn't generate a response."
        )


    # ========================================================
    # EXECUTE FUNCTIONS
    # ========================================================

    function_results = []


    for function_call in function_calls:

        print(
            f"Tool requested: "
            f"{function_call.name}"
        )

        print(
            f"Arguments: "
            f"{function_call.arguments}"
        )


        result = execute_tool(

            function_call.name,

            function_call.arguments
        )


        print(
            f"Tool result: {result}"
        )


        function_results.append(

            {
                "type":
                    "function_result",

                "name":
                    function_call.name,

                "call_id":
                    function_call.id,

                "result": [
                    {
                        "type": "text",

                        "text":
                            json.dumps(
                                result
                            )
                    }
                ]
            }
        )


    # ========================================================
    # SEND TOOL RESULT BACK TO GEMINI
    # ========================================================

    print(
        "Sending tool result to Gemini..."
    )


    final_start = time.perf_counter()


    final_interaction = (
        client.interactions.create(

            model=AGENT_MODEL,

            previous_interaction_id=
                interaction.id,

            input=function_results
        )
    )


    final_time = (
        time.perf_counter()
        - final_start
    )


    total_time = (
        time.perf_counter()
        - start_time
    )


    print(
        f"Gemini final response: "
        f"{final_time:.3f}s"
    )

    print(
        f"Total response time: "
        f"{total_time:.3f}s"
    )

    print(
        "======================================"
    )


    return (
        final_interaction.output_text
        or "I couldn't generate a final response."
    )