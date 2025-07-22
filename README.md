# Cardano MCP Server

## Description

This is a FastAPI-based Model Context Protocol (MCP) server that provides comprehensive Cardano blockchain integration. It enables AI assistants and applications to interact with the Cardano blockchain through a standardized interface, offering tools for querying blockchain data, managing wallets, transferring tokens, and more.

## Features

*   **FastAPI framework** with Server-Sent Events (SSE) support
*   **Cardano blockchain integration** via BlockFrost API
*   **Wallet management** - create, load, and manage Cardano wallets
*   **Token operations** - transfer ADA, mint native tokens, burn tokens
*   **Blockchain queries** - get latest blocks, epoch details, transaction history
*   **Network monitoring** - health checks, transaction charts, pool information
*   **UTxO management** - query and manage unspent transaction outputs
*   **Protocol parameter access** - fetch current Cardano protocol parameters

## Environment Variables

This project uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

*   `PROJECT_ID`: Your BlockFrost API project ID (required for Cardano blockchain access)
*   `MCP_SERVER_NAME`: Name of the MCP server (e.g., "cardano-mcp-server")
*   `MCP_SERVER_DESCRIPTION`: Description of the server
*   `MCP_SERVER_VERSION`: Version of the server
*   `HOST`: Host address (default: "0.0.0.0")
*   `PORT`: Port number (default: 3001)
*   `BASE_UPLOAD_DIR`: Directory for storing wallet files (optional)

## Setup

This project uses `uv` for dependency management and virtual environments, which is highly recommended for its speed and efficiency. You can find installation instructions [here](https://github.com/astral-sh/uv#installation).

1. Clone the repository.
2. Ensure you have Python 3.13+ installed.
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

5. Create a `.env` file with your BlockFrost API credentials:

   ```bash
   PROJECT_ID=your_blockfrost_project_id
   MCP_SERVER_NAME=cardano-mcp-server
   MCP_SERVER_DESCRIPTION=Cardano blockchain MCP server
   MCP_SERVER_VERSION=0.1.0
   HOST=0.0.0.0
   PORT=8004
   BASE_UPLOAD_DIR="../upload"
   ```

## Running the Project

1. Navigate to the project directory.
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

*   **SSE endpoint:** `http://localhost:3001/sse`
*   **Message posting:** `http://localhost:3001/messages/`
*   **Status API:** `http://localhost:3001/status`
*   **Wallet creation:** `http://localhost:3001/create-wallet/{walletId}`
*   **File download:** `http://localhost:3001/files/{walletId}/{filename}`

## Available MCP Tools

The server provides the following Cardano-specific tools:

### Blockchain Information
*   `block_latest` - Get the latest block information
*   `epoch_details` - Get current epoch details
*   `recent_blocks` - Get recent blocks (default 10)
*   `block_transactions` - Get transactions for the latest block
*   `pool_info` - Get pool information for the latest block
*   `chart_transactions` - Get transaction counts grouped by date
*   `network_health_check` - Check BlockFrost API health
*   `get_blockchain_tip` - Fetch latest blockchain tip information

### Wallet Management
*   `derive_addresses` - Derive base, enterprise, and stake addresses
*   `get_wallet_balance` - Get wallet balance with token details
*   `query_utxos` - Query UTxOs at a given Cardano address

### Token Operations
*   `transfer_token` - Transfer ADA from sender to receiver address
*   `mint_native_token` - Mint a new native token using a simple policy
*   `burn_token` - Burn tokens by including negative output

### Transaction & Protocol
*   `get_transaction_details` - Fetch details of a transaction using its hash
*   `get_protocol_params` - Fetch protocol parameters from the Cardano blockchain

## Custom Tools

To add your own custom tools for use with the application or related development workflows, you can define them in the `src/tools.py` file. Follow the existing structure for defining and exporting tools using the `@mcp.tool` decorator.

## Dependencies

*   **blockfrost-python** - Cardano blockchain API client
*   **pycardano** - Cardano blockchain library for Python
*   **fastapi** - Modern web framework for building APIs
*   **mcp** - Model Context Protocol implementation
*   **uvicorn** - ASGI server for running FastAPI applications

## Network Configuration

The server is configured to work with Cardano testnet by default. To switch to mainnet, modify the `network` variable in `src/tools.py`:

```python
network = Network.MAINNET  # For mainnet
network = Network.TESTNET  # For testnet (default)
```

## Security Notes

*   Wallet keys are stored locally in the specified upload directory
*   Ensure proper file permissions for wallet key files
*   Use environment variables for sensitive configuration
*   The server runs on testnet by default - be careful when switching to mainnet 