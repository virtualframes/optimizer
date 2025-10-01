import random

def inject_entropy(prompt, level=0.3):
    words = prompt.split()
    for i in range(len(words)):
        if random.random() < level:
            words[i] = words[i][::-1]  # simple entropy: reverse token
    return " ".join(words)