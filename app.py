"""
Robot Mini — Permainan Coding Sederhana untuk Anak (Streamlit)
Dengan Visual 3D Isometrik Bergerak & Efek Suara (SFX).

Cara menjalankan:
    streamlit run app.py
"""

import math
import struct
import time

import streamlit as st

# ---------------------------------------------------------------------------
# Generator Efek Suara (WAV Sintesis Tanpa Library Eksternal)
# ---------------------------------------------------------------------------
def buat_wav(nada_list, sample_rate=22050):
    """Membuat data WAV mono 16-bit PCM dari daftar nada."""
    raw_samples = []
    for freq, durasi, bentuk, vol in nada_list:
        total_samples = int(sample_rate * durasi)
        for i in range(total_samples):
            t = i / sample_rate
            fade = 1.0 - (i / total_samples)
            if bentuk == "sine":
                val = math.sin(2 * math.pi * freq * t)
            elif bentuk == "square":
                val = 0.5 if (math.sin(2 * math.pi * freq * t) > 0) else -0.5
            elif bentuk == "triangle":
                val = 2.0 * abs(2.0 * (t * freq - math.floor(0.5 + t * freq))) - 1.0
            else:
                val = math.sin(2 * math.pi * freq * t)
            sample = int(val * fade * 32767 * vol)
            raw_samples.append(sample)

    byte_data = bytearray()
    for s in raw_samples:
        byte_data.extend(struct.pack("<h", max(-32768, min(32767, s))))

    wav = bytearray()
    data_size = len(byte_data)
    wav.extend(b"RIFF")
    wav.extend(struct.pack("<I", 36 + data_size))
    wav.extend(b"WAVEfmt ")
    wav.extend(struct.pack("<I", 16))
    wav.extend(struct.pack("<H", 1))
    wav.extend(struct.pack("<H", 1))
    wav.extend(struct.pack("<I", sample_rate))
    wav.extend(struct.pack("<I", sample_rate * 2))
    wav.extend(struct.pack("<H", 2))
    wav.extend(struct.pack("<H", 16))
    wav.extend(b"data")
    wav.extend(struct.pack("<I", data_size))
    wav.extend(byte_data)
    return bytes(wav)


DAFTAR_SUARA = {
    "maju": buat_wav([(480, 0.05, "triangle", 0.45), (720, 0.08, "triangle", 0.45)]),
    "kiri": buat_wav([(380, 0.05, "sine", 0.4), (540, 0.08, "sine", 0.4)]),
    "kanan": buat_wav([(540, 0.05, "sine", 0.4), (380, 0.08, "sine", 0.4)]),
    "tabrak": buat_wav([(160, 0.09, "square", 0.5), (75, 0.18, "square", 0.6)]),
    "menang": buat_wav([
        (523, 0.09, "sine", 0.45),
        (659, 0.09, "sine", 0.45),
        (784, 0.11, "sine", 0.45),
        (1046, 0.32, "triangle", 0.55),
    ]),
    "klik": buat_wav([(650, 0.04, "sine", 0.3)]),
    "hapus": buat_wav([(450, 0.04, "sine", 0.35), (280, 0.06, "sine", 0.35)]),
    "ulang": buat_wav([(520, 0.05, "triangle", 0.3), (320, 0.08, "triangle", 0.3)]),
}


# ---------------------------------------------------------------------------
# Data Level
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
DERAJAT_ARAH = {0: 0, 1: 90, 2: 180, 3: 270}
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
    st.session_state.status_animasi = "diam"


def init_state():
    if "level" not in st.session_state:
        st.session_state.level = 0
        st.session_state.program = []
        st.session_state.bintang = 0
        st.session_state.berhasil = [False] * len(LEVELS)
        st.session_state.suara = None
        st.session_state.status_animasi = "diam"
        st.session_state.tampilan_3d = "🌟 3D Isometrik"
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
# Tampilan Papan 3D Bergerak
# ---------------------------------------------------------------------------
def gambar_papan_3d(pos, arah, lv, status_animasi="diam", mode_tampilan="🌟 3D Isometrik"):
    n = lv["ukuran"]
    tile = 80 if n == 4 else 66
    gap = 8 if n == 4 else 6
    pad = 14
    board_size = pad * 2 + n * tile + (n - 1) * gap

    # Sudut pandang kamera 3D
    if mode_tampilan == "🌟 3D Isometrik":
        transform_board = "rotateX(48deg) rotateZ(-22deg)"
        box_shadow_depth = "-12px 18px 0px #1e293b, -18px 26px 36px rgba(0,0,0,0.35)"
    elif mode_tampilan == "📐 3D Miring Ringan":
        transform_board = "rotateX(28deg) rotateZ(-10deg)"
        box_shadow_depth = "-8px 12px 0px #1e293b, -12px 18px 24px rgba(0,0,0,0.25)"
    else:  # 2D Datar
        transform_board = "none"
        box_shadow_depth = "0 8px 24px rgba(0,0,0,0.12)"

    # Kelas animasi robot
    anim_robot_class = "robot-idle-bob"
    if status_animasi == "tabrak":
        anim_robot_class = "robot-tabrak-shake"
    elif status_animasi == "menang":
        anim_robot_class = "robot-menang-spin"

    tiles_html = []
    entities_html = []

    for r in range(n):
        for c in range(n):
            top = pad + r * (tile + gap)
            left = pad + c * (tile + gap)
            is_target = (r, c) == lv["target"]
            is_rock = (r, c) in lv["rintangan"]

            # Latar ubin 3D kotak-kotak lembut
            bg_color = "#f8fafc" if (r + c) % 2 == 0 else "#e2e8f0"
            tile_shadow = "inset 0 2px 0 rgba(255,255,255,0.8), 0 3px 6px rgba(0,0,0,0.08)"
            extra_style = ""

            if is_target:
                bg_color = "linear-gradient(135deg, #fef08a, #facc15)"
                extra_style = "box-shadow: 0 0 16px rgba(250, 204, 21, 0.7), inset 0 2px 4px #fff; border: 2px dashed #ca8a04;"

            tiles_html.append(
                f"<div style='position:absolute;top:{top}px;left:{left}px;width:{tile}px;height:{tile}px;"
                f"background:{bg_color};border-radius:14px;box-shadow:{tile_shadow};{extra_style}'></div>"
            )

            # Rintangan batu 3D
            if is_rock:
                entities_html.append(
                    f"<div class='rock-3d-entity' style='position:absolute;top:{top}px;left:{left}px;"
                    f"width:{tile}px;height:{tile}px;display:flex;align-items:center;justify-content:center;'>"
                    f"<div class='rock-shadow'></div>"
                    f"<div class='rock-body' style='font-size:{int(tile * 0.58)}px'>🪨</div>"
                    f"</div>"
                )

            # Target 3D (Bola atau Gawang) dengan animasi melayang membal
            if is_target:
                ikon_target = "⚽" if LEVELS.index(lv) < 4 else "🥅"
                entities_html.append(
                    f"<div class='target-3d-entity' style='position:absolute;top:{top}px;left:{left}px;"
                    f"width:{tile}px;height:{tile}px;display:flex;align-items:center;justify-content:center;'>"
                    f"<div class='target-shadow'></div>"
                    f"<div class='target-bounce' style='font-size:{int(tile * 0.55)}px'>{ikon_target}</div>"
                    f"</div>"
                )

    # Posisi koordinat robot saat ini
    r_rob, c_rob = pos
    r_top = pad + r_rob * (tile + gap)
    r_left = pad + c_rob * (tile + gap)
    rot_deg = DERAJAT_ARAH.get(arah, 0)

    # Robot 3D dengan transform translate3d mulus & bayangan dinamis
    entities_html.append(
        f"<div class='robot-3d-container' style='top:{r_top}px;left:{r_left}px;width:{tile}px;height:{tile}px;'>"
        f"  <div class='robot-ground-shadow'></div>"
        f"  <div class='robot-turner' style='transform:rotate({rot_deg}deg);'>"
        f"    <div class='{anim_robot_class} robot-avatar' style='font-size:{int(tile * 0.56)}px;'>"
        f"      🤖"
        f"      <div class='robot-laser-arrow'>{PANAH_ARAH[arah]}</div>"
        f"    </div>"
        f"  </div>"
        f"</div>"
    )

    return f"""
    <style>
    /* Stage 3D Perspective */
    .stage-3d-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        perspective: 900px;
        padding: 24px 0 36px 0;
        overflow: visible;
    }}
    .board-3d {{
        position: relative;
        width: {board_size}px;
        height: {board_size}px;
        transform-style: preserve-3d;
        transform: {transform_board};
        border-radius: 22px;
        background: linear-gradient(145deg, #334155, #1e293b);
        box-shadow: {box_shadow_depth};
        transition: transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
        border: 4px solid #475569;
    }}

    /* Target Animasi 3D Bouncing */
    .target-3d-entity {{
        pointer-events: none;
    }}
    .target-bounce {{
        animation: targetFloat 1.2s ease-in-out infinite alternate;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
    }}
    .target-shadow {{
        position: absolute;
        width: 60%;
        height: 25%;
        bottom: 8%;
        background: radial-gradient(ellipse at center, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 70%);
        animation: shadowPulse 1.2s ease-in-out infinite alternate;
        border-radius: 50%;
    }}

    /* Rintangan Batu 3D */
    .rock-3d-entity {{
        pointer-events: none;
    }}
    .rock-body {{
        transform: translateY(-4px);
        filter: drop-shadow(-4px 8px 6px rgba(0,0,0,0.35));
    }}
    .rock-shadow {{
        position: absolute;
        width: 70%;
        height: 28%;
        bottom: 6%;
        background: radial-gradient(ellipse at center, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0) 70%);
        border-radius: 50%;
    }}

    /* Robot 3D Entities & Transitions */
    .robot-3d-container {{
        position: absolute;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: top 0.45s cubic-bezier(0.34, 1.45, 0.64, 1), 
                    left 0.45s cubic-bezier(0.34, 1.45, 0.64, 1);
        z-index: 20;
        pointer-events: none;
    }}
    .robot-turner {{
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.4s cubic-bezier(0.34, 1.4, 0.64, 1);
    }}
    .robot-ground-shadow {{
        position: absolute;
        width: 68%;
        height: 26%;
        bottom: 6%;
        background: radial-gradient(ellipse at center, rgba(15, 23, 42, 0.6) 0%, rgba(0,0,0,0) 70%);
        border-radius: 50%;
        animation: shadowPulse 0.9s ease-in-out infinite alternate;
    }}
    .robot-avatar {{
        position: relative;
        filter: drop-shadow(0 8px 12px rgba(0,0,0,0.35));
        line-height: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    .robot-laser-arrow {{
        position: absolute;
        top: -10px;
        font-size: 16px;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));
    }}

    /* Keyframe Animations */
    @keyframes targetFloat {{
        0% {{ transform: translateY(0px) scale(1); }}
        100% {{ transform: translateY(-12px) scale(1.08); }}
    }}
    @keyframes shadowPulse {{
        0% {{ transform: scale(1); opacity: 0.6; }}
        100% {{ transform: scale(0.7); opacity: 0.25; }}
    }}
    @keyframes robotBob {{
        0% {{ transform: translateY(0px) scale(1); }}
        100% {{ transform: translateY(-8px) scale(1.05); }}
    }}
    @keyframes bumpWobble {{
        0%, 100% {{ transform: translateX(0) scale(1); }}
        20% {{ transform: translateX(-9px) rotate(-8deg) scale(0.95); }}
        40% {{ transform: translateX(9px) rotate(8deg) scale(1.1); }}
        60% {{ transform: translateX(-6px) rotate(-4deg); }}
        80% {{ transform: translateX(4px) rotate(2deg); }}
    }}
    @keyframes victorySpin3D {{
        0% {{ transform: translateY(0) rotate(0deg) scale(1); }}
        40% {{ transform: translateY(-26px) rotate(180deg) scale(1.3); }}
        80% {{ transform: translateY(-10px) rotate(360deg) scale(1.15); }}
        100% {{ transform: translateY(0) rotate(360deg) scale(1); }}
    }}

    .robot-idle-bob {{
        animation: robotBob 0.9s ease-in-out infinite alternate;
    }}
    .robot-tabrak-shake {{
        animation: bumpWobble 0.5s ease-in-out;
    }}
    .robot-menang-spin {{
        animation: victorySpin3D 0.9s cubic-bezier(0.2, 0.8, 0.2, 1);
    }}
    </style>

    <div class='stage-3d-wrapper'>
      <div class='board-3d'>
        {''.join(tiles_html)}
        {''.join(entities_html)}
      </div>
    </div>
    """


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
            f"background:{warna};color:#fff;text-align:center;border:{tebal};min-width:64px;"
            f"box-shadow:0 4px 10px rgba(0,0,0,0.15)'>"
            f"<div style='font-size:34px'>{ikon}</div>"
            f"<div style='font-size:13px;font-weight:700'>{i + 1}. {nama}</div></div>"
        )
    return "<div style='text-align:center'>" + "".join(kartu) + "</div>"


# ---------------------------------------------------------------------------
# Aksi Tombol
# ---------------------------------------------------------------------------
def tambah(perintah):
    if st.session_state.langsung:
        lv = LEVELS[st.session_state.level]
        pos, arah, err = langkah(st.session_state.pos, st.session_state.arah, perintah, lv)
        st.session_state.pos, st.session_state.arah = pos, arah
        if err:
            st.session_state.pesan = ("warning", err + " Coba arah lain ya!")
            st.session_state.suara = "tabrak"
            st.session_state.status_animasi = "tabrak"
        elif pos == lv["target"]:
            selesai_level()
        else:
            st.session_state.pesan = ("info", "Bagus! Terus...")
            st.session_state.suara = perintah
            st.session_state.status_animasi = "diam"
    else:
        if len(st.session_state.program) < 12:
            st.session_state.program.append(perintah)
            st.session_state.suara = "klik"


def hapus_terakhir():
    if st.session_state.program:
        st.session_state.program.pop()
        st.session_state.suara = "hapus"


def ulang():
    st.session_state.program = []
    st.session_state.suara = "ulang"
    reset_robot()


def selesai_level():
    i = st.session_state.level
    if not st.session_state.berhasil[i]:
        st.session_state.berhasil[i] = True
        st.session_state.bintang += 1
    st.session_state.pesan = ("success", "HORE! Robot sampai! ⭐ Kamu hebat!")
    st.session_state.rayakan = True
    st.session_state.suara = "menang"
    st.session_state.status_animasi = "menang"


def ganti_level(i):
    st.session_state.level = i
    st.session_state.program = []
    st.session_state.suara = "klik"
    reset_robot()


# ---------------------------------------------------------------------------
# Halaman Utama
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Robot Mini 3D", page_icon="🤖", layout="centered")
init_state()

st.markdown(
    """
    <style>
    div.stButton > button {
        height: 86px; border-radius: 20px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.12);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.18);
    }
    div.stButton > button p, div.stButton > button div {
        font-size: 30px !important; font-weight: 700 !important;
    }
    .block-container { padding-top: 1.2rem; }
    div[data-testid="stAudio"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

wadah_suara = st.empty()

with st.sidebar:
    st.header("👨👩👧 Untuk Orang Tua")

    tampilan = st.radio(
        "Kamera & Tampilan Papan",
        ["🌟 3D Isometrik", "📐 3D Miring Ringan", "📋 2D Datar"],
        index=["🌟 3D Isometrik", "📐 3D Miring Ringan", "📋 2D Datar"].index(st.session_state.tampilan_3d),
        help="Pilih perspektif visual 3D yang paling disukai anak.",
    )
    if tampilan != st.session_state.tampilan_3d:
        st.session_state.tampilan_3d = tampilan
        st.rerun()

    st.write("---")
    suara_aktif = st.toggle(
        "🔊 Suara & Efek Bunyi",
        key="suara_aktif",
        value=True,
        help="Nyalakan suara langkah, tabrakan, dan melodi kemenangan.",
    )
    if st.button("🎵 Tes Suara (Cek Speaker)", use_container_width=True):
        st.session_state.suara = "menang"
        st.session_state.status_animasi = "menang"
        st.rerun()

    st.write("---")
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

# Audio playback
suara_diputar = st.session_state.pop("suara", None)
if suara_aktif and suara_diputar and suara_diputar in DAFTAR_SUARA:
    wadah_suara.audio(DAFTAR_SUARA[suara_diputar], format="audio/wav", autoplay=True)

lv = LEVELS[st.session_state.level]
st.markdown(f"<h2 style='text-align:center;margin:0'>🤖 Robot Mini — {lv['nama']}</h2>", unsafe_allow_html=True)

jenis, isi = st.session_state.pesan
getattr(st, jenis)(isi)

# Render Papan 3D Bergerak
papan = st.empty()
papan.markdown(
    gambar_papan_3d(
        st.session_state.pos,
        st.session_state.arah,
        lv,
        status_animasi=st.session_state.status_animasi,
        mode_tampilan=st.session_state.tampilan_3d,
    ),
    unsafe_allow_html=True,
)

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
        papan.markdown(
            gambar_papan_3d(pos, arah, lv, status_animasi="diam", mode_tampilan=st.session_state.tampilan_3d),
            unsafe_allow_html=True,
        )
        error = None
        for i, perintah in enumerate(st.session_state.program):
            kotak_program.markdown(gambar_program(st.session_state.program, aktif=i), unsafe_allow_html=True)
            if suara_aktif:
                s_nama = "maju" if perintah == "maju" else perintah
                wadah_suara.audio(DAFTAR_SUARA.get(s_nama, DAFTAR_SUARA["maju"]), format="audio/wav", autoplay=True)
            time.sleep(0.55)
            pos, arah, error = langkah(pos, arah, perintah, lv)
            anim_step = "tabrak" if error else ("menang" if pos == lv["target"] else "diam")
            papan.markdown(
                gambar_papan_3d(pos, arah, lv, status_animasi=anim_step, mode_tampilan=st.session_state.tampilan_3d),
                unsafe_allow_html=True,
            )
            if error:
                if suara_aktif:
                    wadah_suara.audio(DAFTAR_SUARA["tabrak"], format="audio/wav", autoplay=True)
                break
        time.sleep(0.4)
        st.session_state.pos, st.session_state.arah = pos, arah
        if error:
            st.session_state.pesan = ("warning", f"{error} Kartu nomor {i + 1} perlu diperbaiki 🔧")
            st.session_state.status_animasi = "tabrak"
        elif pos == lv["target"]:
            selesai_level()
        else:
            st.session_state.pesan = ("warning", "Hampir! Robot belum sampai bola. Tambah atau ganti kartunya 🔧")
            st.session_state.status_animasi = "diam"
        st.rerun()
else:
    st.button("🔄 Mulai lagi", on_click=ulang, use_container_width=True)
