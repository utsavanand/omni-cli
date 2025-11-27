#!/usr/bin/env python3
"""
Omni CLI - Unified wrapper for AI models
Multi-provider chat interface with hierarchical organization
"""

import sys
import re
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from prompt_toolkit import PromptSession, Application
from prompt_toolkit.history import FileHistory
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.markdown import Markdown
from rich.table import Table

from chat import ChatManager
from providers import ProviderManager
from project import ProjectManager
from namespace import NamespaceManager
from summary import SummaryManager

# Initialize console for rich output
console = Console()


# ============================================================================
# Helper Functions for Command Parsing and Validation
# ============================================================================

def parse_flag(args_string, flag_name):
    """
    Parse a flag and its value from an argument string.

    Args:
        args_string: The full argument string (e.g., "chat-name --project my-webapp")
        flag_name: The flag to look for (e.g., "--project")

    Returns:
        tuple: (flag_value, remaining_args) or (None, args_string) if flag not found

    Examples:
        >>> parse_flag("chat-name --project webapp", "--project")
        ("webapp", "chat-name")
        >>> parse_flag("just-a-name", "--project")
        (None, "just-a-name")
    """
    if not args_string:
        return None, args_string

    parts = args_string.split()

    if flag_name not in parts:
        return None, args_string

    try:
        flag_idx = parts.index(flag_name)
        if flag_idx + 1 < len(parts):
            flag_value = parts[flag_idx + 1]
            # Remove flag and value from parts
            remaining_parts = [p for i, p in enumerate(parts) if i not in [flag_idx, flag_idx + 1]]
            remaining_args = ' '.join(remaining_parts)
            return flag_value, remaining_args
        else:
            # Flag exists but no value provided
            return '', args_string
    except (ValueError, IndexError):
        return None, args_string


def parse_quoted_flag(args_string, flag_name):
    """
    Parse a flag that may have quoted or unquoted value.

    Args:
        args_string: The full argument string
        flag_name: The flag to look for (e.g., "--description")

    Returns:
        tuple: (flag_value, remaining_args) or (None, args_string) if flag not found

    Examples:
        >>> parse_quoted_flag('name --description "My desc"', "--description")
        ("My desc", "name")
        >>> parse_quoted_flag('name --description simple', "--description")
        ("simple", "name")
    """
    if not args_string:
        return None, args_string

    # Try to match quoted or unquoted value
    pattern = rf'{flag_name}\s+["\']([^"\']+)["\']|{flag_name}\s+(\S+)'
    match = re.search(pattern, args_string)

    if match:
        flag_value = match.group(1) or match.group(2)
        # Remove the flag and value from args_string
        remaining_args = args_string[:match.start()].strip() + ' ' + args_string[match.end():].strip()
        remaining_args = remaining_args.strip()
        return flag_value, remaining_args

    return None, args_string


def parse_subcommand(args_string):
    """
    Parse a subcommand and its arguments.

    Args:
        args_string: The full argument string

    Returns:
        tuple: (subcommand, subargs) or (None, None) if no args

    Examples:
        >>> parse_subcommand("create my-project")
        ("create", "my-project")
        >>> parse_subcommand("list")
        ("list", "")
    """
    if not args_string:
        return None, None

    parts = args_string.split(maxsplit=1)
    subcommand = parts[0]
    subargs = parts[1] if len(parts) > 1 else ''

    return subcommand, subargs


def validate_name(name, entity_type="name"):
    """
    Validate a name for projects, namespaces, or chats.

    Args:
        name: The name to validate
        entity_type: Type of entity (for error messages)

    Returns:
        tuple: (is_valid, error_message)

    Examples:
        >>> validate_name("my-project")
        (True, None)
        >>> validate_name("")
        (False, "Name cannot be empty")
    """
    if not name or not name.strip():
        return False, f"{entity_type.capitalize()} name cannot be empty"

    if len(name) > 100:
        return False, f"{entity_type.capitalize()} name too long (max 100 characters)"

    # Check for invalid characters (basic validation)
    if name.strip() != name:
        return False, f"{entity_type.capitalize()} name cannot start or end with whitespace"

    return True, None


# ============================================================================
# UI Functions
# ============================================================================

def print_welcome():
    """Display welcome message"""
    welcome = """
[bold cyan]Omni CLI[/bold cyan] [dim]v0.1.0[/dim]
Unified wrapper for AI models

Commands:
  /help                   - Show detailed help
  /new <name>             - Create a new named chat
  /list                   - List all saved chats
  /resume [keyword]       - Interactive menu to resume a chat
  /delete <id/name>       - Delete a chat
  /find <term>            - Search through chat history
  /namespace              - Namespace management commands
  /project                - Project management commands
  /providers              - List available AI providers
  /use <provider>         - Switch to different provider
  /consult <provider> ... - Get merged response from multiple providers
  /exit                   - Exit omni

Type your message to start chatting, or /help for more info!
    """.strip()
    console.print(Panel(welcome, border_style="cyan"))

def run_setup_wizard():
    """Run setup wizard to check and guide provider installation"""
    console.print("\n[bold cyan]Omni CLI Setup Wizard[/bold cyan]\n")
    console.print("Checking for installed AI providers...\n")

    provider_manager = ProviderManager()
    installed = provider_manager.get_installed_providers()
    all_providers = provider_manager.get_all_providers()

    # Show status of each provider
    providers_info = {
        'claude': {
            'name': 'Claude Code',
            'url': 'https://claude.ai/download',
            'install': 'Download from https://claude.ai/download'
        },
        'codex': {
            'name': 'OpenAI/Codex CLI',
            'url': 'https://platform.openai.com/docs',
            'install': 'See installation guide at https://platform.openai.com/docs'
        },
        'gemini': {
            'name': 'Google Gemini CLI',
            'url': 'https://ai.google.dev/',
            'install': 'See installation guide at https://ai.google.dev/'
        }
    }

    for provider in all_providers:
        if provider in installed:
            console.print(f"[green]✓[/green] {providers_info[provider]['name']:<25} [dim]installed[/dim]")
        else:
            console.print(f"[red]✗[/red] {providers_info[provider]['name']:<25} [dim]not installed[/dim]")

    console.print()

    if installed:
        console.print(f"[green]✓ Found {len(installed)} provider(s): {', '.join(installed)}[/green]")
        console.print("\n[bold]You're ready to use Omni CLI![/bold]")
        console.print("Run [cyan]omni[/cyan] to start chatting.\n")
    else:
        console.print("[yellow]⚠  No AI providers found![/yellow]\n")
        console.print("[bold]To use Omni CLI, install at least one provider:[/bold]\n")

        for provider in all_providers:
            info = providers_info[provider]
            console.print(f"[cyan]{info['name']}:[/cyan]")
            console.print(f"  {info['install']}\n")

        console.print("After installation, run [cyan]omni --setup[/cyan] again to verify.\n")

def main():
    """Main entry point"""
    # Check for setup flag
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        return run_setup_wizard()

    # Initialize components
    chat_manager = ChatManager()
    provider_manager = ProviderManager()
    project_manager = ProjectManager()
    namespace_manager = NamespaceManager()
    summary_manager = SummaryManager()

    # Check if any provider is available
    if not provider_manager.has_providers():
        console.print("[red]⚠  No AI providers found![/red]\n")
        console.print("Omni CLI is a wrapper that requires AI providers to be installed.")
        console.print("Run [cyan]omni --setup[/cyan] for installation instructions.\n")
        console.print("Quick links:")
        console.print("  - Claude Code: https://claude.ai/download")
        console.print("  - OpenAI CLI: https://platform.openai.com/docs")
        console.print("  - Gemini CLI: https://ai.google.dev/")
        return 1

    # Setup prompt session with history
    history_file = Path.home() / '.omni' / 'history'
    history_file.parent.mkdir(parents=True, exist_ok=True)

    session = PromptSession(history=FileHistory(str(history_file)))

    # Display welcome
    print_welcome()

    # Show detected providers
    installed = ', '.join(provider_manager.get_installed_providers())
    current = provider_manager.get_current_provider_name()
    console.print(f"[dim]Installed providers: {installed}[/dim]")
    console.print(f"[dim]Current provider: {current}[/dim]\n")

    # Main REPL loop
    current_chat = None

    while True:
        try:
            # Get user input
            user_input = session.prompt('omni> ').strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith('/'):
                command_parts = user_input.split(maxsplit=1)
                command = command_parts[0]
                args = command_parts[1] if len(command_parts) > 1 else None

                # /help - show help
                if command == '/help':
                    help_text = """
[bold cyan]Omni CLI - Command Reference[/bold cyan]

[bold]Provider Management:[/bold]
  [cyan]/providers[/cyan]              List all available AI providers
  [cyan]/use <provider>[/cyan]         Switch to different provider
  [cyan]/consult <provider> ...[/cyan] Get merged response from multiple providers
                              Example: /consult codex explain async/await

[bold]Chat Management:[/bold]
  [cyan]/new <name>[/cyan]             Create a new named chat
                              Example: /new my-feature-chat
  [cyan]/list[/cyan]                   List all saved chats with metadata
  [cyan]/resume [keyword][/cyan]       Interactive menu to resume a chat
                              Example: /resume oauth
                              Use arrow keys to navigate, Enter to select
  [cyan]/find <term>[/cyan]            Search through chat history
  [cyan]/search <term>[/cyan]          Alias for /find
                              Example: /find authentication
  [cyan]/summary <id/name>[/cyan]      Summarize a chat and archive it
                              Options: --type short|long (default: long)
                              Example: /summary my-chat --type short
                              Note: Original chat is deleted
  [cyan]/delete <id/name>[/cyan]       Delete a chat (with confirmation)

[bold]Namespace Management:[/bold]
  [cyan]/namespace create <name>[/cyan] Create a new namespace (group of projects)
                              Example: /namespace create work-projects
  [cyan]/namespace list[/cyan]          List all namespaces
  [cyan]/namespace add <namespace> <project-id>[/cyan]
                              Add project to namespace
  [cyan]/namespace remove <namespace> <project-id>[/cyan]
                              Remove project from namespace
  [cyan]/namespace projects <namespace>[/cyan]
                              List projects in namespace
  [cyan]/namespace delete <namespace>[/cyan]
                              Delete a namespace

[bold]Project Management:[/bold]
  [cyan]/project create <name>[/cyan]  Create a new project
  [cyan]/project list[/cyan]           List all projects
  [cyan]/project add <project> <chat-id>[/cyan]
                              Add chat to project
  [cyan]/project remove <project> <chat-id>[/cyan]
                              Remove chat from project
  [cyan]/project chats <project>[/cyan] List chats in project
  [cyan]/project delete <project>[/cyan] Delete a project

[bold]Utilities:[/bold]
  [cyan]/help[/cyan]                   Show this help message
  [cyan]/exit[/cyan] or [cyan]/quit[/cyan]         Exit omni

[bold]Quick Tips:[/bold]
  • Just type naturally to start chatting (no command needed)
  • Chats are auto-saved with context
  • Organize chats into projects, and projects into namespaces
  • Switch providers mid-conversation to get different perspectives
  • Use /consult to merge insights from multiple AIs

[bold]Examples:[/bold]
  omni> how do I implement OAuth?          [dim]# Start chatting[/dim]
  omni> /namespace create work-projects    [dim]# Create a namespace[/dim]
  omni> /project create my-webapp          [dim]# Create a project[/dim]
  omni> /namespace add work-projects proj123 [dim]# Add project to namespace[/dim]
  omni> /project add my-webapp abc123      [dim]# Add chat to project[/dim]
  omni> /use codex                         [dim]# Switch to Codex[/dim]
  omni> can you show code examples?        [dim]# Continue with new provider[/dim]
  omni> /consult gemini what's best?       [dim]# Get merged response[/dim]
  omni> /summary abc123 --type short       [dim]# Summarize and archive chat[/dim]
  omni> /list                              [dim]# See all chats[/dim]
  omni> /resume                            [dim]# Resume previous chat[/dim]
"""
                    console.print(help_text)
                    continue

                # /exit or /quit
                elif command in ['/exit', '/quit']:
                    console.print("[dim]Goodbye![/dim]")
                    break

                # /new - create a new named chat
                elif command == '/new':
                    if not args:
                        console.print("[yellow]Usage: /new <chat-name> [--project <project-name>][/yellow]")
                        console.print("[dim]Examples:[/dim]")
                        console.print("[dim]  /new my-feature-chat[/dim]")
                        console.print("[dim]  /new authentication --project my-webapp[/dim]")
                        continue

                    # Parse --project flag
                    project_name, remaining_args = parse_flag(args, '--project')

                    # Handle flag without value
                    if project_name == '':
                        console.print("[yellow]--project requires a project name[/yellow]")
                        continue

                    # Get chat name from remaining args
                    chat_name = remaining_args.strip() if remaining_args else None
                    if not chat_name:
                        console.print("[yellow]Chat name is required[/yellow]")
                        console.print("[dim]Usage: /new <chat-name> [--project <project-name>][/dim]")
                        continue

                    # Validate chat name
                    valid, error_msg = validate_name(chat_name, "chat")
                    if not valid:
                        console.print(f"[red]{error_msg}[/red]")
                        continue

                    # Get project ID if project name provided
                    project_id = None
                    if project_name:
                        project = project_manager.get_project(project_name)
                        if project:
                            project_id = project['id']
                        else:
                            console.print(f"[yellow]Warning: Project '{project_name}' not found. Creating chat without project.[/yellow]")

                    # Create new chat with provided name and optional project
                    current_chat = chat_manager.create_chat(name=chat_name, project=project_id)
                    console.print(f"[green]✓ Created chat: {chat_name}[/green]")
                    console.print(f"[dim]Chat ID: {current_chat['chat_id']}[/dim]")
                    if project_id:
                        console.print(f"[dim]Project: {project_name}[/dim]")
                        # Add chat to project
                        project_manager.add_chat(project_name, current_chat['chat_id'])
                    console.print("[dim]Start chatting below:[/dim]\n")
                    continue

                # /providers - list providers
                elif command == '/providers':
                    installed = provider_manager.get_installed_providers()
                    all_providers = provider_manager.get_all_providers()
                    current = provider_manager.get_current_provider_name()

                    console.print("\n[bold]Available Providers:[/bold]")
                    for p in all_providers:
                        status = "✓ installed" if p in installed else "✗ not installed"
                        marker = "→" if p == current else " "
                        console.print(f"{marker} {p:10} {status}")
                    console.print()
                    continue

                # /use <provider> - switch provider
                elif command == '/use':
                    if not args:
                        console.print("[yellow]Usage: /use <provider>[/yellow]")
                        console.print(f"Available: {', '.join(provider_manager.get_installed_providers())}")
                        continue

                    try:
                        provider_manager.switch_provider(args)
                        console.print(f"[green]Switched to {args}[/green]")

                        # Update current chat's provider if active
                        if current_chat:
                            current_chat['provider'] = args

                    except ValueError as e:
                        console.print(f"[red]{e}[/red]")
                    continue

                # /consult <provider> - consult another provider
                elif command == '/consult':
                    if not args:
                        console.print("[yellow]Usage: /consult <provider> <your question>[/yellow]")
                        console.print(f"Available: {', '.join(provider_manager.get_installed_providers())}")
                        continue

                    # Parse provider name and question
                    consult_parts = args.split(maxsplit=1)
                    if len(consult_parts) < 2:
                        console.print("[yellow]Usage: /consult <provider> <your question>[/yellow]")
                        continue

                    consult_provider = consult_parts[0]
                    question = consult_parts[1]

                    # Create chat on first message if needed
                    if current_chat is None:
                        current_chat = chat_manager.create_chat(first_message=question)
                        console.print(f"[dim]Created chat: {current_chat['name']}[/dim]\n")

                    # Add user message to chat
                    chat_manager.add_message(current_chat, 'user', question)

                    # Get conversation context
                    context = chat_manager.get_conversation_context(current_chat)
                    current_provider_name = provider_manager.get_current_provider_name()

                    try:
                        # Get responses and merge with animated spinner
                        with console.status(
                            f"[dim]🤔 Consulting {current_provider_name} and {consult_provider}...[/dim]",
                            spinner="dots"
                        ):
                            merged, current_resp, consult_resp = provider_manager.consult_provider(
                                question, consult_provider, context=context
                            )

                        # Display merged response (render as markdown)
                        console.print(f"\n[bold]Merged Response:[/bold]\n")
                        console.print(Markdown(merged))
                        console.print()

                        # Optionally show individual responses
                        console.print(f"[dim]─── Individual Responses ───[/dim]")
                        console.print(f"[dim]{current_provider_name}:[/dim] {current_resp[:200]}...")
                        console.print(f"[dim]{consult_provider}:[/dim] {consult_resp[:200]}...\n")

                        # Add merged response to chat
                        chat_manager.add_message(
                            current_chat,
                            'assistant',
                            merged,
                            provider=f"{current_provider_name}+{consult_provider}"
                        )

                    except ValueError as e:
                        console.print(f"[red]{e}[/red]")
                    except Exception as e:
                        console.print(f"[red]Error consulting providers: {e}[/red]")
                    continue

                # /list - list all chats
                elif command == '/list':
                    # Loop to allow multiple operations
                    keep_showing_list = True

                    while keep_showing_list:
                        chats = chat_manager.list_chats()
                        summaries = summary_manager.list_summaries()

                        if not chats and not summaries and not namespace_manager.list_namespaces() and not project_manager.list_projects():
                            console.print("[dim]No chats, summaries, projects, or namespaces yet. Start chatting to create your first chat![/dim]")
                            break

                        # Get all namespaces and projects for hierarchy
                        namespaces = namespace_manager.list_namespaces()
                        namespace_lookup = {ns['id']: ns for ns in namespaces}

                        projects = project_manager.list_projects()
                        project_lookup = {p['id']: p for p in projects}

                        # Group projects by namespace
                        namespace_projects = {}
                        standalone_projects = []

                        for project in projects:
                            namespace_id = project.get('namespace')
                            if namespace_id and namespace_id in namespace_lookup:
                                if namespace_id not in namespace_projects:
                                    namespace_projects[namespace_id] = []
                                namespace_projects[namespace_id].append(project['id'])
                            else:
                                standalone_projects.append(project['id'])

                        # Group chats by project
                        project_chats = {}
                        standalone_chats = []

                        for chat in chats:
                            project_id = chat.get('project')
                            if project_id and project_id in project_lookup:
                                if project_id not in project_chats:
                                    project_chats[project_id] = []
                                project_chats[project_id].append(chat)
                            else:
                                standalone_chats.append(chat)

                        # Group summaries by project
                        project_summaries = {}
                        standalone_summaries = []

                        for summary in summaries:
                            project_id = summary.get('project')
                            if project_id and project_id in project_lookup:
                                if project_id not in project_summaries:
                                    project_summaries[project_id] = []
                                project_summaries[project_id].append(summary)
                            else:
                                standalone_summaries.append(summary)

                        # Sort chats and summaries within each project by most recent
                        for project_id in project_chats:
                            project_chats[project_id].sort(key=lambda x: x['updated_at'], reverse=True)
                        for project_id in project_summaries:
                            project_summaries[project_id].sort(key=lambda x: x['created_at'], reverse=True)
                        standalone_chats.sort(key=lambda x: x['updated_at'], reverse=True)
                        standalone_summaries.sort(key=lambda x: x['created_at'], reverse=True)

                        # Build flat list for navigation
                        display_items = []  # (type, data) tuples

                        # Add namespace → project → (chats + summaries) hierarchy
                        for namespace_id, project_ids in namespace_projects.items():
                            namespace = namespace_lookup[namespace_id]
                            display_items.append(('namespace', namespace))

                            for project_id in project_ids:
                                project = project_lookup[project_id]
                                display_items.append(('project', project))

                                # Add chats for this project
                                for chat in project_chats.get(project_id, []):
                                    display_items.append(('chat', chat))

                                # Add summaries for this project
                                for summary in project_summaries.get(project_id, []):
                                    display_items.append(('summary', summary))

                        # Add empty namespaces (namespaces with no projects)
                        for namespace_id, namespace in namespace_lookup.items():
                            if namespace_id not in namespace_projects:
                                display_items.append(('namespace', namespace))

                        # Add standalone projects
                        if standalone_projects:
                            for project_id in standalone_projects:
                                project = project_lookup[project_id]
                                display_items.append(('project', project))

                                # Add chats for this project
                                for chat in project_chats.get(project_id, []):
                                    display_items.append(('chat', chat))

                                # Add summaries for this project
                                for summary in project_summaries.get(project_id, []):
                                    display_items.append(('summary', summary))

                        # Add standalone chats
                        for chat in standalone_chats:
                            display_items.append(('chat', chat))

                        # Add standalone summaries
                        for summary in standalone_summaries:
                            display_items.append(('summary', summary))

                        if not display_items:
                            console.print("[dim]Nothing to display[/dim]")
                            break

                        # Interactive selection
                        selected_index = [0]
                        action_result = [None]  # ('action', data) or None

                        def get_formatted_text():
                            lines = []
                            lines.append(('class:title', f"\n  Browse & Manage - {len(display_items)} items\n"))
                            lines.append(('', "  " + "─" * 75 + "\n"))
                            lines.append(('class:help', "  ↑/↓: Navigate  |  Enter: Open  |  d: Delete  |  r: Rename  |  Esc: Exit\n"))
                            lines.append(('', "  " + "─" * 75 + "\n\n"))

                            for i, (item_type, data) in enumerate(display_items):
                                indent = ""
                                icon = ""
                                label = ""

                                if item_type == 'namespace':
                                    indent = " "
                                    icon = "📦"
                                    project_count = len(namespace_projects.get(data['id'], []))
                                    label = f"{data['name']} ({project_count} projects)"
                                elif item_type == 'project':
                                    indent = "   "
                                    icon = "📁"
                                    chat_count = len(project_chats.get(data['id'], []))
                                    summary_count = len(project_summaries.get(data['id'], []))
                                    total = chat_count + summary_count
                                    label = f"{data['name']} ({chat_count} chats, {summary_count} summaries)"
                                elif item_type == 'chat':
                                    indent = "     "
                                    icon = "💬"
                                    label = f"{data['name'][:35]:<37} {data['provider']:<7} {data['message_count']:>2} msgs"
                                elif item_type == 'summary':
                                    indent = "     "
                                    icon = "📄"
                                    summary_type = data.get('type', 'long')
                                    label = f"{data['name'][:35]:<37} {data['provider']:<7} {summary_type} summary"

                                if i == selected_index[0]:
                                    lines.append(('class:selected', f"{indent}→ {icon} {label}\n"))
                                else:
                                    lines.append(('', f"{indent}  {icon} {label}\n"))

                            return lines

                        kb = KeyBindings()

                        @kb.add('up')
                        def move_up(event):
                            if selected_index[0] > 0:
                                selected_index[0] -= 1

                        @kb.add('down')
                        def move_down(event):
                            if selected_index[0] < len(display_items) - 1:
                                selected_index[0] += 1

                        @kb.add('enter')
                        def select_item(event):
                            item_type, data = display_items[selected_index[0]]
                            if item_type == 'chat':
                                action_result[0] = ('resume', data)
                                event.app.exit()
                            elif item_type == 'summary':
                                action_result[0] = ('view_summary', data)
                                event.app.exit()

                        @kb.add('d')
                        def delete_item(event):
                            action_result[0] = ('delete', display_items[selected_index[0]])
                            event.app.exit()

                        @kb.add('r')
                        def rename_item(event):
                            action_result[0] = ('rename', display_items[selected_index[0]])
                            event.app.exit()

                        @kb.add('escape')
                        @kb.add('c-c')
                        def cancel(event):
                            action_result[0] = ('cancel', None)
                            event.app.exit()

                        control = FormattedTextControl(text=get_formatted_text, focusable=True)
                        layout = Layout(Window(content=control, wrap_lines=True))
                        app = Application(layout=layout, key_bindings=kb, full_screen=False, mouse_support=False)

                        try:
                            app.run()

                            # Handle cancel/escape
                            if action_result[0] and action_result[0][0] == 'cancel':
                                keep_showing_list = False
                            elif action_result[0]:
                                action, item_data = action_result[0]
                                item_type, data = item_data if action in ['delete', 'rename'] else (None, None)

                                if action == 'resume':
                                    # Resume chat and exit list
                                    loaded_chat = chat_manager.load_chat(action_result[0][1]['chat_id'])
                                    if loaded_chat:
                                        current_chat = loaded_chat
                                        console.print(f"\n[green]✓ Resumed: {current_chat['name']}[/green]")
                                        console.print(f"[dim]  Provider: {current_chat['provider']} | Messages: {current_chat['message_count']}[/dim]\n")
                                    keep_showing_list = False

                                elif action == 'view_summary':
                                    # View summary content and stay in list
                                    summary_data = action_result[0][1]
                                    loaded_summary = summary_manager.load_summary(summary_data['summary_id'])
                                    if loaded_summary:
                                        console.print(f"\n[bold cyan]Summary: {loaded_summary['name']}[/bold cyan]")
                                        console.print(f"[dim]Type: {loaded_summary['type']} | Created: {loaded_summary['created_at'][:10]} | Provider: {loaded_summary['provider']}[/dim]")
                                        console.print(f"[dim]Original Chat ID: {loaded_summary['original_chat_id']}[/dim]")
                                        console.print("─" * 75)

                                        # Display summary content
                                        summary_md = Markdown(loaded_summary['content'])
                                        console.print(summary_md)
                                        console.print("─" * 75)

                                        # Prompt to continue
                                        session.prompt("\n[Press Enter to continue]")
                                    else:
                                        console.print(f"[red]Failed to load summary[/red]")
                                        session.prompt("\n[Press Enter to continue]")

                                elif action == 'delete':
                                    # Delete item with confirmation
                                    console.print()
                                    if item_type == 'namespace':
                                        console.print(f"[yellow]⚠  Delete namespace: {data['name']}?[/yellow]")
                                        console.print(f"[dim]  Projects will be preserved[/dim]")
                                    elif item_type == 'project':
                                        console.print(f"[yellow]⚠  Delete project: {data['name']}?[/yellow]")
                                        console.print(f"[dim]  Chats and summaries will be preserved[/dim]")
                                    elif item_type == 'chat':
                                        console.print(f"[yellow]⚠  Delete chat: {data['name']}?[/yellow]")
                                        console.print(f"[dim]  ID: {data['chat_id']} | Messages: {data['message_count']}[/dim]")
                                    elif item_type == 'summary':
                                        console.print(f"[yellow]⚠  Delete summary: {data['name']}?[/yellow]")
                                        console.print(f"[dim]  ID: {data['summary_id']} | Type: {data.get('type', 'long')}[/dim]")

                                    confirm = session.prompt("\nType 'yes' to confirm: ").strip().lower()
                                    if confirm == 'yes':
                                        if item_type == 'namespace':
                                            namespace_manager.delete_namespace(data['name'])
                                            console.print(f"[green]✓ Deleted namespace: {data['name']}[/green]\n")
                                        elif item_type == 'project':
                                            project_manager.delete_project(data['name'])
                                            console.print(f"[green]✓ Deleted project: {data['name']}[/green]\n")
                                        elif item_type == 'chat':
                                            chat_manager.delete_chat(data['chat_id'])
                                            console.print(f"[green]✓ Deleted chat: {data['name']}[/green]\n")
                                            if current_chat and current_chat.get('chat_id') == data['chat_id']:
                                                current_chat = None
                                        elif item_type == 'summary':
                                            summary_manager.delete_summary(data['summary_id'])
                                            console.print(f"[green]✓ Deleted summary: {data['name']}[/green]\n")
                                    else:
                                        console.print("[dim]Deletion cancelled[/dim]\n")

                                elif action == 'rename':
                                    # Rename item
                                    console.print()
                                    if item_type == 'namespace':
                                        console.print(f"[cyan]Rename namespace: {data['name']}[/cyan]")
                                        new_name = session.prompt("New name: ").strip()
                                        if new_name:
                                            try:
                                                if namespace_manager.rename_namespace(data['id'], new_name):
                                                    console.print(f"[green]✓ Renamed to: {new_name}[/green]\n")
                                                else:
                                                    console.print("[red]Failed to rename namespace[/red]\n")
                                            except ValueError as e:
                                                console.print(f"[red]{e}[/red]\n")
                                            except Exception as e:
                                                console.print(f"[red]Error: {e}[/red]\n")
                                        else:
                                            console.print("[dim]Rename cancelled[/dim]\n")
                                    elif item_type == 'project':
                                        console.print(f"[cyan]Rename project: {data['name']}[/cyan]")
                                        new_name = session.prompt("New name: ").strip()
                                        if new_name:
                                            try:
                                                if project_manager.rename_project(data['id'], new_name):
                                                    console.print(f"[green]✓ Renamed to: {new_name}[/green]\n")
                                                else:
                                                    console.print("[red]Failed to rename project[/red]\n")
                                            except Exception as e:
                                                console.print(f"[red]Error: {e}[/red]\n")
                                        else:
                                            console.print("[dim]Rename cancelled[/dim]\n")
                                    elif item_type == 'chat':
                                        console.print(f"[cyan]Rename chat: {data['name']}[/cyan]")
                                        new_name = session.prompt("New name: ").strip()
                                        if new_name:
                                            try:
                                                if chat_manager.rename_chat(data['chat_id'], new_name):
                                                    console.print(f"[green]✓ Renamed to: {new_name}[/green]\n")
                                                    # Update current_chat if it was renamed
                                                    if current_chat and current_chat.get('chat_id') == data['chat_id']:
                                                        current_chat['name'] = new_name
                                                else:
                                                    console.print("[red]Failed to rename chat[/red]\n")
                                            except ValueError as e:
                                                console.print(f"[red]{e}[/red]\n")
                                            except Exception as e:
                                                console.print(f"[red]Error: {e}[/red]\n")
                                        else:
                                            console.print("[dim]Rename cancelled[/dim]\n")

                        except Exception as e:
                            console.print(f"[red]Error: {e}[/red]")

                    continue

                # /resume - interactively resume a previous chat
                elif command == '/resume':
                    chats = chat_manager.list_chats()

                    if not chats:
                        console.print("[yellow]No chats to resume. Start chatting to create your first chat![/yellow]")
                        continue

                    # Filter by keyword if provided
                    keyword = args.lower() if args else None
                    if keyword:
                        filtered_chats = [
                            c for c in chats
                            if keyword in c['name'].lower() or keyword in c.get('provider', '').lower()
                        ]
                        if not filtered_chats:
                            console.print(f"[yellow]No chats matching '{args}'[/yellow]")
                            continue
                        chats = filtered_chats

                    # Get all namespaces, projects, and build hierarchy
                    namespaces = namespace_manager.list_namespaces()
                    namespace_lookup = {ns['id']: ns for ns in namespaces}

                    projects = project_manager.list_projects()
                    project_lookup = {p['id']: p for p in projects}

                    # Group projects by namespace
                    namespace_projects = {}  # namespace_id -> list of project_ids
                    standalone_projects = []  # projects without namespace

                    for project in projects:
                        namespace_id = project.get('namespace')
                        if namespace_id and namespace_id in namespace_lookup:
                            if namespace_id not in namespace_projects:
                                namespace_projects[namespace_id] = []
                            namespace_projects[namespace_id].append(project['id'])
                        else:
                            standalone_projects.append(project['id'])

                    # Group chats by project
                    project_chats = {}  # project_id -> list of chats
                    standalone_chats = []  # chats without project

                    for chat in chats:
                        project_id = chat.get('project')
                        if project_id and project_id in project_lookup:
                            if project_id not in project_chats:
                                project_chats[project_id] = []
                            project_chats[project_id].append(chat)
                        else:
                            standalone_chats.append(chat)

                    # Sort chats within each project by most recent
                    for project_id in project_chats:
                        project_chats[project_id].sort(key=lambda x: x['updated_at'], reverse=True)
                    standalone_chats.sort(key=lambda x: x['updated_at'], reverse=True)

                    # Build flat list for navigation with hierarchy headers
                    display_items = []  # List of (type, data) tuples

                    # Add namespace → project → chat hierarchy
                    for namespace_id, project_ids in namespace_projects.items():
                        namespace = namespace_lookup[namespace_id]
                        display_items.append(('namespace_header', namespace))

                        for project_id in project_ids:
                            project = project_lookup[project_id]
                            chat_count = len(project_chats.get(project_id, []))
                            display_items.append(('project_header', {'project': project, 'chat_count': chat_count}))

                            for chat in project_chats.get(project_id, []):
                                display_items.append(('chat', chat))

                    # Add standalone projects (not in any namespace)
                    if standalone_projects:
                        if namespace_projects:  # Only show header if there are namespaces above
                            display_items.append(('standalone_projects_header', None))

                        for project_id in standalone_projects:
                            project = project_lookup[project_id]
                            chat_count = len(project_chats.get(project_id, []))
                            display_items.append(('project_header', {'project': project, 'chat_count': chat_count}))

                            for chat in project_chats.get(project_id, []):
                                display_items.append(('chat', chat))

                    # Add standalone chats (not in any project)
                    if standalone_chats:
                        display_items.append(('standalone_chats_header', None))
                        for chat in standalone_chats:
                            display_items.append(('chat', chat))

                    if not display_items:
                        console.print("[yellow]No chats available[/yellow]")
                        continue

                    # Interactive selection with pure keyboard
                    # Find first chat index (skip headers)
                    first_chat_index = 0
                    for i, (item_type, _) in enumerate(display_items):
                        if item_type == 'chat':
                            first_chat_index = i
                            break

                    selected_index = [first_chat_index]  # Mutable container for closure
                    result_chat = [None]   # Selected chat

                    def get_formatted_text():
                        """Generate the formatted text for display"""
                        lines = []

                        # Title
                        title = f"Resume Chat - {len(chats)} chat(s) available"
                        if keyword:
                            title += f" (filtered by '{args}')"
                        lines.append(('class:title', f"\n  {title}\n"))
                        lines.append(('', "  " + "─" * 70 + "\n"))
                        lines.append(('class:help', "  ↑/↓: Navigate  |  Enter: Select  |  Esc: Cancel\n"))
                        lines.append(('', "  " + "─" * 70 + "\n\n"))

                        # Display hierarchical list
                        for i, (item_type, data) in enumerate(display_items):
                            if item_type == 'namespace_header':
                                namespace = data
                                project_count = len(namespace_projects[namespace['id']])
                                lines.append(('class:namespace', f" [Namespace: {namespace['name']} ({project_count} projects)]\n"))
                            elif item_type == 'project_header':
                                project = data['project']
                                chat_count = data['chat_count']
                                lines.append(('class:project', f"   [Project: {project['name']} ({chat_count} chats)]\n"))
                            elif item_type == 'standalone_projects_header':
                                lines.append(('class:namespace', f" [Standalone Projects]\n"))
                            elif item_type == 'standalone_chats_header':
                                lines.append(('class:project', f"   [Standalone Chats]\n"))
                            elif item_type == 'chat':
                                chat_info = data
                                updated = chat_info['updated_at'][:10]
                                name = chat_info['name'][:32]
                                provider = chat_info['provider']
                                msg_count = chat_info['message_count']

                                if i == selected_index[0]:
                                    # Highlighted
                                    lines.append(('class:selected', f"     → {name:<34} {provider:<7} {msg_count:>2} msgs {updated}\n"))
                                else:
                                    # Normal
                                    lines.append(('', f"       {name:<34} {provider:<7} {msg_count:>2} msgs {updated}\n"))

                        return lines

                    # Key bindings
                    kb = KeyBindings()

                    @kb.add('up')
                    def move_up(event):
                        # Skip headers
                        new_index = selected_index[0] - 1
                        while new_index >= 0:
                            item_type, _ = display_items[new_index]
                            if item_type == 'chat':
                                selected_index[0] = new_index
                                break
                            new_index -= 1

                    @kb.add('down')
                    def move_down(event):
                        # Skip headers
                        new_index = selected_index[0] + 1
                        while new_index < len(display_items):
                            item_type, _ = display_items[new_index]
                            if item_type == 'chat':
                                selected_index[0] = new_index
                                break
                            new_index += 1

                    @kb.add('enter')
                    def select(event):
                        item_type, data = display_items[selected_index[0]]
                        if item_type == 'chat':
                            result_chat[0] = data
                            event.app.exit()

                    @kb.add('escape')
                    @kb.add('c-c')
                    def cancel(event):
                        event.app.exit()

                    # Create layout
                    control = FormattedTextControl(
                        text=get_formatted_text,
                        focusable=True,
                    )

                    layout = Layout(
                        Window(content=control, wrap_lines=True)
                    )

                    # Create and run application
                    app = Application(
                        layout=layout,
                        key_bindings=kb,
                        full_screen=False,
                        mouse_support=False,
                    )

                    try:
                        app.run()

                        if result_chat[0]:
                            # Load and resume the selected chat
                            loaded_chat = chat_manager.load_chat(result_chat[0]['chat_id'])
                            if loaded_chat:
                                current_chat = loaded_chat
                                console.print(f"\n[green]✓ Resumed: {current_chat['name']}[/green]")
                                console.print(f"[dim]  Provider: {current_chat['provider']} | Messages: {current_chat['message_count']}[/dim]")

                                # Show last few messages as context
                                messages = current_chat.get('messages', [])
                                if messages:
                                    console.print("\n[bold]Recent conversation:[/bold]")
                                    for msg in messages[-3:]:
                                        role_display = "[cyan]You[/cyan]" if msg['role'] == 'user' else f"[yellow]Assistant[/yellow]"
                                        preview = msg['content'][:150].replace('\n', ' ')
                                        if len(msg['content']) > 150:
                                            preview += "..."
                                        console.print(f"  {role_display}: {preview}")

                                console.print("\n[dim]Continue the conversation:[/dim]\n")
                        else:
                            console.print("\n[dim]Cancelled[/dim]")
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")

                    continue

                # /delete - delete a chat
                elif command == '/delete':
                    if not args:
                        console.print("[yellow]Usage: /delete <chat-id or chat-name>[/yellow]")
                        console.print("[dim]Tip: Use /list to see available chats[/dim]")
                        continue

                    # Try to find the chat first
                    chat_to_delete = None
                    chats = chat_manager.list_chats()
                    for chat in chats:
                        if chat['chat_id'] == args or chat['name'] == args:
                            chat_to_delete = chat
                            break

                    if not chat_to_delete:
                        console.print(f"[red]Chat '{args}' not found[/red]")
                        console.print("[dim]Use /list to see available chats[/dim]")
                        continue

                    # Show confirmation
                    console.print(f"\n[yellow]⚠  Delete chat: {chat_to_delete['name']}?[/yellow]")
                    console.print(f"[dim]  ID: {chat_to_delete['chat_id']}[/dim]")
                    console.print(f"[dim]  Messages: {chat_to_delete['message_count']}[/dim]")
                    console.print(f"[dim]  Last updated: {chat_to_delete['updated_at'][:10]}[/dim]")

                    confirm = session.prompt("\nType 'yes' to confirm deletion: ").strip().lower()

                    if confirm == 'yes':
                        if chat_manager.delete_chat(args):
                            console.print(f"[green]✓ Deleted chat: {chat_to_delete['name']}[/green]")

                            # Clear current_chat if it was deleted
                            if current_chat and current_chat.get('chat_id') == chat_to_delete['chat_id']:
                                current_chat = None
                        else:
                            console.print("[red]Error deleting chat[/red]")
                    else:
                        console.print("[dim]Deletion cancelled[/dim]")

                    continue

                # /summary - summarize a chat and archive it
                elif command == '/summary':
                    if not args:
                        console.print("[yellow]Usage: /summary <chat-id or chat-name> [--type short|long][/yellow]")
                        console.print("\n[dim]Examples:[/dim]")
                        console.print("[dim]  /summary abc123              # Generate long summary[/dim]")
                        console.print("[dim]  /summary my-chat --type short  # Generate 50-100 word summary[/dim]")
                        console.print("\n[dim]Note: The original chat will be deleted and replaced with the summary[/dim]")
                        continue

                    # Parse --type flag
                    summary_type, remaining_args = parse_flag(args, '--type')

                    # Validate summary type
                    if summary_type and summary_type not in ['short', 'long']:
                        console.print("[yellow]--type must be either 'short' or 'long'[/yellow]")
                        continue

                    # Default to long if not specified
                    if not summary_type:
                        summary_type = 'long'

                    # Get chat identifier from remaining args
                    chat_identifier = remaining_args.strip() if remaining_args else None
                    if not chat_identifier:
                        console.print("[yellow]Chat ID or name is required[/yellow]")
                        console.print("[dim]Usage: /summary <chat-id or chat-name> [--type short|long][/dim]")
                        continue

                    # Try to find and load the chat
                    chat_to_summarize = chat_manager.load_chat(chat_identifier)

                    if not chat_to_summarize:
                        console.print(f"[red]Chat '{chat_identifier}' not found[/red]")
                        console.print("[dim]Use /list to see available chats[/dim]")
                        continue

                    # Check if chat has messages
                    if not chat_to_summarize.get('messages') or len(chat_to_summarize['messages']) == 0:
                        console.print("[yellow]Chat has no messages to summarize[/yellow]")
                        continue

                    # Show confirmation
                    console.print(f"\n[cyan]Summarize chat: {chat_to_summarize['name']}[/cyan]")
                    console.print(f"[dim]  ID: {chat_to_summarize['chat_id']}[/dim]")
                    console.print(f"[dim]  Messages: {chat_to_summarize['message_count']}[/dim]")
                    console.print(f"[dim]  Type: {summary_type}[/dim]")
                    console.print(f"[dim]  Last updated: {chat_to_summarize['updated_at'][:10]}[/dim]")
                    console.print("\n[yellow]⚠  The original chat will be deleted and replaced with a summary file[/yellow]")

                    confirm = session.prompt("\nType 'yes' to confirm: ").strip().lower()

                    if confirm != 'yes':
                        console.print("[dim]Summary cancelled[/dim]")
                        continue

                    # Generate summary using AI provider
                    try:
                        # Build conversation context
                        conversation_text = []
                        for msg in chat_to_summarize['messages']:
                            role_label = "User" if msg['role'] == 'user' else "Assistant"
                            conversation_text.append(f"{role_label}: {msg['content']}")

                        full_conversation = "\n\n".join(conversation_text)

                        # Create summary prompt based on type
                        if summary_type == 'short':
                            summary_prompt = f"""Please provide a concise summary of the following conversation in 50-100 words. Focus on the key topics discussed and main conclusions.

Conversation:
{full_conversation}

Summary (50-100 words):"""
                        else:  # long
                            summary_prompt = f"""Please provide a detailed summary of the following conversation. Include:
1. Main topics and questions discussed
2. Key solutions or insights provided
3. Important code examples or technical details
4. Action items or next steps (if any)
5. Overall conclusions

Conversation:
{full_conversation}

Detailed Summary:"""

                        # Show status while generating
                        with console.status("[cyan]Generating summary...[/cyan]"):
                            summary_content = provider_manager.send_message(summary_prompt)

                        # Create summary
                        summary = summary_manager.create_summary(
                            chat_name=chat_to_summarize['name'],
                            chat_id=chat_to_summarize['chat_id'],
                            summary_content=summary_content,
                            summary_type=summary_type,
                            project=chat_to_summarize.get('project'),
                            provider=provider_manager.get_current_provider_name()
                        )

                        # Delete the original chat
                        chat_manager.delete_chat(chat_to_summarize['chat_id'])

                        # Clear current_chat if it was summarized
                        if current_chat and current_chat.get('chat_id') == chat_to_summarize['chat_id']:
                            current_chat = None

                        console.print(f"\n[green]✓ Summary created: {summary['name']}[/green]")
                        console.print(f"[dim]  Type: {summary_type}[/dim]")
                        console.print(f"[dim]  Words: {summary['word_count']}[/dim]")
                        console.print(f"[dim]  Original chat deleted[/dim]")

                        # Show preview of summary
                        console.print("\n[cyan]Preview:[/cyan]")
                        preview = summary_content[:200] + "..." if len(summary_content) > 200 else summary_content
                        console.print(f"[dim]{preview}[/dim]\n")

                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")

                    continue

                # /namespace - namespace management commands
                elif command == '/namespace':
                    if not args:
                        console.print("[yellow]Usage: /namespace <subcommand> [args][/yellow]")
                        console.print("\nAvailable subcommands:")
                        console.print("  [cyan]create <name> [--description <desc>][/cyan] - Create a new namespace")
                        console.print("  [cyan]list[/cyan]                                  - List all namespaces")
                        console.print("  [cyan]add <namespace> <project-id>[/cyan]          - Add project to namespace")
                        console.print("  [cyan]remove <namespace> <project-id>[/cyan]       - Remove project from namespace")
                        console.print("  [cyan]projects <namespace>[/cyan]                  - List projects in namespace")
                        console.print("  [cyan]delete <namespace>[/cyan]                    - Delete a namespace")
                        console.print("\nExamples:")
                        console.print("  /namespace create work-projects --description 'All work-related projects'")
                        console.print("  /namespace add work-projects proj123")
                        console.print("  /namespace projects work-projects")
                        continue

                    # Parse subcommand
                    subcommand, subargs = parse_subcommand(args)

                    if not subcommand:
                        console.print("[yellow]Usage: /namespace <subcommand> [args][/yellow]")
                        console.print("[dim]Use /namespace without arguments to see available subcommands[/dim]")
                        continue

                    # /namespace create <name> [--description <desc>]
                    if subcommand == 'create':
                        if not subargs:
                            console.print("[yellow]Usage: /namespace create <name> [--description <desc>][/yellow]")
                            console.print("[dim]Examples:[/dim]")
                            console.print("[dim]  /namespace create work-projects[/dim]")
                            console.print("[dim]  /namespace create personal --description 'Personal projects'[/dim]")
                            continue

                        # Parse --description flag
                        description, remaining_args = parse_quoted_flag(subargs, '--description')

                        # Handle flag without value
                        if description == '':
                            console.print("[yellow]--description requires a value[/yellow]")
                            continue

                        # Get namespace name from remaining args
                        namespace_name = remaining_args.strip() if remaining_args else None
                        if not namespace_name:
                            console.print("[yellow]Namespace name is required[/yellow]")
                            console.print("[dim]Usage: /namespace create <name> [--description <desc>][/dim]")
                            continue

                        # Validate namespace name
                        valid, error_msg = validate_name(namespace_name, "namespace")
                        if not valid:
                            console.print(f"[red]{error_msg}[/red]")
                            continue

                        try:
                            namespace = namespace_manager.create_namespace(namespace_name, description)
                            console.print(f"[green]✓ Created namespace: {namespace['name']}[/green]")
                            console.print(f"[dim]Namespace ID: {namespace['id']}[/dim]")
                            if description:
                                console.print(f"[dim]Description: {description}[/dim]")
                        except ValueError as e:
                            console.print(f"[red]{e}[/red]")

                    # /namespace list
                    elif subcommand == 'list':
                        namespaces = namespace_manager.list_namespaces(include_stats=True)

                        if not namespaces:
                            console.print("[dim]No namespaces yet. Create one with /namespace create <name>[/dim]")
                            continue

                        console.print("\n[bold]Namespaces:[/bold]")
                        console.print("[dim]Name                     Projects  Description[/dim]")
                        console.print("[dim]" + "─" * 70 + "[/dim]")

                        for ns in namespaces:
                            name = ns['name'][:25]
                            project_count = ns['project_count']
                            description = ns.get('description', '')[:35]
                            console.print(f"{name:<25} {project_count:<9} {description}")

                        console.print()

                    # /namespace add <namespace> <project-id>
                    elif subcommand == 'add':
                        parts = subargs.split(maxsplit=1)
                        if len(parts) < 2:
                            console.print("[yellow]Usage: /namespace add <namespace> <project-id>[/yellow]")
                            console.print("[dim]Example: /namespace add work-projects proj123[/dim]")
                            continue

                        namespace_name = parts[0]
                        project_id = parts[1]

                        # Get namespace to get its ID
                        namespace = namespace_manager.get_namespace(namespace_name)
                        if not namespace:
                            console.print(f"[red]Namespace '{namespace_name}' not found[/red]")
                            continue

                        # Add project to namespace
                        result = namespace_manager.add_project(namespace_name, project_id)
                        if result:
                            # Also update the project's namespace field
                            project_manager.set_namespace(project_id, namespace['id'])
                            console.print(f"[green]✓ Added project {project_id} to namespace {namespace_name}[/green]")
                        else:
                            console.print(f"[red]Failed to add project to namespace[/red]")

                    # /namespace remove <namespace> <project-id>
                    elif subcommand == 'remove':
                        parts = subargs.split(maxsplit=1)
                        if len(parts) < 2:
                            console.print("[yellow]Usage: /namespace remove <namespace> <project-id>[/yellow]")
                            continue

                        namespace_name = parts[0]
                        project_id = parts[1]

                        result = namespace_manager.remove_project(namespace_name, project_id)
                        if result:
                            # Also clear the project's namespace field
                            project_manager.set_namespace(project_id, None)
                            console.print(f"[green]✓ Removed project {project_id} from namespace {namespace_name}[/green]")
                        else:
                            console.print(f"[red]Namespace or project not found[/red]")

                    # /namespace projects <namespace>
                    elif subcommand == 'projects':
                        if not subargs:
                            console.print("[yellow]Usage: /namespace projects <namespace>[/yellow]")
                            continue

                        namespace_name = subargs.strip()
                        project_ids = namespace_manager.get_namespace_projects(namespace_name)

                        if project_ids is None:
                            console.print(f"[red]Namespace '{namespace_name}' not found[/red]")
                            continue

                        if not project_ids:
                            console.print(f"[dim]No projects in namespace '{namespace_name}' yet[/dim]")
                            continue

                        # Get project details
                        console.print(f"\n[bold]Projects in '{namespace_name}':[/bold]")
                        console.print("[dim]ID       Name                          Chats  Last Updated[/dim]")
                        console.print("[dim]" + "─" * 70 + "[/dim]")

                        for project_id in project_ids:
                            project = project_manager.get_project(project_id)
                            if project:
                                name = project['name'][:28] + '...' if len(project['name']) > 28 else project['name']
                                chat_count = len(project.get('chat_ids', []))
                                updated = project['updated_at'][:10]
                                console.print(f"{project_id}  {name:<30} {chat_count:<6} {updated}")

                        console.print()

                    # /namespace delete <namespace>
                    elif subcommand == 'delete':
                        if not subargs:
                            console.print("[yellow]Usage: /namespace delete <namespace>[/yellow]")
                            continue

                        namespace_name = subargs.strip()
                        namespace = namespace_manager.get_namespace(namespace_name)

                        if not namespace:
                            console.print(f"[red]Namespace '{namespace_name}' not found[/red]")
                            continue

                        # Show confirmation
                        console.print(f"\n[yellow]⚠  Delete namespace: {namespace['name']}?[/yellow]")
                        console.print(f"[dim]  Projects: {len(namespace.get('project_ids', []))}[/dim]")
                        console.print(f"[dim]  Created: {namespace['created_at'][:10]}[/dim]")
                        console.print("\n[dim]Note: This will NOT delete the projects, only the namespace.[/dim]")

                        confirm = session.prompt("\nType 'yes' to confirm deletion: ").strip().lower()

                        if confirm == 'yes':
                            if namespace_manager.delete_namespace(namespace_name):
                                console.print(f"[green]✓ Deleted namespace: {namespace['name']}[/green]")
                            else:
                                console.print("[red]Error deleting namespace[/red]")
                        else:
                            console.print("[dim]Deletion cancelled[/dim]")

                    else:
                        console.print(f"[red]Unknown subcommand: {subcommand}[/red]")
                        console.print("[dim]Use /namespace without arguments to see available subcommands[/dim]")

                    continue

                # /project - project management commands
                elif command == '/project':
                    if not args:
                        console.print("[yellow]Usage: /project <subcommand> [args][/yellow]")
                        console.print("\nAvailable subcommands:")
                        console.print("  [cyan]create <name> [--namespace <ns>][/cyan] - Create a new project")
                        console.print("  [cyan]list[/cyan]                             - List all projects")
                        console.print("  [cyan]add <project> <chat-id>[/cyan]          - Add chat to project")
                        console.print("  [cyan]remove <project> <chat-id>[/cyan]       - Remove chat from project")
                        console.print("  [cyan]chats <project>[/cyan]                  - List chats in project")
                        console.print("  [cyan]delete <project>[/cyan]                 - Delete a project")
                        console.print("\nExamples:")
                        console.print("  /project create my-webapp")
                        console.print("  /project create api-service --namespace work-projects")
                        console.print("  /project add my-webapp abc123")
                        console.print("  /project chats my-webapp")
                        continue

                    # Parse subcommand
                    subcommand, subargs = parse_subcommand(args)

                    if not subcommand:
                        console.print("[yellow]Usage: /project <subcommand> [args][/yellow]")
                        console.print("[dim]Use /project without arguments to see available subcommands[/dim]")
                        continue

                    # /project create <name> [--namespace <namespace>]
                    if subcommand == 'create':
                        if not subargs:
                            console.print("[yellow]Usage: /project create <name> [--namespace <namespace>][/yellow]")
                            console.print("[dim]Examples:[/dim]")
                            console.print("[dim]  /project create my-webapp[/dim]")
                            console.print("[dim]  /project create api-service --namespace work-projects[/dim]")
                            continue

                        # Parse --namespace flag
                        namespace_name, remaining_args = parse_flag(subargs, '--namespace')

                        # Handle flag without value
                        if namespace_name == '':
                            console.print("[yellow]--namespace requires a namespace name[/yellow]")
                            continue

                        # Get project name from remaining args
                        project_name = remaining_args.strip() if remaining_args else None
                        if not project_name:
                            console.print("[yellow]Project name is required[/yellow]")
                            console.print("[dim]Usage: /project create <name> [--namespace <namespace>][/dim]")
                            continue

                        # Validate project name
                        valid, error_msg = validate_name(project_name, "project")
                        if not valid:
                            console.print(f"[red]{error_msg}[/red]")
                            continue

                        try:
                            # Create project with namespace
                            project = project_manager.create_project(project_name, namespace=namespace_name)
                            console.print(f"[green]✓ Created project: {project['name']}[/green]")
                            console.print(f"[dim]Project ID: {project['id']}[/dim]")

                            # If namespace specified, add project to namespace
                            if namespace_name:
                                namespace = namespace_manager.get_namespace(namespace_name)
                                if namespace:
                                    namespace_manager.add_project(namespace_name, project['id'])
                                    console.print(f"[dim]Added to namespace: {namespace_name}[/dim]")
                                else:
                                    console.print(f"[yellow]Warning: Namespace '{namespace_name}' not found. Project created without namespace.[/yellow]")

                        except ValueError as e:
                            console.print(f"[red]{e}[/red]")

                    # /project list
                    elif subcommand == 'list':
                        projects = project_manager.list_projects(include_stats=True)

                        if not projects:
                            console.print("[dim]No projects yet. Create one with /project create <name>[/dim]")
                            continue

                        console.print("\n[bold]Projects:[/bold]")
                        console.print("[dim]Name                     Chats  Last Updated[/dim]")
                        console.print("[dim]" + "─" * 50 + "[/dim]")

                        for proj in projects:
                            name = proj['name'][:25]
                            chat_count = proj['chat_count']
                            updated = proj['updated_at'][:10]
                            console.print(f"{name:<25} {chat_count:<6} {updated}")

                        console.print()

                    # /project add <project> <chat-id>
                    elif subcommand == 'add':
                        if len(subargs) < 2:
                            console.print("[yellow]Usage: /project add <project> <chat-id>[/yellow]")
                            console.print("[dim]Example: /project add my-webapp abc123[/dim]")
                            continue

                        project_name = subargs[0]
                        chat_id = subargs[1]

                        try:
                            result = project_manager.add_chat(project_name, chat_id)
                            if result:
                                # Update chat index
                                if chat_id in chat_manager.index['chats']:
                                    chat_manager.index['chats'][chat_id]['project'] = project_manager.get_project(project_name)['id']
                                    chat_manager._save_index()

                                console.print(f"[green]✓ Added chat {chat_id} to project {project_name}[/green]")
                            else:
                                console.print(f"[red]Project '{project_name}' not found[/red]")
                        except ValueError as e:
                            console.print(f"[red]{e}[/red]")

                    # /project remove <project> <chat-id>
                    elif subcommand == 'remove':
                        if len(subargs) < 2:
                            console.print("[yellow]Usage: /project remove <project> <chat-id>[/yellow]")
                            continue

                        project_name = subargs[0]
                        chat_id = subargs[1]

                        result = project_manager.remove_chat(project_name, chat_id)
                        if result:
                            # Update chat index
                            if chat_id in chat_manager.index['chats']:
                                chat_manager.index['chats'][chat_id]['project'] = None
                                chat_manager._save_index()

                            console.print(f"[green]✓ Removed chat {chat_id} from project {project_name}[/green]")
                        else:
                            console.print(f"[red]Project or chat not found[/red]")

                    # /project chats <project>
                    elif subcommand == 'chats':
                        if not subargs:
                            console.print("[yellow]Usage: /project chats <project>[/yellow]")
                            continue

                        project_name = subargs[0]
                        chat_ids = project_manager.get_project_chats(project_name)

                        if chat_ids is None:
                            console.print(f"[red]Project '{project_name}' not found[/red]")
                            continue

                        if not chat_ids:
                            console.print(f"[dim]No chats in project '{project_name}' yet[/dim]")
                            continue

                        # Get chat details
                        console.print(f"\n[bold]Chats in '{project_name}':[/bold]")
                        console.print("[dim]ID       Name                          Provider  Messages  Last Updated[/dim]")
                        console.print("[dim]" + "─" * 75 + "[/dim]")

                        for chat_id in chat_ids:
                            chat_info = chat_manager.index['chats'].get(chat_id)
                            if chat_info:
                                name = chat_info['name'][:28] + '...' if len(chat_info['name']) > 28 else chat_info['name']
                                provider = chat_info['provider']
                                msg_count = chat_info['message_count']
                                updated = chat_info['updated_at'][:10]
                                console.print(f"{chat_id}  {name:<30} {provider:<9} {msg_count:<9} {updated}")

                        console.print()

                    # /project delete <project>
                    elif subcommand == 'delete':
                        if not subargs:
                            console.print("[yellow]Usage: /project delete <project>[/yellow]")
                            continue

                        project_name = subargs[0]
                        project = project_manager.get_project(project_name)

                        if not project:
                            console.print(f"[red]Project '{project_name}' not found[/red]")
                            continue

                        # Show confirmation
                        console.print(f"\n[yellow]⚠  Delete project: {project['name']}?[/yellow]")
                        console.print(f"[dim]  Chats: {project['chat_count']}[/dim]")
                        console.print(f"[dim]  Created: {project['created_at'][:10]}[/dim]")
                        console.print("\n[dim]Note: This will NOT delete the chats, only the project.[/dim]")

                        confirm = session.prompt("\nType 'yes' to confirm deletion: ").strip().lower()

                        if confirm == 'yes':
                            if project_manager.delete_project(project_name):
                                console.print(f"[green]✓ Deleted project: {project['name']}[/green]")
                            else:
                                console.print("[red]Error deleting project[/red]")
                        else:
                            console.print("[dim]Deletion cancelled[/dim]")

                    else:
                        console.print(f"[yellow]Unknown subcommand: {subcommand}[/yellow]")
                        console.print("Type [cyan]/project[/cyan] for usage information")

                    continue

                # /find or /search - search through chats
                elif command in ['/find', '/search']:
                    if not args:
                        console.print("[yellow]Usage: /find <search term>[/yellow]")
                        continue

                    search_term = args.lower()
                    chats = chat_manager.list_chats()
                    results = []

                    # Search through chat files
                    for chat_info in chats:
                        file_path = Path(chat_info['file_path'])
                        if file_path.exists():
                            try:
                                with open(file_path, 'r') as f:
                                    content = f.read()
                                    if search_term in content.lower():
                                        # Find context around match
                                        lines = content.split('\n')
                                        matching_lines = [
                                            (i, line) for i, line in enumerate(lines)
                                            if search_term in line.lower()
                                        ]
                                        results.append({
                                            'chat': chat_info,
                                            'matches': matching_lines[:3]  # Show up to 3 matches
                                        })
                            except:
                                continue

                    if not results:
                        console.print(f"[yellow]No results found for '{args}'[/yellow]")
                        continue

                    console.print(f"\n[bold]Search results for '{args}':[/bold] ({len(results)} chat(s))\n")

                    for result in results:
                        chat_info = result['chat']
                        console.print(f"[cyan]• {chat_info['name']}[/cyan] [dim](ID: {chat_info['chat_id']})[/dim]")
                        console.print(f"  [dim]Provider: {chat_info['provider']} | Messages: {chat_info['message_count']} | Updated: {chat_info['updated_at'][:10]}[/dim]")

                        if result['matches']:
                            console.print(f"  [dim]Matches:[/dim]")
                            for line_num, line in result['matches'][:2]:  # Show first 2 matches
                                preview = line.strip()[:100]
                                if len(line.strip()) > 100:
                                    preview += "..."
                                console.print(f"    [dim]{preview}[/dim]")

                        console.print()
                    continue

                # Unknown command
                else:
                    console.print(f"[yellow]Unknown command: {command}[/yellow]")
                    console.print("Type [cyan]/help[/cyan] to see all available commands")
                    continue

            # Create chat on first message if needed
            if current_chat is None:
                current_chat = chat_manager.create_chat(first_message=user_input)
                console.print(f"[dim]Created chat: {current_chat['name']}[/dim]\n")

            # Add user message to chat
            chat_manager.add_message(current_chat, 'user', user_input)

            # Get conversation context (all previous messages)
            context = chat_manager.get_conversation_context(current_chat)

            # Get response from provider with context
            current_provider_name = provider_manager.get_current_provider_name()
            try:
                with console.status(f"[dim]💭 Thinking ({current_provider_name})...[/dim]", spinner="dots"):
                    response = provider_manager.send_message(user_input, context=context)

                # Display response (render as markdown)
                console.print()
                console.print(Markdown(response))
                console.print()

                # Add assistant message to chat
                chat_manager.add_message(current_chat, 'assistant', response, provider=current_provider_name)

            except Exception as e:
                console.print(f"[red]Error getting response: {e}[/red]")
                continue

        except KeyboardInterrupt:
            console.print("\n[dim]Use /exit to quit[/dim]")
            continue

        except EOFError:
            break

    return 0

if __name__ == '__main__':
    sys.exit(main())
