"""
Summary management - create and store chat summaries
"""

from pathlib import Path
from datetime import datetime
import hashlib
import json


class SummaryManager:
    """Manages chat summaries and storage"""

    def __init__(self, base_path=None):
        self.base_path = Path(base_path or Path.home() / '.omni')
        self.summaries_path = self.base_path / 'summaries'
        self.index_path = self.base_path / 'summary_index.json'

        # Create directories
        self.summaries_path.mkdir(parents=True, exist_ok=True)

        # Load or create index
        self.index = self._load_index()

    def _load_index(self):
        """Load summary index from file"""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r') as f:
                    return json.load(f)
            except:
                return {'summaries': {}}
        return {'summaries': {}}

    def _save_index(self):
        """Save summary index to file"""
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _generate_summary_id(self):
        """Generate unique summary ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]

    def _get_summary_file_path(self, summary):
        """Get file path for summary"""
        # Format: YYYYMMDD-HHMMSS_summary-name.md
        timestamp = summary['created_at'][:19].replace(':', '').replace('-', '').replace('T', '-')
        filename = f"{timestamp}_{summary['name']}_summary.md"

        # If summary belongs to a project, store in project's summaries folder
        if summary.get('project'):
            project_summaries_path = self.base_path / 'projects' / summary['project'] / 'summaries'
            project_summaries_path.mkdir(parents=True, exist_ok=True)
            return project_summaries_path / filename

        return self.summaries_path / filename

    def create_summary(self, chat_name, chat_id, summary_content, summary_type='long', project=None, provider=None):
        """
        Create a new summary from a chat

        Args:
            chat_name: Name of the original chat
            chat_id: ID of the original chat
            summary_content: The generated summary text
            summary_type: 'short' (50-100 words) or 'long' (detailed)
            project: Project ID if chat belongs to a project
            provider: AI provider used to generate summary

        Returns:
            dict: Summary metadata
        """
        # Generate summary ID
        summary_id = self._generate_summary_id()

        # Create summary metadata
        now = datetime.now().isoformat()
        summary = {
            'summary_id': summary_id,
            'name': chat_name,
            'original_chat_id': chat_id,
            'type': summary_type,  # 'short' or 'long'
            'provider': provider or 'unknown',
            'created_at': now,
            'project': project,
            'word_count': len(summary_content.split())
        }

        # Create file immediately
        file_path = self._get_summary_file_path(summary)

        with open(file_path, 'w') as f:
            # Write YAML-like frontmatter
            f.write('---\n')
            f.write(f"summary_id: {summary['summary_id']}\n")
            f.write(f"name: {summary['name']}\n")
            f.write(f"original_chat_id: {summary['original_chat_id']}\n")
            f.write(f"type: {summary['type']}\n")
            f.write(f"provider: {summary['provider']}\n")
            f.write(f"created_at: {summary['created_at']}\n")
            f.write(f"project: {summary.get('project') or 'null'}\n")
            f.write(f"word_count: {summary['word_count']}\n")
            f.write('---\n\n')
            f.write(f"# Summary: {summary['name']}\n\n")
            f.write(f"**Type:** {summary['type'].capitalize()}  \n")
            f.write(f"**Generated:** {summary['created_at'][:10]}  \n")
            f.write(f"**Original Chat:** {summary['original_chat_id']}  \n\n")
            f.write("---\n\n")
            f.write(summary_content)
            f.write('\n')

        # Update index
        self.index['summaries'][summary_id] = {
            'summary_id': summary_id,
            'name': summary['name'],
            'file_path': str(file_path),
            'created_at': summary['created_at'],
            'type': summary['type'],
            'provider': summary['provider'],
            'original_chat_id': summary['original_chat_id'],
            'project': summary.get('project'),
            'word_count': summary['word_count']
        }
        self._save_index()

        return summary

    def list_summaries(self, project=None):
        """
        List all summaries, optionally filtered by project

        Args:
            project: Optional project ID to filter by

        Returns:
            list: List of summary metadata dicts
        """
        summaries = []
        for summary_id, summary_info in self.index['summaries'].items():
            # Ensure summary_id is in the data
            if 'summary_id' not in summary_info:
                summary_info['summary_id'] = summary_id

            # Filter by project if specified
            if project is None or summary_info.get('project') == project:
                summaries.append(summary_info)

        # Sort by created_at descending
        summaries.sort(key=lambda x: x['created_at'], reverse=True)
        return summaries

    def get_summary(self, summary_id_or_name):
        """
        Get summary by ID or name

        Returns:
            dict: Summary metadata or None if not found
        """
        # Try by ID
        if summary_id_or_name in self.index['summaries']:
            return self.index['summaries'][summary_id_or_name]

        # Try by name
        for summary_id, summary in self.index['summaries'].items():
            if summary['name'] == summary_id_or_name:
                return summary

        return None

    def load_summary(self, summary_id_or_name):
        """
        Load a summary by ID or name and return full content

        Returns:
            dict: Summary with 'content' field added, or None if not found
        """
        summary_info = self.get_summary(summary_id_or_name)
        if not summary_info:
            return None

        # Load content from file
        file_path = Path(summary_info['file_path'])
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r') as f:
                full_content = f.read()

                # Extract content after frontmatter (after second ---)
                parts = full_content.split('---\n')
                if len(parts) >= 3:
                    # Everything after the second --- is the content
                    content = '---\n'.join(parts[2:]).strip()
                else:
                    content = full_content

                summary_info['content'] = content
                return summary_info
        except:
            return None

    def delete_summary(self, summary_id_or_name):
        """
        Delete a summary by ID or name

        Returns:
            bool: True if deleted, False if not found
        """
        import os

        # Find summary
        summary_id = None
        for sid, info in self.index['summaries'].items():
            if sid == summary_id_or_name or info.get('name') == summary_id_or_name:
                summary_id = sid
                break

        if not summary_id:
            return False

        # Get file path and delete file
        summary_info = self.index['summaries'][summary_id]
        file_path = Path(summary_info['file_path'])

        if file_path.exists():
            os.remove(file_path)

        # Remove from index
        del self.index['summaries'][summary_id]
        self._save_index()

        return True
