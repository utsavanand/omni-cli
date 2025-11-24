# AI CLI Wrapper - Requirements Document

## Project Overview
A unified CLI tool that provides a consistent interface to interact with multiple AI CLI tools (Claude CLI, Codex CLI, etc.) with enhanced features for chat management, project organization, and workflow optimization.

## Priority Levels
- **P0**: Must have for MVP - core functionality
- **P1**: Should have for early releases - important features
- **P2**: Nice to have - future enhancements

## MVP (P0) Feature Summary
For quick reference, here are the must-have features for v1.0:
- Support Claude CLI and Codex/OpenAI CLI with unified interface
- Create, list, resume, and delete permanent and temporary chats
- Basic project management (create, list, add/remove chats)
- Full-text search with project filtering and context preview
- Extract code snippets and create files from AI responses
- Secure API key storage and basic configuration
- Interactive mode with syntax highlighting and multi-line input
- Help system and basic documentation

## Core Requirements

### 1. Multi-CLI Integration
- **[P0] REQ-1.1**: Support Claude CLI as a backend AI provider
- **[P0] REQ-1.2**: Support Codex/OpenAI CLI as a backend AI provider
- **[P0] REQ-1.3**: Provide unified command interface regardless of backend
- **[P1] REQ-1.4**: Allow easy switching between AI providers mid-conversation
- **[P1] REQ-1.5**: Support fallback providers if primary is unavailable
- **[P1] REQ-1.6**: Auto-detect installed AI CLI tools
- **[P2] REQ-1.7**: Support custom AI CLI integrations via plugin system

### 2. Chat Management
- **[P0] REQ-2.1**: Create new chat sessions with descriptive names
- **[P0] REQ-2.2**: Support temporary chats (auto-delete after configurable time period, default 7 days)
- **[P0] REQ-2.3**: Support permanent chats (saved to disk)
- **[P0] REQ-2.4**: List all saved chats with metadata (date, provider, message count)
- **[P0] REQ-2.5**: Resume previous chat sessions
- **[P0] REQ-2.6**: Delete old chats
- **[P0] REQ-2.7**: Auto-generate chat names from first user message (max 3-4 words) if not provided
- **[P0] REQ-2.8**: Create chat file immediately when conversation starts
- **[P0] REQ-2.9**: Continuously append to chat file as conversation progresses
- **[P1] REQ-2.10**: Rename chat sessions
- **[P1] REQ-2.11**: Export chats to markdown and JSON
- **[P1] REQ-2.12**: Archive chats
- **[P2] REQ-2.13**: Import conversations from other tools
- **[P2] REQ-2.14**: Fork/branch conversations at any point
- **[P2] REQ-2.15**: Merge conversation branches
- **[P2] REQ-2.16**: Export to HTML, PDF formats

### 3. Project Organization
- **[P0] REQ-3.1**: Create projects to group related chats
- **[P0] REQ-3.2**: Add/remove chats to/from projects
- **[P0] REQ-3.3**: List all projects with basic info
- **[P1] REQ-3.4**: List projects with statistics (chat count, last activity)
- **[P1] REQ-3.5**: Archive/restore projects
- **[P1] REQ-3.6**: Export entire projects with all chats
- **[P1] REQ-3.7**: Attach context files/folders to projects
- **[P2] REQ-3.8**: Share project templates
- **[P2] REQ-3.9**: Auto-include project context in all project chats
- **[P2] REQ-3.10**: Tag projects with categories/labels
- **[P2] REQ-3.11**: Set project-specific AI provider defaults

### 4. Search & Discovery
- **[P0] REQ-4.1**: Full-text search across all chat history
- **[P0] REQ-4.2**: Filter search by project
- **[P0] REQ-4.3**: Display search results with context preview
- **[P1] REQ-4.4**: Filter search by date range
- **[P1] REQ-4.5**: Filter search by AI provider
- **[P1] REQ-4.6**: Search within specific chat
- **[P2] REQ-4.7**: Search by tags/labels
- **[P2] REQ-4.8**: Regex support in search
- **[P2] REQ-4.9**: Jump to search result in original chat
- **[P2] REQ-4.10**: Save search queries for reuse

### 5. File Generation & Management
- **[P0] REQ-5.1**: Extract code snippets to files directly from chat
- **[P0] REQ-5.2**: Create files with content from AI responses
- **[P1] REQ-5.3**: Auto-detect programming language for syntax highlighting
- **[P1] REQ-5.4**: Update existing files based on chat suggestions
- **[P1] REQ-5.5**: Show diffs before applying file changes
- **[P1] REQ-5.6**: Batch create multiple files from single conversation
- **[P2] REQ-5.7**: Undo file operations
- **[P2] REQ-5.8**: Generate project scaffolding from chat
- **[P2] REQ-5.9**: Export conversation as executable script
- **[P2] REQ-5.10**: Version control integration (git commit with context)

### 6. Configuration & Settings
- **[P0] REQ-6.1**: Store API keys securely
- **[P0] REQ-6.2**: Configure default AI provider
- **[P0] REQ-6.3**: Configure storage location for chats
- **[P1] REQ-6.4**: Set per-project configurations
- **[P1] REQ-6.5**: Set default models/parameters per provider
- **[P1] REQ-6.6**: Customize output formatting
- **[P2] REQ-6.7**: Create configuration profiles (work, personal, etc.)
- **[P2] REQ-6.8**: Import/export configuration
- **[P2] REQ-6.9**: Set cost limits and alerts
- **[P2] REQ-6.10**: Configure keyboard shortcuts

### 7. User Experience
- **[P0] REQ-7.1**: Interactive mode with basic formatting
- **[P0] REQ-7.2**: Syntax highlighting for code blocks
- **[P0] REQ-7.3**: Multi-line input support
- **[P0] REQ-7.4**: Help system with examples
- **[P1] REQ-7.5**: Auto-completion for commands
- **[P1] REQ-7.6**: Command history with search
- **[P1] REQ-7.7**: Streaming responses from AI
- **[P1] REQ-7.8**: Colored output with themes
- **[P2] REQ-7.9**: Progress indicators for long operations
- **[P2] REQ-7.10**: Vim/Emacs keybindings option
- **[P2] REQ-7.11**: Shell completion (bash, zsh, fish)
- **[P2] REQ-7.12**: Notifications for long-running operations

### 8. Analytics & Insights
- **[P1] REQ-8.1**: Track token/cost usage per chat
- **[P1] REQ-8.2**: Track token/cost usage per project
- **[P2] REQ-8.3**: Display usage statistics and trends
- **[P2] REQ-8.4**: Export usage reports
- **[P2] REQ-8.5**: Show most active projects/chats
- **[P2] REQ-8.6**: Track response times per provider
- **[P2] REQ-8.7**: Compare provider performance
- **[P2] REQ-8.8**: Set budget alerts

### 9. Advanced Features
- **[P1] REQ-9.1**: Templates for common prompts
- **[P1] REQ-9.2**: Pipe input/output to other CLI tools
- **[P2] REQ-9.3**: Macro/script support for automated workflows
- **[P2] REQ-9.4**: Run commands from chat responses
- **[P2] REQ-9.5**: Scheduled chats (cron-like)
- **[P2] REQ-9.6**: Watch mode (monitor files and ask AI about changes)
- **[P2] REQ-9.7**: Collaborative chats (shared sessions)
- **[P2] REQ-9.8**: Context-aware suggestions
- **[P2] REQ-9.9**: Local caching for faster responses
- **[P2] REQ-9.10**: Offline mode with cached responses

### 10. Security & Privacy
- **[P0] REQ-10.1**: Secure credential storage (keyring integration)
- **[P1] REQ-10.2**: Configurable data retention policies
- **[P2] REQ-10.3**: Encrypt stored chat history
- **[P2] REQ-10.4**: Support for local LLMs (no API calls)
- **[P2] REQ-10.5**: Redact sensitive information before sending
- **[P2] REQ-10.6**: Audit log of all operations
- **[P2] REQ-10.7**: Option to disable telemetry completely

## Use Cases

### UC-1: Quick One-off Question
**Actor**: Developer
**Flow**:
1. Run `ai chat "explain this error"` with temporary chat
2. Get response
3. Chat auto-deletes after session

### UC-2: Long-running Project Development
**Actor**: Developer
**Flow**:
1. Create project `ai project create my-webapp`
2. Create multiple chats within project for different features
3. Attach project codebase as context
4. Search across all project chats for previous solutions
5. Generate files directly from conversations
6. Track token usage for budgeting

### UC-3: Research & Documentation
**Actor**: Technical Writer
**Flow**:
1. Create research project
2. Have multiple conversations exploring topics
3. Tag conversations by category
4. Search across all research
5. Export consolidated markdown documentation

### UC-4: Code Review Assistant
**Actor**: Developer
**Flow**:
1. Start chat with current git diff as context
2. Ask AI for review suggestions
3. Apply suggested changes with preview
4. Commit with AI-generated commit message

### UC-5: Learning & Experimentation
**Actor**: Student
**Flow**:
1. Create learning project for a new language
2. Have conversations about concepts
3. Fork conversations to try different approaches
4. Search previous learnings
5. Export study notes

### UC-6: Multi-Provider Comparison
**Actor**: Power User
**Flow**:
1. Start chat with Claude
2. Switch to GPT-4 mid-conversation
3. Compare responses from both
4. Track which provider gives better results

### UC-7: Automated Workflow
**Actor**: DevOps Engineer
**Flow**:
1. Create template for deployment questions
2. Schedule recurring chats for health checks
3. Pipe output to monitoring tools
4. Get notifications on issues

## Non-Functional Requirements

### NFR-1: Performance
- Response time < 100ms for local operations
- Search across 10k messages in < 2 seconds
- Startup time < 500ms

### NFR-2: Reliability
- No data loss on crashes
- Graceful degradation if provider unavailable
- Atomic file operations

### NFR-3: Usability
- Zero-config startup for basic features
- Intuitive command structure
- Comprehensive documentation

### NFR-4: Compatibility
- Support Linux, macOS, Windows
- Python 3.9+
- Work in standard terminals and modern terminal emulators

### NFR-5: Maintainability
- Modular architecture
- Plugin system for extensions
- Well-documented code
- Comprehensive test coverage

## Out of Scope (for v1.0)
- Web or GUI interface
- Mobile app
- Voice input/output
- Image generation
- Real-time collaboration/multi-user features
- Built-in AI model training
- Custom fine-tuned models
- Video/audio processing
- Browser extensions

## Success Metrics (MVP)
- User can start first chat in < 60 seconds from install
- User can find previous conversations via search in < 10 seconds
- 80% of users successfully create and manage projects
- File generation works without errors 95% of the time
- Positive feedback on unified interface vs using individual CLIs separately

## Technical Requirements (MVP)

### Platform & Compatibility
- Works on macOS, Linux, Windows
- Python 3.9+
- Compatible with latest Claude CLI and OpenAI CLI versions
- Minimal external dependencies
- Easy installation via pip or similar package manager

### Chat Storage & File Naming
- **Immediate file creation**: Chat file must be created immediately when conversation starts (before first AI response)
- **File naming convention**: `{timestamp}_{chat-name}.md`
  - Timestamp format: `YYYYMMDD-HHMMSS` (e.g., `20250124-143022`)
  - Chat name: User-provided or auto-generated
  - Examples:
    - User-provided: `20250124-143022_my-feature-chat.md`
    - Auto-generated: `20250124-143022_implement-oauth-nodejs.md`
- **Auto-generated names**:
  - Generated from first user message if no name provided
  - Max 3-4 words, kebab-case
  - Remove special characters, keep alphanumeric and hyphens
  - Examples:
    - "How do I implement OAuth in Node.js?" → `implement-oauth-nodejs`
    - "Explain React hooks" → `explain-react-hooks`
    - "What's the best database for my app?" → `best-database-app`
- **Continuous updates**: Append each message to file as conversation progresses
- **File format**: Markdown format with structured sections
  - Metadata header (chat ID, provider, timestamps, etc.)
  - Conversation history (user/assistant messages)
  - Code blocks properly formatted
- **Storage location**: Default `~/.omni/chats/`
  - Temporary chats: `~/.omni/chats/temp/`
  - Permanent chats: `~/.omni/chats/permanent/`
  - Project chats: `~/.omni/projects/{project-name}/chats/`
- **Atomic writes**: Use atomic file operations to prevent corruption
- **Chat ID**: UUID or short hash for unique identification
  - Used in metadata and for programmatic access
  - Example: `a1b2c3d4` or full UUID

### Example Chat File Format
```markdown
---
chat_id: a1b2c3d4
name: implement-oauth-nodejs
provider: claude
created_at: 2025-01-24T14:30:22Z
updated_at: 2025-01-24T14:35:10Z
message_count: 6
project: null
temporary: false
ttl: null
tags: []
---

# Chat: implement-oauth-nodejs

## Message 1 - User (2025-01-24 14:30:22)
How do I implement OAuth in Node.js?

## Message 2 - Assistant (claude) (2025-01-24 14:30:45)
I'll help you implement OAuth in Node.js. Here's a step-by-step guide...

[Response content]

```javascript
const express = require('express');
// ... code example
```

## Message 3 - User (2025-01-24 14:32:10)
Can you show me how to handle refresh tokens?

## Message 4 - Assistant (claude) (2025-01-24 14:32:35)
Sure! Here's how to handle refresh tokens...

[Continue conversation...]
```

### Chat Metadata Index
- **Index file**: `~/.omni/index.json` or similar
- Contains quick lookup for all chats:
  - Chat ID → file path mapping
  - Searchable metadata (name, tags, project, dates)
  - Provider information
  - Message count, last activity
- Updated on every chat modification
- Enables fast `/list` and `/search` operations without reading all files

## License Considerations
**Recommended: MIT License**
- Most permissive and widely adopted
- Allows commercial and private use
- Simple and easy to understand
- Compatible with AI provider terms of service
- Encourages community contributions
- Low friction for adoption

**Alternative: Apache 2.0**
- Includes explicit patent grant
- Better for organizations concerned about patents
- Still very permissive

Both licenses are suitable for this project. MIT is simpler and more common for CLI tools.
