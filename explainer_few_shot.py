import os
from dotenv import load_dotenv
from google import genai
from rich.console import Console
from rich.panel import Panel

# Load environment variables
load_dotenv()
console = Console()
client = genai.Client()

def explain_code_few_shot(code_snippet: str):
    # Defining our few-shot blueprint inside the system instruction block
    system_instruction = """You are an expert code explainer for junior developers. 
Always structure your explanation using exactly three clear headers: Summary, How it Works, and Why it Matters. Keep your explanations brief and highly readable.

Here are examples of the exact explanation style and formatting I expect from you:

---
Code:
def greet(name):
    return f"Hello, {name}!"

Explanation:
### Summary
A simple function that takes a person's name as an input string and returns a personalized greeting string using an f-string.

### How it Works
* **Function definition:** `def greet(name):` sets up a reusable function that accepts a single parameter called `name`.
* **String Formatting:** The `f"Hello, {name}!"` uses a Python f-string to instantly inject the variable directly inside the string.
* **Return Value:** The `return` keyword sends the completed string back to whatever code called the function.

### Why it Matters
Using f-strings is the modern, readable, and highly optimized standard for combining text and variables in Python code.
---

Code:
items = [10, 20, 30]
first_item = items[0]

Explanation:
### Summary
Creating a standard python list of integers and extracting the very first element using bracket index referencing.

### How it Works
* **List Initialization:** `items = [10, 20, 30]` creates a sequenced collection storing three integers.
* **Zero-Based Indexing:** `items[0]` accesses the target item at position 0. Python lists always begin counting positions at 0, not 1.
* **Assignment:** The integer value `10` is read from the list and saved cleanly inside the new variable `first_item`.

### Why it Matters
Understanding zero-based indexing is a core foundation of data retrieval across almost all programming languages to prevent "index out of range" runtime crashes.
---
"""

    console.print("\n[bold yellow]Sending request to Gemini (Few-Shot)...[/bold yellow]")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=code_snippet,
        config={
            'system_instruction': system_instruction,
            'temperature': 1.0,
        }
    )
    
    console.print(Panel(response.text, title="[bold green]Few-Shot Explanation[/bold green]", expand=False))

if __name__ == "__main__":
    # We pass the exact same sample code used in the zero-shot baseline
    sample_code = """
numbers = [1, 2, 3, 4, 5, 6]
even_squares = [x**2 for x in numbers if x % 2 == 0]
print(even_squares)
"""
    console.print("[bold cyan]Running identical code target through Few-Shot pipeline...[/bold cyan]")
    explain_code_few_shot(sample_code)