"""
Centralized registry for all LLM prompt templates used in the project.
"""

PROMPT_REGISTRY = {
    "document_comparator": """
You are an expert document analyst. Compare the information provided in the combined text below.

Custom User Instructions:
{custom_instructions}

Format Instructions:
{format_instructions}

Combined Document Text:
{combined_text}
"""
}
