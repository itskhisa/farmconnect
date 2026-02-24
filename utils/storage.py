"""Storage utility for web app - NO KIVY."""

import json
import os
from pathlib import Path

def get_app_dir():
    """Get application data directory."""
    # For web app, use a data folder in the project
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    data_dir.mkdir(exist_ok=True)
    return str(data_dir)

class Storage:
    def __init__(self):
        self.app_dir = get_app_dir()
    
    def _get_path(self, filename):
        """Get full path for a file."""
        return os.path.join(self.app_dir, filename)
    
    def save_json(self, filename, data):
        """Save data as JSON."""
        try:
            path = self._get_path(filename)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False
    
    def load_json(self, filename):
        """Load JSON data."""
        try:
            path = self._get_path(filename)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
        return None
    
    def delete(self, filename):
        """Delete a file."""
        try:
            path = self._get_path(filename)
            if os.path.exists(path):
                os.remove(path)
                return True
        except Exception as e:
            print(f"Error deleting {filename}: {e}")
        return False
    
    def exists(self, filename):
        """Check if file exists."""
        path = self._get_path(filename)
        return os.path.exists(path)
    
    def list_files(self, pattern=None):
        """List all files in storage."""
        try:
            files = os.listdir(self.app_dir)
            if pattern:
                import fnmatch
                files = [f for f in files if fnmatch.fnmatch(f, pattern)]
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
