import os
import sys
import argparse
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Confirm

from analyzer import StackTraceAnalyzer
from sandbox import DockerSandbox

load_dotenv()
console = Console()

def main():
    parser = argparse.ArgumentParser(description="AI Stack Trace Investigator")
    parser.add_argument("input_file", help="Path to a text file containing the stack trace/logs")
    parser.add_argument("--context", help="Path to an optional text file with code context", default=None)
    parser.add_argument("--auto-run", action="store_true", help="Automatically run sandbox if reproduction is found")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        console.print(f"[bold red]Error: Input file {args.input_file} not found.[/bold red]")
        sys.exit(1)
        
    with open(args.input_file, "r") as f:
        error_input = f.read()
        
    code_context = ""
    if args.context and os.path.exists(args.context):
        with open(args.context, "r") as f:
            code_context = f.read()
            
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Error: OPENAI_API_KEY environment variable not set.[/bold red]")
        sys.exit(1)

    console.print("[bold blue]Analyzing stack trace...[/bold blue]")
    analyzer = StackTraceAnalyzer()
    
    try:
        result = analyzer.analyze(error_input, code_context)
    except Exception as e:
        console.print(f"[bold red]Failed to analyze using OpenAI: {e}[/bold red]")
        sys.exit(1)
        
    if result.causes:
        console.print(Panel("Likely Causes", style="bold green"))
        for i, cause in enumerate(result.causes):
            console.print(f"[bold]{i+1}. {cause.description}[/bold] (Likelihood: {cause.likelihood})")
            console.print(f"   [cyan]Fix Suggestion:[/cyan] {cause.fix_suggestion}\n")
            
    if result.missing_evidence:
        console.print(Panel("Missing Evidence / Questions", style="bold yellow"))
        for item in result.missing_evidence:
            console.print(f"- {item}")
            
    if result.reproduction_code:
        console.print(Panel("Reproduction Code", style="bold magenta"))
        console.print(result.reproduction_code)
        
        run_sandbox = args.auto_run
        if not run_sandbox:
            run_sandbox = Confirm.ask("Do you want to run this reproduction code in a Docker sandbox?")
            
        if run_sandbox:
            console.print("\n[bold blue]Running in Sandbox...[/bold blue]")
            sandbox = DockerSandbox()
            
            # Use dockerfile from current directory
            res = sandbox.run_reproduction(result.reproduction_code)
            
            if res["status"] == "success":
                exit_code = res.get("exit_code")
                logs = res.get("logs")
                if exit_code == 0:
                    console.print("[bold green]Sandbox executed successfully with exit code 0.[/bold green]")
                else:
                    console.print(f"[bold red]Sandbox execution failed with exit code {exit_code}.[/bold red]")
                
                if logs:
                    console.print(Panel(logs, title="Sandbox Logs"))
            else:
                console.print(f"[bold red]Sandbox error: {res.get('message')}[/bold red]")

if __name__ == "__main__":
    main()
