from typing import Any
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
from utils import load_saved_policy_script, load_or_create_key_pair, get_wallet_file_paths
from blockfrost import BlockFrostApi, ApiError, ApiUrls
from typing import Dict, List, Union
from pycardano import (
    Address, TransactionBuilder, TransactionOutput, Value, Transaction,
    BlockFrostChainContext, Network, ScriptPubkey, ScriptAll, Asset,
    AssetName, MultiAsset, PaymentSigningKey, PaymentVerificationKey
)
from fractions import Fraction
from datetime import datetime, timedelta
import time

load_dotenv()

project_id = os.getenv("PROJECT_ID") or ""
mcp_server_name = os.getenv("MCP_SERVER_NAME") or ""
BASE_URL: str = ApiUrls.preview.value or ""
network = Network.TESTNET

mcp = FastMCP(mcp_server_name)
blockFrostApi: BlockFrostApi = BlockFrostApi(project_id=project_id, base_url=BASE_URL)
context = BlockFrostChainContext(project_id, base_url=BASE_URL)    


@mcp.tool(name="block_latest", description="Get latest block")
def block_latest() -> dict:
    try:
        latest_block = blockFrostApi.block_latest()
        block = latest_block if isinstance(latest_block, dict) else latest_block.__dict__
        return {
            "slot": block.get("slot"),
            "epoch": block.get("epoch"),
            "height": block.get("height"),
            "hash": block.get("hash")
        }
    except ApiError as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool(name="epoch_details", description="Get current epoch details")
def epoch_details() -> dict:
    try:
        latest_block = blockFrostApi.block_latest()
        block = latest_block if isinstance(latest_block, dict) else latest_block.__dict__
        epoch_num = block.get("epoch")
        if epoch_num is None:
            return {"status": "error", "message": "Could not determine epoch from latest block."}
        epoch = blockFrostApi.epoch(int(epoch_num))
        epoch_data = epoch if isinstance(epoch, dict) else epoch.__dict__
        return {
            "epoch": epoch_data.get("epoch"),
            "start_time": epoch_data.get("start_time"),
            "end_time": epoch_data.get("end_time"),
            "first_block_time": epoch_data.get("first_block_time"),
            "last_block_time": epoch_data.get("last_block_time"),
            "block_count": epoch_data.get("block_count"),
            "tx_count": epoch_data.get("tx_count")
        }
    except ApiError as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool(name="recent_blocks", description="Get recent n blocks (default 10)")
def recent_blocks(count: int=10) -> dict:
    try:
        latest_block = blockFrostApi.block_latest()
        block = latest_block if isinstance(latest_block, dict) else latest_block.__dict__
        blocks = [block]
        current_hash = block.get("hash")
        for _ in range(count - 1):
            if not current_hash:
                break
            prev_blocks = blockFrostApi.blocks_previous(current_hash, count=1)
            if not prev_blocks:
                break
            prev_block = prev_blocks[0]
            prev_block_dict = prev_block if isinstance(prev_block, dict) else prev_block.__dict__
            blocks.append(prev_block_dict)
            current_hash = prev_block_dict.get("hash")
        return {
            "blocks": [
                {
                    "height": b.get("height"),
                    "epoch": b.get("epoch"),
                    "slot": b.get("slot"),
                    "hash": b.get("hash"),
                    "pool": b.get("pool")
                }
                for b in blocks
            ]
        }
    except ApiError as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool(name="block_transactions", description="Get transactions for latest block (default 10)")
def block_transactions(count: int=10) -> dict:
    try:
        latest_block = blockFrostApi.block_latest()
        block = latest_block if isinstance(latest_block, dict) else latest_block.__dict__
        block_hash = block.get("hash")
        if not block_hash:
            return {"status": "error", "message": "Could not determine block hash from latest block."}
        transactions = blockFrostApi.block_transactions(block_hash, count=10)
        return {
            "block_hash": block_hash,
            "transactions": transactions
        }
    except ApiError as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool(name="pool_info", description="Get pool info for latest block if available")
def pool_info() -> dict:
    try:
        latest_block = blockFrostApi.block_latest()
        block = latest_block if isinstance(latest_block, dict) else latest_block.__dict__
        pool_id = block.get("pool")
        if not pool_id:
            return {"message": "No pool information for latest block"}

        pool = blockFrostApi.pool(pool_id)
        pool_data = pool if isinstance(pool, dict) else pool.__dict__
        return {
            "pool_id": pool_data.get("pool_id"),
            "hex": pool_data.get("hex"),
            "vrf_key": pool_data.get("vrf_key"),
            "live_stake": pool_data.get("live_stake"),
            "live_saturation": pool_data.get("live_saturation")
        }
    except ApiError as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool(name="chart_transactions", description="Get transaction counts grouped by date for past N days (default 15)")
def chart_transactions(days: int = 15) -> dict:
    try:
        end_time = int(time.time())
        start_time = end_time - (days * 24 * 60 * 60)  # N days ago

        transactions_per_day = {}

        latest_block = blockFrostApi.block_latest()
        current_block = latest_block if isinstance(latest_block, dict) else latest_block.__dict__

        while True:
            block_time = current_block.get("time")
            block_hash = current_block.get("hash")
            if block_time is None or block_hash is None or block_time <= start_time:
                break
            block = blockFrostApi.block(block_hash)
            block_data = block if isinstance(block, dict) else block.__dict__
            block_date = block_data.get("time")
            if block_date is None:
                break
            block_date_str = datetime.utcfromtimestamp(block_date).strftime("%Y-%m-%d")
            transactions_per_day[block_date_str] = transactions_per_day.get(block_date_str, 0) + block_data.get("tx_count", 0)

            prev_block_hash = block_data.get("previous_block")
            if not prev_block_hash:
                break  # Genesis block reached

            prev_block = blockFrostApi.block(prev_block_hash)
            current_block = prev_block if isinstance(prev_block, dict) else prev_block.__dict__

        # Fill missing dates with 0
        date_cursor = datetime.utcnow() - timedelta(days=days - 1)
        for i in range(days):
            date_str = date_cursor.strftime("%Y-%m-%d")
            transactions_per_day.setdefault(date_str, 0)
            date_cursor += timedelta(days=1)

        # Sort results by date
        sorted_data = dict(sorted(transactions_per_day.items()))

        return {
            "transactions_chart": sorted_data
        }

    except ApiError as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool(name="network_health_check", description="Check Health Of Network") #working
def check_api_health() -> Dict[str, Union[str, Any]]:
    """
    Check Blockfrost API health.

    Returns:
        dict: Dictionary with health status or error info
    """
    try:
        health_response = blockFrostApi.health(return_type='json')  # type: ignore
        return {
            "status": "ok",
            "health_json": health_response
        }
    except ApiError as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool(name="transfer_token", description="Transfer Tokens from sender to reciver address") #working
def transfer_token(
    receiver_addr_str: str,
    amount: int,
    walletId: str,
) -> dict:
    """
    Transfer ADA from the sender wallet to a receiver address.

    Args:
        walletId (str): Wallet ID that contains the payment.skey and payment.vkey files.
        receiver_addr_str (str): Receiver address in Bech32 format.
        amount (int): Amount to send in lovelace (1 ADA = 1_000_000 lovelace).

    Returns:
        dict: {
            "success": bool,
            "tx_hash": str (if successful),
            "error": str (if failed)
        }
    """

    sender_address = ""
    receiver_address = ""
    try:
        if amount <= 0:
            return {"success": False, "tx_hash": None, "error": "Amount must be greater than zero."}

        context = BlockFrostChainContext(project_id, base_url=BASE_URL)
        lovelace_amount = int(amount * 1_000_000)

        skey, vkey = load_or_create_key_pair(walletId, "payment")
        sender_address = Address(payment_part=vkey.hash(), network=network)
        receiver_address = Address.from_primitive(receiver_addr_str)

        builder = TransactionBuilder(context)
        builder.add_input_address(sender_address)

        builder.add_output(TransactionOutput(receiver_address, Value(lovelace_amount)))

        # Type cast the signing key to fix type error
        signed_tx: Transaction = builder.build_and_sign([skey], change_address=sender_address)  # type: ignore
        tx_hash = context.submit_tx(signed_tx.to_cbor())

        return {"success": True, "tx_hash":tx_hash, "sender_address": sender_address, "receiver_address": receiver_address, "error": None}

    except FileNotFoundError as e:
        return {"success": False, "walletId": walletId, "sender_address": sender_address, "receiver_address": receiver_address, "tx_hash": None, "error": f"Key file not found: {e}"}
    except Exception as e:
        return {"success": False, "walletId": walletId, "sender_address": sender_address, "receiver_address": receiver_address, "tx_hash": None, "error": f"Unexpected error: {e}"}

@mcp.tool(name="derive_addresses", description="Derives base, enterprise, and stake addresses from given verification keys") #working
def derive_addresses(
    walletId: str,
) -> dict:
    """
    Derives base, enterprise, and stake addresses from given verification keys.

    Args:
        walletId (str): Wallet ID that contains the payment.vkey and stake.vkey files.

    Returns:
        dict: {
            "base_address": str,
            "enterprise_address": str,
            "stake_address": str
        }
    """
    try:

        # Load keys using compressed helper functions
        skey, vkey = load_or_create_key_pair(walletId, "payment")

        # Generate addresses
        base_address = Address(vkey.hash(), vkey.hash(), network=network)
        enterprise_address = Address(vkey.hash(), network=network)
        stake_address = Address(staking_part=vkey.hash(), network=network)

        return {
            "base_address": str(base_address),
            "enterprise_address": str(enterprise_address),
            "stake_address": str(stake_address)
        }

    except Exception as e:
        return {"error": f"Failed to derive addresses: {str(e)}"}

@mcp.tool(name="get_wallet_balance", description="Gets wallet balance with details of policies, tokens, and amounts available in the account.") #working
def get_wallet_balance(walletId: str) -> dict:
    """
    Gets wallet balance with details of policies, tokens, and amounts available in the account.
    
    Returns:
        dict: Dictionary containing account information and token balances
    """
    try:
        # Load keys to get the address
        skey, vkey = load_or_create_key_pair(walletId, "payment")
        address = Address(payment_part=vkey.hash(), network=network)
        
        # Get all UTxOs for the address
        utxos = context.utxos(str(address))
        
        # Initialize tracking variables
        total_ada = 0
        token_balances = {}
                
        for utxo in utxos:
            # Add ADA balance
            total_ada += utxo.output.amount.coin
            
            # Process multi-asset tokens
            if utxo.output.amount.multi_asset:
                for policy_id, assets in utxo.output.amount.multi_asset.items():
                    policy_id_hex = policy_id.payload.hex()
                    
                    if policy_id_hex not in token_balances:
                        token_balances[policy_id_hex] = {}
                    
                    for asset_name, amount in assets.items():
                        asset_name_str = asset_name.payload.decode('utf-8', errors='ignore')
                        
                        if asset_name_str not in token_balances[policy_id_hex]:
                            token_balances[policy_id_hex][asset_name_str] = 0
                        
                        token_balances[policy_id_hex][asset_name_str] += amount
        
        return {
            "success": True,
            "address": str(address),
            "total_ada": total_ada,
            "ada_balance": total_ada / 1000000,
            "tokens": token_balances
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(name="get_protocol_params", description="Fetch protocol parameters from the Cardano blockchain using Blockfrost.") #working
def get_protocol_params() -> dict:
    """
    Fetch protocol parameters from the Cardano blockchain using Blockfrost.

    Returns:
        dict: Protocol parameters or error message.
    """
    try:
        context = BlockFrostChainContext(project_id=project_id, base_url=BASE_URL)
        params = context.protocol_param  # This is a ProtocolParams object
        
        def serialize(value):
            if isinstance(value, Fraction):
                return float(value)
            return value
        
        return {
            "min_fee_coefficient": serialize(params.min_fee_coefficient),
            "min_fee_constant": serialize(params.min_fee_constant),
            "max_tx_size": params.max_tx_size,
            "max_val_size": params.max_val_size,
            "key_deposit": params.key_deposit,
            "pool_deposit": params.pool_deposit,
            "price_mem": serialize(params.price_mem),
            "price_step": serialize(params.price_step),
            "coins_per_utxo_word": params.coins_per_utxo_word,
            "collateral_percent": params.collateral_percent,
            "max_collateral_inputs": params.max_collateral_inputs
        }

    except Exception as e:
        return {"error": f"Failed to fetch protocol parameters: {str(e)}"}

@mcp.tool(name="query_utxos", description="Query UTxOs at a given Cardano address") #working
def query_utxos(address_str: str):
    """
    Query UTxOs at a given Cardano address.
    
    Args:
        address_str (str): Bech32 Cardano address

    Returns:
        list: List of UTxO objects
    """
    try:
        address = Address.from_primitive(address_str)
        utxos = context.utxos(address)
        return utxos
    except Exception as e:
        return {"error": f"Failed to query UTxOs: {str(e)}"}

@mcp.tool(name="get_blockchain_tip", description="Fetch latest blockchain tip information.") #working
def get_blockchain_tip():
    """
    Fetch latest blockchain tip information.

    Returns:
        dict: Contains latest slot, block number, and hash.
    """
    try:
        tip = context.last_block_slot
        return {"latest_slot": tip}
    except Exception as e:
        return {"error": f"Failed to fetch blockchain tip: {str(e)}"}

@mcp.tool(name="get_transaction_details", description="Fetch details of a transaction using its hash.") #working
def get_transaction_details(tx_hash: str):
    """
    Fetch details of a transaction using its hash.

    Args:
        tx_hash (str): Transaction hash (string)

    Returns:
        dict: Transaction metadata or error
    """
    try:
        tx = context.api.transaction(tx_hash)
        return tx
    except Exception as e:
        return {"error": f"Failed to fetch transaction details: {str(e)}"}

@mcp.tool(name="mint_native_token", description="Mint a new native token using a simple policy (ScriptPubkey).")
def mint_native_token(
    token_name: str,
    token_amount: int,
    walletId: str
) -> dict:
    """
    Mint a new native token using a simple policy (ScriptPubkey).
    """
    try:
        # Load keys
        skey, vkey = load_or_create_key_pair(walletId, "payment")
        address = Address(payment_part=vkey.hash(), network=network)
        
        pubkey_policy = ScriptPubkey(vkey.hash())
        policy = ScriptAll([pubkey_policy])

        policy_id = policy.hash()
        wallet_path = get_wallet_file_paths(walletId)

        policy_script_name = "policy_"+str(policy_id)+".cbor"
        policy_script_path = os.path.join(wallet_path, policy_script_name)
        with open(policy_script_path, "wb") as f:
            f.write(policy.to_cbor())

        my_asset = Asset()

        nft = AssetName(token_name.encode())
        my_asset[nft] = token_amount

        multi_asset = MultiAsset()
        multi_asset[policy_id] = my_asset

        # Use 2 ADA (2000000 lovelace) to meet minimum UTxO requirement
        value = Value(2000000, multi_asset)

        builder = TransactionBuilder(context)
        builder.add_input_address(address)
        builder.mint = multi_asset
        builder.native_scripts = [policy]
        builder.add_output(TransactionOutput(address, value))

        # Cast the signing keys to the correct type
        signed_tx = builder.build_and_sign([skey], address)  # type: ignore
        tx_hash = context.submit_tx(signed_tx.to_cbor())
        return {"success": True, "tx_hash": tx_hash, "policy_id": str(policy_id)}

    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool(name="burn_token", description="Burn tokens by including negative output for the asset.") #working
def burn_token(
    token_name: str,
    amount_to_burn: int,
    walletId: str
) -> dict:
    """
    Burn tokens by including negative output for the asset.
    """
    try:
        skey, vkey = load_or_create_key_pair(walletId, "payment")
        address = Address(payment_part=vkey.hash(), network=network)

        policy_skey, policy_vkey = load_or_create_key_pair(walletId, "policy")

        pubkey_policy = ScriptPubkey(vkey.hash())
        policy = ScriptAll([pubkey_policy])

        policy_id = policy.hash()
        
        # Try to load the saved policy script first
        saved_policy_result = load_saved_policy_script(walletId)
        if saved_policy_result["success"]:
            policy = saved_policy_result["policy_script"]
            derived_policy_id = policy.hash()
        else:
            # Fallback to creating a new policy script
            script = ScriptPubkey(policy_vkey.hash())
            policy = ScriptAll([script])
            derived_policy_id = policy.hash()
        
        
        # If the derived policy ID doesn't match, we need the original policy script
        if str(derived_policy_id) != str(policy_id):
            return {"success": False, "error": "Policy ID mismatch. Need original policy script."}
        
        
        asset_name = AssetName(token_name.encode())
        
        # Create MultiAsset with proper structure for burning
        my_asset = Asset()
        my_asset[asset_name] = -abs(amount_to_burn)  # Negative amount for burning
        
        multi_asset = MultiAsset()
        multi_asset[policy_id] = my_asset
        
        
        builder = TransactionBuilder(context)
        builder.add_input_address(address)
        builder.mint = multi_asset  # Use multi_asset directly, not wrapped in Value
        builder.native_scripts = [policy]
        builder.add_output(TransactionOutput(address, Value(2_000_000)))  # Min ADA

        # Sign with both payment and policy keys - use type: ignore to bypass type checking
        signed_tx = builder.build_and_sign([skey, policy_skey], change_address=address)  # type: ignore
        tx_hash = context.submit_tx(signed_tx.to_cbor())
        return {"success": True, "tx_hash": tx_hash}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="sse")
