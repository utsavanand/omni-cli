#!/usr/bin/env python3
"""
Omni CLI - Unified wrapper for AI models
Phase 1: Proof of Concept
"""

import sys
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

# Initialize console for rich output
console = Console()

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
  [cyan]/delete <id/name>[/cyan]       Delete a chat (with confirmation)

[bold]Utilities:[/bold]
  [cyan]/help[/cyan]                   Show this help message
  [cyan]/exit[/cyan] or [cyan]/quit[/cyan]         Exit omni

[bold]Quick Tips:[/bold]
  • Just type naturally to start chatting (no command needed)
  • Chats are auto-saved with context
  • Switch providers mid-conversation to get different perspectives
  • Use /consult to merge insights from multiple AIs

[bold]Examples:[/bold]
  omni> how do I implement OAuth?          [dim]# Start chatting[/dim]
  omni> /use codex                         [dim]# Switch to Codex[/dim]
  omni> can you show code examples?        [dim]# Continue with new provider[/dim]
  omni> /consult gemini what's best?       [dim]# Get merged response[/dim]
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
                        console.print("[yellow]Usage: /new <chat-name>[/yellow]")
                        console.print("[dim]Example: /new my-feature-chat[/dim]")
                        continue

                    # Create new chat with provided name
                    current_chat = chat_manager.create_chat(name=args)
                    console.print(f"[green]✓ Created new chat: {args}[/green]")
                    console.print(f"[dim]Chat ID: {current_chat['chat_id']}[/dim]")
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
                    chats = chat_manager.list_chats()

                    if not chats:
                        console.print("[dim]No chats yet. Start chatting to create your first chat![/dim]")
                        continue

                    console.print("\n[bold]Saved Chats:[/bold]")
                    console.print("[dim]ID       Name                          Provider  Messages  Last Updated[/dim]")
                    console.print("[dim]" + "─" * 75 + "[/dim]")

                    for chat_info in sorted(chats, key=lambda x: x['updated_at'], reverse=True):
                        chat_id = chat_info['chat_id']
                        name = chat_info['name'][:28] + '...' if len(chat_info['name']) > 28 else chat_info['name']
                        provider = chat_info['provider']
                        msg_count = chat_info['message_count']
                        updated = chat_info['updated_at'][:10]  # Just the date

                        console.print(f"{chat_id}  {name:<30} {provider:<9} {msg_count:<9} {updated}")

                    console.print()
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

                    # Sort by most recent
                    chats = sorted(chats, key=lambda x: x['updated_at'], reverse=True)

                    # Interactive selection with pure keyboard
                    selected_index = [0]  # Mutable container for closure
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

                        # Chat list
                        for i, chat_info in enumerate(chats):
                            updated = chat_info['updated_at'][:10]
                            name = chat_info['name'][:35]
                            provider = chat_info['provider']
                            msg_count = chat_info['message_count']

                            if i == selected_index[0]:
                                # Highlighted
                                lines.append(('class:selected', f"  → {name:<37} {provider:<8} {msg_count:>3} msgs  {updated}\n"))
                            else:
                                # Normal
                                lines.append(('', f"    {name:<37} {provider:<8} {msg_count:>3} msgs  {updated}\n"))

                        return lines

                    # Key bindings
                    kb = KeyBindings()

                    @kb.add('up')
                    def move_up(event):
                        if selected_index[0] > 0:
                            selected_index[0] -= 1

                    @kb.add('down')
                    def move_down(event):
                        if selected_index[0] < len(chats) - 1:
                            selected_index[0] += 1

                    @kb.add('enter')
                    def select(event):
                        result_chat[0] = chats[selected_index[0]]
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
