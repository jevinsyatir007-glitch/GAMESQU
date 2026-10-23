"""
Robot Mini — permainan coding sederhana untuk anak (Streamlit)

Cara menjalankan:
    pip install streamlit
    streamlit run app.py

Anak menekan tombol panah untuk menyusun "program", lalu menekan JALAN.
Robot bergerak sesuai urutan kartu. Kalau meleset, perbaiki kartunya (debugging).
"""

import time

import streamlit as st

# ---------------------------------------------------------------------------
# Data level
# arah: 0 = atas, 1 = kanan, 2 = bawah, 3 = kiri
# ---------------------------------------------------------------------------
LEVELS = [
    {
        "nama": "Level 1 - Maju Terus",
        "petunjuk": "Bola ada di depan robot. Tekan MAJU sampai robot ketemu bola!",
        "ukuran": 4,
        "start": (3, 1),
        "arah": 0,
        "target": (1, 1),
        "rintangan": [],
    },
    {
        "nama": "Level 2 - Belok Satu Kali",
        "petunjuk": "Robot harus belok untuk sampai ke bola.",
        "ukuran": 4,
        "start": (3, 0),
        "arah": 0,
        "target": (1, 2),
        "rintangan": [],
    },
    {
        "nama": "Level 3 - Rencana Panjang",
        "petunjuk": "Susun beberapa kartu dulu, baru tekan JALAN.",
        "ukuran": 5,
        "start": (4, 0),
        "arah": 1,
        "target": (0, 4),
        "rintangan": [],
    },
    {
        "nama": "Level 4 - Awas Batu!",
        "petunjuk": "Jangan tabrak batu. Cari jalan memutar.",
        "ukuran": 5,
        "start": (4, 0),
        "arah": 0,
        "target": (0, 2),
        "rintangan": [(2, 0), (2, 1), (1, 3)],
    },
    {
        "nama": "Level 5 - Gawang!",
        "petunjuk": "Bawa robot ke gawang. Hati-hati banyak batu.",
        "ukuran": 5,
        "start": (4, 4),
        "arah": 3,
        "target": (0, 0),
        "rintangan": [(3, 1), (3, 2), (1, 1), (1, 2), (2, 4)],
    },
]

GERAK = {0: (-1, 0), 1: (0, 1), 2: (1, 0), 3: (0, -1)}
PANAH_ARAH = {0: "⬆️", 1: "➡️", 2: "⬇️", 3: "⬅️"}
KARTU = {
    "maju": ("⬆️", "MAJU", "#2e9e5b"),
    "kiri": ("↩️", "KIRI", "#2f6fd6"),
    "kanan": ("↪️", "KANAN", "#e8833a"),
}


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
def reset_robot():
    lv = LEVELS[st.session_state.level]
    st.session_state.pos = lv["start"]
    st.session_state.arah = lv["arah"]
    st.session_state.pesan = ("info", lv["petunjuk"])


def init_state():
    if "level" not in st.session_state:
        st.session_state.level = 0
        st.session_state.program = []
        st.session_state.bintang = 0
        st.session_state.berhasil = [False] * len(LEVELS)
        reset_robot()


def langkah(pos, arah, perintah, lv):
    """Jalankan satu perintah. Kembalikan (pos, arah, error)."""
    if perintah == "kiri":
        return pos, (arah - 1) % 4, None
    if perintah == "kanan":
        return pos, (arah + 1) % 4, None
    dr, dc = GERAK[arah]
    baru = (pos[0] + dr, pos[1] + dc)
    n = lv["ukuran"]
    if not (0 <= baru[0] < n and 0 <= baru[1] < n):
        return pos, arah, "Duk! Robot menabrak pinggir papan."
    if baru in lv["rintangan"]:
        return pos, arah, "Aduh! Robot menabrak batu."
    return baru, arah, None


# ---------------------------------------------------------------------------
# Tampilan papan
# ---------------------------------------------------------------------------
def gambar_papan(pos, arah, lv, sorot=None):
    n = lv["ukuran"]
    sel = 92 if n == 4 else 76
    baris_html = []
    for r in range(n):
        kolom = []
        for c in range(n):
            isi = ""
            latar = "#f4efe3" if (r + c) % 2 == 0 else "#ebe4d3"
            if (r, c) in lv["rintangan"]:
                isi = "🪨"
            if (r, c) == lv["target"]:
                isi = "⚽" if LEVELS.index(lv) < 4 else "🥅"
                latar = "#fff3b0"
            if (r, c) == pos:
                isi = (
                    f"<div style='line-height:1'>🤖</div>"
                    f"<div style='font-size:0.45em;line-height:1.2'>{PANAH_ARAH[arah]}</div>"
                )
                latar = "#cfe8ff"
            if (r, c) == pos and pos == lv["target"]:
                isi = "<div style='line-height:1'>🤖⚽</div><div style='font-size:0.45em'>🎉</div>"
                latar = "#c9f2c7"
            kolom.append(
                f"<td style='width:{sel}px;height:{sel}px;background:{latar};"
                f"text-align:center;vertical-align:middle;font-size:{int(sel * 0.48)}px;"
                f"border:3px solid #fff;border-radius:14px'>{isi}</td>"
            )
        baris_html.append("<tr>" + "".join(kolom) + "</tr>")
    return (
        "<table style='border-collapse:separate;border-spacing:4px;margin:auto'>"
        + "".join(baris_html)
        + "</table>"
    )


def gambar_program(program, aktif=None):
    if not program:
        return (
            "<div style='padding:14px;border:3px dashed #bbb;border-radius:16px;"
            "text-align:center;color:#888;font-size:20px'>Belum ada kartu. Tekan tombol panah! 👇</div>"
        )
    kartu = []
    for i, p in enumerate(program):
        ikon, nama, warna = KARTU[p]
        tebal = "6px solid #ffd400" if i == aktif else "3px solid transparent"
        kartu.append(
            f"<div style='display:inline-block;margin:4px;padding:6px 10px;border-radius:14px;"
            f"background:{warna};color:#fff;text-align:center;border:{tebal};min-width:64px'>"
            f"<div style='font-size:34px'>{ikon}</div>"
            f"<div style='font-size:13px;font-weight:700'>{i + 1}. {nama}</div></div>"
        )
    return "<div style='text-align:center'>" + "".join(kartu) + "</div>"


# ---------------------------------------------------------------------------
# Aksi tombol
# ---------------------------------------------------------------------------
def tambah(perintah):
    if st.session_state.langsung:
        # Mode langsung (anak 3 tahun): tiap tombol langsung menggerakkan robot
        lv = LEVELS[st.session_state.level]
        pos, arah, err = langkah(st.session_state.pos, st.session_state.arah, perintah, lv)
        st.session_state.pos, st.session_state.arah = pos, arah
        if err:
            st.session_state.pesan = ("warning", err + " Coba arah lain ya!")
        elif pos == lv["target"]:
            selesai_level()
        else:
            st.session_state.pesan = ("info", "Bagus! Terus...")
    else:
        if len(st.session_state.program) < 12:
            st.session_state.program.append(perintah)


def hapus_terakhir():
    if st.session_state.program:
        st.session_state.program.pop()


def ulang():
    st.session_state.program = []
    reset_robot()


def selesai_level():
    i = st.session_state.level
    if not st.session_state.berhasil[i]:
        st.session_state.berhasil[i] = True
        st.session_state.bintang += 1
    st.session_state.pesan = ("success", "HORE! Robot sampai! ⭐ Kamu hebat!")
    st.session_state.rayakan = True


def ganti_level(i):
    st.session_state.level = i
    st.session_state.program = []
    reset_robot()


# ---------------------------------------------------------------------------
# Halaman
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Robot Mini", page_icon="🤖", layout="centered")
init_state()

st.markdown(
    """
    <style>
    div.stButton > button {
        height: 86px; border-radius: 20px;
    }
    div.stButton > button p, div.stButton > button div {
        font-size: 30px !important; font-weight: 700 !important;
    }
    .block-container { padding-top: 1.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("👨👩👧 Untuk Orang Tua")
    st.toggle(
        "Mode langsung (usia 3 th)",
        key="langsung",
        value=True,
        help="Tiap tombol langsung menggerakkan robot. Matikan untuk mode 'susun dulu, baru JALAN' (usia 4+).",
    )
    pilihan = st.radio(
        "Pilih level",
        list(range(len(LEVELS))),
        index=st.session_state.level,
        format_func=lambda i: LEVELS[i]["nama"],
    )
    if pilihan != st.session_state.level:
        ganti_level(pilihan)
        st.rerun()
    st.markdown(f"### ⭐ Bintang: {st.session_state.bintang} / {len(LEVELS)}")
    st.markdown(" ".join("⭐" if b else "☆" for b in st.session_state.berhasil))
    st.caption(
        "Batasi 10–15 menit per sesi dan temani anak. "
        "Saat robot meleset, ajak anak mencari kartu yang salah: itulah debugging."
    )

lv = LEVELS[st.session_state.level]
st.markdown(f"<h2 style='text-align:center;margin:0'>🤖 Robot Mini — {lv['nama']}</h2>", unsafe_allow_html=True)

jenis, isi = st.session_state.pesan
getattr(st, jenis)(isi)

papan = st.empty()
papan.markdown(gambar_papan(st.session_state.pos, st.session_state.arah, lv), unsafe_allow_html=True)

if st.session_state.pop("rayakan", False):
    st.balloons()

st.write("")
c1, c2, c3 = st.columns(3)
c1.button("↩️ KIRI", on_click=tambah, args=("kiri",), use_container_width=True)
c2.button("⬆️ MAJU", on_click=tambah, args=("maju",), use_container_width=True)
c3.button("↪️ KANAN", on_click=tambah, args=("kanan",), use_container_width=True)

if not st.session_state.langsung:
    st.markdown("#### 🧩 Program robot")
    kotak_program = st.empty()
    kotak_program.markdown(gambar_program(st.session_state.program), unsafe_allow_html=True)

    d1, d2, d3 = st.columns([2, 1, 1])
    jalan = d1.button("▶️ JALAN!", type="primary", use_container_width=True)
    d2.button("⌫ Hapus", on_click=hapus_terakhir, use_container_width=True)
    d3.button("🔄 Ulang", on_click=ulang, use_container_width=True)

    if jalan and st.session_state.program:
        pos, arah = lv["start"], lv["arah"]
        papan.markdown(gambar_papan(pos, arah, lv), unsafe_allow_html=True)
        error = None
        for i, perintah in enumerate(st.session_state.program):
            kotak_program.markdown(gambar_program(st.session_state.program, aktif=i), unsafe_allow_html=True)
            time.sleep(0.6)
            pos, arah, error = langkah(pos, arah, perintah, lv)
            papan.markdown(gambar_papan(pos, arah, lv), unsafe_allow_html=True)
            if error:
                break
        time.sleep(0.4)
        st.session_state.pos, st.session_state.arah = pos, arah
        if error:
            st.session_state.pesan = ("warning", f"{error} Kartu nomor {i + 1} perlu diperbaiki 🔧")
        elif pos == lv["target"]:
            selesai_level()
        else:
            st.session_state.pesan = ("warning", "Hampir! Robot belum sampai bola. Tambah atau ganti kartunya 🔧")
        st.rerun()
else:
    st.button("🔄 Mulai lagi", on_click=ulang, use_container_width=True)
