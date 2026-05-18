import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BSC_WSS_URL = os.getenv("BSC_WSS_URL", "wss://bsc-ws-node.nariox.org")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    AI_MODEL = "gemini-flash-latest"
    
    MIN_VOLUME_USD = float(os.getenv("MIN_VOLUME_USD", 50000))
    MIN_LIQUIDITY_USD = float(os.getenv("MIN_LIQUIDITY_USD", 10000))
    
    SLIPPAGE = float(os.getenv("SLIPPAGE", 0.5))
    GAS_LIMIT = int(os.getenv("GAS_LIMIT", 250000))
    MAX_BNB_PER_TRADE = float(os.getenv("MAX_BNB_PER_TRADE", 0.001))
    
    DEFAULT_STOP_LOSS_PCT = 2.0
    DEFAULT_TAKE_PROFIT_PCT = 5.0
    GLOBAL_TP_PCT = float(os.getenv("GLOBAL_TP_PCT", 4.0))
    AI_COOLDOWN = int(os.getenv("AI_COOLDOWN", 10))
    
    DRY_RUN = os.getenv("DRY_RUN", "True").lower() == "true"
    USE_TESTNET = os.getenv("USE_TESTNET", "False").lower() == "true"

    # Mainnet
    MAINNET_ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
    MAINNET_WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
    
    # Testnet
    TESTNET_ROUTER = "0x9Ac6a34890A1d019f0E99F9444B6D8c8942b0833"
    TESTNET_WBNB = "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"
    TESTNET_WSS = "wss://bsc-testnet.drpc.org"

    @property
    def PANCAKE_ROUTER_ADDRESS(self):
        return self.TESTNET_ROUTER if self.USE_TESTNET else self.MAINNET_ROUTER

    @property
    def WBNB_ADDRESS(self):
        return self.TESTNET_WBNB if self.USE_TESTNET else self.MAINNET_WBNB
        
    @property
    def WSS_URL(self):
        return self.TESTNET_WSS if self.USE_TESTNET else self.BSC_WSS_URL

Config = Config()
