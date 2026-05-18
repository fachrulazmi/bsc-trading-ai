import requests
from core.config import Config
from core.logger import get_logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()
log = get_logger("scanner")

class Scanner:
    def __init__(self):
        self.anchors = [
            "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c", # WBNB
            "0x55d398326f99059fF775485246999027B3197955", # USDT
            "0x8AC76a51cc950d9822D68b83fE1Ad97B44439102"  # USDC
        ]

    def scan_pancakeswap_pairs(self):
        all_pairs = []
        for token in self.anchors:
            try:
                url = f"https://api.dexscreener.com/latest/dex/tokens/{token}"
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    all_pairs.extend(resp.json().get('pairs', []))
            except Exception as e:
                log.error(f"Error scanning anchor {token}: {e}")
                continue

        try:
            search_url = "https://api.dexscreener.com/latest/dex/search?q=pancakeswap"
            resp = requests.get(search_url, timeout=15)
            if resp.status_code == 200:
                all_pairs.extend(resp.json().get('pairs', []))
        except Exception as e:
            log.error(f"Error in broad search: {e}")

        filtered_pairs = []
        seen_addresses = set()

        for pair in all_pairs:
            addr = pair.get('pairAddress')
            if not addr or addr in seen_addresses:
                continue
            
            # Filter network based on USE_TESTNET
            # DexScreener doesn't have a direct testnet chainId in the same way, 
            # so we focus on BSC mainnet pairs for discovery, but execute on testnet if requested.
            if pair.get('chainId') != 'bsc' or pair.get('dexId') != 'pancakeswap':
                continue

            vol = float(pair.get('volume', {}).get('h24', 0) or 0)
            liq = float(pair.get('liquidity', {}).get('usd', 0) or 0)
            chg = float(pair.get('priceChange', {}).get('h1', 0) or 0)

            if vol >= Config.MIN_VOLUME_USD and liq >= Config.MIN_LIQUIDITY_USD:
                seen_addresses.add(addr)
                base_token = pair.get('baseToken', {})
                quote_token = pair.get('quoteToken', {})
                target = base_token if "BNB" not in base_token.get('symbol', '') else quote_token
                
                filtered_pairs.append({
                    "address": addr,
                    "baseToken": target.get('address'),
                    "symbol": target.get('symbol', 'Unknown'),
                    "price_usd": pair.get('priceUsd'),
                    "volume_24h": vol,
                    "liquidity": liq,
                    "price_change_1h": chg
                })

        filtered_pairs.sort(key=lambda x: x['volume_24h'], reverse=True)
        return filtered_pairs[:30]

scanner = Scanner()
