import os
import sys
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field
import instructor
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text

load_dotenv()
console = Console()

# Step 1: Initialize the API client and wrap it with Instructor for streaming support
try:
    raw_client = genai.Client()
    # We patch the Gemini client with instructor to enable advanced partial parsing
    client = instructor.from_genai(client=raw_client)
except Exception as e:
    console.print(f"[bold red]Initialization Error:[/bold red] Make sure GEMINI_API_KEY is set in your .env file. Details: {e}")
    sys.exit(1)

# Step A: Define the rigid schema blueprint using Pydantic
class ResumeReview(BaseModel):
    strengths: list[str] = Field(default_factory=list, description="List of core technical or professional strengths found in the resume.")
    weaknesses: list[str] = Field(default_factory=list, description="List of noticeable gaps, layout problems, or missing achievements.")
    suggestions: list[str] = Field(default_factory=list, description="Specific, highly actionable suggestions to improve the resume content or layout.")
    score: int = Field(default=0, description="An overall evaluation score from 1 (terrible) to 10 (perfect).")
    verdict: str = Field(default="", description="A punchy, one-line career summary verdict regarding the overall marketability.")

def generate_report_ui(data: ResumeReview, is_streaming: bool = True) -> Table:
    """Helper function to compile the state of our Pydantic model into a gorgeous Rich layout."""
    # Determine the color of the score dynamically
    score_val = data.score or 0
    if score_val >= 7:
        score_color = "bold green"
    elif score_val >= 4:
        score_color = "bold yellow"
    else:
        score_color = "bold red"

    # Create a layout structure using a master table to organize panels side-by-side
    layout_table = Table.grid(expand=True)
    layout_table.add_column(ratio=1)

    # 1. Header Banner
    header = Panel(
        Text("RESUME REVIEW REPORT", justify="center", style="bold cyan"),
        subtitle="Powered by Gemini 2.5 & Instructor",
        border_style="cyan"
    )
    layout_table.add_row(header)
    layout_table.add_row("")  # Spacer

    # 2. Score Panel
    score_text = Text()
    score_text.append("Overall Assessment Score: ", style="bold white")
    score_text.append(f"{score_val}/10", style=score_color)
    score_panel = Panel(score_text, border_style="yellow" if score_val == 0 else ("green" if score_val >= 7 else "red"), expand=False)
    layout_table.add_row(score_panel)
    layout_table.add_row("")  # Spacer

    # 3. Strengths Table/Panel
    strengths_table = Table(show_header=False, box=None, padding=(0, 1, 0, 1))
    for idx, s in enumerate(data.strengths or [], 1):
        strengths_table.add_row(f"[green]✔[/green] [bold white]{idx}.[/bold white] {s}")
    strengths_panel = Panel(
        strengths_table if data.strengths else "[dim italic white]Analyzing strengths...[/dim italic white]",
        title="[bold green]✅ Identified Key Strengths[/bold green]",
        border_style="green"
    )
    layout_table.add_row(strengths_panel)
    layout_table.add_row("")  # Spacer

    # 4. Weaknesses Panel
    weaknesses_table = Table(show_header=False, box=None, padding=(0, 1, 0, 1))
    for idx, w in enumerate(data.weaknesses or [], 1):
        weaknesses_table.add_row(f"[red]✗[/red] [bold white]{idx}.[/bold white] {w}")
    weaknesses_panel = Panel(
        weaknesses_table if data.weaknesses else "[dim italic white]Analyzing areas of improvement...[/dim italic white]",
        title="[bold red]⚠️ Gaps & Areas of Improvement[/bold red]",
        border_style="red"
    )
    layout_table.add_row(weaknesses_panel)
    layout_table.add_row("")  # Spacer

    # 5. Actionable Suggestions Panel
    suggestions_table = Table(show_header=False, box=None, padding=(0, 1, 0, 1))
    for idx, sug in enumerate(data.suggestions or [], 1):
        suggestions_table.add_row(f"[magenta]⚡[/magenta] [bold white]{idx}.[/bold white] {sug}")
    suggestions_panel = Panel(
        suggestions_table if data.suggestions else "[dim italic white]Generating engineering action points...[/dim italic white]",
        title="[bold magenta]🛠️ Actionable Recommendations[/bold magenta]",
        border_style="magenta"
    )
    layout_table.add_row(suggestions_panel)
    layout_table.add_row("")  # Spacer

    # 6. Final Verdict Box
    verdict_text = data.verdict if data.verdict else "[dim italic white]Formulating career verdict...[/dim italic white]"
    verdict_panel = Panel(
        verdict_text,
        title="[bold cyan]Final Verdict[/bold cyan]",
        border_style="cyan",
        expand=False
    )
    layout_table.add_row(verdict_panel)

    return layout_table

def analyze_resume_stream(resume_text: str):
    console.print("\n[bold yellow]⚡ Initializing secure stream channel with partial parsing...[/bold yellow]\n")
    
    # We initialize an empty state schema
    current_review = ResumeReview()
    
    try:
        # Step B & C: Request partial streaming of structured objects
        response_stream = client.chat.completions.create_partial(
            model='gemini-2.5-flash',
            response_model=ResumeReview,
            messages=[
                {"role": "system", "content": "You are an elite, highly critical technical recruiter and resume reviewer. Be honest, granular, and realistic."},
                {"role": "user", "content": f"Please analyze the following resume content thoroughly:\n\n{resume_text}"}
            ]
        )
        
        # We hook into Rich Live display to refresh the output in real-time as chunks land
        with Live(generate_report_ui(current_review), refresh_per_second=10, auto_refresh=True) as live:
            for partial_data in response_stream:
                # Update current review fields safely
                current_review = partial_data
                live.update(generate_report_ui(current_review))
                
        # Final display update to lock it in
        console.print("\n[bold green]✓ Complete analysis finalized successfully![/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]An unexpected streaming error occurred:[/bold red] {e}")

def print_usage():
    console.print("[bold cyan]Usage options:[/bold cyan]")
    console.print("  [green]python resume_reviewer.py[/green]                  -> Interactive mode (paste your resume)")
    console.print("  [green]python resume_reviewer.py <file_path>[/green]        -> Read and analyze a specific text file\n")

if __name__ == "__main__":
    resume_content = ""
    args = sys.argv[1:]
    
    if len(args) > 0:
        target_file = args[0]
        if os.path.exists(target_file):
            try:
                try:
                    with open(target_file, "r", encoding="utf-8") as f:
                        resume_content = f.read().strip()
                except UnicodeDecodeError:
                    with open(target_file, "r", encoding="windows-1252", errors="replace") as f:
                        resume_content = f.read().strip()
                console.print(f"[bold green]✓ Loaded resume from file:[/bold green] {target_file}")
            except Exception as e:
                console.print(f"[bold red]Error reading file {target_file}:[/bold red] {e}")
                sys.exit(1)
        else:
            console.print(Panel(f"The file path '[bold red]{target_file}[/bold red]' does not exist.\nPlease check the spelling and try again.", title="[bold red]File Not Found[/bold red]"))
            print_usage()
            sys.exit(1)
    else:
        print_usage()
        console.print("[bold magenta]Paste your resume plain text below. (Press Ctrl+D or Ctrl+Z then Enter to process):[/bold magenta]\n")
        try:
            resume_content = sys.stdin.read().strip()
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled.[/yellow]")
            sys.exit(0)

    if resume_content:
        analyze_resume_stream(resume_content)
    else:
        console.print("[bold red]Error: No resume content provided to analyze.[/bold red]")