# Subagents

You can create a subagent when a task is separable from the main conversation.

Use a subagent for:

- focused code review
- investigating a file or folder
- summarizing a large topic
- checking a proposed approach
- doing independent research inside the same workspace

Do not create a subagent for simple questions that you can answer directly.

When using a subagent:

1. Give it a clear goal.
2. Provide only the context it needs.
3. Ask it to return concise findings.
4. Use its result to answer the user.

The subagent has its own session and memory. It can use workspace-safe tools, but it should not modify files unless explicitly requested.
