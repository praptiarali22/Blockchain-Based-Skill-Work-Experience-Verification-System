from web3 import Web3
import json
import requests
import os

# Connect to local Ethereum node or Infura endpoint
w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))  # Or Infura/Alchemy endpoint

# Load ABI
ABI_PATH = os.path.join("contracts", "abi.json")
with open(ABI_PATH, "r") as f:
    abi = json.load(f)

# Set your deployed contract address
contract_address = "0xf62df01E63e9E4c07620AE08b83C1574058C6357"  # ⬅ Replace with actual contract address
contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)


def get_nfts_for_wallet(wallet_address):
    """
    Returns a list of token IDs owned by a wallet.
    """
    try:
        wallet_address = Web3.to_checksum_address(wallet_address)
        balance = contract.functions.balanceOf(wallet_address).call()
        token_ids = []
        for i in range(balance):
            token_id = contract.functions.tokenOfOwnerByIndex(wallet_address, i).call()
            token_ids.append(token_id)
        return token_ids
    except Exception as e:
        print(f"Error getting NFTs for {wallet_address}: {e}")
        return []


def get_token_metadata(token_id):
    """
    Fetches metadata from tokenURI. Returns a dictionary.
    """
    try:
        token_uri = contract.functions.tokenURI(token_id).call()
        response = requests.get(token_uri)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching metadata from {token_uri}: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error retrieving metadata for token {token_id}: {e}")
        return {}
