"""
Namespace management - organize projects into namespaces
"""

from pathlib import Path
from datetime import datetime
import hashlib
import json


class NamespaceManager:
    """Manages namespaces for organizing projects"""

    def __init__(self, base_path=None):
        self.base_path = Path(base_path or Path.home() / '.omni')
        self.namespaces_path = self.base_path / 'namespaces'
        self.index_path = self.base_path / 'namespace_index.json'

        # Create directories
        self.namespaces_path.mkdir(parents=True, exist_ok=True)

        # Load or create index
        self.index = self._load_index()

    def _load_index(self):
        """Load namespace index"""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r') as f:
                    return json.load(f)
            except:
                return {'namespaces': {}}
        return {'namespaces': {}}

    def _save_index(self):
        """Save namespace index"""
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _generate_namespace_id(self):
        """Generate unique namespace ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]

    def create_namespace(self, name, description=None):
        """
        Create a new namespace

        Returns namespace dict or raises ValueError if exists
        """
        # Check if namespace already exists
        for ns_id, ns in self.index['namespaces'].items():
            if ns['name'] == name:
                raise ValueError(f"Namespace '{name}' already exists")

        # Generate namespace ID
        ns_id = self._generate_namespace_id()

        # Create namespace
        now = datetime.now().isoformat()
        namespace = {
            'id': ns_id,
            'name': name,
            'description': description or '',
            'created_at': now,
            'updated_at': now,
            'project_ids': []
        }

        # Save to index
        self.index['namespaces'][ns_id] = namespace
        self._save_index()

        # Create namespace directory
        ns_dir = self.namespaces_path / name
        ns_dir.mkdir(parents=True, exist_ok=True)

        return namespace

    def list_namespaces(self, include_stats=False):
        """List all namespaces"""
        namespaces = list(self.index['namespaces'].values())

        if include_stats:
            for ns in namespaces:
                ns['project_count'] = len(ns.get('project_ids', []))

        return namespaces

    def get_namespace(self, name_or_id):
        """Get namespace by name or ID"""
        # Try by ID
        if name_or_id in self.index['namespaces']:
            return self.index['namespaces'][name_or_id]

        # Try by name
        for ns_id, ns in self.index['namespaces'].items():
            if ns['name'] == name_or_id:
                return ns

        return None

    def add_project(self, namespace_name, project_id):
        """Add project to namespace"""
        namespace = self.get_namespace(namespace_name)
        if not namespace:
            return False

        if project_id not in namespace['project_ids']:
            namespace['project_ids'].append(project_id)
            namespace['updated_at'] = datetime.now().isoformat()

            # Update in index
            self.index['namespaces'][namespace['id']] = namespace
            self._save_index()

        return True

    def remove_project(self, namespace_name, project_id):
        """Remove project from namespace"""
        namespace = self.get_namespace(namespace_name)
        if not namespace:
            return False

        if project_id in namespace['project_ids']:
            namespace['project_ids'].remove(project_id)
            namespace['updated_at'] = datetime.now().isoformat()

            # Update in index
            self.index['namespaces'][namespace['id']] = namespace
            self._save_index()

        return True

    def get_namespace_projects(self, namespace_name):
        """Get all project IDs in a namespace"""
        namespace = self.get_namespace(namespace_name)
        if not namespace:
            return None

        return namespace.get('project_ids', [])

    def delete_namespace(self, namespace_name):
        """
        Delete a namespace

        Note: This does NOT delete the projects, just the namespace
        """
        namespace = self.get_namespace(namespace_name)
        if not namespace:
            return False

        # Remove from index
        del self.index['namespaces'][namespace['id']]
        self._save_index()

        # Remove directory (if empty)
        ns_dir = self.namespaces_path / namespace['name']
        try:
            if ns_dir.exists() and not any(ns_dir.iterdir()):
                ns_dir.rmdir()
        except:
            pass

        return True

    def rename_namespace(self, namespace_name_or_id, new_name):
        """
        Rename a namespace

        Args:
            namespace_name_or_id: Current namespace name or ID
            new_name: New namespace name

        Returns:
            bool: True if renamed, False if not found

        Raises:
            ValueError: If new name already exists
        """
        namespace = self.get_namespace(namespace_name_or_id)
        if not namespace:
            return False

        # Check if new name already exists
        for ns_id, ns in self.index['namespaces'].items():
            if ns['name'] == new_name and ns_id != namespace['id']:
                raise ValueError(f"Namespace '{new_name}' already exists")

        old_name = namespace['name']
        namespace_id = namespace['id']

        # Update name in index
        self.index['namespaces'][namespace_id]['name'] = new_name
        self.index['namespaces'][namespace_id]['updated_at'] = datetime.now().isoformat()
        self._save_index()

        # Rename directory
        old_dir = self.namespaces_path / old_name
        new_dir = self.namespaces_path / new_name
        try:
            if old_dir.exists():
                old_dir.rename(new_dir)
        except Exception as e:
            # Rollback if directory rename fails
            self.index['namespaces'][namespace_id]['name'] = old_name
            self._save_index()
            raise Exception(f"Failed to rename namespace directory: {e}")

        return True
