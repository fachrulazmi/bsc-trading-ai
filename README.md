# BSC AI Scalping Bot (Scan-Analyze-Execute)

Bot trading scalping otomatis untuk Binance Smart Chain (BSC) menggunakan **Gemini 1.5 Flash (Free Tier)** untuk analisis teknikal mendalam.

## Alur Kerja 3-Fase
1.  **Phase 1 — SCAN**: Memindai seluruh pair di PancakeSwap BSC yang memiliki Volume 24 jam > $1M dan likuiditas memadai.
2.  **Phase 2 — ANALISIS**: Menghitung indikator (EMA, RSI, MACD) dan menggunakan Gemini AI untuk menginterpretasi sinyal, menentukan TP/SL, dan menilai Risk/Reward.
3.  **Phase 3 — EKSEKUSI**: Eksekusi trade otomatis di BSC dengan manajemen risiko ketat.

## Persiapan
1. Dapatkan Gemini API Key GRATIS di [Google AI Studio](https://aistudio.google.com/).
2. Install dependencies: `pip install -r requirements.txt`.
3. Konfigurasi file `.env` (gunakan `.env.example` sebagai template).

## Keunggulan Solusi 1 (Gemini Free Tier)
- **Gratis Selamanya**: Menggunakan kuota gratis dari Google.
- **Stabil**: Rate limit yang cukup luas (15 request/menit).
- **Cepat**: Gemini 1.5 Flash dirancang untuk respon instan.
