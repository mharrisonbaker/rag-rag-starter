
def create_analysis_prompt(user_text: str, guidelines: list[str]) -> tuple[str, str]:
    """
    Creates the system and user prompts for the LLM analysis.
    """
    
    context_str = "\n\n".join(f"- {g}" for g in guidelines)

    system_prompt = """You are an expert in plain language writing, specializing in the Federal Plain Language Guidelines. Your task is to analyze a user's text and provide a single, comprehensive analysis with actionable suggestions for improvement, citing the relevant guidelines.
"""

    user_prompt = f"""Please analyze the following text based on the provided plain language guidelines:

**User's Text:**
---
{user_text}
---

**Relevant Guidelines:**
---
{context_str}
---

Please provide a single, comprehensive analysis with a title, a summary of the issue, and a detailed suggestion for improvement based on the text and the guidelines.
"""
    return system_prompt, user_prompt
