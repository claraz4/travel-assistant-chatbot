from langchain.tools import tool

@tool
def add_two_numbers(a: int, b: int) -> str:
    """Adds two numbers."""
    return str(a + b)
