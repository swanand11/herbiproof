"""
CropToken Flask API Server
A comprehensive REST API for interacting with the CropToken smart contract using Flask and Web3.py

Installation requirements:
pip install flask web3 python-dotenv flask-cors

Environment variables needed (.env file):
RPC_URL=http://localhost:8545
PRIVATE_KEY=your_private_key_here
CONTRACT_ADDRESS=your_deployed_contract_address_here
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
import json
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from functools import wraps

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug: Check Web3.py version
import web3
logger.info(f"Web3.py version: {web3.__version__}")


app = Flask(__name__)
CORS(app)  

# Configuration
class Config:
    RPC_URL = os.getenv("RPC_URL", "http://localhost:8545")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
    
    # Contract ABI 
    CONTRACT_ABI = [
        {
            "inputs": [],
            "name": "nextId",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "name": "crops",
            "outputs": [
                {"internalType": "uint256", "name": "id", "type": "uint256"},
                {"internalType": "string", "name": "metadata", "type": "string"},
                {"internalType": "address", "name": "owner", "type": "address"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "address", "name": "", "type": "address"}],
            "name": "registeredUsers",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "registerUser",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "string", "name": "_metadata", "type": "string"}],
            "name": "createCrop",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "_id", "type": "uint256"},
                {"internalType": "address", "name": "_owner", "type": "address"}
            ],
            "name": "authenticate",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "_id", "type": "uint256"},
                {"internalType": "address", "name": "_to", "type": "address"}
            ],
            "name": "transferCrop",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "uint256", "name": "_id", "type": "uint256"}],
            "name": "getCrop",
            "outputs": [
                {"internalType": "uint256", "name": "", "type": "uint256"},
                {"internalType": "string", "name": "", "type": "string"},
                {"internalType": "address", "name": "", "type": "address"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"},
                {"indexed": False, "internalType": "string", "name": "metadata", "type": "string"},
                {"indexed": False, "internalType": "address", "name": "owner", "type": "address"}
            ],
            "name": "CropCreated",
            "type": "event"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"},
                {"indexed": False, "internalType": "address", "name": "from", "type": "address"},
                {"indexed": False, "internalType": "address", "name": "to", "type": "address"}
            ],
            "name": "CropTransferred",
            "type": "event"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": False, "internalType": "address", "name": "user", "type": "address"}
            ],
            "name": "UserRegistered",
            "type": "event"
        }
    ]

# Initialize Web3
try:
    w3 = Web3(Web3.HTTPProvider(Config.RPC_URL))
    if not w3.is_connected():
        raise Exception("Failed to connect to blockchain")
    
    # Initialize contract
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(Config.CONTRACT_ADDRESS),
        abi=Config.CONTRACT_ABI
    )
    
    # Initialize account
    if Config.PRIVATE_KEY:
        account = w3.eth.account.from_key(Config.PRIVATE_KEY)
        default_address = account.address
    else:
        default_address = None
    
    logger.info(f"Connected to blockchain. Contract at: {Config.CONTRACT_ADDRESS}")
    
except Exception as e:
    logger.error(f"Failed to initialize Web3: {e}")
    contract = None
    default_address = None

# Utility functions
def validate_address(address):
    """Validate Ethereum address format"""
    try:
        return Web3.is_address(address) and Web3.to_checksum_address(address)
    except:
        return False

def handle_transaction(tx_function, *args, **kwargs):
    """Handle transaction execution with proper error handling"""
    try:
        if not Config.PRIVATE_KEY:
            return {"error": "Private key not configured"}, 400
        
        logger.info(f"Building transaction for function: {tx_function}")
        
        # Build transaction
        tx = tx_function(*args, **kwargs)
        tx_dict = tx.build_transaction({
            'from': default_address,
            'gas': 3000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': w3.eth.get_transaction_count(default_address)
        })
        
        logger.info(f"Transaction dict built: {tx_dict}")
        
        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx_dict, Config.PRIVATE_KEY)
        logger.info(f"Transaction signed. Type: {type(signed_tx)}")
        logger.info(f"Signed transaction attributes: {dir(signed_tx)}")
        
        # Try different attribute names for Web3.py version compatibility
        raw_transaction = None
        if hasattr(signed_tx, 'rawTransaction'):
            raw_transaction = signed_tx.rawTransaction
            logger.info("Using 'rawTransaction' attribute")
        elif hasattr(signed_tx, 'raw_transaction'):
            raw_transaction = signed_tx.raw_transaction
            logger.info("Using 'raw_transaction' attribute")
        elif hasattr(signed_tx, 'raw'):
            raw_transaction = signed_tx.raw
            logger.info("Using 'raw' attribute")
        else:
            # Fallback: try to get the raw transaction data
            logger.error(f"Could not find raw transaction attribute. Available: {[attr for attr in dir(signed_tx) if not attr.startswith('_')]}")
            return {"error": "Could not access raw transaction data"}, 500
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(raw_transaction)
        logger.info(f"Transaction sent. Hash: {tx_hash.hex()}")
        
        # Wait for confirmation
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        logger.info(f"Transaction confirmed. Block: {tx_receipt.blockNumber}")
        
        return {
            "success": True,
            "tx_hash": tx_hash.hex(),
            "gas_used": tx_receipt.gasUsed,
            "block_number": tx_receipt.blockNumber
        }, 200
        
    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": str(e)}, 500

# API Routes

@app.route('/', methods=['GET'])
def health_check():
   
    try:
        latest_block = w3.eth.block_number
        return jsonify({
            "status": "healthy",
            "api_version": "1.0.0",
            "blockchain_connected": w3.is_connected(),
            "latest_block": latest_block,
            "contract_address": Config.CONTRACT_ADDRESS,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/api/v1/users/register', methods=['POST'])
def register_user():
    """
    Register a new user on the blockchain
    
    Request body:
    {
        "user_address": "0x..." (optional, uses default if not provided)
    }
    
    Returns:
    {
        "success": true,
        "tx_hash": "0x...",
        "gas_used": 123456,
        "block_number": 12345,
        "user_address": "0x..."
    }
    """
    data = request.get_json() or {}
    user_address = data.get('user_address', default_address)
    
    if not user_address:
        return jsonify({"error": "User address required"}), 400
    
    if not validate_address(user_address):
        return jsonify({"error": "Invalid address format"}), 400
    
    # Check if already registered
    try:
        is_registered = contract.functions.registeredUsers(user_address).call()
        if is_registered:
            return jsonify({"error": "User already registered"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to check registration status: {e}"}), 500
    
    # Register user
    result, status_code = handle_transaction(contract.functions.registerUser)
    
    if status_code == 200:
        result["user_address"] = user_address
    
    return jsonify(result), status_code

@app.route('/api/v1/users/<address>/status', methods=['GET'])

def check_user_registration(address):
    """
    Check if a user is registered
    
    Parameters:
    - address: Ethereum address to check
    
    Returns:
    {
        "address": "0x...",
        "is_registered": true/false
    }
    """
    if not validate_address(address):
        return jsonify({"error": "Invalid address format"}), 400
    
    try:
        is_registered = contract.functions.registeredUsers(address).call()
        return jsonify({
            "address": address,
            "is_registered": is_registered
        })
    except Exception as e:
        return jsonify({"error": f"Failed to check registration: {e}"}), 500

@app.route('/api/v1/crops', methods=['POST'])

def create_crop():
    """
    Create a new crop token
    
    Request body:
    {
        "metadata": "crop metadata string",
        "owner_address": "0x..." (optional, uses default if not provided)
    }
    
    Returns:
    {
        "success": true,
        "tx_hash": "0x...",
        "gas_used": 123456,
        "block_number": 12345,
        "crop_id": 1,
        "metadata": "crop metadata",
        "owner": "0x..."
    }
    """
    data = request.get_json()
    if not data or 'metadata' not in data:
        return jsonify({"error": "Metadata is required"}), 400
    
    metadata = data['metadata']
    owner_address = data.get('owner_address', default_address)
    
    if not owner_address:
        return jsonify({"error": "Owner address required"}), 400
    
    if not validate_address(owner_address):
        return jsonify({"error": "Invalid owner address format"}), 400
    
    # Check if user is registered
    try:
        is_registered = contract.functions.registeredUsers(owner_address).call()
        if not is_registered:
            return jsonify({"error": "User must be registered first"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to check registration: {e}"}), 500
    
    # Get next crop ID before creating
    try:
        next_id = contract.functions.nextId().call()
    except Exception as e:
        return jsonify({"error": f"Failed to get next ID: {e}"}), 500
    
    # Create crop
    result, status_code = handle_transaction(
        contract.functions.createCrop,
        metadata
    )
    
    if status_code == 200:
        result.update({
            "crop_id": next_id,
            "metadata": metadata,
            "owner": owner_address
        })
    
    return jsonify(result), status_code

@app.route('/api/v1/crops/<int:crop_id>', methods=['GET'])

def get_crop(crop_id):
    """
    Get crop information by ID
    
    Parameters:
    - crop_id: Crop token ID
    
    Returns:
    {
        "id": 1,
        "metadata": "crop metadata",
        "owner": "0x...",
        "exists": true
    }
    """
    try:
        crop_data = contract.functions.getCrop(crop_id).call()
        
        # Check if crop exists (owner will be zero address if not)
        exists = crop_data[2] != "0x0000000000000000000000000000000000000000"
        
        return jsonify({
            "id": crop_data[0],
            "metadata": crop_data[1],
            "owner": crop_data[2],
            "exists": exists
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get crop: {e}"}), 500

@app.route('/api/v1/crops/<int:crop_id>/authenticate', methods=['POST'])
def authenticate_crop(crop_id):
    """
    Authenticate crop ownership
    
    Request body:
    {
        "owner_address": "0x..."
    }
    
    Returns:
    {
        "crop_id": 1,
        "owner_address": "0x...",
        "is_authentic": true/false
    }
    """
    data = request.get_json()
    if not data or 'owner_address' not in data:
        return jsonify({"error": "Owner address is required"}), 400
    
    owner_address = data['owner_address']
    
    if not validate_address(owner_address):
        return jsonify({"error": "Invalid owner address format"}), 400
    
    try:
        is_authentic = contract.functions.authenticate(crop_id, owner_address).call({
            'from': default_address
        })
        
        return jsonify({
            "crop_id": crop_id,
            "owner_address": owner_address,
            "is_authentic": is_authentic
        })
    except Exception as e:
        return jsonify({"error": f"Authentication failed: {e}"}), 500

@app.route('/api/v1/crops/<int:crop_id>/transfer', methods=['POST'])

def transfer_crop(crop_id):
    """
    Transfer crop to another address
    
    Request body:
    {
        "to_address": "0x...",
        "from_address": "0x..." (optional, uses default if not provided)
    }
    
    Returns:
    {
        "success": true,
        "tx_hash": "0x...",
        "gas_used": 123456,
        "block_number": 12345,
        "crop_id": 1,
        "from_address": "0x...",
        "to_address": "0x..."
    }
    """
    data = request.get_json()
    if not data or 'to_address' not in data:
        return jsonify({"error": "Recipient address is required"}), 400
    
    to_address = data['to_address']
    from_address = data.get('from_address', default_address)
    
    if not validate_address(to_address):
        return jsonify({"error": "Invalid recipient address format"}), 400
    
    if not validate_address(from_address):
        return jsonify({"error": "Invalid sender address format"}), 400
    
    # Check if recipient is registered
    try:
        is_registered = contract.functions.registeredUsers(to_address).call()
        if not is_registered:
            return jsonify({"error": "Recipient must be registered"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to check recipient registration: {e}"}), 500
    
    # Verify ownership
    try:
        crop_data = contract.functions.getCrop(crop_id).call()
        if crop_data[2].lower() != from_address.lower():
            return jsonify({"error": "Only the owner can transfer this crop"}), 403
    except Exception as e:
        return jsonify({"error": f"Failed to verify ownership: {e}"}), 500
    
    # Transfer crop
    result, status_code = handle_transaction(
        contract.functions.transferCrop,
        crop_id,
        to_address
    )
    
    if status_code == 200:
        result.update({
            "crop_id": crop_id,
            "from_address": from_address,
            "to_address": to_address
        })
    
    return jsonify(result), status_code

@app.route('/api/v1/crops/next-id', methods=['GET'])

def get_next_crop_id():
    """
    Get the next available crop ID
    
    Returns:
    {
        "next_id": 5
    }
    """
    try:
        next_id = contract.functions.nextId().call()
        return jsonify({"next_id": next_id})
    except Exception as e:
        return jsonify({"error": f"Failed to get next ID: {e}"}), 500

@app.route('/api/v1/crops/owner/<address>', methods=['GET'])
def get_crops_by_owner(address):
    """
    Get all crops owned by an address
    Note: This requires iterating through all crops. For large datasets,
    consider implementing event-based indexing.
    
    Parameters:
    - address: Owner's Ethereum address
    
    Query parameters:
    - limit: Maximum number of crops to return (default: 100)
    
    Returns:
    {
        "owner": "0x...",
        "crops": [
            {
                "id": 1,
                "metadata": "crop1",
                "owner": "0x..."
            },
            ...
        ],
        "total_found": 5
    }
    """
    if not validate_address(address):
        return jsonify({"error": "Invalid address format"}), 400
    
    limit = min(int(request.args.get('limit', 100)), 1000)  # Cap at 1000
    
    try:
        next_id = contract.functions.nextId().call()
        owned_crops = []
        
        for crop_id in range(min(next_id, limit)):
            try:
                crop_data = contract.functions.getCrop(crop_id).call()
                if crop_data[2].lower() == address.lower():
                    owned_crops.append({
                        "id": crop_data[0],
                        "metadata": crop_data[1],
                        "owner": crop_data[2]
                    })
            except:
                continue  
        
        return jsonify({
            "owner": address,
            "crops": owned_crops,
            "total_found": len(owned_crops)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get crops by owner: {e}"}), 500


if __name__ == '__main__':
    if not Config.CONTRACT_ADDRESS or not Config.PRIVATE_KEY:
        logger.warning("CONTRACT_ADDRESS or PRIVATE_KEY not set. Some functionality may not work.")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )