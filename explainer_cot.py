import os
import sys
import re
from dotenv import load_dotenv
from google import genai
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()
client = genai.Client()

def explain_code_with_cot(code_snippet: str, show_reasoning: bool = True):
    system_instruction = """You are an expert code explainer for junior developers. 
Before you write your final explanation, you must reason through the code step-by-step.

You MUST structure your response exactly like this:
<thinking>
1. Identify what each individual part/line of the code does.
2. Figure out the overall purpose and what problem this code solves.
3. Identify any edge cases or tricky logical steps.
</thinking>

### Summary
[Write a concise summary here]

### How it Works
[Write bulleted, step-by-step points here]

### Why it Matters
[Write the real-world engineering significance here]
"""

    console.print("\n[bold yellow]Processing code with Chain-of-Thought (CoT)...[/bold yellow]")
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=code_snippet,
            config={
                'system_instruction': system_instruction,
                'temperature': 0.2,
            }
        )
        full_output = response.text
    except Exception as e:
        console.print(f"[bold red]API Communication Error:[/bold red] {e}")
        return

    thinking_match = re.search(r'<thinking>(.*?)</thinking>', full_output, re.DOTALL)
    thinking_content = thinking_match.group(1).strip() if thinking_match else "No explicit reasoning trace returned."
    clean_explanation = re.sub(r'<thinking>.*?</thinking>', '', full_output, flags=re.DOTALL).strip()

    if show_reasoning and thinking_match:
        console.print(Panel(thinking_content, title="[bold orange3]🧠 Model Internal Reasoning (CoT Tracking)[/bold orange3]", border_style="orange3"))
        console.print("\n" + "="*80 + "\n")

    console.print(Panel(clean_explanation, title="[bold green]Final Code Explanation[/bold green]", expand=False))

def print_usage():
    console.print("[bold cyan]Usage options:[/bold cyan]")
    console.print("  [green]python explainer_cot.py[/green]                  -> Interactive mode (paste your code)")
    console.print("  [green]python explainer_cot.py <file_path>[/green]        -> Read and explain a specific file")
    console.print("  [green]python explainer_cot.py --hide <file_path>[/green] -> Read file and hide the reasoning trace\n")

if __name__ == "__main__":
    show_reasoning = True
    code_to_analyze = ""
    
    # Simple argument parsing logic
    args = sys.argv[1:]
    
    if "--hide" in args:
        show_reasoning = False
        args.remove("--hide")
        
    if len(args) > 0:
        # User provided a file path as an argument
        target_file = args[0]
        if os.path.exists(target_file):
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    code_to_analyze = f.read()
                console.print(f"[bold green]✓ Loaded code from file:[/bold green] {target_file}")
            except Exception as e:
                console.print(f"[bold red]Error reading file {target_file}:[/bold red] {e}")
                sys.exit(1)
        else:
            # Graceful safety handling instead of standard crash
            console.print(Panel(f"The path '[bold red]{target_file}[/bold red]' does not exist.\nPlease check the file spelling and try again.", title="[bold red]File Not Found[/bold red]"))
            print_usage()
            sys.exit(1)
    else:
        # Fallback to interactive terminal paste mode
        print_usage()
        console.print("[bold magenta]Enter/Paste your code snippet below (Press Ctrl+D or Ctrl+Z followed by Enter to finish):[/bold magenta]")
        try:
            lines = sys.stdin.read()
            code_to_analyze = lines.strip()
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled.[/yellow]")
            sys.exit(0)

    if code_to_analyze:
        explain_code_with_cot(code_to_analyze, show_reasoning=show_reasoning)
    else:
        console.print("[bold red]Error: No code provided to analyze.[/bold red]")