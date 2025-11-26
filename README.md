<p align="center">
  <img src="banner.png" alt="Omni CLI" width="100%"/>
</p>

# Omni CLI

Unified CLI wrapper for AI models - one interface for Claude, Codex/OpenAI, Gemini, and more.

**Key Features:** Multi-provider support • Hierarchical organization (Namespaces → Projects → Chats) • Context sharing • Persistent memory • Full-text search

## Quick Start

```bash
# Install
npm install -g omni-cli

# Start chatting
omni
```

> **Note**: Omni CLI is a lightweight wrapper. Install at least one AI provider first: [Claude Code](https://claude.ai/download), [OpenAI](https://platform.openai.com/docs), or [Gemini](https://ai.google.dev/)

---

## Commands Reference

### Getting Started

**Start a conversation:**
```bash
omni
omni> hello, can you help me with Python?
```

Just type naturally - no command needed. Your chat is auto-saved with a generated name.

**Get help:**
```bash
omni> /help
```

**Exit:**
```bash
omni> /exit    # or /quit
```

---

### Chat Management

#### Create a Named Chat

```bash
omni> /new my-feature-chat
```

Creates a new chat with a specific name instead of auto-generated.

**With a project:**
```bash
omni> /new authentication --project my-webapp
```

Creates a chat and adds it to a project in one command.

#### List All Chats

```bash
omni> /list
```

Shows all your chats in hierarchical tree format:
```
📦 work-projects (2 projects)
  📁 api-service (3 chats)
    abc123  authentication               claude   5 msgs  2025-11-26
    def456  user-management             claude   3 msgs  2025-11-25
  📁 webapp (2 chats)
    jkl012  frontend-design             claude   7 msgs  2025-11-23

📄 Standalone Chats
  stu901  quick-question                claude   1 msg   2025-11-20
```

#### Resume a Previous Chat

```bash
omni> /resume
```

Interactive menu with arrow keys to select which chat to continue:
- ↑/↓ to navigate
- Enter to select
- Esc to cancel

**Filter by keyword:**
```bash
omni> /resume authentication    # Shows only chats matching "authentication"
omni> /resume claude            # Shows only chats using Claude provider
```

#### Search Chats

```bash
omni> /find OAuth              # or /search OAuth
```

Searches through all chat content for "OAuth" and shows matching chats.

#### Delete a Chat

```bash
omni> /delete abc123           # By chat ID
omni> /delete my-chat-name     # By name
```

Shows confirmation before deleting.

---

### Organization: Namespaces & Projects

Organize your work with a three-level hierarchy:
- **Namespaces** → Group of related projects (e.g., "work-projects", "personal")
- **Projects** → Group of related chats (e.g., "api-service", "webapp")
- **Chats** → Individual conversations

#### Namespace Commands

**Create a namespace:**
```bash
omni> /namespace create work-projects
omni> /namespace create personal --description "Personal projects and learning"
```

**List all namespaces:**
```bash
omni> /namespace list
```

**Add a project to a namespace:**
```bash
omni> /namespace add work-projects my-webapp
```

**List projects in a namespace:**
```bash
omni> /namespace projects work-projects
```

**Remove a project from a namespace:**
```bash
omni> /namespace remove work-projects my-webapp
```

**Delete a namespace:**
```bash
omni> /namespace delete work-projects
```
Note: Deletes the namespace but preserves all projects.

#### Project Commands

**Create a project:**
```bash
omni> /project create my-webapp
```

**Create a project in a namespace:**
```bash
omni> /project create api-service --namespace work-projects
```

**List all projects:**
```bash
omni> /project list
```

**Add a chat to a project:**
```bash
omni> /project add my-webapp abc123
```

**List chats in a project:**
```bash
omni> /project chats my-webapp
```

**Remove a chat from a project:**
```bash
omni> /project remove my-webapp abc123
```

**Delete a project:**
```bash
omni> /project delete my-webapp
```
Note: Deletes the project but preserves all chats.

---

### Provider Management

#### List Available Providers

```bash
omni> /providers
```

Shows which AI providers are installed and available:
```
Available Providers:
→ claude     ✓ installed
  codex      ✓ installed (OpenAI CLI)
  gemini     ✗ not installed
```

#### Switch Providers

```bash
omni> /use codex
```

Switches to Codex for subsequent messages. The new provider sees the full conversation history!

**Example workflow:**
```bash
omni> explain async/await in JavaScript
# Claude responds...

omni> /use codex
omni> can you give me a code example?
# Codex sees Claude's explanation and builds on it!
```

#### Consult Multiple Providers

```bash
omni> /consult codex explain the difference between async and defer
```

Sends your question to BOTH your current provider (e.g., Claude) and the specified provider (Codex), then:
1. Collects both responses
2. Uses your current provider to synthesize a merged answer
3. Shows you both individual responses for comparison

Perfect for complex questions where you want multiple perspectives!

---

## Common Workflows

### Workflow 1: Organized Project Development

```bash
# 1. Create a namespace for work projects
omni> /namespace create work-projects

# 2. Create projects in the namespace
omni> /project create api-service --namespace work-projects
omni> /project create webapp --namespace work-projects

# 3. Create chats within projects
omni> /new authentication --project api-service
omni> how do I implement OAuth 2.0 in Node.js?
# ... conversation continues ...

omni> /new database-design --project api-service
omni> what's the best schema for user authentication?

# 4. Later, resume to continue work
omni> /resume
# Navigate to your chat and press Enter
```

### Workflow 2: Multi-Provider Comparison

```bash
# Ask Claude first
omni> what are the best practices for React state management?
# Claude responds...

# Get Codex's opinion
omni> /use codex
omni> what do you think about Redux vs Context API?
# Codex sees the full conversation and responds

# Get a merged perspective
omni> /use claude
omni> /consult codex summarize the key differences
# Get a synthesized answer from both providers
```

### Workflow 3: Research and Organization

```bash
# Create a namespace for learning
omni> /namespace create learning --description "Personal learning projects"

# Create topic-specific projects
omni> /project create machine-learning --namespace learning
omni> /project create web3 --namespace learning

# Create focused chats
omni> /new neural-networks --project machine-learning
omni> explain backpropagation in simple terms

# Later, find related discussions
omni> /find backpropagation
omni> /project chats machine-learning
```

---

## Installation

### Prerequisites

Omni CLI is a **lightweight wrapper** - you need to install AI providers first:

**Required:**
- Node.js 16+
- Python 3.9+

**AI Providers (Install at least one):**
- [Claude Code](https://claude.ai/download) (Recommended)
- [OpenAI/Codex CLI](https://platform.openai.com/docs)
- [Google Gemini CLI](https://ai.google.dev/)

### Install Omni CLI

**From npm:**
```bash
npm install -g omni-cli
omni --setup    # Verify installation
```

**Local Development:**
```bash
git clone https://github.com/omni-cli/omni.git
cd omni
npm install
npm link
```

---

## Storage

All chats are stored in `~/.omni/` as human-readable Markdown files:

```
~/.omni/
├── chats/permanent/           # Standalone chats
├── projects/                  # Project folders
│   └── my-webapp/
│       └── chats/            # Chats in this project
├── namespaces/               # Namespace folders
├── index.json               # Chat index
├── projects.json            # Project index
└── namespace_index.json     # Namespace index
```

Each chat file format:
```
YYYYMMDD-HHMMSS_chat-name.md
```

---

## Tips & Tricks

**1. Use descriptive names:**
```bash
omni> /new api-authentication-research --project backend
```

**2. Organize as you go:**
Create namespaces and projects early to keep things organized.

**3. Use keywords in /resume:**
```bash
omni> /resume auth    # Quickly find authentication-related chats
```

**4. Search is powerful:**
```bash
omni> /find "error handling"    # Finds all discussions about errors
```

**5. Switch providers for different tasks:**
- Claude: Great for explanations and discussions
- Codex: Excellent for code generation
- Gemini: Good for diverse perspectives

---

## Coming Soon

- `/add-note` - Add manual notes to chats, projects, or namespaces
- `/ask --project` - Ask questions scoped to specific projects
- `/summarize` - Create chat summaries
- `/archive` - Archive old chats
- `/merge` - Merge and summarize multiple chats

See [todo.md](todo.md) for full roadmap.

---

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR at [github.com/omni-cli/omni](https://github.com/omni-cli/omni)
