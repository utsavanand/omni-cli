# Omni CLI - Design Document

## Overview
This document outlines the design and implementation strategy for Omni CLI, a unified wrapper for multiple AI CLI tools with persistent chat management.

---

## Architecture Overview

### High-Level Architecture
```
┌─────────────────────────────────────────────────┐
│              Omni CLI (Python)                   │
│                                                  │
│  ┌─────────────────────────────────────────┐   │
│  │   Interactive Shell (REPL)               │   │
│  │   - Command parser                       │   │
│  │   - Auto-completion                      │   │
│  │   - Input handling                       │   │
│  └─────────────────────────────────────────┘   │
│                      │                          │
│  ┌─────────────────────────────────────────┐   │
│  │   Command Router                         │   │
│  │   - /commands → handlers                 │   │
│  │   - text → chat handler                  │   │
│  └─────────────────────────────────────────┘   │
│                      │                          │
│  ┌──────────────────┬─────────────────────┐   │
│  │  Chat Manager    │  Provider Manager    │   │
│  │  - Create        │  - Detect installed  │   │
│  │  - Resume        │  - Execute commands  │   │
│  │  - Save          │  - Parse responses   │   │
│  │  - Search        │                      │   │
│  └──────────────────┴─────────────────────┘   │
│                      │                          │
│  ┌─────────────────────────────────────────┐   │
│  │   Storage Layer                          │   │
│  │   - File management                      │   │
│  │   - Index updates                        │   │
│  │   - Metadata                             │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
    ┌────▼─────┐              ┌─────▼──────┐
    │ Claude   │              │  OpenAI    │
    │   CLI    │              │    CLI     │
    └──────────┘              └────────────┘
```

### Core Principles
1. **Wrapper Pattern**: Omni doesn't implement AI - it wraps existing CLIs
2. **Stateless Execution**: Each AI CLI call is independent
3. **Persistent Storage**: All state (chats, metadata) stored in files
4. **Extensible**: Easy to add new providers without core changes

---

## Tech Stack

### Language & Core Libraries
- **Python 3.9+**: Main language
  - Wide adoption, good CLI libraries
  - Easy subprocess management
  - Rich ecosystem

### Key Dependencies (MVP)
```python
# Core CLI
prompt_toolkit>=3.0      # Interactive shell, auto-completion
click>=8.1              # Command parsing (optional, for direct mode)
rich>=13.0              # Rich formatting, syntax highlighting

# Storage & Data
pyyaml>=6.0             # Config and metadata files
python-dateutil>=2.9    # Date/time handling

# File operations
pathlib                 # Built-in, file path handling
json                    # Built-in, index file
hashlib                 # Built-in, chat ID generation

# Process management
subprocess              # Built-in, running CLI commands
shutil                  # Built-in, which() for detecting CLIs
```

### File Storage Format
- **Chat files**: Markdown (`.md`) - human-readable, version-control friendly
- **Index**: JSON (`.json`) - fast parsing, simple structure
- **Config**: YAML (`.yaml`) - human-friendly, comments support

---

## MVP Implementation Phases

### Phase 1: Proof of Concept (1-2 days)
**Goal**: Get basic chat working with one provider

**Features**:
- Start omni session
- Type and get response from Claude CLI (hardcoded)
- Save chat to file with timestamp
- Exit

**Implementation**:
```python
# Minimal structure
src/
  main.py           # Entry point, basic REPL
  chat.py           # Chat file creation and saving
  provider.py       # Execute Claude CLI
```

**Success Criteria**:
- `$ omni` starts shell
- `omni> hello` gets Claude response
- Creates file `~/.omni/chats/20250124-143022_hello.md`
- `omni> /exit` exits

---

### Phase 2: Core Chat Management (2-3 days)
**Goal**: Full chat lifecycle with proper file naming

**Features**:
- Auto-generate chat names from first message
- Create chat file immediately (before AI response)
- Append messages as conversation progresses
- Basic commands: `/new`, `/list`, `/exit`
- Simple index for listing chats

**New Components**:
```python
src/
  main.py
  chat_manager.py   # Chat CRUD operations
  storage.py        # File I/O, index management
  name_generator.py # Auto-generate chat names
  provider.py
```

**Chat File Structure**:
```markdown
---
chat_id: abc123
name: hello-world
provider: claude
created_at: 2025-01-24T14:30:22Z
---

# Chat: hello-world

## Message 1 - User (2025-01-24 14:30:22)
hello

## Message 2 - Assistant (claude) (2025-01-24 14:30:25)
Hello! How can I help you today?
```

**Success Criteria**:
- `/new my-chat` creates named chat
- Unnamed chat auto-generates name from first message
- `/list` shows all chats
- File created immediately, updated continuously

---

### Phase 3: Multi-Provider Support (2-3 days)
**Goal**: Support multiple AI providers with switching

**Features**:
- Auto-detect installed providers (Claude, OpenAI)
- `/use <provider>` to switch providers
- `/providers` to list available
- Provider-specific config
- Shared conversation history across providers

**New Components**:
```python
src/
  providers/
    __init__.py
    base.py         # Provider interface
    claude.py       # Claude CLI wrapper
    openai.py       # OpenAI CLI wrapper
    detector.py     # Detect installed CLIs
```

**Provider Interface**:
```python
class Provider:
    def __init__(self, name: str):
        self.name = name

    def is_installed(self) -> bool:
        """Check if CLI is installed"""
        pass

    def send_message(self, message: str, context: list) -> str:
        """Send message and get response"""
        pass
```

**Success Criteria**:
- `/providers` shows installed CLIs
- `/use claude` switches to Claude
- `/use openai` switches to OpenAI
- Same chat history visible to both providers

---

### Phase 4: Projects & Search (3-4 days)
**Goal**: Organize chats into projects, basic search

**Features**:
- Create/list/delete projects
- Add chats to projects
- Search across all chats
- Search within project
- Project-based file organization

**New Components**:
```python
src/
  project_manager.py  # Project CRUD
  search.py           # Full-text search
```

**Directory Structure**:
```
~/.omni/
├── chats/
│   ├── permanent/
│   │   └── 20250124-143022_implement-oauth.md
│   └── temp/
│       └── 20250125-100000_quick-question.md
├── projects/
│   ├── my-saas-app/
│   │   ├── metadata.yaml
│   │   └── chats/
│   │       ├── 20250124-160000_database-design.md
│   │       └── 20250124-170000_api-routes.md
│   └── learning-rust/
│       ├── metadata.yaml
│       └── chats/
│           └── 20250125-090000_ownership.md
├── index.json
└── config.yaml
```

**Success Criteria**:
- `/project new my-app` creates project
- `/new chat1 --project my-app` adds chat to project
- `/search "oauth"` finds matching chats
- `/search "database" --project my-app` searches in project only

---

### Phase 5: Polish & Remaining P0 Features (2-3 days)
**Goal**: Complete MVP with all P0 features

**Features**:
- Temporary chats with TTL
- `/save` for code extraction
- `/export` for markdown/JSON
- `/context` for adding files
- `/resume` for continuing chats
- Better error handling
- Config management
- Syntax highlighting

**Success Criteria**:
- All P0 requirements from REQUIREMENTS.md implemented
- Error handling for all edge cases
- Help system working
- Ready for alpha testing

---

## Detailed Component Design

### 1. Main Entry Point (`main.py`)
```python
#!/usr/bin/env python3
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

from chat_manager import ChatManager
from provider_manager import ProviderManager
from command_router import CommandRouter

def main():
    # Initialize
    chat_manager = ChatManager()
    provider_manager = ProviderManager()
    router = CommandRouter(chat_manager, provider_manager)

    # Auto-complete for commands
    commands = WordCompleter([
        '/new', '/list', '/resume', '/delete',
        '/use', '/providers', '/search',
        '/save', '/export', '/help', '/exit'
    ], ignore_case=True)

    session = PromptSession(completer=commands)

    print("Omni CLI - Type /help for commands")

    # REPL
    while True:
        try:
            user_input = session.prompt('omni> ')

            if not user_input.strip():
                continue

            # Route command or chat
            if user_input.startswith('/'):
                router.handle_command(user_input)
            else:
                router.handle_chat(user_input)

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

    print("Goodbye!")

if __name__ == '__main__':
    main()
```

### 2. Chat Manager (`chat_manager.py`)
```python
from pathlib import Path
from datetime import datetime
import hashlib
import json

from storage import Storage
from name_generator import generate_name

class ChatManager:
    def __init__(self):
        self.storage = Storage()
        self.current_chat = None

    def create_chat(self, name=None, first_message=None, project=None, temporary=False):
        """Create new chat"""
        # Generate chat ID
        chat_id = hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]

        # Generate or use provided name
        if name is None and first_message:
            name = generate_name(first_message)
        elif name is None:
            name = f"chat-{chat_id}"

        # Create chat metadata
        chat = {
            'chat_id': chat_id,
            'name': name,
            'provider': 'claude',  # Default
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'message_count': 0,
            'project': project,
            'temporary': temporary,
            'messages': []
        }

        # Save to file immediately
        self.storage.save_chat(chat)
        self.current_chat = chat

        return chat

    def add_message(self, role, content, provider=None):
        """Add message to current chat"""
        if not self.current_chat:
            raise ValueError("No active chat")

        message = {
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'provider': provider or self.current_chat['provider'],
            'timestamp': datetime.now().isoformat()
        }

        self.current_chat['messages'].append(message)
        self.current_chat['message_count'] += 1
        self.current_chat['updated_at'] = datetime.now().isoformat()

        # Append to file
        self.storage.append_message(self.current_chat, message)

        return message

    def list_chats(self, project=None, temporary=None):
        """List all chats"""
        return self.storage.list_chats(project=project, temporary=temporary)

    def get_chat(self, chat_id_or_name):
        """Get chat by ID or name"""
        return self.storage.get_chat(chat_id_or_name)

    def resume_chat(self, chat_id_or_name):
        """Resume existing chat"""
        chat = self.get_chat(chat_id_or_name)
        if chat:
            self.current_chat = chat
            return chat
        return None
```

### 3. Storage Layer (`storage.py`)
```python
from pathlib import Path
import json
import yaml

class Storage:
    def __init__(self, base_path=None):
        self.base_path = Path(base_path or Path.home() / '.omni')
        self.chats_path = self.base_path / 'chats'
        self.index_path = self.base_path / 'index.json'

        # Create directories
        (self.chats_path / 'permanent').mkdir(parents=True, exist_ok=True)
        (self.chats_path / 'temp').mkdir(parents=True, exist_ok=True)

        # Load or create index
        self.index = self._load_index()

    def _load_index(self):
        """Load chat index"""
        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                return json.load(f)
        return {'chats': {}}

    def _save_index(self):
        """Save chat index"""
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _get_chat_file_path(self, chat):
        """Generate file path for chat"""
        timestamp = chat['created_at'][:19].replace(':', '').replace('-', '')
        filename = f"{timestamp}_{chat['name']}.md"

        if chat.get('temporary'):
            return self.chats_path / 'temp' / filename
        else:
            return self.chats_path / 'permanent' / filename

    def save_chat(self, chat):
        """Save chat to file and update index"""
        file_path = self._get_chat_file_path(chat)

        # Write chat file
        with open(file_path, 'w') as f:
            # Write YAML frontmatter
            f.write('---\n')
            metadata = {k: v for k, v in chat.items() if k != 'messages'}
            yaml.dump(metadata, f)
            f.write('---\n\n')
            f.write(f"# Chat: {chat['name']}\n\n")

        # Update index
        self.index['chats'][chat['chat_id']] = {
            'name': chat['name'],
            'file_path': str(file_path),
            'created_at': chat['created_at'],
            'updated_at': chat['updated_at'],
            'provider': chat['provider'],
            'message_count': chat['message_count']
        }
        self._save_index()

    def append_message(self, chat, message):
        """Append message to chat file"""
        file_path = self._get_chat_file_path(chat)

        with open(file_path, 'a') as f:
            msg_num = chat['message_count']
            role = message['role'].capitalize()
            timestamp = message['timestamp']
            provider = message.get('provider', '')

            if role == 'Assistant' and provider:
                f.write(f"## Message {msg_num} - {role} ({provider}) ({timestamp})\n")
            else:
                f.write(f"## Message {msg_num} - {role} ({timestamp})\n")

            f.write(f"{message['content']}\n\n")

        # Update index
        self.index['chats'][chat['chat_id']]['updated_at'] = chat['updated_at']
        self.index['chats'][chat['chat_id']]['message_count'] = chat['message_count']
        self._save_index()

    def list_chats(self, project=None, temporary=None):
        """List chats from index"""
        chats = self.index['chats'].values()

        # Filter if needed
        if project:
            chats = [c for c in chats if c.get('project') == project]
        if temporary is not None:
            chats = [c for c in chats if c.get('temporary') == temporary]

        return list(chats)

    def get_chat(self, chat_id_or_name):
        """Get chat by ID or name"""
        # Try by ID first
        if chat_id_or_name in self.index['chats']:
            chat_meta = self.index['chats'][chat_id_or_name]
            # Load full chat from file
            return self._load_chat_from_file(chat_meta['file_path'])

        # Try by name
        for chat_id, chat_meta in self.index['chats'].items():
            if chat_meta['name'] == chat_id_or_name:
                return self._load_chat_from_file(chat_meta['file_path'])

        return None

    def _load_chat_from_file(self, file_path):
        """Load chat from markdown file"""
        # Parse YAML frontmatter and messages
        # Implementation details...
        pass
```

### 4. Name Generator (`name_generator.py`)
```python
import re

def generate_name(text, max_words=4):
    """Generate kebab-case name from text"""
    # Remove special characters
    text = re.sub(r'[^\w\s-]', '', text.lower())

    # Split into words
    words = text.split()

    # Take first max_words meaningful words
    meaningful_words = [w for w in words if len(w) > 2][:max_words]

    # Join with hyphens
    name = '-'.join(meaningful_words)

    # Limit length
    if len(name) > 50:
        name = name[:50].rsplit('-', 1)[0]

    return name or 'chat'

# Examples:
# "How do I implement OAuth in Node.js?" → "implement-oauth-nodejs"
# "Explain React hooks" → "explain-react-hooks"
# "What's the best database?" → "best-database"
```

### 5. Provider Manager (`provider_manager.py`)
```python
import subprocess
import shutil
from typing import Optional, List

class ProviderManager:
    def __init__(self):
        self.providers = self._detect_providers()
        self.current_provider = self._get_default_provider()

    def _detect_providers(self):
        """Detect installed AI CLIs"""
        providers = {}

        # Check for Claude CLI
        if shutil.which('claude'):
            providers['claude'] = ClaudeProvider()

        # Check for OpenAI CLI
        if shutil.which('openai'):
            providers['openai'] = OpenAIProvider()

        # Check for Grok (when available)
        if shutil.which('grok'):
            providers['grok'] = GrokProvider()

        return providers

    def _get_default_provider(self):
        """Get default provider"""
        # Priority: claude > openai > others
        if 'claude' in self.providers:
            return 'claude'
        elif 'openai' in self.providers:
            return 'openai'
        elif self.providers:
            return list(self.providers.keys())[0]
        return None

    def list_providers(self):
        """List available providers"""
        return list(self.providers.keys())

    def switch_provider(self, provider_name):
        """Switch active provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not installed")
        self.current_provider = provider_name
        return True

    def send_message(self, message, context=None):
        """Send message to current provider"""
        if not self.current_provider:
            raise ValueError("No provider available")

        provider = self.providers[self.current_provider]
        return provider.send_message(message, context)

class ClaudeProvider:
    def send_message(self, message, context=None):
        """Send message to Claude CLI"""
        # Build command
        cmd = ['claude', message]

        # Execute
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI error: {result.stderr}")

        return result.stdout.strip()

class OpenAIProvider:
    def send_message(self, message, context=None):
        """Send message to OpenAI CLI"""
        # Similar to Claude
        cmd = ['openai', 'chat', message]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise RuntimeError(f"OpenAI CLI error: {result.stderr}")

        return result.stdout.strip()
```

---

## File Structure

```
omni/
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── README.md
├── LICENSE
├── DESIGN.md               # This file
├── REQUIREMENTS.md
├── COMMANDS.md
│
├── src/
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── cli.py              # CLI setup
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── chat_manager.py
│   │   ├── project_manager.py
│   │   ├── storage.py
│   │   ├── search.py
│   │   └── config.py
│   │
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── claude.py
│   │   ├── openai.py
│   │   ├── grok.py
│   │   └── detector.py
│   │
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── chat_commands.py
│   │   ├── project_commands.py
│   │   └── utility_commands.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── name_generator.py
│       ├── file_utils.py
│       └── formatters.py
│
└── tests/
    ├── __init__.py
    ├── test_chat_manager.py
    ├── test_storage.py
    ├── test_name_generator.py
    └── test_providers.py
```

---

## Implementation Roadmap

### Week 1: Foundation
- **Days 1-2**: Phase 1 - Proof of Concept
  - Basic REPL
  - Single provider (Claude)
  - Simple file storage

- **Days 3-5**: Phase 2 - Core Chat Management
  - Auto-generated names
  - Immediate file creation
  - Index management
  - Basic commands

### Week 2: Multi-Provider & Projects
- **Days 1-3**: Phase 3 - Multi-Provider
  - Provider detection
  - Provider interface
  - Provider switching

- **Days 4-7**: Phase 4 - Projects & Search
  - Project management
  - Full-text search
  - Project organization

### Week 3: Polish
- **Days 1-5**: Phase 5 - Remaining P0
  - Temporary chats
  - Code extraction
  - Export functionality
  - Context management

- **Days 6-7**: Testing & Documentation
  - Integration testing
  - User documentation
  - Bug fixes

---

## Testing Strategy

### Unit Tests
```python
# test_name_generator.py
def test_generate_name():
    assert generate_name("How do I implement OAuth?") == "implement-oauth"
    assert generate_name("Explain React hooks") == "explain-react-hooks"
    assert generate_name("a") == "chat"  # Too short

# test_storage.py
def test_save_and_load_chat():
    storage = Storage('/tmp/test-omni')
    chat = {...}
    storage.save_chat(chat)
    loaded = storage.get_chat(chat['chat_id'])
    assert loaded['name'] == chat['name']
```

### Integration Tests
```python
# test_chat_flow.py
def test_full_chat_flow():
    # Create chat
    # Add messages
    # Save to file
    # Resume chat
    # Verify continuity
    pass
```

### Manual Testing Checklist
- [ ] Start omni session
- [ ] Type message, get response
- [ ] File created immediately
- [ ] `/list` shows chat
- [ ] `/resume` continues chat
- [ ] Switch providers
- [ ] Create project
- [ ] Search chats
- [ ] Export chat

---

## Success Metrics

### MVP Completion Criteria
- [ ] All P0 requirements implemented
- [ ] Works with Claude and OpenAI CLIs
- [ ] Chat files created correctly with naming convention
- [ ] Search works across all chats
- [ ] Projects organize chats correctly
- [ ] No data loss on crashes
- [ ] Handles errors gracefully
- [ ] Installation takes < 5 minutes
- [ ] First chat takes < 30 seconds

### Performance Targets
- Startup time: < 500ms
- Command response: < 100ms (for local operations)
- Search 1000 chats: < 2 seconds
- File operations: atomic and safe

---

## Future Enhancements (Post-MVP)

### P1 Features
- Templates for common prompts
- Better auto-completion
- Shell integration (bash, zsh)
- Cost tracking
- Export to HTML/PDF
- Archive functionality

### P2 Features
- Conversation branching
- Local LLM support
- Plugin system
- Shared/collaborative chats
- Web interface (optional)
- Mobile sync

---

## Risk Mitigation

### Risks & Mitigation
1. **Provider CLI changes**: Abstract provider interface, easy to update
2. **File corruption**: Atomic writes, backup before updates
3. **Performance with many chats**: Index file, lazy loading
4. **Different CLI interfaces**: Provider abstraction layer
5. **Cross-platform issues**: Use pathlib, test on all platforms

---

## Installation & Distribution

### Distribution Strategy

Given that target users are developers who:
- Already have npm installed
- Are using npm-based AI CLIs (Claude, OpenAI, etc.)
- Want simple, fast installation

**Recommended: npm package** (primary distribution)

### Option 1: npm Package (Recommended)

**Installation:**
```bash
npm install -g omni-cli
```

**Implementation Approach:**
```json
// package.json
{
  "name": "omni-cli",
  "version": "0.1.0",
  "description": "Unified CLI wrapper for AI models",
  "bin": {
    "omni": "./bin/omni"
  },
  "scripts": {
    "postinstall": "node scripts/setup.js"
  },
  "dependencies": {},
  "engines": {
    "node": ">=16.0.0"
  }
}
```

**Wrapper Script** (`bin/omni`):
```javascript
#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

// Check if Python is available
function checkPython() {
  const pythonCommands = ['python3', 'python'];

  for (const cmd of pythonCommands) {
    try {
      const result = require('child_process').spawnSync(cmd, ['--version'], {
        stdio: 'pipe'
      });

      if (result.status === 0) {
        return cmd;
      }
    } catch (e) {
      continue;
    }
  }

  return null;
}

const pythonCmd = checkPython();

if (!pythonCmd) {
  console.error('Error: Python 3.9+ is required');
  console.error('Install from: https://www.python.org/downloads/');
  process.exit(1);
}

// Run the Python app
const pythonApp = path.join(__dirname, '..', 'src', 'main.py');

const child = spawn(pythonCmd, [pythonApp, ...process.argv.slice(2)], {
  stdio: 'inherit'
});

child.on('exit', (code) => {
  process.exit(code);
});
```

**Post-install Setup** (`scripts/setup.js`):
```javascript
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('Setting up omni-cli...');

// Check Python version
try {
  const pythonCmd = 'python3';
  const version = execSync(`${pythonCmd} --version`, { encoding: 'utf8' });
  console.log(`✓ Found ${version.trim()}`);

  // Install Python dependencies in isolated environment
  const requirementsPath = path.join(__dirname, '..', 'requirements.txt');

  if (fs.existsSync(requirementsPath)) {
    console.log('Installing Python dependencies...');
    execSync(`${pythonCmd} -m pip install --user -r "${requirementsPath}"`, {
      stdio: 'inherit'
    });
    console.log('✓ Dependencies installed');
  }

  // Create omni config directory
  const homeDir = require('os').homedir();
  const omniDir = path.join(homeDir, '.omni');

  if (!fs.existsSync(omniDir)) {
    fs.mkdirSync(omniDir, { recursive: true });
    console.log(`✓ Created config directory: ${omniDir}`);
  }

  console.log('✓ omni-cli setup complete!');
  console.log('\nRun "omni" to get started');

} catch (error) {
  console.error('Setup failed:', error.message);
  console.error('\nPlease ensure Python 3.9+ is installed:');
  console.error('https://www.python.org/downloads/');
  process.exit(1);
}
```

**Pros:**
- Familiar to target audience (`npm install -g omni-cli`)
- Consistent with other AI CLIs
- Easy updates (`npm update -g omni-cli`)
- Can check/install Python dependencies automatically
- Works cross-platform

**Cons:**
- Requires Python installed (but we check and guide user)
- Slightly more complex packaging

---

### Option 2: pipx (Alternative for Python users)

**Installation:**
```bash
pipx install omni-cli
```

**Pros:**
- Standard Python application installer
- Isolated environment (no conflicts)
- Clean uninstall

**Cons:**
- Users need to install pipx first
- Less familiar to npm-focused developers

---

### Option 3: Standalone Binary (Future consideration)

Using PyInstaller to create self-contained executables:

```bash
# macOS
curl -L https://github.com/omni-cli/omni/releases/download/v0.1.0/omni-macos -o omni
chmod +x omni
sudo mv omni /usr/local/bin/

# Linux
curl -L https://github.com/omni-cli/omni/releases/download/v0.1.0/omni-linux -o omni
chmod +x omni
sudo mv omni /usr/local/bin/

# Windows
# Download omni.exe from releases
```

**Pros:**
- No dependencies
- Just works

**Cons:**
- Large file size (~50MB)
- Separate binary for each OS
- More maintenance overhead
- Slower startup time

---

### Recommended Approach: Multi-Distribution

**Primary: npm (easiest for target audience)**
```bash
npm install -g omni-cli
```

**Alternative: pipx (for Python enthusiasts)**
```bash
pipx install omni-cli
```

**Future: Homebrew/Chocolatey**
```bash
# macOS/Linux
brew install omni-cli

# Windows
choco install omni-cli
```

---

### Updated File Structure for npm Distribution

```
omni-cli/
├── package.json              # npm package config
├── bin/
│   └── omni                  # Node wrapper script
├── scripts/
│   └── setup.js              # Post-install setup
├── src/                      # Python source code
│   ├── __init__.py
│   ├── main.py
│   └── ...
├── requirements.txt          # Python dependencies
├── setup.py                  # For pipx distribution
├── pyproject.toml           # Modern Python packaging
├── README.md
├── LICENSE
└── docs/
    ├── DESIGN.md
    ├── REQUIREMENTS.md
    └── COMMANDS.md
```

### package.json (Complete)

```json
{
  "name": "omni-cli",
  "version": "0.1.0",
  "description": "Unified CLI wrapper for AI models (Claude, ChatGPT, Grok)",
  "keywords": [
    "ai",
    "cli",
    "claude",
    "chatgpt",
    "openai",
    "grok",
    "llm",
    "chat"
  ],
  "homepage": "https://github.com/omni-cli/omni#readme",
  "bugs": {
    "url": "https://github.com/omni-cli/omni/issues"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/omni-cli/omni.git"
  },
  "license": "MIT",
  "author": "Your Name",
  "bin": {
    "omni": "./bin/omni"
  },
  "files": [
    "bin/",
    "src/",
    "scripts/",
    "requirements.txt",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "postinstall": "node scripts/setup.js",
    "test": "pytest tests/",
    "preuninstall": "node scripts/cleanup.js"
  },
  "engines": {
    "node": ">=16.0.0"
  },
  "os": [
    "darwin",
    "linux",
    "win32"
  ]
}
```

### setup.py (For pipx distribution)

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="omni-cli",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Unified CLI wrapper for AI models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/omni-cli/omni",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "omni=main:main",
        ],
    },
)
```

---

### Installation Experience

**Via npm (Recommended):**
```bash
$ npm install -g omni-cli

# Auto-detects Python
✓ Found Python 3.11.5
Installing Python dependencies...
✓ Dependencies installed
✓ Created config directory: /Users/you/.omni
✓ omni-cli setup complete!

Run "omni" to get started

$ omni
Omni CLI v0.1.0 - Type /help for commands
Detected providers: claude, openai
Default provider: claude

omni>
```

**Via pipx (Alternative):**
```bash
$ pipx install omni-cli
  installed package omni-cli 0.1.0, Python 3.11.5
  These apps are now globally available
    - omni
done! ✨ 🌟 ✨

$ omni
Omni CLI v0.1.0 - Type /help for commands
omni>
```

---

## Next Steps

1. Set up npm package structure
2. Create wrapper script and setup
3. Implement Phase 1 (Proof of Concept)
4. Test installation on different platforms
5. Publish to npm (start with beta/alpha tag)
6. Iterate based on feedback

Ready to start implementation!
