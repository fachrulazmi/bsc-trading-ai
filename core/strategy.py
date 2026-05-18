import json
import os
import time
import random
import threading
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from core.config import Config
from core.scanner import scanner
from core.analyzer import analyzer
from core.dex import dex
from core.logger import get_logger

console = Console()
log = get_logger("strategy")

class ScalpingStrategy:
    def __init__(self):
        self.db_path = "data/positions.json"
        self.history_path = "data/trade_history.json"
        self.active_positions = self.load_positions()
        self.last_scan_results = []
        self.current_prices = {}
        self.ui_logs = []
        self._stop_event = threading.Event()
        self._scan_lock = threading.Lock()
        self.is_scanning_flag = False
        self.scroll_index = 0
        self.scroll_counter = 0
        self.pos_scroll_index = 0
        self.pos_scroll_counter = 0

    def add_ui_log(self, message):
        timestamp = time.strftime('%H:%M:%S')
        self.ui_logs.append(f"[{timestamp}] {message}")
        if len(self.ui_logs) > 12:
            self.ui_logs.pop(0)
        log.info(message)

    def get_logs_panel(self):
        log_text = "\n".join(self.ui_logs)
        status = "[bold green]● PARALLEL SCANNING[/bold green]" if self.is_scanning_flag else "[dim]○ IDLE[/dim]"
        return Panel(log_text, title=f"Background Parallel Monitor | {status}", border_style="dim white", box=box.ROUNDED)

    def load_positions(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                log.error(f"Failed to load positions: {e}")
        return {}

    def save_positions(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w') as f:
                json.dump(self.active_positions, f, indent=4)
        except Exception as e:
            log.error(f"Error saving positions: {e}")

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
            log.error(f"Failed to log analysis: {e}")

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
                p['symbol'], f"${live_price:.2f}", p['address'], 
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
                pos['symbol'], f"${pos['entry']:.2f}", f"{pos['tp']:.2f}", f"{pos['sl']:.2f}",
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

    def stop(self):
        self._stop_event.set()
        log.info("Shutdown signal received.")

    def run_cycle_background(self):
        if self.is_scanning_flag: return
        thread = threading.Thread(target=self.run_cycle)
        thread.daemon = True
        thread.start()

    def run_cycle(self):
        if not self._scan_lock.acquire(blocking=False):
            return
        
        self.is_scanning_flag = True
        self.add_ui_log("Memulai market scan...")
        try:
            results = scanner.scan_pancakeswap_pairs()
            if results:
                self.last_scan_results = results
                for p in results:
                    if self._stop_event.is_set(): return
                    self.current_prices[p['address'].lower()] = float(p['price_usd'])
            
            for pair in self.last_scan_results:
                if self._stop_event.is_set(): break
                if pair['address'] in self.active_positions: continue

                self.add_ui_log(f"AI Analis: {pair['symbol']}...")
                base_price = float(pair['price_usd'])
                mock_history = [base_price * (1 + random.uniform(-0.002, 0.002)) for _ in range(30)]
                technicals = analyzer.calculate_indicators(mock_history)
                
                ai_result = analyzer.analyze_with_gemini(pair, technicals)
                self.log_analysis(pair, technicals, ai_result)
                
                if ai_result['decision'] == "BUY":
                    self.execute_trade(pair, ai_result)
                
                # Gemini Rate Limiter
                time.sleep(Config.AI_COOLDOWN) 
        except Exception as e:
            log.exception("Error in scan cycle")
            self.add_ui_log(f"Scan error: {e}")
        finally:
            self.is_scanning_flag = False
            self._scan_lock.release()
            self.add_ui_log("Cycle complete.")

    def execute_trade(self, pair, ai_result):
        token_address = pair['baseToken']
        self.add_ui_log(f"🚀 BELI: {pair['symbol']}")
        tx = dex.buy_token(token_address, Config.MAX_BNB_PER_TRADE)
        if tx:
            self.active_positions[pair['address']] = {
                "symbol": pair['symbol'], "entry": float(pair['price_usd']),
                "tp": ai_result['tp'], "sl": ai_result['sl'], "baseToken": token_address
            }
            self.save_positions()
            self.add_ui_log(f"✅ Berhasil: {pair['symbol']}")
        else:
            self.add_ui_log(f"❌ Gagal: {pair['symbol']}")

    def monitor_positions(self):
        for p in self.last_scan_results:
            addr = p['address'].lower()
            old = self.current_prices.get(addr, float(p['price_usd']))
            self.current_prices[addr] = old * (1 + random.uniform(-0.0001, 0.0001))

        if not self.active_positions: return

        total_profit = 0
        for addr, pos in self.active_positions.items():
            curr = self.current_prices.get(addr.lower(), pos['entry'])
            total_profit += ((curr - pos['entry']) / pos['entry']) * 100

        if total_profit >= Config.GLOBAL_TP_PCT:
            self.add_ui_log(f"🚀 GLOBAL TP REACHED! Closing all.")
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
        self.add_ui_log(f"🔔 {reason}: Menjual {pos['symbol']}...")
        tx = dex.sell_token(pos.get('baseToken'), 0)
        if tx:
            self.add_ui_log(f"💰 Closed: {pos['symbol']}")
            if addr in self.active_positions:
                del self.active_positions[addr]
            self.save_positions()
        else:
            self.add_ui_log(f"❌ Gagal jual: {pos['symbol']}")

strategy = ScalpingStrategy()
