import os
import openai
from dotenv import load_dotenv

load_dotenv()

class Generator:
    """
    A generator model that uses the OpenAI API to generate suggestions.
    """
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, query: str, context: list[str]) -> str:
        """
        Generates a suggestion using the OpenAI API.
        """
        if not context:
            return "No relevant guidelines found to generate a suggestion."

        context_str = "\n\n".join(f"- {c}" for c in context)
        
        system_prompt = """You are an expert in plain language writing. Your goal is to provide clear, concise, and actionable suggestions to help users improve their writing based on the Federal Plain Language Guidelines."""
        
        user_prompt = f"""A user's text has triggered the following rule: '{query}'.

Here are the most relevant guidelines:
{context_str}

Based on these guidelines, please provide a brief, actionable suggestion to help the user improve their text."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating suggestion: {e}")
            return "There was an error generating a suggestion."