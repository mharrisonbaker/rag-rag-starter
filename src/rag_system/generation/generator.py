
class Generator:
    """
    Simulates a generator model. In a real system, this would call an LLM.
    """
    def __init__(self):
        pass

    def generate(self, query: str, context: list[str]) -> str:
        """
        Combines the query and context into a formatted string.
        """
        if not context:
            return "No relevant guidelines found to generate a suggestion."

        context_str = "\n\n".join(f"- {c}" for c in context)
        
        prompt = f"""
Based on your input and the following guidelines, here is a suggestion for improvement:

**Relevant Guidelines:**
{context_str}

**Suggestion:**
Consider revising your text to address the issues raised by these guidelines. For example, for the query '{query}', you could try to rephrase it to be more direct and use simpler language.
"""
        return prompt.strip()
