import re

BLOCKED_PATTERNS = [
    r"(?i)ignore (all )?previous instructions",
    r"(?i)system prompt",
    r"(?i)bypass restrictions",
]

def check_input_guardrail(query: str) -> None:
    """
    Input guardrails block malicious queries, topical violations, 
    and sensitive data before the system retrieves documents.
    """
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, query):
            raise ValueError(f"Security violation detected: {pattern}")
    if len(query.strip()) < 3:
        raise ValueError("Query too short for retrieval.")
