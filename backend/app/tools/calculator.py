def calculate(expression: str) -> str:
    """
    Safely evaluate basic mathematical expressions.
    """

    allowed_characters = (
        "0123456789"
        "+-*/(). "
    )

    if not all(
        char in allowed_characters
        for char in expression
    ):
        return "Invalid mathematical expression."

    try:

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return str(result)

    except Exception:

        return "Unable to calculate the expression."