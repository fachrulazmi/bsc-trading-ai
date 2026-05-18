# BSC AI Scalping Bot (Scan-Analyze-Execute) - Pro Edition

Bot trading scalping otomatis untuk Binance Smart Chain (BSC) menggunakan **Gemini AI** untuk analisis teknikal mendalam dan **RTK AI** untuk efisiensi token.

## ⚠️ DISCLAIMER RISIKO FINANSIAL
**PENTING:** Perdagangan aset kripto memiliki risiko yang sangat tinggi. Bot ini disediakan **hanya untuk tujuan edukasi dan eksperimen**. **KAMI TIDAK BERTANGGUNG JAWAB** atas kerugian finansial, kesalahan sistem, atau kegagalan transaksi yang mungkin terjadi. Gunakan modal yang Anda siap untuk kehilangan. **Uji coba di Mode Testnet sangat disarankan sebelum menggunakan dana asli.**

## Fitur Utama & Keunggulan
- **Real-Time Dashboard**: Antarmuka terminal modern (4 FPS) dengan pembaruan harga dan profit instan.
- **Background Parallel Scanning**: Memindai peluang pasar secara terus-menerus tanpa mengganggu monitoring harga.
- **Gemini AI Analysis**: Menggunakan kecerdasan buatan untuk menentukan entri, TP, dan SL berdasarkan indikator teknis (EMA, RSI, MACD).
- **RTK (Rust Token Killer)**: Kompresi data cerdas untuk menghemat hingga 90% kuota token API Gemini.
- **Customizable Global Take Profit**: Amankan keuntungan seluruh portofolio secara otomatis.
- **Persistent Storage & Logs**: Menyimpan posisi terbuka ke `data/positions.json` dan mencatat seluruh audit trail ke `logs/trade_bot.log`.
- **Graceful Shutdown**: Penanganan thread yang aman saat bot dihentikan (Ctrl+C).

## Persyaratan Sistem
- **Python**: v3.10 ke atas (Teruji di v3.11/v3.12).
- **Node**: RPC/WSS (Websocket) BSC yang stabil.
- **Koneksi**: Internet stabil (disarankan VPS untuk penggunaan live).

## Instalasi
1. Clone atau download folder bot ini.
2. Dapatkan API Key Gemini GRATIS di [Google AI Studio](https://aistudio.google.com/).
3. Install semua library yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
   ```
4. Salin file `.env.example` menjadi `.env`:
   ```bash
   cp .env.example .env
   ```
5. Isi data sensitif Anda di `.env` (Private Key, Wallet Address, Gemini Key).

## Cara Menjalankan
```bash
py main.py
```

## Struktur Folder
- `/core`: Logika inti sistem (Strategi, Scanner, AI, Network).
- `/data`: Database transaksi aktif dan riwayat.
- `/logs`: File log aktivitas sistem untuk audit.
- `/scripts`: Script bantuan untuk pengujian manual.

## Keamanan & Kontrol
- **`DRY_RUN=True`**: Bot hanya mensimulasikan transaksi (tanpa uang asli).
- **`USE_TESTNET=True`**: Menggunakan jaringan BSC Testnet.
- **`AI_COOLDOWN`**: Jeda antar analisis untuk mencegah limitasi API Gemini.
