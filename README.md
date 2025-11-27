<p align="center">
  <img src="banner.png" alt="Omni CLI" width="100%"/>
</p>

# Omni CLI

Unified CLI wrapper for AI models - one interface for Claude, Codex/OpenAI, Gemini, and more.

**Key Features:** Multi-provider support • Hierarchical organization (Namespaces → Projects → Chats + Summaries) • Chat summarization & archiving • Context sharing • Persistent memory • Full-text search

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

#### Browse & Manage with /list

```bash
omni> /list
```

Interactive browser for all your namespaces, projects, chats, and summaries:
```
📦 work-projects (2 projects)
  📁 api-service (3 chats, 1 summaries)
    💬 authentication               claude   5 msgs
    💬 user-management             claude   3 msgs
    📄 research-summary            claude   long summary
  📁 webapp (2 chats, 0 summaries)
    💬 frontend-design             claude   7 msgs

📦 learning (0 projects)

📁 Standalone Projects
  📁 side-project (1 chats, 0 summaries)

💬 Standalone Chats
  quick-question                   claude   1 msg
```

**Interactive controls:**
- **↑/↓**: Navigate through items
- **Enter**: Resume chat or view summary (with formatted markdown)
- **d**: Delete item (with confirmation)
- **r**: Rename namespaces, projects, or chats
- **Esc**: Exit back to prompt

All actions loop back to the list, making it easy to manage multiple items!

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

#### Summarize & Archive Chats

```bash
omni> /summary my-chat-name
omni> /summary abc123 --type short
```

Condenses a chat into an AI-generated summary and archives it:
- **Two summary types:**
  - `short`: 50-100 word concise summary
  - `long` (default): Detailed summary with topics, solutions, code examples, and conclusions
- **Original chat is deleted** and replaced with a markdown summary file
- Summaries appear in `/list` with a 📄 icon
- Press Enter in `/list` to view summary with formatted markdown

**Example workflow:**
```bash
# Have a long research conversation
omni> /new oauth-research --project backend
omni> explain OAuth 2.0 flow in detail
# ... many messages ...

# Summarize when done to save space
omni> /summary oauth-research --type long
✓ Summary created: oauth-research
  Type: long
  Words: 234
  Original chat deleted

# View later in /list or search for it
omni> /list
# Press Enter on the summary to read it
```

**Benefits:**
- Saves storage space by condensing long conversations
- Creates searchable knowledge base of key insights
- Maintains project organization (summaries stay in their projects)
- AI-powered distillation captures important details

---

### Organization: Namespaces & Projects

Organize your work with a four-level hierarchy:
- **Namespaces** → Group of related projects (e.g., "work-projects", "personal")
- **Projects** → Group of related chats and summaries (e.g., "api-service", "webapp")
- **Chats** → Individual active conversations
- **Summaries** → Archived, condensed versions of chats

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

### Workflow 3: Research and Knowledge Management

```bash
# Create a namespace for learning
omni> /namespace create learning --description "Personal learning projects"

# Create topic-specific projects
omni> /project create machine-learning --namespace learning
omni> /project create web3 --namespace learning

# Create focused chats for deep research
omni> /new neural-networks --project machine-learning
omni> explain backpropagation in simple terms
omni> how does gradient descent work?
omni> show me a simple neural network implementation
# ... lengthy conversation with code examples ...

# Summarize the research session to save space
omni> /summary neural-networks --type long
✓ Summary created: neural-networks
  Type: long
  Words: 312
  Original chat deleted

# Create more research chats
omni> /new transformers --project machine-learning
omni> explain transformer architecture
# ... another long conversation ...

# View all summaries in your project
omni> /list
# Navigate to machine-learning project
# See both chats and summaries organized together

# Later, search across summaries and chats
omni> /find "gradient descent"
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

All data is stored in `~/.omni/` as human-readable Markdown files with JSON indexes:

```
~/.omni/
├── chats/permanent/           # Standalone chats
├── summaries/                 # Standalone summaries
├── projects/                  # Project folders
│   └── my-webapp/
│       ├── chats/            # Chats in this project
│       └── summaries/        # Summaries in this project
├── namespaces/               # Namespace folders
├── index.json               # Chat index
├── summary_index.json       # Summary index
├── projects.json            # Project index
└── namespace_index.json     # Namespace index
```

**File naming formats:**
- Chats: `YYYYMMDD-HHMMSS_chat-name.md`
- Summaries: `YYYYMMDD-HHMMSS_chat-name_summary.md`

**Summary file structure:**
```markdown
---
summary_id: abc12345
name: oauth-research
original_chat_id: xyz789
type: long
provider: claude
created_at: 2025-11-26T10:30:00
project: backend
word_count: 234
---

# Summary: oauth-research

**Type:** Long
**Generated:** 2025-11-26
**Original Chat:** xyz789

---

[AI-generated summary content with markdown formatting]
```

---

## Tips & Tricks

**1. Use descriptive names:**
```bash
omni> /new api-authentication-research --project backend
```

**2. Organize as you go:**
Create namespaces and projects early to keep things organized.

**3. Summarize long conversations:**
After research or exploratory chats, use `/summary` to condense into searchable knowledge:
```bash
omni> /summary my-research --type long
```

**4. Use keywords in /resume:**
```bash
omni> /resume auth    # Quickly find authentication-related chats
```

**5. Search is powerful:**
```bash
omni> /find "error handling"    # Finds all discussions about errors
```

**6. Browse with /list:**
Use the interactive `/list` command to navigate, view summaries, and manage everything in one place.

**7. Switch providers for different tasks:**
- Claude: Great for explanations and discussions
- Codex: Excellent for code generation
- Gemini: Good for diverse perspectives

---

## Coming Soon

- `/add-note` - Add manual notes to chats, projects, or namespaces
- `/ask --project` - Ask questions scoped to specific projects
- `/archive` - Archive old chats without summarizing
- `/merge` - Merge and summarize multiple chats
- Artifacts support - Store code snippets, configs, and files in projects

See [todo.md](todo.md) for full roadmap.

---

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR at [github.com/omni-cli/omni](https://github.com/omni-cli/omni)
