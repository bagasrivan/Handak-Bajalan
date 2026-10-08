import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import build_system_prompt

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_UTAMA = "gemini-3.6-flash"
MODEL_CADANGAN = "gemini-3.8-flash"

WILAYAH = [
    "Semua Kalsel", "Banjarmasin", "Banjarbaru", "Banjar", "Barito Kuala",
    "Tapin", "Hulu Sungai Selatan", "Hulu Sungai Tengah", "Hulu Sungai Utara",
    "Balangan", "Tabalong", "Tanah Laut", "Tanah Bumbu", "Kotabaru",
]
GAYA_LIBURAN = ["Backpacker hemat", "Keluarga", "Kuliner", "Petualangan alam", "Budaya"]

SAPAAN = {
    "Banjar kental": "Halo, Sanak Sabarataan! Ulun **Handak Bajalan**, pemandu wisata banua Kalimantan Selatan. "
                     "Handak bajalan ka mana kita hari ini? Tanyakan saja, ulun bantu rancang "
                     "jalan-jalan pian. 🛶",
    "Banjar ringan": "Halo, Sanak! Ulun **Handak Bajalan**, teman jalan-jalan pian menjelajahi "
                     "Kalimantan Selatan. Mau wisata alam, kuliner, atau susur sungai? "
                     "Ayo, kita rencanakan! 🛶",
    "Indonesia netral": "Halo! Saya **Handak Bajalan**, asisten wisata Kalimantan Selatan. "
                        "Mau cari wisata alam, kuliner, budaya, atau oleh-oleh? Tanyakan saja, "
                        "saya bantu rencanakan perjalananmu. 🛶",
}

QUICK_PROMPTS = [
    ("🌿 Wisata alam", "Rekomendasi wisata alam di Kalimantan Selatan untuk akhir pekan"),
    ("🛶 Sungai & budaya", "Apa saja yang bisa dilakukan di wisata sungai dan budaya Banjar?"),
    ("🍜 Kuliner khas", "Makanan khas Banjar apa yang wajib dicoba?"),
    ("🎁 Oleh-oleh", "Rekomendasi oleh-oleh khas Kalimantan Selatan"),
]

st.set_page_config(page_title="Handak Bajalan", page_icon="🛶")

# ------------------------------------------------------------ Sidebar
with st.sidebar:
    st.header("⚙️ Pengaturan")

    logat = st.radio("Logat", ["Banjar kental", "Banjar ringan", "Indonesia netral"], index=1)
    wilayah = st.selectbox("Wilayah fokus", WILAYAH)
    gaya = st.selectbox("Gaya liburan", GAYA_LIBURAN)

    st.subheader("🔎 Mode Faktual")
    grounding = st.toggle(
        "Verifikasi dengan Google Search",
        value=True,
        help="Bot mengecek informasi terkini (harga, jam buka, dll.) lewat Google Search "
             "dan menampilkan sumbernya. Jika tidak tersedia, bot memakai pengetahuan model saja.",
    )

    if st.button("🗑️ Reset percakapan", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending = None
        st.rerun()

# ------------------------------------------------------------ Fungsi bantu
def ambil_sumber(response):
    """Ambil daftar (judul, url) dari metadata grounding, tanpa duplikat."""
    hasil, terlihat = [], set()
    try:
        meta = response.candidates[0].grounding_metadata
        for chunk in (meta.grounding_chunks or []):
            if chunk.web and chunk.web.uri not in terlihat:
                terlihat.add(chunk.web.uri)
                hasil.append((chunk.web.title or chunk.web.uri, chunk.web.uri))
    except Exception:
        pass
    return hasil


def tampil_sumber(sumber):
    if sumber:
        with st.expander(f"📚 Sumber ({len(sumber)})"):
            for judul, url in sumber:
                st.markdown(f"- [{judul}]({url})")


def tanya_gemini(contents, system_prompt, pakai_grounding):
    """Urutan percobaan: (grounding x2) -> model utama tanpa grounding -> model cadangan."""
    rencana = []
    if pakai_grounding:
        rencana += [(MODEL_UTAMA, True)] * 2
    rencana += [(MODEL_UTAMA, False), (MODEL_CADANGAN, False)]

    galat_terakhir = None
    for model, dengan_grounding in rencana:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[types.Tool(google_search=types.GoogleSearch())] if dengan_grounding else None,
        )
        try:
            r = client.models.generate_content(model=model, contents=contents, config=config)
            if r.text:
                return r.text, ambil_sumber(r), dengan_grounding
        except Exception as e:
            galat_terakhir = e
            time.sleep(2)
    raise galat_terakhir or RuntimeError("Model tidak mengembalikan jawaban.")


# ------------------------------------------------------------ Header & riwayat
st.title("🛶 Handak Bajalan")
st.caption("Asisten wisata Kalimantan Selatan")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        tampil_sumber(m.get("sumber"))

# Sapaan dan quick prompt hanya tampil saat chat masih kosong.
# Sapaan tidak disimpan ke riwayat supaya percakapan ke Gemini tetap diawali pesan user.
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(SAPAAN[logat])
    kol = st.columns(2)
    for i, (label, teks) in enumerate(QUICK_PROMPTS):
        if kol[i % 2].button(label, use_container_width=True, key=f"qp{i}"):
            st.session_state.pending = teks
            st.rerun()

# ------------------------------------------------------------ Chat
prompt = st.chat_input("Handak bajalan ka mana?")
if not prompt and st.session_state.pending:
    prompt, st.session_state.pending = st.session_state.pending, None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])],
        )
        for m in st.session_state.messages
    ]

    system_prompt = build_system_prompt(logat, wilayah, gaya, grounding)

    with st.chat_message("assistant"):
        with st.spinner("Sabantar, ulun cari dulu..."):
            sumber, dipakai = [], False
            try:
                jawaban, sumber, dipakai = tanya_gemini(
                    contents, system_prompt, grounding
                )
            except Exception as e:
                jawaban = f"⚠️ Server Gemini sedang sibuk atau bermasalah. Coba lagi sebentar.\n\n`{e}`"
        st.markdown(jawaban)
        tampil_sumber(sumber)
        if grounding and not dipakai:
            st.caption("ℹ️ Pencarian Google tidak tersedia, jawaban memakai pengetahuan model.")

    st.session_state.messages.append(
        {"role": "assistant", "content": jawaban, "sumber": sumber}
    )