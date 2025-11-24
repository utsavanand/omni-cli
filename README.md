<p align="center">
  <img src="banner.png" alt="Omni CLI" width="100%"/>
</p>

# Omni CLI

Unified CLI wrapper for AI models - one interface for Claude, Codex/OpenAI, Gemini, and more.

## Features

- **Multi-Provider Support** - Claude, Codex/OpenAI, and Gemini in one place
- **Switch Providers Mid-Conversation** - Compare responses from different AIs
- **Consult Multiple Providers** - Get merged insights from multiple AIs in one response
- **Persistent Memory** - All conversations saved automatically with full context
- **Context Sharing** - Ask Claude, then get Codex's opinion with full conversation history
- **Project Organization** - Group related chats into projects
- **Full-Text Search** - Find any conversation instantly
- **Simple Interface** - Just type to chat, use `/commands` for features
- **Markdown Storage** - All chats saved as readable markdown files

## Installation

### Prerequisites

Omni CLI is a **lightweight wrapper** - you need to install AI providers first:

#### Required:
- **Node.js 16+** - For omni-cli installation
- **Python 3.9+** - Runtime requirement

#### AI Providers (Install at least one):

**Claude Code** (Recommended):
```bash
# Download from https://claude.ai/download
# Or install via npm (if available)
```
[Installation Guide →](https://claude.ai/download)

**OpenAI/Codex CLI**:
```bash
# Installation instructions at OpenAI's docs
```
[Installation Guide →](https://platform.openai.com/docs)

**Google Gemini CLI**:
```bash
# Installation instructions at Google AI
```
[Installation Guide →](https://ai.google.dev/)

> **Note**: Omni CLI will detect which providers you have installed and make them available automatically. You don't need all of them - just install the ones you want to use!

### Install Omni CLI

**Option 1: From npm** (once published):
```bash
npm install -g omni-cli

# Run setup wizard to check providers
omni --setup
```

**Option 2: Local Development**

Since this package is not yet published to npm, install it locally:

```bash
# Clone or navigate to the project directory
cd /path/to/omni-cli

# Install dependencies (automatically installs Python deps too)
npm install

# Link the package globally for local testing
npm link

# Or run directly without linking
node bin/omni
```

> **Note**: `npm install` automatically runs the setup script which installs Python dependencies. No need to run `pip install` separately!

### Verify Installation

Run the setup wizard to check which providers are detected:

```bash
omni --setup
```

Output example:
```
Omni CLI Setup Wizard

Checking for installed AI providers...

✓ Claude Code              installed
✗ OpenAI/Codex CLI        not installed
✗ Google Gemini CLI       not installed

✓ Found 1 provider(s): claude

You're ready to use Omni CLI!
Run omni to start chatting.
```

Then start chatting:
```bash
omni
```

### Publishing (For Maintainers)

Once ready to publish:

```bash
npm publish
```

Then users can install via:
```bash
npm install -g omni-cli
```

## Quick Start

```bash
# Start omni
omni

# Detects installed providers automatically
Installed providers: claude, codex
Current provider: claude

# Just type to chat
omni> how do I reverse a string in python?

# Switch providers anytime
omni> /use codex
omni> what's your take on this?
# Codex sees the full conversation!

# Use commands with /
omni> /providers         # List available providers
omni> /list              # List all chats
omni> /search "auth"     # Search chats
omni> /exit              # Exit
```

## Usage

### Multi-Provider Chat (The Killer Feature!)

```bash
$ omni
omni> explain async/await in JavaScript
Thinking (claude)...
[Claude's explanation...]

omni> /use codex
Switched to codex

omni> can you give me a code example?
Thinking (codex)...
# Codex sees Claude's explanation and builds on it!
[Codex's code example...]

omni> /use gemini
Switched to gemini

omni> any performance tips?
Thinking (gemini)...
# Gemini sees the full conversation from both Claude and Codex!
[Gemini's performance advice...]
```

### Consult Multiple Providers (Get Best of Both!)

```bash
$ omni
omni> /consult codex explain the difference between async and defer in JavaScript

💭 Consulting claude and codex...

Merged Response:
[Combined insights from both Claude and Codex, highlighting different perspectives
and providing a comprehensive answer that synthesizes both responses]

─── Individual Responses ───
claude: Async and defer are both attributes for <script> tags that control...
codex: The key difference is timing: async downloads in parallel and executes...
```

The `/consult` command:
- Sends your question to BOTH your current provider and the specified provider
- Collects both responses
- Uses your current provider to synthesize a merged answer
- Shows you both individual responses for comparison
- Perfect for complex questions where you want multiple perspectives!

### Provider Commands

```bash
# List all providers
omni> /providers

Available Providers:
→ claude     ✓ installed
  codex      ✓ installed (OpenAI CLI)
  gemini     ✗ not installed

# Switch providers
omni> /use codex
Switched to codex

# Continue chatting with new provider
omni> [new provider sees full conversation history]
```

### Resuming Previous Chats

```bash
# Interactive menu - use arrow keys to select
omni> /resume

# Filter by keyword
omni> /resume oauth          # Shows only chats with "oauth" in the name
omni> /resume claude         # Shows only chats using Claude provider

# Navigate with arrow keys, Enter to select, Esc to cancel
```

### Available Commands

**Getting Help:**
- `/help` - Show detailed command reference with examples

**Chat Management:**
- `/new <name>` - Create a new named chat
- `/list` - List all saved chats with metadata
- `/resume [keyword]` - Interactive menu to resume a chat (use arrow keys to select)
  - Without keyword: Shows all chats
  - With keyword: Filters chats by name or provider (e.g., `/resume oauth` or `/resume claude`)
- `/delete <id/name>` - Delete a chat (with confirmation)
- `/find <term>` or `/search <term>` - Search through chat history

**Provider Management:**
- `/providers` - List all available providers
- `/use <provider>` - Switch to different provider
- `/consult <provider> <question>` - Get merged response from current and specified provider

**Utilities:**
- `/exit` or `/quit` - Exit omni

## Current Status

**MVP Complete - Ready for v0.1.0**

**Core Features:**
- Multi-provider support (Claude, Codex/OpenAI, Gemini)
- Switch providers mid-conversation with full context sharing
- `/consult` command to merge insights from multiple providers
- Auto-generated chat names with manual naming option
- Persistent file storage in Markdown format
- Full conversation history preserved across sessions
- Interactive `/resume` with arrow key navigation
- Full-text search with `/find`
- Complete help system
- Chat deletion with confirmation

**Coming in Future Versions:**
- Projects and folders for better organization
- `/merge` - Merge and summarize multiple chats
- `/summarize` - Create chat summaries
- `/archive` - Archive old chats
- Export to HTML/PDF
- Temporary chats with TTL
- And more! (See todo.md)

## Storage

Chats are stored in `~/.omni/chats/` as Markdown files with the format:
```
YYYYMMDD-HHMMSS_chat-name.md
```

## Development

```bash
# Clone the repo
git clone https://github.com/omni-cli/omni.git
cd omni

# Install dependencies
npm install
pip install -r requirements.txt

# Run locally
python src/main.py
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
