import tiktoken

def truncate_to_token_budget(
    chunks: list[str], max_tokens: int, model: str = "gpt-4o"
) -> list[str]:
    """
    Enforces a strict maximum context limit by allocating token budgets.
    """
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        # fallback to cl100k_base if model not found
        enc = tiktoken.get_encoding("cl100k_base")
        
    selected: list[str] = []
    used = 0
    
    for chunk in chunks:
        count = len(enc.encode(chunk))
        if used + count > max_tokens:
            break
        selected.append(chunk)
        used += count
        
    return selected
