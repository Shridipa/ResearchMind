# Phase 6: Model Context Protocol (MCP) Architecture

## Architecture Overview

The Model Context Protocol (MCP) acts as the bridge connecting our internal multi-agent framework with external tools, systems, and APIs in a standardized manner. It allows our platform to both expose tools (as a Server) and consume tools (as a Client).

### Core Components

1. **MCP Server (`server/jsonrpc.py`)**:
   * Implements the **JSON-RPC 2.0** specification.
   * Exposes two main methods: `discover_tools` and `call_tool`.
   * Integrates natively with the `ToolRegistry` from Phase 5, automatically converting registered Python functions into MCP-compliant tools with strict permission checks.

2. **MCP Client (`clients/mcp_client.py`)**:
   * Provides an asynchronous interface (via `httpx`) to communicate with external external MCP instances.
   * Agents can use this client to discover capabilities offered by 3rd party providers (e.g., a corporate ERP MCP server) and seamlessly execute them just like local tools.

### Design Decisions

* **JSON-RPC 2.0**: The industry standard for MCP. It allows lightweight, bidirectional communication over standard HTTP or WebSockets.
* **Separation of Protocols**: By wrapping our `ToolRegistry` in the MCP Server, we decouple our internal execution logic from the transport protocol. This means tools can be executed directly in Python memory (by our agents) or over the network (by external consumers) without duplicating the tool logic.
