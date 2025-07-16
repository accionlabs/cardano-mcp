from typing import Any
import os
from dotenv import load_dotenv
import pathlib
from pycardano import (
    PaymentSigningKey, PaymentVerificationKey, NativeScript, PaymentKeyPair
)

load_dotenv()

BASE_UPLOAD_DIR=os.getenv("BASE_UPLOAD_DIR","")

def get_wallet_file_paths(walletId: str, file_type: str = "") -> str:
    base_path = os.path.join(BASE_UPLOAD_DIR, walletId)
    return base_path + "/" + file_type if file_type else base_path

def load_or_create_key_pair(walletId: str, base_name: str):
    
    skey_path = get_wallet_file_paths(walletId, f"{base_name}.skey")
    vkey_path = get_wallet_file_paths(walletId, f"{base_name}.vkey")
    print(skey_path, vkey_path)
    
    # Ensure directory exists
    pathlib.Path(BASE_UPLOAD_DIR + "/" + walletId).mkdir(parents=True, exist_ok=True)
    
    if pathlib.Path(skey_path).exists():
        print("insdie if")
        skey = PaymentSigningKey.load(skey_path)
        vkey = PaymentVerificationKey.from_signing_key(skey) # type: ignore
    else:
        print("insdie else")
        key_pair = PaymentKeyPair.generate()
        key_pair.signing_key.save(skey_path)
        key_pair.verification_key.save(vkey_path)
        skey = key_pair.signing_key
        vkey = key_pair.verification_key
    return skey, vkey

def load_saved_policy_script(walletId: str) -> dict:
    """
    Load the policy script that was saved during minting.
    
    Returns:
        dict: Dictionary containing the policy script if found
    """
    try:
        wallet_path = pathlib.Path(get_wallet_file_paths(walletId))
        
        # Find files that start with "policy_" and end with ".cbor"
        policy_files = list(wallet_path.glob("policy_*.cbor"))
        
        if policy_files:
            # Use the first policy file found
            policy_script_path = policy_files[0]
            with open(policy_script_path, "rb") as f:
                policy_script_bytes = f.read()
            
            # Load the policy script from CBOR
            policy_script = NativeScript.from_cbor(policy_script_bytes)
            return {"success": True, "policy_script": policy_script}
        else:
            return {"success": False, "error": "Policy script file not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

