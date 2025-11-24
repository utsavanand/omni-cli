"""
Gemini CLI provider (Google's AI)
"""

import subprocess
from .base import BaseProvider

class GeminiProvider(BaseProvider):
    """Gemini CLI provider"""

    def __init__(self):
        # Gemini might be accessed via 'gemini' or 'gcloud ai' command
        # Try 'gemini' first as it's simpler
        super().__init__(name='gemini', cli_command='gemini')

    def send_message(self, message, context=None):
        """Send message to Gemini CLI and get response"""
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

        # Build command - use full path for reliable execution
        # Note: Adjust based on actual Gemini CLI interface
        # This is a placeholder - actual command may vary
        cmd = [self.cli_path, full_prompt]

        try:
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise RuntimeError(f"Gemini CLI error: {result.stderr}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError("Gemini CLI timeout - no response after 60 seconds")

        except Exception as e:
            raise RuntimeError(f"Failed to communicate with Gemini CLI: {e}")
