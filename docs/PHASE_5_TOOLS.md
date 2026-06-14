# Phase 5: Tool Calling Framework Architecture

## Architecture Overview

The Tool Calling Framework provides a secure, auditable method for agents to interact with external systems, databases, and computational utilities.

### Core Components:

1. **ToolRegistry (`registry.py`)**:
   * A centralized manager for all available agent tools.
   * Uses a Python decorator (`@tool_registry.register`) to dynamically load tools into the registry.
   * Maintains strict metadata schemas (`name`, `description`, `input_schema`, `permissions`) required for binding tools to LLMs (like Claude's tool_use feature).

2. **Security & Auditing**:
   * **Permissions**: Every tool invocation must be accompanied by a user's capability list (`user_permissions`). If a tool requires `db:read` and the user/agent only has `search:read`, execution is blocked.
   * **Validation**: Inputs are checked against the defined `input_schema` before passing to the function to prevent malformed queries or injection attacks.
   * **Audit Log**: Every tool attempt (success, failure, permission denial) is logged with its timestamp and parameters, satisfying enterprise compliance requirements.

3. **Tool Implementations**:
   * `search_tool`: Web/Internal search (simulated).
   * `calculator_tool`: Mathematical operations.
   * `document_tool`: Reading specific file IDs.
   * `api_tool`: External HTTP requests.
   * `sql_tool`: Read-only database queries.

### Design Decisions:

* **Dynamic Registration**: The decorator pattern means we don't need a massive `switch` statement. Developers can add new tools by simply creating a new file in `app/tools/` and decorating the function.
* **Separation from Agents**: Tools are not tied to specific agents. The Planner agent might use the search tool to find metadata, while the Reasoning agent might use the calculator tool to crunch numbers.
