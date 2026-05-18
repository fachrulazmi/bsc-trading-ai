import requests

base_url = "https://api.dexscreener.com/latest/dex/search?q=WBNB"
response = requests.get(base_url)
data = response.json()
pairs = data.get('pairs', [])

print(f"Total pairs found: {len(pairs)}")
for pair in pairs:
    if pair.get('chainId') == 'bsc':
        print(f"Symbol: {pair.get('baseToken', {}).get('symbol')}, DEX: {pair.get('dexId')}, Vol: {pair.get('volume', {}).get('h24')}")
