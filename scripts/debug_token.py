import requests

# WBNB token address on BSC
token_address = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
response = requests.get(url)
data = response.json()
pairs = data.get('pairs', [])

print(f"Total pairs found for WBNB: {len(pairs)}")
for pair in pairs[:10]:
    base = pair.get('baseToken', {}).get('symbol')
    quote = pair.get('quoteToken', {}).get('symbol')
    print(f"Pair: {base}/{quote}, DEX: {pair.get('dexId')}, Vol: {pair.get('volume', {}).get('h24')}")
