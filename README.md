# 🛶 Handak Bajalan

Chatbot asisten wisata **Kalimantan Selatan** berbasis **Gemini API** dan **Streamlit**.
"Handak bajalan" berarti "mau jalan-jalan" dalam bahasa Banjar.

Final Project: *LLM-Based Tools and Gemini API Integration for Data Scientists*.

## Use Case
Travel assistant yang bertindak sebagai pemandu lokal untuk Kalimantan Selatan. Bot membantu
pengguna merencanakan itinerary, mencari destinasi, kuliner, dan oleh-oleh, dengan jawaban yang
disesuaikan dengan gaya liburan dan wilayah yang dipilih.

Cakupan keahlian:
- Wisata alam
- Wisata sungai dan budaya
- Kuliner khas Banjar
- Oleh-oleh dan kerajinan

## Parameter Kreatif
| Parameter | Fungsi |
|---|---|
| Logat (Banjar kental / Banjar ringan / Indonesia netral) | Mengubah gaya bahasa dan persona pemandu |
| Wilayah fokus (13 kabupaten/kota + semua Kalsel) | Mempersempit rekomendasi ke area tertentu |
| Gaya liburan (backpacker, keluarga, kuliner, petualangan alam, budaya) | Menyesuaikan jenis tempat dan ritme perjalanan |
| Temperature | Rendah = faktual dan konsisten, tinggi = kreatif dan bervariasi |
| Top-p | Mengatur keragaman pilihan kata |
| Mode faktual (Google Search grounding) | Memverifikasi info terkini dan menampilkan sumber |
| Memory | Seluruh riwayat percakapan dikirim ke model sehingga konteks terjaga |

## Pengurangan Halusinasi
Pengetahuan lokal Kalsel tidak selalu lengkap di model, sehingga dipakai pendekatan berlapis:
1. **Aturan di system prompt**: tidak mengarang nama tempat, tidak memberi angka pasti untuk harga/jam buka, dan boleh menjawab "tidak yakin".
2. **Label keyakinan**: ✅ untuk informasi umum yang stabil, ⚠️ untuk detail yang perlu dicek ulang.
3. **Google Search grounding** (opsional lewat toggle): jawaban disertai sumber.
4. **Fallback**: jika grounding atau model utama gagal, bot otomatis mencoba cara/model lain.

> Catatan: pendekatan ini **mengurangi** risiko halusinasi, tetapi tidak menghilangkannya.
> Informasi seperti harga dan jam buka tetap perlu diverifikasi sebelum bepergian.

## Teknologi
- Python 3.10+
- Streamlit
- Google Gen AI SDK (`google-genai`), model `gemini-2.5-flash` (cadangan `gemini-2.5-flash-lite`)

## Struktur Proyek
```
handak-bajalan/
├── app.py              # UI Streamlit dan logika chat
├── prompts.py          # Penyusunan system prompt
├── requirements.txt
├── .streamlit/config.toml   # Tema warna
├── .env.example        # Contoh konfigurasi API key
└── screenshots/        # Tangkapan layar antarmuka
```

## Cara Menjalankan
```bash
git clone <URL-REPOSITORI-ANDA>
cd handak-bajalan

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt

cp .env.example .env             # lalu isi GEMINI_API_KEY di file .env
python -m streamlit run app.py
```
API key gratis dapat dibuat di https://aistudio.google.com/apikey

## Screenshot
| Tampilan awal | Itinerary (logat Banjar kental) |
|---|---|
| ![Tampilan awal](screenshots/01-tampilan-awal.png) | ![Itinerary](screenshots/02-itinerary.png) |

| Kuliner dengan label ✅/⚠️ | Mode faktual dengan sumber |
|---|---|
| ![Kuliner](screenshots/03-kuliner-label.png) | ![Sumber](screenshots/04-sumber-grounding.png) |

| Temperature rendah vs tinggi | Penolakan topik di luar cakupan |
|---|---|
| ![Temperature](screenshots/05-temperature.png) | ![Penolakan](screenshots/06-penolakan.png) |

## Keterbatasan
- Bot dapat keliru pada detail lokal yang sangat spesifik.
- Grounding bergantung pada ketersediaan dan kuota API.
- Rekomendasi bersifat panduan awal, bukan pengganti informasi resmi pengelola wisata.