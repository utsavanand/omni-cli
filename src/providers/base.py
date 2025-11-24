"""
Base provider interface
"""

from abc import ABC, abstractmethod
import shutil

class BaseProvider(ABC):
    """Base class for AI CLI providers"""

    def __init__(self, name, cli_command):
        self.name = name
        self.cli_command = cli_command
        # Get full path to command for reliable execution
        self.cli_path = shutil.which(cli_command)

    def is_installed(self):
        """Check if the CLI is installed"""
        return self.cli_path is not None

    @abstractmethod
    def send_message(self, message, context=None):
        """
        Send message to AI and get response

        Args:
            message: User message
            context: Optional conversation context (list of previous messages)

        Returns:
            str: AI response
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} installed={self.is_installed()}>"
