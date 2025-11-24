"""
Provider manager - detects and manages multiple AI providers
"""

from .claude import ClaudeProvider
from .codex import CodexProvider
from .gemini import GeminiProvider

class ProviderManager:
    """Manages multiple AI providers"""

    def __init__(self):
        # List of all supported providers
        self.all_providers = [
            ClaudeProvider(),
            CodexProvider(),  # Codex is the OpenAI CLI
            GeminiProvider(),
        ]

        # Detect installed providers
        self.providers = {
            p.name: p for p in self.all_providers if p.is_installed()
        }

        # Set default provider
        self.current_provider = self._get_default_provider()

    def _get_default_provider(self):
        """Get default provider (priority: claude > codex > gemini > first available)"""
        if 'claude' in self.providers:
            return 'claude'
        elif 'codex' in self.providers:
            return 'codex'
        elif 'gemini' in self.providers:
            return 'gemini'
        elif self.providers:
            return list(self.providers.keys())[0]
        return None

    def get_installed_providers(self):
        """Get list of installed provider names"""
        return list(self.providers.keys())

    def get_all_providers(self):
        """Get list of all supported provider names"""
        return [p.name for p in self.all_providers]

    def get_current_provider_name(self):
        """Get name of current provider"""
        return self.current_provider

    def get_current_provider(self):
        """Get current provider instance"""
        if self.current_provider and self.current_provider in self.providers:
            return self.providers[self.current_provider]
        return None

    def switch_provider(self, provider_name):
        """
        Switch to a different provider

        Args:
            provider_name: Name of provider to switch to

        Returns:
            bool: True if successful

        Raises:
            ValueError: If provider not installed
        """
        if provider_name not in self.providers:
            installed = ', '.join(self.providers.keys()) if self.providers else 'none'
            raise ValueError(
                f"Provider '{provider_name}' not installed. "
                f"Installed providers: {installed}"
            )

        self.current_provider = provider_name
        return True

    def send_message(self, message, context=None):
        """
        Send message using current provider

        Args:
            message: User message
            context: Optional conversation context (list of previous messages)

        Returns:
            str: AI response

        Raises:
            RuntimeError: If no provider available
        """
        provider = self.get_current_provider()

        if not provider:
            raise RuntimeError(
                "No AI provider available. "
                "Please install Claude CLI or OpenAI CLI."
            )

        # Pass conversation context to provider
        return provider.send_message(message, context=context)

    def has_providers(self):
        """Check if any providers are installed"""
        return len(self.providers) > 0

    def consult_provider(self, message, consult_provider_name, context=None):
        """
        Send message to both current provider and specified provider,
        then merge their responses using the current provider.

        Args:
            message: User message
            consult_provider_name: Name of provider to consult
            context: Optional conversation context

        Returns:
            tuple: (merged_response, current_response, consult_response)

        Raises:
            ValueError: If consult provider not installed
            RuntimeError: If no current provider available
        """
        # Validate current provider
        current_provider = self.get_current_provider()
        if not current_provider:
            raise RuntimeError(
                "No AI provider available. "
                "Please install Claude CLI or Codex CLI."
            )

        # Validate consult provider
        if consult_provider_name not in self.providers:
            installed = ', '.join(self.providers.keys()) if self.providers else 'none'
            raise ValueError(
                f"Provider '{consult_provider_name}' not installed. "
                f"Installed providers: {installed}"
            )

        consult_provider = self.providers[consult_provider_name]

        # Get responses from both providers
        current_response = current_provider.send_message(message, context=context)
        consult_response = consult_provider.send_message(message, context=context)

        # Create merge prompt
        merge_prompt = f"""I asked the following question to two different AI assistants:

Question: {message}

{self.current_provider}'s response:
{current_response}

{consult_provider_name}'s response:
{consult_response}

Please synthesize these two responses into a single, comprehensive answer that combines the best insights from both. Highlight any differences in perspective and provide a balanced view."""

        # Get merged response from current provider
        merged_response = current_provider.send_message(merge_prompt, context=None)

        return (merged_response, current_response, consult_response)
