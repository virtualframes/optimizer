# FLAWMODE: Semantic Drift Generator
# This module is designed to introduce subtle logical flaws by altering
# the meaning of data or code constructs. It tests the agent's ability
# to perform deeper semantic analysis.

def invert_boolean_logic(condition):
    """
    Simulates a flaw where a boolean condition is inverted.
    For example, `if (x > 5)` becomes `if not (x > 5)`.
    """
    print(f"SEMANTIC DRIFT: Inverting boolean logic for condition '{condition}'")
    return not condition


def off_by_one_error_simulator(data_list):
    """
    Simulates a classic off-by-one error by accessing an index
    that is either one too early or one too late.
    """
    if len(data_list) > 0:
        # This will either be the last element or raise an IndexError
        # if the list has only one item. The agent must detect this.
        index = len(data_list)
        print(f"SEMANTIC DRIFT: Simulating off-by-one with index {index}")
        # return data_list[index] # Commented out to avoid crashing
    return "Off-by-one pattern recognized."


def misinterpret_data_type(value):
    """
    Simulates a flaw where a value is treated as the wrong type.
    For example, treating a number as a string.
    """
    if isinstance(value, int):
        # The agent should recognize that string concatenation on an int is a type error.
        result = str(value) + " is now a string"
        print(f"SEMANTIC DRIFT: Misinterpreting int as string. Result: '{result}'")
        return result
    return "Type misinterpretation pattern recognized."