"""
Codex CLI provider
"""

import subprocess
from .base import BaseProvider

class CodexProvider(BaseProvider):
    """Codex CLI provider"""

    def __init__(self):
        super().__init__(name='codex', cli_command='codex')

    def send_message(self, message, context=None):
        """Send message to Codex CLI and get response"""
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

        # Use 'exec' subcommand with file access enabled
        # --skip-git-repo-check: Run from anywhere
        # --sandbox read-only: Allow file reading but not writing
        # --full-auto: Auto-approve operations without prompts
        cmd = [
            self.cli_path,
            'exec',
            '--skip-git-repo-check',
            '--sandbox', 'read-only',  # Safe: allows file reading
            '--full-auto',  # Auto-approve for automation
            full_prompt
        ]

        try:
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # Increased for file operations
            )

            if result.returncode != 0:
                raise RuntimeError(f"Codex CLI error: {result.stderr}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError("Codex CLI timeout - no response after 120 seconds")

        except Exception as e:
            raise RuntimeError(f"Failed to communicate with Codex CLI: {e}")
