# Omni CLI - Command Reference (P0/MVP)

## Base Command
`omni` - Omniscient AI CLI wrapper

**Why "omni"?**
- Short, memorable, fun to type
- Means "all/everything" - perfect for multi-provider tool
- Suggests omniscient (all-knowing)
- Only 4 letters

Works with Claude CLI, OpenAI CLI, Grok, and other AI providers installed on your system.

---

## How It Works

### Interactive Session Mode (Primary Usage)
```bash
# Start omni session
$ omni

# You're now in omni - just type naturally to chat with default AI
omni> how do I reverse a string in python?

# Use /commands for built-in functionality (auto-complete available)
omni> /use claude               # Switch to Claude
omni> /new my-feature           # Start named chat
omni> /search "authentication"  # Search chats
omni> /project new my-app       # Create project
omni> /list                     # List chats
omni> /exit                     # Exit session
```

**Key concept:**
- **Regular text** = chat with AI
- **`/commands`** = built-in omni commands (all start with `/`)
- **Auto-complete** shows all available `/commands` when you type `/`

### Direct Command Mode (Optional)
You can also run one-off commands without entering the session:
```bash
$ omni /list                    # Quick list
$ omni /search "error"          # Quick search
```

---

## Setup & Configuration

### Prerequisites
Users should install the actual AI CLIs via their native methods:
```bash
# Install Claude CLI
npm install -g @anthropic-ai/claude-cli

# Install OpenAI CLI
npm install -g openai-cli

# Install Grok CLI (when available)
# etc.
```

### Initial Setup
```bash
# First time - run setup wizard
$ omni init

# Automatically:
# - Detects installed AI CLIs
# - Sets up storage location (~/.omni)
# - Configures default provider
# - Creates initial config
```

### Configuration (inside omni session)
```bash
omni> /config set provider claude      # Set default provider
omni> /config set provider openai
omni> /config set storage ~/.omni      # Set storage location
omni> /config show                     # View current config
omni> /providers                       # List detected providers
omni> /providers --installed           # Show only installed
```

---

## Chat Management

All commands below assume you're inside an omni session (`$ omni`).

### Creating & Managing Chats
```bash
# By default, typing anything starts chatting with default provider
omni> how do I implement authentication?

# Create named chat
omni> /new my-feature-chat
omni> /chat my-feature-chat

# Create temporary chat (auto-deletes after 7 days by default)
omni> /temp
omni> /temp my-experiment        # Named temporary chat

# Temporary chat with custom TTL (time-to-live)
omni> /temp --ttl 3d             # Delete after 3 days
omni> /temp --ttl 1w             # Delete after 1 week
omni> /temp --ttl 24h            # Delete after 24 hours
```

### Switching Providers
```bash
# Switch to specific provider for current session
omni> /use claude
omni> /use openai
omni> /use grok

# Create named chat with specific provider
omni> /new my-chat --provider claude
omni> /new my-chat -p openai
```

### Managing Existing Chats
```bash
# Resume existing chat by name or ID
omni> /resume my-feature-chat
omni> /resume <chat-id>

# Resume last chat
omni> /resume

# List all chats
omni> /list
omni> /ls

# List chats with details (date, provider, message count, TTL)
omni> /list --detailed
omni> /ls -l

# List only permanent chats
omni> /list --permanent

# List only temporary chats
omni> /list --temp

# Delete chat
omni> /delete my-feature-chat
omni> /rm <chat-id>

# Rename chat
omni> /rename old-name new-name
```

### Context & Options
```bash
# Add context file(s) to current session
omni> /context add ./src/app.py
omni> /context add ./src/*.py

# Start new chat with context
omni> /new my-chat --context ./src/app.py
omni> /new -c ./src/*.py

# Remove context
omni> /context clear
```

---

## Project Management

### Creating & Managing Projects
```bash
# Create new project
omni> /project new my-webapp
omni> /proj new my-webapp
omni> /p new my-webapp

# List all projects
omni> /project list
omni> /proj ls
omni> /p ls

# Delete project
omni> /project delete my-webapp
omni> /proj rm my-webapp

# Show project details
omni> /project show my-webapp
omni> /proj info my-webapp
```

### Working with Projects
```bash
# Add current/last chat to project
omni> /project add my-webapp
omni> /proj add my-webapp <chat-id>

# Remove chat from project
omni> /project remove my-webapp <chat-id>
omni> /proj rm my-webapp <chat-id>

# List all chats in project
omni> /project chats my-webapp
omni> /proj chats my-webapp

# Start new chat within project context
omni> /new --project my-webapp
omni> /new --proj my-webapp
omni> /new --project my-webapp --provider claude

# Set active project (all new chats go here)
omni> /project use my-webapp
omni> /proj use my-webapp
```

---

## Search

### Basic Search
```bash
# Search all chats
omni> /search "authentication"
omni> /find "authentication"
omni> /s "authentication"

# Search with results preview
omni> /search "error handling" --preview
omni> /search "error handling" -p

# Search and show match count
omni> /search "database" --count
```

### Filtered Search
```bash
# Search within specific project
omni> /search "bug fix" --project my-webapp
omni> /search "bug fix" -P my-webapp

# Search within specific chat
omni> /search "function name" --chat <chat-id>

# Search by date range
omni> /search "deploy" --from 2024-01-01
omni> /search "deploy" --since "last week"

# Search by provider
omni> /search "prompt" --provider claude
```

### Search Output
```bash
# Show search results with line numbers
omni> /search "TODO" --line-numbers
omni> /search "TODO" -n

# Export search results
omni> /search "API" --export results.txt
omni> /search "API" > results.txt
```

---

## File Operations

### Saving Code
```bash
# Save last code block to file
omni> /save output.py

# Save specific code block (by number)
omni> /save 2 utils.py
omni> /save --block 2 utils.py

# Preview before saving
omni> /save output.py --preview
omni> /save output.py -p

# Save all code blocks from current/last chat
omni> /save-all ./output-dir
omni> /save-all <chat-id> ./output-dir
```

### Exporting Chats
```bash
# Export chat to markdown
omni> /export <chat-id> chat.md
omni> /export <chat-id> --format markdown

# Export to JSON
omni> /export <chat-id> chat.json
omni> /export <chat-id> --format json

# Export entire project
omni> /project export my-webapp ./export-dir
```

---

## General Utilities

### Information & Help
```bash
# Show help
omni> /help
omni> /help search        # Help for specific command
omni> /?                  # Alternative

# Show version
omni> /version

# Show current status
omni> /status
# Output example:
# Current Provider: claude
# Active Chat: my-feature-chat (ID: abc123)
# Active Project: my-webapp
# Installed Providers: claude, openai, grok
# Total Chats: 15 (3 temporary)
# Total Projects: 3
```

### History & Statistics
```bash
# Show recent activity
omni> /history
omni> /recent

# Show usage statistics
omni> /stats
omni> /stats --project my-webapp
```

### Cleanup
```bash
# Clean up expired temporary chats
omni> /cleanup
omni> /clean

# Show what would be deleted (dry run)
omni> /cleanup --dry-run
```

### Session Management
```bash
# Exit omni session (return to shell)
omni> /exit
omni> /quit
omni> /q

# Clear screen
omni> /clear
```

---

## Available Commands (Auto-Complete)

When you type `/` in omni, all available commands appear. Here's the full list:

### P0 (MVP) Commands
```bash
# Chat & Provider
/new, /chat, /temp         # Create chats
/resume, /use              # Resume/switch
/list, /ls                 # List chats
/delete, /rm               # Delete chat
/rename                    # Rename chat

# Project
/project, /proj, /p        # Project commands
  new, list, delete, add, remove, chats, use, export

# Search & Discovery
/search, /find, /s         # Search chats

# Files
/save, /save-all           # Save code blocks
/export                    # Export chats
/context                   # Manage context files

# Configuration
/config                    # Configure omni
/providers                 # List providers

# Utilities
/help, /?                  # Help
/status                    # Current status
/history, /recent          # Activity
/stats                     # Statistics
/cleanup, /clean           # Clean temp chats
/clear                     # Clear screen
/exit, /quit, /q           # Exit
```

---

## Example Workflows

### Workflow 1: First Time Setup
```bash
$ omni init
# Detects installed CLIs, sets up config

$ omni
omni> /status
# Shows: Current Provider: claude
#        Installed Providers: claude, openai, grok
#        Total Chats: 0
```

### Workflow 2: Quick Question
```bash
$ omni
omni> how do I reverse a string in python?
# Gets response from default provider
omni> /exit
```

### Workflow 3: Development Session with Project
```bash
$ omni
omni> /project new my-api
omni> /new user-auth --project my-api --provider claude

# Chat about authentication
omni> how do I implement JWT authentication?
omni> can you show me an example with refresh tokens?
omni> /save auth.py

# Later, search across project
omni> /search "authentication" --project my-api

# Resume previous chat
omni> /resume user-auth
omni> let's add rate limiting to the auth endpoint
omni> /save rate-limiter.py

omni> /exit
```

### Workflow 4: Code Review with Temporary Chat
```bash
$ omni
omni> /temp code-review --ttl 3d
omni> /context add ./src/app.py
omni> review this code for security issues
omni> /save security-fixes.md
omni> /exit
# Chat auto-deletes after 3 days
```

### Workflow 5: Multi-Provider Comparison
```bash
$ omni
omni> /use claude
omni> what's the best way to handle state in React?
# Get Claude's response

omni> /use openai
omni> what's the best way to handle state in React?
# Get OpenAI's response

omni> /use grok
omni> what's the best way to handle state in React?
# Get Grok's response

# Compare all responses
omni> /exit
```

### Workflow 6: Managing Multiple Chats
```bash
$ omni
omni> /list
# Shows all chats

omni> /new backend-refactor --provider claude
omni> help me refactor this API
omni> /save refactor-plan.md

# Switch to different chat
omni> /new frontend-bug --provider openai
omni> I have a React rendering issue
omni> /save bug-fix.js

# Resume first chat
omni> /resume backend-refactor
omni> continue with the refactoring plan

omni> /exit
```

---

## Day-to-Day Usage Patterns

### Pattern 1: Starting Your First Chat
```bash
$ omni
# First time - just start typing
omni> how do I implement OAuth in Node.js?
# Conversation happens...
# Auto-saved as unnamed chat

# Give it a name for later
omni> /rename oauth-implementation

# Or create a named chat from the start
omni> /new oauth-research
omni> what are the different OAuth flows?
```

### Pattern 2: Resuming Previous Chats
```bash
$ omni
omni> /list
# Output:
# ID      Name                  Provider  Messages  Last Activity
# -------------------------------------------------------------------
# a1b2    oauth-implementation  claude    12        2 hours ago
# c3d4    debugging-session     openai    5         yesterday
# e5f6    code-review          claude    20        3 days ago

# Resume by name
omni> /resume oauth-implementation
omni> let's continue - how do I handle refresh tokens?

# Or resume by ID
omni> /resume a1b2

# Resume last active chat
omni> /resume
```

### Pattern 3: Working with Multiple Chats in One Session
```bash
$ omni

# Start first chat
omni> /new backend-api
omni> help me design a REST API for user management
omni> /save api-design.md

# Start a second chat (first one auto-saves)
omni> /new frontend-components
omni> how do I create a reusable button component in React?
omni> /save Button.jsx

# Go back to first chat
omni> /resume backend-api
omni> let's add authentication endpoints
omni> /save auth-endpoints.md

# List all active chats
omni> /list

# Switch between them
omni> /resume frontend-components
omni> now let's add TypeScript types
```

### Pattern 4: Working Within a Project/Folder
```bash
$ omni

# Create project for your work
omni> /project new my-saas-app

# Create chats within this project
omni> /new database-design --project my-saas-app
omni> help me design a PostgreSQL schema for multi-tenant app
omni> /save schema.sql

omni> /new api-routes --project my-saas-app
omni> what API routes do I need for this schema?
omni> /save routes.md

omni> /new frontend-pages --project my-saas-app
omni> what pages does the frontend need?
omni> /save pages-list.md

# List all chats in this project
omni> /project chats my-saas-app
# Output:
# - database-design (15 messages)
# - api-routes (8 messages)
# - frontend-pages (12 messages)

# Search within project only
omni> /search "authentication" --project my-saas-app

# Set as active project (all new chats go here)
omni> /project use my-saas-app
omni> /new deployment-strategy
# Auto-added to my-saas-app project
```

### Pattern 5: Sharing Context Across Different Models
```bash
$ omni

# Start with Claude
omni> /use claude
omni> /new architecture-discussion
omni> I'm building a real-time chat app. What architecture would you suggest?
# Claude gives detailed response about WebSockets, scaling, etc.

# Get OpenAI's perspective on the SAME conversation
omni> /use openai
omni> what do you think about this architecture?
# OpenAI sees the full conversation history and responds

# Try Grok's take
omni> /use grok
omni> any concerns with this approach?
# Grok sees everything and adds its perspective

# All responses are in the SAME chat history
# You can compare different models' answers to the same question
```

### Pattern 6: Quick Question vs Long Research Session
```bash
# Quick question (temporary chat, auto-deletes in 7 days)
$ omni
omni> /temp
omni> what's the syntax for array map in JavaScript?
# Gets answer
omni> /exit
# Chat auto-deletes after 7 days

# Long research session (permanent, organized)
$ omni
omni> /project new learning-rust
omni> /new rust-basics --project learning-rust
omni> explain ownership in Rust
omni> can you give me examples?
omni> /save ownership-examples.rs

omni> /new rust-async --project learning-rust
omni> how does async work in Rust?
omni> /save async-examples.rs

# Later, search all your Rust learning
omni> /search "async" --project learning-rust
```

### Pattern 7: Context-Aware Development
```bash
$ cd ~/my-project
$ omni

# Add project files as context
omni> /context add ./src/app.py
omni> /context add ./src/utils.py
omni> review this code for bugs

# Context persists in the session
omni> now help me refactor the database queries
# AI knows about your files

# Save suggested changes
omni> /save refactored-queries.py

# Start new chat with same context
omni> /new testing --context ./src/app.py
omni> write unit tests for this file
omni> /save test_app.py
```

### Pattern 8: Daily Development Workflow
```bash
# Morning - Resume where you left off
$ omni
omni> /resume
# Continues yesterday's chat
omni> let's implement the feature we discussed

# Need to check something else quickly
omni> /new quick-question
omni> how do I merge two dictionaries in Python?
# Gets answer

# Back to main work
omni> /resume my-feature-work
omni> /save feature.py

# Afternoon - Code review
omni> /temp code-review --ttl 1d
omni> /context add ./pull-request-diff.txt
omni> review this PR for issues
omni> /save review-comments.md
omni> /exit
# Temp chat auto-deletes tomorrow

# Evening - Check what you worked on today
omni> /history
# Shows all today's activity
```

### Pattern 9: Cross-Project Search
```bash
$ omni

# You have multiple projects
omni> /project list
# my-saas-app (15 chats)
# learning-rust (8 chats)
# blog-website (5 chats)

# Search across ALL chats
omni> /search "authentication"
# Finds: oauth-implementation, api-security, rust-auth-example

# Search in specific project
omni> /search "database" --project my-saas-app

# Search by provider
omni> /search "performance" --provider claude

# Search by date
omni> /search "bug fix" --since "last week"
```

### Pattern 10: Iterating with Different Models
```bash
$ omni
omni> /new algorithm-optimization

# Ask Claude for initial approach
omni> /use claude
omni> I need to optimize this sorting algorithm. Here's the code...
# Claude suggests approach A

# Get GPT's opinion
omni> /use openai
omni> the previous suggestion was approach A. Any alternatives?
# GPT suggests approach B

# Try Grok
omni> /use grok
omni> we have approach A and B. Which is better for large datasets?
# Grok compares both

# Implement the best one
omni> /save optimized-sort.py

# All responses saved in one chat - you have a complete discussion log
```

---

## Common Use Cases

### Use Case 1: Learning New Technology
**Goal:** Learn Rust while maintaining organized notes
```bash
$ omni
omni> /project new learning-rust
omni> /project use learning-rust

# Day 1
omni> /new basics
omni> explain Rust ownership
omni> /save day1-notes.md

# Day 2
omni> /new borrowing
omni> explain borrowing and lifetimes
omni> /save day2-notes.md

# Day 5 - Need to recall something
omni> /search "ownership" --project learning-rust
# Finds your Day 1 conversation

# Week later - compare what different AIs say
omni> /new ownership-deep-dive
omni> /use claude
omni> explain ownership edge cases
omni> /use openai
omni> same question - explain ownership edge cases
# Compare both explanations
```

### Use Case 2: Debugging Production Issue
**Goal:** Quick debugging session with context
```bash
$ omni
omni> /temp production-bug --ttl 2d
omni> /context add ./logs/error.log
omni> /context add ./src/api.py

omni> I'm getting this error: [paste error]
omni> /save investigation-notes.md

# Try different AI perspectives
omni> /use claude
omni> what could cause this?

omni> /use openai
omni> any other possibilities?

omni> /save solution.md
# Chat deletes after 2 days (keep your chats clean)
```

### Use Case 3: Building a Feature
**Goal:** Full feature development with organized conversations
```bash
$ omni
omni> /project new payment-integration

# Planning
omni> /new planning --project payment-integration
omni> I need to integrate Stripe. What's the architecture?
omni> /save architecture.md

# Implementation
omni> /new stripe-api --project payment-integration
omni> show me Stripe checkout implementation
omni> /save checkout.js

omni> /new webhooks --project payment-integration
omni> how do I handle Stripe webhooks?
omni> /save webhook-handler.js

# Testing
omni> /new testing --project payment-integration
omni> /context add ./src/checkout.js
omni> write tests for this
omni> /save checkout.test.js

# Later - find specific discussion
omni> /search "webhook" --project payment-integration
```

### Use Case 4: Code Review & Refactoring
**Goal:** Get AI assistance for code review
```bash
$ omni
omni> /new refactor-user-service
omni> /context add ./src/services/user.js

omni> review this code for improvements
omni> /save review-notes.md

# Get multiple perspectives
omni> /use claude
omni> suggest refactoring for better performance

omni> /use openai
omni> suggest refactoring for better readability

# Compare suggestions and implement
omni> /save refactored-user-service.js
```

### Use Case 5: Research & Comparison
**Goal:** Research different approaches with full history
```bash
$ omni
omni> /new database-comparison

omni> /use claude
omni> compare PostgreSQL vs MongoDB for e-commerce

omni> /use openai
omni> same question - PostgreSQL vs MongoDB for e-commerce

omni> /use grok
omni> which is better for high-traffic e-commerce: Postgres or Mongo?

# All answers in one chat - easy to compare
omni> /save database-research.md
omni> /export database-comparison database-comparison.json
# Share with team
```

---

## Environment Variables

Optional environment variables:

```bash
# Set default provider
export OMNI_DEFAULT_PROVIDER=claude

# Set storage location
export OMNI_STORAGE_PATH=~/.omni

# Disable auto-save
export OMNI_AUTO_SAVE=false

# Set default TTL for temp chats (in hours)
export OMNI_TEMP_TTL=168  # 7 days

# Theme
export OMNI_THEME=dark
```

**Note:** API keys are managed by the individual CLI tools (Claude CLI, OpenAI CLI, etc.), not by omni.

---

## Configuration File

Located at `~/.omni/config.yaml`:

```yaml
default_provider: claude
storage_path: ~/.omni/data
auto_save: true
theme: dark
temp_ttl_hours: 168  # 7 days

providers:
  claude:
    cli_command: claude
    installed: true
  openai:
    cli_command: openai
    installed: true
  grok:
    cli_command: grok
    installed: false

# P1 features (not in MVP)
# templates:
#   - name: code-review
#     prompt: "Review this code for..."
```

---

## Command Syntax Patterns

Inside omni session:

```bash
# Pattern 1: Natural language = chat with AI
omni> how do I implement authentication?
omni> explain this error message
omni> write a function to parse JSON

# Pattern 2: Commands start with /
omni> /new <name>           # Create chat
omni> /list                 # List chats
omni> /search "query"       # Search

# Pattern 3: Resource + Action (with /)
omni> /project new <name>
omni> /project delete <name>
omni> /chat my-feature

# Pattern 4: Provider switching
omni> /use claude           # Switch to Claude
omni> /use openai           # Switch to OpenAI

# Pattern 5: Options/Flags (with /)
omni> /new --provider openai
omni> /list --project my-webapp
omni> /search "query" --preview
```

---

## Exit Codes

```bash
0   # Success
1   # General error
2   # Configuration error (provider not installed, etc.)
3   # Provider error (underlying CLI failed, etc.)
4   # Not found (chat/project doesn't exist)
5   # Invalid input
```

---

## Notes

- **Default behavior**: Typing without `/` = chatting with AI
- **Commands**: All built-in commands start with `/`
- **Auto-complete**: Type `/` to see all available commands
- **Help**: All commands support `--help` (e.g., `/search --help`)
- **Names with spaces**: Use quotes (e.g., `/new "my feature chat"`)
- **IDs vs names**: IDs can be used instead of names for precision
- **Aliases**: Most commands have short aliases (e.g., `/ls` = `/list`)
- **Tab completion**: Available for bash, zsh, fish (P1 feature)
- **API management**: API keys are managed by underlying CLI tools (Claude CLI, OpenAI CLI, etc.), not by omni

---

## Philosophy

**omni** is a wrapper over all popular AI models (Claude, ChatGPT, Grok, etc.) that lets you:
- **Access any model from your CLI** - No switching between different tools
- **Maintain persistent memory** - All conversations are saved and searchable
- **Share context across models** - Ask Claude, then ask the same thing to ChatGPT with full context
- **Organize your work** - Projects, search, tags - your AI conversations become a knowledge base
- **Work from the terminal** - Stay in your developer flow

**Core principles:**
- **Natural**: Just type to chat, use `/commands` when you need features
- **Fast**: Short commands, aliases, auto-complete
- **Unified**: One interface for all AI providers
- **Persistent**: Every conversation is saved automatically
- **Portable**: Share chat history across different AI models seamlessly
