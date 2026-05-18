from web3 import Web3
from web3.providers import LegacyWebSocketProvider
from core.config import Config

class Network:
    def __init__(self):
        self.connect()

    def connect(self):
        try:
            self.w3 = Web3(LegacyWebSocketProvider(Config.WSS_URL))
            print(f"Koneksi WSS aktif (Legacy): {Config.WSS_URL}")
        except Exception as e:
            from rich.console import Console
            from rich.panel import Panel
            Console().print(Panel(f"[bold red]Websocket Connection Error[/bold red]\n[white]{e}[/white]", border_style="red", title="Critical Error"))
            raise

    def get_bnb_balance(self, address):
        balance_wei = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance_wei, 'ether')

    def get_gas_price(self):
        return self.w3.eth.gas_price

    @property
    def is_connected(self):
        try:
            return self.w3.is_connected()
        except:
            return False

network = Network()
