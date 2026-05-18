import pandas as pd
import google.generativeai as genai
from core.config import Config
import json
import subprocess

class Analyzer:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.AI_MODEL)

    def _rtk_compress(self, data):
        try:
            json_str = json.dumps(data)
            result = subprocess.run(['rtk', 'json'], input=json_str, capture_output=True, text=True, shell=True)
            return result.stdout.strip() if result.returncode == 0 else json_str
        except:
            return json.dumps(data)

    def calculate_indicators(self, price_history):
        df = pd.DataFrame(price_history, columns=['close'])
        df['ema_fast'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=21, adjust=False).mean()
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        return df.tail(1).to_dict('records')[0]

    def analyze_with_gemini(self, pair_data, technicals):
        if not Config.GEMINI_API_KEY:
            return {"decision": "HOLD", "reason": "No Gemini API Key"}
        compressed_market = self._rtk_compress(pair_data)
        compressed_tech = self._rtk_compress(technicals)
        prompt = f"""
        Tugas: Analisis Trading Crypto Scalping (BSC)
        Data Terkompresi (RTK-Optimized):
        Market: {compressed_market}
        Technicals: {compressed_tech}
        Interpretasikan sinyal ini. Berikan keputusan apakah harus Entry BUY sekarang untuk scalping cepat.
        Berikan jawaban dalam format JSON:
        {{
            "decision": "BUY" | "HOLD",
            "entry_price": float,
            "tp": float,
            "sl": float,
            "risk_reward": string,
            "reason": "rangkuman singkat maksimal 15 kata"
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_json)
        except Exception as e:
            from rich.console import Console
            from rich.panel import Panel
            Console().print(Panel(f"[bold red]AI Analysis Failed[/bold red]\n[dim]{e}[/dim]", border_style="red", title="Gemini Error"))
            return {"decision": "HOLD", "reason": "AI Error"}

analyzer = Analyzer()
