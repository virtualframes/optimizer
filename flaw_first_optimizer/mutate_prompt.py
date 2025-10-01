from .entropy_injector import inject_entropy

def mutate_prompt(prompt):
    """
    Mutates a prompt by injecting entropy.

    This function simulates adversarial drift by reordering or altering
    clauses in the prompt.
    """
    return inject_entropy(prompt, level=0.4)