from core.config import Config
from core.scanner import scanner
from core.analyzer import analyzer
from core.dex import dex
import time
import json
import os
import random
import threading
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

class ScalpingStrategy:
    def __init__(self):
        self.db_path = "data/positions.json"
        self.history_path = "data/trade_history.json"
        self.active_positions = self.load_positions()
        self.last_scan_results = []
        self.current_prices = {}
        self.logs = []
        self.is_scanning = False
        self.scroll_index = 0
        self.scroll_counter = 0
        self.pos_scroll_index = 0
        self.pos_scroll_counter = 0

    def log(self, message, style="white"):
        timestamp = time.strftime('%H:%M:%S')
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > 10:
            self.logs.pop(0)

    def get_logs_panel(self):
        log_text = "\n".join(self.logs)
        status = "[bold green]● PARALLEL SCANNING[/bold green]" if self.is_scanning else "[dim]○ IDLE[/dim]"
        return Panel(log_text, title=f"Background Parallel Monitor | {status}", border_style="dim white", box=box.ROUNDED)

    def load_positions(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_positions(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w') as f:
                json.dump(self.active_positions, f, indent=4)
        except Exception as e:
            self.log(f"Error saving positions: {e}", "red")

    def log_analysis(self, pair, technicals, ai_result):
        try:
            entry = {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "symbol": pair['symbol'],
                "address": pair['address'],
                "price": pair['price_usd'],
                "indicators": {
                    "rsi": technicals.get('rsi'),
                    "macd": technicals.get('macd')
                },
                "ai_decision": ai_result['decision'],
                "ai_reason": ai_result.get('reason'),
                "tp": ai_result.get('tp'),
                "sl": ai_result.get('sl')
            }
            history = []
            if os.path.exists(self.history_path):
                with open(self.history_path, 'r') as f:
                    try: history = json.load(f)
                    except: history = []
            history.append(entry)
            os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
            with open(self.history_path, 'w') as f:
                json.dump(history[-500:], f, indent=4)
        except Exception as e:
            self.log(f"Failed to log history: {e}", "red")

    def get_market_table(self):
        table = Table(title="Live Market Scan (Auto-Scrolling)", box=box.ROUNDED, border_style="blue", expand=True)
        table.add_column("Symbol", style="cyan")
        table.add_column("Price (USD)", justify="right", style="yellow")
        table.add_column("Address", style="dim white")
        table.add_column("Volume 24h", justify="right", style="green")
        table.add_column("Liquidity", justify="right", style="magenta")
        table.add_column("Chg 1h", justify="right")
        
        display_count = 15
        total = len(self.last_scan_results)
        
        if total > display_count:
            start = self.scroll_index % (total - display_count + 1)
            display_items = self.last_scan_results[start : start + display_count]
            self.scroll_counter += 1
            if self.scroll_counter >= 15:
                self.scroll_index += 1
                self.scroll_counter = 0
        else:
            display_items = self.last_scan_results

        for p in display_items:
            chg = p['price_change_1h']
            live_price = self.current_prices.get(p['address'].lower(), float(p['price_usd']))
            table.add_row(
                p['symbol'],
                f"${live_price:.2f}",
                p['address'], 
                f"${p['volume_24h']:,.0f}", f"${p['liquidity']:,.0f}",
                f"{'[green]' if chg > 0 else '[red]'}{chg:.2f}%"
            )
        return table

    def get_positions_table(self):
        table = Table(title="Active Positions", box=box.ROUNDED, border_style="green", expand=True, show_footer=True)
        table.add_column("Symbol", style="cyan", footer="TOTAL")
        table.add_column("Entry", justify="right", style="dim white")
        table.add_column("TP", justify="right", style="green")
        table.add_column("SL", justify="right", style="red")
        
        total_profit = 0
        all_rows = []
        for addr, pos in self.active_positions.items():
            curr = self.current_prices.get(addr.lower(), pos['entry'])
            profit = ((curr - pos['entry']) / pos['entry']) * 100
            total_profit += profit
            color = "green" if profit > 0 else "red"
            all_rows.append([
                pos['symbol'], 
                f"${pos['entry']:.2f}",
                f"{pos['tp']:.2f}",
                f"{pos['sl']:.2f}",
                f"[{color}]{profit:.2f}%[/{color}]"
            ])

        total_color = "bold green" if total_profit > 0 else "bold red"
        table.add_column("%", justify="right", footer=f"[{total_color}]{total_profit:.2f}%[/{total_color}]")

        display_count = 10
        if len(all_rows) > display_count:
            start = self.pos_scroll_index % (len(all_rows) - display_count + 1)
            display_rows = all_rows[start : start + display_count]
            self.pos_scroll_counter += 1
            if self.pos_scroll_counter >= 15:
                self.pos_scroll_index += 1
                self.pos_scroll_counter = 0
        else:
            display_rows = all_rows

        for row in display_rows:
            table.add_row(*row)
        return table

    def run_cycle_background(self):
        if self.is_scanning: return
        thread = threading.Thread(target=self.run_cycle)
        thread.daemon = True
        thread.start()

    def run_cycle(self):
        self.is_scanning = True
        self.log(f"Memulai market scan untuk {Config.WSS_URL}...")
        try:
            results = scanner.scan_pancakeswap_pairs()
            if results:
                self.last_scan_results = results
                for p in results:
                    self.current_prices[p['address'].lower()] = float(p['price_usd'])
            
            for pair in self.last_scan_results:
                if pair['address'] in self.active_positions:
                    continue

                self.log(f"AI Analis: Mengevaluasi {pair['symbol']}...")
                base_price = float(pair['price_usd'])
                mock_history = [base_price * (1 + random.uniform(-0.002, 0.002)) for _ in range(30)]
                technicals = analyzer.calculate_indicators(mock_history)
                ai_result = analyzer.analyze_with_gemini(pair, technicals)
                self.log_analysis(pair, technicals, ai_result)
                self.log(f"Keputusan {pair['symbol']}: {ai_result['decision']}")
                if ai_result['decision'] == "BUY":
                    self.execute_trade(pair, ai_result)
        except Exception as e:
            self.log(f"Scan error: {e}", "red")
        finally:
            self.is_scanning = False
            self.log("Scan selesai. Menyiapkan siklus berikutnya...")
            time.sleep(5)

    def execute_trade(self, pair, ai_result):
        token_address = pair['baseToken']
        self.log(f"🚀 EKSEKUSI TRADE: {pair['symbol']}")
        tx = dex.buy_token(token_address, Config.MAX_BNB_PER_TRADE)
        if tx:
            self.active_positions[pair['address']] = {
                "symbol": pair['symbol'],
                "entry": float(pair['price_usd']),
                "tp": ai_result['tp'],
                "sl": ai_result['sl'],
                "baseToken": token_address
            }
            self.save_positions()
            self.log(f"✅ Beli berhasil: {pair['symbol']} | TP: {ai_result['tp']}")
        else:
            self.log(f"❌ Beli gagal: {pair['symbol']}", "red")

    def monitor_positions(self):
        for p in self.last_scan_results:
            addr = p['address'].lower()
            old = self.current_prices.get(addr, float(p['price_usd']))
            self.current_prices[addr] = old * (1 + random.uniform(-0.0001, 0.0001))
            p['volume_24h'] *= (1 + random.uniform(-0.00005, 0.00005))
            p['liquidity'] *= (1 + random.uniform(-0.00005, 0.00005))
            p['price_change_1h'] += random.uniform(-0.01, 0.01)

        if not self.active_positions:
            return

        total_profit = 0
        for addr, pos in self.active_positions.items():
            curr = self.current_prices.get(addr.lower(), pos['entry'])
            profit = ((curr - pos['entry']) / pos['entry']) * 100
            total_profit += profit

        if total_profit >= Config.GLOBAL_TP_PCT:
            self.log(f"🚀 GLOBAL TAKE PROFIT TERCAPAI ({total_profit:.2f}%)! Menjual semua aset...", "bold green")
            all_addrs = list(self.active_positions.keys())
            for addr in all_addrs:
                self.execute_sell(addr, self.active_positions[addr], "GLOBAL TP")
            return

        for addr, pos in list(self.active_positions.items()):
            current_price = self.current_prices.get(addr.lower(), pos['entry'])
            if current_price >= pos['tp']:
                self.execute_sell(addr, pos, "TAKE PROFIT")
            elif current_price <= pos['sl']:
                self.execute_sell(addr, pos, "STOP LOSS")

    def execute_sell(self, addr, pos, reason):
        self.log(f"🔔 {reason}: Menjual {pos['symbol']}...")
        tx = dex.sell_token(pos.get('baseToken'), 0)
        if tx:
            self.log(f"💰 Posisi ditutup: {pos['symbol']} ({reason})")
            del self.active_positions[addr]
            self.save_positions()
        else:
            self.log(f"❌ Gagal menjual: {pos['symbol']}", "red")

strategy = ScalpingStrategy()
