import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()

# We track simulation attempts globally to know when to let the API call succeed
SIMULATED_ATTEMPTS = 0

try:
    client = genai.Client()
except Exception as e:
    console.print(f"[bold red]Initialization Error:[/bold red] Make sure GEMINI_API_KEY is set in your .env. Details: {e}")
    sys.exit(1)

class EmailResponse(BaseModel):
    subject: str = Field(description="A highly professional, attention-grabbing subject line.")
    body: str = Field(description="The full, polished body of the email. Use natural line breaks (\n) for paragraphs.")

def estimate_input_cost(prompt: str) -> tuple[int, float]:
    """Counts prompt tokens and calculates input cost before calling the generation API."""
    system_instruction = (
        "You are a professional administrative assistant. Draft clear, polite, "
        "and highly effective business emails. Never include conversational placeholders "
        "like 'Here is your email:' in your output. Just populate the structured schema."
    )
    full_payload = f"{system_instruction}\n\nDraft an email based on the following instructions:\n\n{prompt}"
    
    try:
        count_response = client.models.count_tokens(
            model='gemini-2.5-flash',
            contents=full_payload
        )
        token_count = count_response.total_tokens
        estimated_cost = (token_count / 1_000_000) * 0.075
        return token_count, estimated_cost
    except Exception:
        approx_tokens = int(len(full_payload.split()) * 1.3)
        estimated_cost = (approx_tokens / 1_000_000) * 0.075
        return approx_tokens, estimated_cost

def generate_email(prompt: str):
    global SIMULATED_ATTEMPTS
    
    # Calculate and display the costs first!
    tokens, cost = estimate_input_cost(prompt)
    
    console.print(
        f"\n[bold blue]📊 Cost Analysis:[/bold blue] "
        f"This request will use approximately [bold yellow]{tokens}[/bold yellow] input tokens. "
        f"Estimated cost: [bold green]${cost:.7f}[/bold green]\n"
    )
    
    # Retry logic variables
    max_retries = 3
    backoff_factor = 2  # This doubles our wait time each failure (1s, 2s, 4s...)
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                console.print(f"[bold yellow]🔄 Retry attempt {attempt}/{max_retries}...[/bold yellow]")
            else:
                console.print("[bold yellow]⚡ Draft generation in progress...[/bold yellow]")

            # 🔬 SIMULATION BLOCK: Force-trigger rate limit failures on the first 2 attempts
            if SIMULATED_ATTEMPTS < 2:
                SIMULATED_ATTEMPTS += 1
                console.print("[bold magenta]🔬 [MOCK] Intercepting request to simulate HTTP 429 Rate Limit...[/bold magenta]")
                # We raise a mock APIError with HTTP code 429 using proper positional parameters
                raise APIError(429, None, None)

            # Request structured response from Gemini (Succeeds on Attempt 3)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"Draft an email based on the following instructions:\n\n{prompt}",
                config={
                    'system_instruction': (
                        "You are a professional administrative assistant. Draft clear, polite, "
                        "and highly effective business emails. Never include conversational placeholders "
                        "like 'Here is your email:' in your output. Just populate the structured schema."
                    ),
                    'response_mime_type': 'application/json',
                    'response_schema': EmailResponse,
                    'temperature': 0.7,
                }
            )
            
            # If we reached this line, the request was successful! Let's parse and print.
            email_data: EmailResponse = response.parsed
            
            console.print("\n" + "="*80 + "\n")
            console.print(Panel(email_data.subject, title="[bold cyan]Subject Line[/bold cyan]", expand=False))
            console.print("\n")
            console.print(Panel(email_data.body, title="[bold green]Email Body[/bold green]", expand=False))
            console.print("\n" + "="*80)
            return  # Exit function successfully

        except APIError as e:
            # Check if this is an HTTP 429 (Rate Limit / Resource Exhausted) error
            if e.code == 429:
                if attempt < max_retries:
                    # Calculate wait time: 1s, 2s, 4s...
                    wait_time = backoff_factor ** attempt
                    console.print(
                        f"[bold red]⚠️ Rate limited (HTTP 429).[/bold red] "
                        f"Waiting [bold cyan]{wait_time}s[/bold cyan] before retrying..."
                    )
                    time.sleep(wait_time)
                else:
                    console.print(f"\n[bold red]❌ Failed after {max_retries} retries due to rate limits.[/bold red]")
                    sys.exit(1)
            else:
                # If it's a different API error (like invalid model name or billing error), raise it immediately
                console.print(f"[bold red]API Error encountered:[/bold red] {e}")
                sys.exit(1)
        except Exception as e:
            # Handle non-API errors (like connection dropouts, keyboard interrupts, etc.)
            console.print(f"[bold red]An unexpected fatal error occurred:[/bold red] {e}")
            sys.exit(1)

if __name__ == "__main__":
    console.print("[bold cyan]====================================================================[/bold cyan]")
    console.print("[bold cyan]                       AI BUSINESS EMAIL WRITER                     [/bold cyan]")
    console.print("[bold cyan]====================================================================[/bold cyan]")
    
    console.print("[bold magenta]Describe the email you want to write (e.g., 'polite follow-up to a recruiter'):[/bold magenta]")
    try:
        user_prompt = input("\n>>> ").strip()
        if user_prompt:
            generate_email(user_prompt)
        else:
            console.print("[bold red]Error: No prompt provided.[/bold red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")