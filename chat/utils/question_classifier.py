GENERIC_KEYWORDS = [
    "where is", "who is", "what is the capital", "how many", "population of", 
    "define", "explain", "when did", "what is", "area of"
]

def is_generic_question(q: str) -> bool:
    q = q.lower()
    return any(keyword in q for keyword in GENERIC_KEYWORDS)