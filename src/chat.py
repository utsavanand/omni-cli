"""
Chat management - file creation and saving
"""

from pathlib import Path
from datetime import datetime
import hashlib
import json

class ChatManager:
    """Manages chat creation, storage, and retrieval"""

    def __init__(self, base_path=None):
        # Set up storage paths
        self.base_path = Path(base_path or Path.home() / '.omni')
        self.chats_path = self.base_path / 'chats' / 'permanent'
        self.index_path = self.base_path / 'index.json'

        # Create directories
        self.chats_path.mkdir(parents=True, exist_ok=True)

        # Load or create index
        self.index = self._load_index()

    def _load_index(self):
        """Load chat index from file"""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r') as f:
                    return json.load(f)
            except:
                return {'chats': {}}
        return {'chats': {}}

    def _save_index(self):
        """Save chat index to file"""
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _generate_chat_id(self):
        """Generate unique chat ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]

    def _generate_chat_name(self, first_message):
        """Generate chat name from first message (max 3-4 words)"""
        import re

        # Remove special characters
        text = re.sub(r'[^\w\s-]', '', first_message.lower())

        # Split into words
        words = text.split()

        # Take first 4 meaningful words (length > 2)
        meaningful_words = [w for w in words if len(w) > 2][:4]

        # Join with hyphens
        name = '-'.join(meaningful_words)

        # Limit length
        if len(name) > 50:
            name = name[:50].rsplit('-', 1)[0]

        return name if name else 'chat'

    def _get_chat_file_path(self, chat):
        """Get file path for chat"""
        # Format: YYYYMMDD-HHMMSS_chat-name.md
        timestamp = chat['created_at'][:19].replace(':', '').replace('-', '').replace('T', '-')
        filename = f"{timestamp}_{chat['name']}.md"

        # If chat belongs to a project, store in project's chats folder
        if chat.get('project'):
            project_chats_path = self.base_path / 'projects' / chat['project'] / 'chats'
            project_chats_path.mkdir(parents=True, exist_ok=True)
            return project_chats_path / filename

        return self.chats_path / filename

    def create_chat(self, name=None, first_message=None, project=None):
        """Create new chat and file immediately"""
        # Generate chat ID
        chat_id = self._generate_chat_id()

        # Generate or use provided name
        if name is None and first_message:
            name = self._generate_chat_name(first_message)
        elif name is None:
            name = f"chat-{chat_id}"

        # Create chat metadata
        now = datetime.now().isoformat()
        chat = {
            'chat_id': chat_id,
            'name': name,
            'provider': 'claude',
            'created_at': now,
            'updated_at': now,
            'message_count': 0,
            'messages': [],
            'project': project
        }

        # Create file immediately
        file_path = self._get_chat_file_path(chat)

        with open(file_path, 'w') as f:
            # Write YAML-like frontmatter
            f.write('---\n')
            f.write(f"chat_id: {chat['chat_id']}\n")
            f.write(f"name: {chat['name']}\n")
            f.write(f"provider: {chat['provider']}\n")
            f.write(f"created_at: {chat['created_at']}\n")
            f.write(f"updated_at: {chat['updated_at']}\n")
            f.write(f"message_count: 0\n")
            f.write(f"project: {chat.get('project') or 'null'}\n")
            f.write('---\n\n')
            f.write(f"# Chat: {chat['name']}\n\n")

        # Update index
        self.index['chats'][chat_id] = {
            'chat_id': chat_id,
            'name': chat['name'],
            'file_path': str(file_path),
            'created_at': chat['created_at'],
            'updated_at': chat['updated_at'],
            'provider': chat['provider'],
            'message_count': 0,
            'project': chat.get('project')
        }
        self._save_index()

        return chat

    def add_message(self, chat, role, content, provider=None):
        """Add message to chat and append to file"""
        # Update chat metadata
        chat['message_count'] += 1
        chat['updated_at'] = datetime.now().isoformat()

        message = {
            'role': role,
            'content': content,
            'provider': provider or chat['provider'],
            'timestamp': chat['updated_at']
        }

        chat['messages'].append(message)

        # Append to file
        file_path = self._get_chat_file_path(chat)

        with open(file_path, 'a') as f:
            msg_num = chat['message_count']
            timestamp = message['timestamp'][:19].replace('T', ' ')

            if role == 'user':
                f.write(f"## Message {msg_num} - User ({timestamp})\n")
            else:
                provider_name = message.get('provider', '')
                f.write(f"## Message {msg_num} - Assistant ({provider_name}) ({timestamp})\n")

            f.write(f"{content}\n\n")

        # Update index
        chat_id = chat['chat_id']
        if chat_id in self.index['chats']:
            self.index['chats'][chat_id]['updated_at'] = chat['updated_at']
            self.index['chats'][chat_id]['message_count'] = chat['message_count']
            self._save_index()

        return message

    def list_chats(self):
        """List all chats"""
        chats = []
        for chat_id, chat_info in self.index['chats'].items():
            # Ensure chat_id is in the data (migration for old index format)
            if 'chat_id' not in chat_info:
                chat_info['chat_id'] = chat_id
            chats.append(chat_info)
        return chats

    def load_chat(self, chat_id_or_name):
        """
        Load a chat by ID or name from the index and reconstruct its messages

        Returns chat dict with messages loaded, or None if not found
        """
        # Try to find chat by ID or name
        chat_info = None
        for cid, info in self.index['chats'].items():
            if cid == chat_id_or_name or info.get('name') == chat_id_or_name:
                chat_info = info.copy()
                chat_info['chat_id'] = cid
                break

        if not chat_info:
            return None

        # Load messages from file
        file_path = Path(chat_info['file_path'])
        if not file_path.exists():
            return None

        # Parse the markdown file to extract messages
        messages = []
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Split by message headers
            import re
            message_pattern = r'## Message \d+ - (User|Assistant)(?: \(([^)]+)\))? \(([^)]+)\)\n(.*?)(?=## Message|\Z)'
            matches = re.findall(message_pattern, content, re.DOTALL)

            for role, provider, timestamp, msg_content in matches:
                messages.append({
                    'role': role.lower(),
                    'content': msg_content.strip(),
                    'provider': provider if provider else chat_info.get('provider'),
                    'timestamp': timestamp
                })
        except:
            # If parsing fails, return chat with empty messages
            pass

        chat_info['messages'] = messages
        return chat_info

    def delete_chat(self, chat_id_or_name):
        """
        Delete a chat by ID or name

        Returns True if deleted, False if not found
        """
        import os

        # Try to find chat by ID or name
        chat_id = None
        for cid, info in self.index['chats'].items():
            if cid == chat_id_or_name or info.get('name') == chat_id_or_name:
                chat_id = cid
                break

        if not chat_id:
            return False

        # Get file path and delete file
        chat_info = self.index['chats'][chat_id]
        file_path = Path(chat_info['file_path'])

        if file_path.exists():
            os.remove(file_path)

        # Remove from index
        del self.index['chats'][chat_id]
        self._save_index()

        return True

    def get_conversation_context(self, chat):
        """
        Get conversation context for passing to AI providers

        Returns list of messages in format:
        [
            {'role': 'user', 'content': '...'},
            {'role': 'assistant', 'content': '...'},
            ...
        ]
        """
        return [
            {
                'role': msg['role'],
                'content': msg['content'],
                'provider': msg.get('provider')
            }
            for msg in chat.get('messages', [])
        ]
