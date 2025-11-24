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

### `/delete`
- Delete a chat entirely
- Should include confirmation prompt
- Permanent deletion (consider trash/recovery option)

## Improvements to Existing Commands

### Update `find` command
- Add ability to search only in specific folders
- Filter search scope to improve performance and relevance

### Update `/resume` command
- Show folders first in search results
- Then show chats inside each folder
- Hierarchical display for better navigation
