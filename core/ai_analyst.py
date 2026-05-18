from openai import OpenAI
from config import Config

class AIAnalyst:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def analyze_market(self, token_data):
        if not Config.OPENAI_API_KEY:
            print("Peringatan: OPENAI_API_KEY tidak ditemukan. Menggunakan analisis dasar.")
            return "HOLD"

        prompt = f"""
        Anda adalah analis trading crypto pro untuk BSC.
        Data Token:
        - Symbol: {token_data.get('symbol')}
        - Address: {token_data.get('address')}
        - Harga Sekarang (BNB): {token_data.get('current_price')}
        - Riwayat Harga Singkat: {token_data.get('history')}
        - Volume 24 jam: {token_data.get('volume')}

        Berdasarkan data di atas untuk strategi SCALPING cepat, apa tindakan yang harus diambil?
        Berikan jawaban dalam format JSON:
        {{
            "signal": "BUY" | "SELL" | "HOLD",
            "confidence": 0-100,
            "reason": "alasan singkat"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=Config.AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            result = response.choices[0].message.content
            import json
            return json.loads(result)
        except Exception as e:
            print(f"Error AI Analysis: {e}")
            return {"signal": "HOLD", "confidence": 0, "reason": "Error connecting to AI"}

ai_analyst = AIAnalyst()
