import time
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich import box
from core.config import Config
from core.network import network
from core.strategy import strategy

console = Console()

def make_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="logs", size=10),
        Layout(name="footer", size=1)
    )
    layout["main"].split_row(
        Layout(name="market", ratio=2),
        Layout(name="positions", ratio=1)
    )
    return layout

def main():
    layout = make_layout()
    layout["header"].update(Panel("[bold cyan]🚀 BSC AI SCALPING BOT - PRO REAL-TIME DASHBOARD[/bold cyan]", border_style="bright_magenta"))
    
    with Live(layout, refresh_per_second=4, screen=True):
        try:
            while True:
                conn_status = "[bold green]CONNECTED[/bold green]" if network.is_connected else "[bold red]DISCONNECTED[/bold red]"
                layout["footer"].update(f"[dim]Network: {('TESTNET' if Config.USE_TESTNET else 'MAINNET')} | WSS Status: {conn_status} | Time: {time.strftime('%H:%M:%S')}[/dim]")

                if not strategy.is_scanning:
                    strategy.run_cycle_background()
                
                strategy.monitor_positions()
                
                layout["market"].update(strategy.get_market_table())
                layout["positions"].update(strategy.get_positions_table())
                layout["logs"].update(strategy.get_logs_panel())
                
                time.sleep(0.2)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
