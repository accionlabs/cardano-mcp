# FastAPI MCP SSE Project

## Description

This is a Boilerplate FastAPI application with Server-Sent Events (SSE). It is part of a larger project (MCP) and includes integrations with external services.

## Environment Variables

This project uses environment variables for configuration. Create a `.env` file in the root directory of the project to set these variables. A `.env.example` file might be available as a template, or you may need to add variables such as:

*   `PORT`: The port the FastAPI application will run on (default is likely 8000).
*   Any API keys or credentials required for integrations (e.g., Jira, PlanetX).

## Setup

This project uses `uv` for dependency management and virtual environments, which is highly recommended for its speed and efficiency. You can find installation instructions [here](https://github.com/astral-sh/uv#installation).

1. Clone the repository.
2. Ensure you have Python installed.
3. Create and activate a virtual environment using uv:

   ```bash
   uv venv
   ```
   ###### Use source for Unix-like shells
   ```bash
   source .venv/bin/activate 
   ```
   ###### For Windows, use 
   ```bash
   .venv\Scripts\activate
   ```

4. Install dependencies using uv:

   ```bash
   uv pip install -r pyproject.toml
   ```

## Running the Project

1. Navigate to the project directory.a
2. Activate the virtual environment (if not already active):

   ###### Use source for Unix-like shells
   ```bash
   source .venv/bin/activate 
   ```
   ###### For Windows, use
   ```bash
   .venv\Scripts\activate
   ```

3. Run the FastAPI application using one of the following commands:

   ```bash
   python src/server.py
   ```
   ###### OR
   ```bash
   uv run start
   ```

### Endpoints

*   **SSE endpoint:** `http://localhost:8000/sse`
*   **Message posting:** `http://localhost:8000/messages/`
*   **Status API:** `http://localhost:8000/status`

## Custom Tools

To add your own custom tools for use with the application or related development workflows, you can define them in the `src/tools.py` file. Follow the existing structure for defining and exporting tools.

## Features

*   FastAPI framework
*   Server-Sent Events (SSE)
*   (Potentially) Integration with external APIs like Jira MCP or PlanetX Translator. 