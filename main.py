"""
Command-line interface for the RFP Accelerator Agent.
"""

import sys
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from rfp_agent import RFPAcceleratorAgent


console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """RFP Accelerator Agent - Automated Project Kickoff Manager"""
    pass


@cli.command()
@click.option('--rfp-files', '-f', multiple=True, required=True, help='RFP document files')
@click.option('--client', '-c', required=True, help='Client name')
@click.option('--title', '-t', required=True, help='RFP title')
@click.option('--team-members', '-m', multiple=True, help='Team member email addresses')
@click.option('--project', '-p', default='gcp-sandpit-intelia', help='GCP project ID')
@click.option('--config', help='Path to configuration file')
@click.option('--steps', help='Comma-separated list of steps to run (e.g., "1,2,3")')
@click.option('--log-level', default='INFO', help='Logging level')
def run(rfp_files, client, title, team_members, project, config, steps, log_level):
    """Run the complete RFP acceleration workflow."""
    
    console.print(Panel.fit(
        "[bold blue]RFP Accelerator Agent[/bold blue]\n"
        "Automated Project Kickoff Manager",
        border_style="blue"
    ))
    
    # Validate files exist
    for file_path in rfp_files:
        if not Path(file_path).exists():
            console.print(f"[red]Error: File not found: {file_path}[/red]")
            sys.exit(1)
    
    # Parse steps if provided
    steps_to_run = None
    if steps:
        try:
            steps_to_run = [int(s.strip()) for s in steps.split(',')]
        except ValueError:
            console.print("[red]Error: Invalid steps format. Use comma-separated numbers (e.g., '1,2,3')[/red]")
            sys.exit(1)
    
    # Initialize agent
    console.print(f"\n[cyan]Initializing agent for project: {project}[/cyan]")
    agent = RFPAcceleratorAgent(
        gcp_project=project,
        config_path=config,
        log_level=log_level
    )
    
    # Display configuration
    table = Table(title="Workflow Configuration")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Client", client)
    table.add_row("RFP Title", title)
    table.add_row("RFP Files", str(len(rfp_files)))
    table.add_row("Team Members", str(len(team_members)) if team_members else "None (will prompt)")
    table.add_row("GCP Project", project)
    table.add_row("Steps", steps if steps else "All (1-7)")
    
    console.print(table)
    
    # Confirm execution
    if not click.confirm("\nProceed with workflow execution?"):
        console.print("[yellow]Workflow cancelled[/yellow]")
        sys.exit(0)
    
    # Execute workflow
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Executing workflow...", total=None)
            
            result = agent.execute_workflow(
                rfp_files=list(rfp_files),
                client_name=client,
                rfp_title=title,
                team_members=list(team_members) if team_members else None,
                steps_to_run=steps_to_run
            )
            
            progress.update(task, completed=True)
        
        # Display results
        console.print("\n[bold green]✓ Workflow completed successfully![/bold green]\n")
        
        # Show resource URLs
        context = result['context']
        
        resources_table = Table(title="Project Resources")
        resources_table.add_column("Resource", style="cyan")
        resources_table.add_column("URL", style="blue")
        
        if 'folder_url' in context:
            resources_table.add_row("Project Folder", context['folder_url'])
        if 'notebook_url' in context:
            resources_table.add_row("NotebookLM", context['notebook_url'])
        if 'questions_doc_url' in context:
            resources_table.add_row("Follow-up Questions", context['questions_doc_url'])
        if 'answers_doc_url' in context:
            resources_table.add_row("Draft Answers", context['answers_doc_url'])
        if 'plan_doc_url' in context:
            resources_table.add_row("Project Plan", context['plan_doc_url'])
        
        console.print(resources_table)
        
        # Show NotebookLM manual setup instructions if needed
        if context.get('notebooklm_manual_setup'):
            console.print("\n[yellow]Note: NotebookLM requires manual setup[/yellow]")
            console.print(Panel(context['notebooklm_manual_setup'], title="NotebookLM Setup Instructions"))
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Workflow failed: {e}[/bold red]")
        if log_level == 'DEBUG':
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option('--project', '-p', default='gcp-sandpit-intelia', help='GCP project ID')
@click.option('--config', help='Path to configuration file')
def status(project, config):
    """Check the status of the agent and configuration."""
    
    console.print("[cyan]Checking agent status...[/cyan]\n")
    
    # Initialize agent
    agent = RFPAcceleratorAgent(
        gcp_project=project,
        config_path=config,
        log_level='INFO'
    )
    
    # Display status
    status_info = agent.get_status()
    
    table = Table(title="Agent Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Status", status_info['status'])
    table.add_row("Current Step", f"{status_info['current_step']}/7")
    table.add_row("Progress", f"{status_info['progress_percent']:.1f}%")
    
    console.print(table)
    
    if status_info['errors']:
        console.print("\n[red]Errors:[/red]")
        for error in status_info['errors']:
            console.print(f"  • {error}")


@cli.command()
def interactive():
    """Run the agent in interactive mode."""
    
    console.print(Panel.fit(
        "[bold blue]RFP Accelerator Agent[/bold blue]\n"
        "Interactive Mode",
        border_style="blue"
    ))
    
    # Prompt for inputs
    console.print("\n[cyan]Please provide the following information:[/cyan]\n")
    
    client = click.prompt("Client name")
    title = click.prompt("RFP title")
    project = click.prompt("GCP project ID", default="gcp-sandpit-intelia")
    
    # Get RFP files
    rfp_files = []
    console.print("\n[cyan]Enter RFP file paths (press Enter with empty path to finish):[/cyan]")
    while True:
        file_path = click.prompt("File path", default="", show_default=False)
        if not file_path:
            break
        if Path(file_path).exists():
            rfp_files.append(file_path)
        else:
            console.print(f"[red]File not found: {file_path}[/red]")
    
    if not rfp_files:
        console.print("[red]Error: At least one RFP file is required[/red]")
        sys.exit(1)
    
    # Get team members
    team_members = []
    if click.confirm("\nAdd team members now?"):
        console.print("[cyan]Enter team member email addresses (press Enter with empty email to finish):[/cyan]")
        while True:
            email = click.prompt("Email", default="", show_default=False)
            if not email:
                break
            team_members.append(email)
    
    # Run the workflow
    ctx = click.Context(cli)
    ctx.invoke(
        run,
        rfp_files=rfp_files,
        client=client,
        title=title,
        team_members=team_members,
        project=project,
        config=None,
        steps=None,
        log_level='INFO'
    )


if __name__ == '__main__':
    cli()
