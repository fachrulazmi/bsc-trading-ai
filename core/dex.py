import json
import time
from web3 import Web3
from eth_account import Account
from core.config import Config
from core.network import network

PANCAKE_ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForETH",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"}
        ],
        "name": "getAmountsOut",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function"
    }
]

ERC20_ABI = [
    {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"}
]

class DEX:
    def __init__(self):
        self.w3 = network.w3
        router_addr = self.w3.to_checksum_address(Config.PANCAKE_ROUTER_ADDRESS)
        self.router = self.w3.eth.contract(address=router_addr, abi=PANCAKE_ROUTER_ABI)

    def get_token_price(self, token_address):
        try:
            path = [Config.WBNB_ADDRESS, token_address]
            amounts = self.router.functions.getAmountsOut(self.w3.to_wei(1, 'ether'), path).call()
            return amounts[1] / 10**18
        except:
            return 0

    def buy_token(self, token_address, bnb_amount):
        if Config.DRY_RUN:
            return "dry_run_tx_hash"
        try:
            account = Account.from_key(Config.PRIVATE_KEY)
            path = [Config.WBNB_ADDRESS, token_address]
            deadline = int(time.time()) + 600
            nonce = self.w3.eth.get_transaction_count(account.address)
            txn = self.router.functions.swapExactETHForTokens(
                0, path, account.address, deadline
            ).build_transaction({
                'from': account.address,
                'value': self.w3.to_wei(bnb_amount, 'ether'),
                'gas': Config.GAS_LIMIT,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            signed_txn = self.w3.eth.account.sign_transaction(txn, Config.PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            return tx_hash.hex()
        except Exception as e:
            from rich.console import Console
            from rich.panel import Panel
            Console().print(Panel(f"[bold red]Transaction Failed[/bold red]\n[white]{e}[/white]", border_style="red", title="DEX Error"))
            return None

    def sell_token(self, token_address, token_amount):
        if Config.DRY_RUN:
            return "dry_run_tx_hash"
        try:
            account = Account.from_key(Config.PRIVATE_KEY)
            path = [token_address, Config.WBNB_ADDRESS]
            deadline = int(time.time()) + 600
            nonce = self.w3.eth.get_transaction_count(account.address)
            txn = self.router.functions.swapExactTokensForETH(
                token_amount, 0, path, account.address, deadline
            ).build_transaction({
                'from': account.address,
                'gas': Config.GAS_LIMIT,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            signed_txn = self.w3.eth.account.sign_transaction(txn, Config.PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            return tx_hash.hex()
        except:
            return None

dex = DEX()
