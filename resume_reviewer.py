import os
import sys
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()
client = genai.Client()

# Step A: Define the rigid schema blueprint using Pydantic
class ResumeReview(BaseModel):
    strengths: list[str] = Field(description="List of core technical or professional strengths found in the resume.")
    weaknesses: list[str] = Field(description="List of noticeable gaps, layout problems, or missing achievements.")
    suggestions: list[str] = Field(description="Specific, highly actionable suggestions to improve the resume content or layout.")
    score: int = Field(description="An overall evaluation score from 1 (terrible) to 10 (perfect).")
    verdict: str = Field(description="A punchy, one-line career summary verdict regarding the overall marketability.")

def analyze_resume(resume_text: str):
    console.print("\n[bold yellow]Analyzing resume with strict structured schema validation...[/bold yellow]")
    
    # Step B & C: native structured configuration
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Please analyze the following resume content thoroughly:\n\n{resume_text}",
            config={
                'system_instruction': "You are an elite, highly critical technical recruiter and resume reviewer. Be honest, granular, and realistic.",
                'response_mime_type': 'application/json',
                'response_schema': ResumeReview, # Enforces the exact Pydantic structural format
                'temperature': 0.1
            }
        )
        
        # The SDK automatically parses the matching JSON into an instance of our class!
        review_data: ResumeReview = response.parsed
        
        # Step E: Display the typed attributes cleanly inside the terminal using rich
        console.print("\n" + "="*80 + "\n")
        
        console.print(f"[bold cyan]🎯 Score Assessment:[/bold cyan] [bold yellow]{review_data.score}/10[/bold yellow]\n")
        
        console.print("[bold green]✅ Strengths Identified:[/bold green]")
        for idx, s in enumerate(review_data.strengths, 1):
            console.print(f"  {idx}. {s}")
            
        console.print("\n[bold red]⚠️ Areas for Improvement (Weaknesses):[/bold red]")
        for idx, w in enumerate(review_data.weaknesses, 1):
            console.print(f"  {idx}. {w}")
            
        console.print("\n[bold magenta]🛠️ Actionable Suggestions:[/bold magenta]")
        for idx, sug in enumerate(review_data.suggestions, 1):
            console.print(f"  {idx}. {sug}")
            
        console.print("\n" + "="*80)
        console.print(Panel(review_data.verdict, title="[bold green]Final Verdict[/bold green]", expand=False))
        
    except Exception as e:
        console.print(f"[bold red]An unexpected compilation or API schema error occurred:[/bold red] {e}")

if __name__ == "__main__":
    # Step D: Accept paste text input
    console.print("[bold cyan]====================================================================[/bold cyan]")
    console.print("[bold cyan]                  AI CRITICAL RESUME REVIEWER ENGINE                [/bold cyan]")
    console.print("[bold cyan]====================================================================[/bold cyan]")
    console.print("[bold magenta]Paste your resume plain text below. (Press Ctrl+D or Ctrl+Z then Enter to process):[/bold magenta]\n")
    
    try:
        user_input = sys.stdin.read().strip()
        if user_input:
            analyze_resume(user_input)
        else:
            console.print("[bold red]Error: No content received.[/bold red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Exiting tool.[/yellow]")