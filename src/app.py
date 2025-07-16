from fastapi import FastAPI, Request
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from tools import mcp
import os
from dotenv import load_dotenv

load_dotenv()
title = os.getenv("MCP_SERVER_NAME")
description = os.getenv("MCP_SERVER_DESCRIPTION")
version = os.getenv("MCP_SERVER_VERSION")

# Create FastAPI application with metadata
app = FastAPI(
    title=title,
    description=description,
    version=version,
)

# Create SSE transport instance for handling server-sent events
sse = SseServerTransport("/messages/")

# Mount the /messages path to handle SSE message posting
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))

# Add documentation for the /messages endpoint
@app.get("/messages", tags=["MCP"], include_in_schema=True)
def messages_docs():
    """
    Messages endpoint for SSE communication

    This endpoint is used for posting messages to SSE clients.
    Note: This route is for documentation purposes only.
    The actual implementation is handled by the SSE transport.
    """
    pass  # This is just for documentation, the actual handler is mounted above


@app.get("/sse", tags=["MCP"])
async def handle_sse(request: Request):
    """
    SSE endpoint that connects to the MCP server

    This endpoint establishes a Server-Sent Events connection with the client
    and forwards communication to the Model Context Protocol server.
    """
    # Use sse.connect_sse to establish an SSE connection with the MCP server
    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        # Run the MCP server with the established streams
        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            mcp._mcp_server.create_initialization_options(),
        )


# Import routes at the end to avoid circular imports
# This ensures all routes are registered to the app
import routes  # noqa
