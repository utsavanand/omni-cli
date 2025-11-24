"""
Claude CLI provider
"""

import subprocess
from .base import BaseProvider

class ClaudeProvider(BaseProvider):
    """Claude CLI provider"""

    def __init__(self):
        super().__init__(name='claude', cli_command='claude')

    def send_message(self, message, context=None):
        """Send message to Claude CLI and get response"""
        # Build the full prompt with conversation history
        if context and len(context) > 0:
            # Format conversation history for context
            conversation = []
            for msg in context:
                role = msg['role'].capitalize()
                content = msg['content']
                provider = msg.get('provider', 'unknown')

                if msg['role'] == 'assistant':
                    conversation.append(f"{role} ({provider}): {content}")
                else:
                    conversation.append(f"{role}: {content}")

            # Add current message
            conversation.append(f"User: {message}")

            # Join with newlines and add instruction
            full_prompt = "Previous conversation:\n\n" + "\n\n".join(conversation) + "\n\nPlease respond to the latest message, keeping the conversation context in mind."
        else:
            full_prompt = message

        # Build command with tools enabled
        # Enable: WebSearch (web), Grep (file search), Glob (folder search), Read (file reading)
        cmd = [
            self.cli_path,
            '--print',  # Non-interactive mode
            '--tools', 'WebSearch,Grep,Glob,Read',  # Enable search and read tools
            '--dangerously-skip-permissions',  # Auto-approve tools for automation
            full_prompt
        ]

        try:
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # Increased for web search and file operations
            )

            if result.returncode != 0:
                raise RuntimeError(f"Claude CLI error: {result.stderr}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude CLI timeout - no response after 120 seconds")

        except Exception as e:
            raise RuntimeError(f"Failed to communicate with Claude CLI: {e}")
