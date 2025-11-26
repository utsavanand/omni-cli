"""
Project management - organize and group related chats
"""

from pathlib import Path
from datetime import datetime
import json

class ProjectManager:
    """Manages projects and chat organization"""

    def __init__(self, base_path=None):
        # Set up storage paths
        self.base_path = Path(base_path or Path.home() / '.omni')
        self.projects_path = self.base_path / 'projects'
        self.projects_index_path = self.base_path / 'projects.json'

        # Create directories
        self.projects_path.mkdir(parents=True, exist_ok=True)

        # Load or create projects index
        self.projects = self._load_projects()

    def _load_projects(self):
        """Load projects index from file"""
        if self.projects_index_path.exists():
            try:
                with open(self.projects_index_path, 'r') as f:
                    return json.load(f)
            except:
                return {'projects': {}}
        return {'projects': {}}

    def _save_projects(self):
        """Save projects index to file"""
        with open(self.projects_index_path, 'w') as f:
            json.dump(self.projects, f, indent=2)

    def create_project(self, name, description=None, namespace=None):
        """
        Create a new project

        Args:
            name: Project name (used as ID and folder name)
            description: Optional project description
            namespace: Optional namespace this project belongs to

        Returns:
            dict: Project metadata

        Raises:
            ValueError: If project already exists
        """
        # Validate name
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")

        # Sanitize name for filesystem
        import re
        sanitized_name = re.sub(r'[^\w\s-]', '', name.lower())
        sanitized_name = re.sub(r'[\s]+', '-', sanitized_name)

        if sanitized_name in self.projects['projects']:
            raise ValueError(f"Project '{name}' already exists")

        # Create project metadata
        now = datetime.now().isoformat()
        project = {
            'name': name,
            'id': sanitized_name,
            'description': description or '',
            'namespace': namespace,
            'created_at': now,
            'updated_at': now,
            'chat_count': 0,
            'chats': []
        }

        # Create project directory
        project_dir = self.projects_path / sanitized_name
        project_dir.mkdir(parents=True, exist_ok=True)
        chats_dir = project_dir / 'chats'
        chats_dir.mkdir(parents=True, exist_ok=True)

        # Save to index
        self.projects['projects'][sanitized_name] = project
        self._save_projects()

        return project

    def list_projects(self, include_stats=False):
        """
        List all projects

        Args:
            include_stats: Include detailed statistics

        Returns:
            list: List of project metadata dictionaries
        """
        projects = []
        for project_id, project_info in self.projects['projects'].items():
            project_data = project_info.copy()

            if include_stats:
                # Add statistics
                project_data['last_activity'] = self._get_last_activity(project_id)

            projects.append(project_data)

        return sorted(projects, key=lambda x: x['updated_at'], reverse=True)

    def get_project(self, project_id_or_name):
        """
        Get project by ID or name

        Args:
            project_id_or_name: Project ID or name

        Returns:
            dict: Project metadata or None if not found
        """
        # Try by ID first
        if project_id_or_name in self.projects['projects']:
            return self.projects['projects'][project_id_or_name].copy()

        # Try by name
        for project_id, project_info in self.projects['projects'].items():
            if project_info['name'].lower() == project_id_or_name.lower():
                return project_info.copy()

        return None

    def delete_project(self, project_id_or_name, delete_chats=False):
        """
        Delete a project

        Args:
            project_id_or_name: Project ID or name
            delete_chats: If True, also delete all chats in the project

        Returns:
            bool: True if deleted, False if not found
        """
        import shutil

        # Find project
        project = self.get_project(project_id_or_name)
        if not project:
            return False

        project_id = project['id']

        # Delete project directory
        project_dir = self.projects_path / project_id
        if project_dir.exists():
            if delete_chats:
                shutil.rmtree(project_dir)
            else:
                # Just delete metadata, keep chats
                chats_dir = project_dir / 'chats'
                if chats_dir.exists() and any(chats_dir.iterdir()):
                    # Move chats back to main chats folder
                    # This would require ChatManager integration
                    pass

        # Remove from index
        del self.projects['projects'][project_id]
        self._save_projects()

        return True

    def add_chat(self, project_id_or_name, chat_id):
        """
        Add a chat to a project

        Args:
            project_id_or_name: Project ID or name
            chat_id: Chat ID to add

        Returns:
            bool: True if added, False if project not found

        Raises:
            ValueError: If chat already in project
        """
        # Find project
        project = self.get_project(project_id_or_name)
        if not project:
            return False

        project_id = project['id']

        # Check if chat already in project
        if chat_id in self.projects['projects'][project_id]['chats']:
            raise ValueError(f"Chat '{chat_id}' already in project '{project['name']}'")

        # Add chat to project
        self.projects['projects'][project_id]['chats'].append(chat_id)
        self.projects['projects'][project_id]['chat_count'] += 1
        self.projects['projects'][project_id]['updated_at'] = datetime.now().isoformat()
        self._save_projects()

        return True

    def remove_chat(self, project_id_or_name, chat_id):
        """
        Remove a chat from a project

        Args:
            project_id_or_name: Project ID or name
            chat_id: Chat ID to remove

        Returns:
            bool: True if removed, False if not found
        """
        # Find project
        project = self.get_project(project_id_or_name)
        if not project:
            return False

        project_id = project['id']

        # Check if chat in project
        if chat_id not in self.projects['projects'][project_id]['chats']:
            return False

        # Remove chat from project
        self.projects['projects'][project_id]['chats'].remove(chat_id)
        self.projects['projects'][project_id]['chat_count'] -= 1
        self.projects['projects'][project_id]['updated_at'] = datetime.now().isoformat()
        self._save_projects()

        return True

    def get_project_chats(self, project_id_or_name):
        """
        Get all chats in a project

        Args:
            project_id_or_name: Project ID or name

        Returns:
            list: List of chat IDs or None if project not found
        """
        project = self.get_project(project_id_or_name)
        if not project:
            return None

        return project['chats'].copy()

    def get_chat_project(self, chat_id):
        """
        Get the project a chat belongs to

        Args:
            chat_id: Chat ID

        Returns:
            dict: Project metadata or None if chat not in any project
        """
        for project_id, project_info in self.projects['projects'].items():
            if chat_id in project_info['chats']:
                return project_info.copy()

        return None

    def _get_last_activity(self, project_id):
        """
        Get last activity timestamp for a project

        Args:
            project_id: Project ID

        Returns:
            str: ISO timestamp or None
        """
        project = self.projects['projects'].get(project_id)
        if not project:
            return None

        return project.get('updated_at')

    def rename_project(self, project_id_or_name, new_name):
        """
        Rename a project

        Args:
            project_id_or_name: Current project ID or name
            new_name: New project name

        Returns:
            bool: True if renamed, False if not found
        """
        project = self.get_project(project_id_or_name)
        if not project:
            return False

        project_id = project['id']

        # Update name
        self.projects['projects'][project_id]['name'] = new_name
        self.projects['projects'][project_id]['updated_at'] = datetime.now().isoformat()
        self._save_projects()

        return True
