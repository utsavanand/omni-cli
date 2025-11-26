# TODO - Future Commands

## New Commands to Implement

### `/merge`
- Merge two or more chats together and then summarize them
- Should handle multiple chat files as input
- Generate a combined summary after merging

### `/summarize`
- Summarize a chat and store in separate folder
- Two modes:
  - **Short**: 50-100 word summary
  - **Long**: Detailed summary
- Store summaries in dedicated folder

### `/archive`
- Move chat to archive folder
- Remove from search results
- Keep chat accessible but out of main view

### `/add-note`
- Add manual non-AI notes to chats, projects, or namespaces
- Notes can have a title and content
- Useful for documenting decisions, TODOs, or important information
- Syntax:
  - `/add-note --chat <chat-id> --title "Note Title" --content "Note content"`
  - `/add-note --project <project-id> --title "Project Decision" --content "We decided to..."`
  - `/add-note --namespace <namespace-id> --title "Overview" --content "This namespace contains..."`
- Notes should be stored with timestamps and be viewable/editable
- Consider markdown support for note content

### `/ask`
- Interactive help assistant for omni-cli AND scoped Q&A
- **Two modes:**
  1. **Help mode**: Answer questions about how to use omni-cli
     - `/ask how do I create a namespace?`
     - `/ask what's the difference between projects and namespaces?`
  2. **Scoped Q&A mode**: Ask questions about specific content
     - `/ask --project api-service "what authentication methods did we discuss?"`
     - `/ask --namespace work-projects "what are the common patterns across projects?"`
     - `/ask --chat abc123,def456 "summarize the key decisions from these chats"`
     - `/ask --project webapp,api-service "what dependencies do these projects share?"`
- Only considers the specified scope (chats/projects/namespaces) for answers
- Can accept multiple targets (comma-separated)
- Loads conversation history from specified scope and uses it as context for AI

## Improvements to Existing Commands

### Update `find` command
- Add ability to search only in specific folders/namespaces/projects
- Filter search scope to improve performance and relevance
- Examples:
  - `/find "authentication" --namespace work-projects`
  - `/find "bug fix" --project api-service`
