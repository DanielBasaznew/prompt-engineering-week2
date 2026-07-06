import os
from dotenv import load_dotenv
from google import genai
from rich.console import Console
from rich.panel import Panel

# Load environment variables
load_dotenv()

# Initialize Rich console for beautiful output
console = Console()

# Initialize the Gemini Client
# It automatically picks up GEMINI_API_KEY from the environment
client = genai.Client()

def explain_code_zero_shot(code_snippet: str):
    system_instruction = "You are a code explainer for junior developers. Explain the provided code simply."
    
    console.print("\n[bold yellow]Sending request to Gemini (Zero-Shot)...[/bold yellow]")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=code_snippet,
        config={
            'system_instruction': system_instruction,
            'temperature': 1.0,
        }
    )
    
    # Display the output inside a clean panel box
    console.print(Panel(response.text, title="[bold green]Zero-Shot Explanation[/bold green]", expand=False))

if __name__ == "__main__":
    # A simple test case: a list comprehension with a condition
    sample_code = """
numbers = [1, 2, 3, 4, 5, 6]
even_squares = [x**2 for x in numbers if x % 2 == 0]
print(even_squares)
"""
    console.print("[bold cyan]Sample Code to Explain:[/bold cyan]")
    console.print(sample_code, style="dim")
    
    explain_code_zero_shot(sample_code)