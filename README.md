# 🤖 Robot Mini 3D — Permainan Coding Sederhana untuk Anak
file:///Users/jevin/game/bolaa/index.html
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gamesku.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Graphics](https://img.shields.io/badge/Graphics-3D%20Isometric%20CSS-orange.svg)]()
[![Audio](https://img.shields.io/badge/Audio-Procedural%20WAV%20SFX-green.svg)]()
[![Target](https://img.shields.io/badge/Target-Usia%203--6%20Tahun-purple.svg)]()

> **Platform edukasi berbasis web interaktif untuk memperkenalkan fondasi *Computational Thinking* (algoritma, urutan sekuensial, orientasi spasial, dan *debugging*) kepada anak usia dini melalui simulasi robot bola 3D yang ceria, bebas stres, dan aman.**

---

### 🚀 **[KLIK DI SINI UNTUK MAINKAN ONLINE DI STREAMLIT CLOUD](https://gamesku.streamlit.app/)**
*(Bisa dimainkan langsung di Browser HP, Tablet, iPad, maupun Komputer)*

---

## 🌟 Fitur Utama

* **🌟 Tampilan 3D Isometrik Bergerak**:
  * Papan arena 3D dengan kedalaman fisik dan bayangan lembut.
  * Robot melompat dan meluncur secara elastis (*smooth cubic-bezier transition*).
  * Rotasi arah 3D halus saat belok kiri/kanan (`0°`, `90°`, `180°`, `270°`).
  * Bola ⚽ dan gawang 🥅 melayang dan membal (*floating & bouncing*).
  * Efek visual goyah saat tabrakan dan putaran kemenangan saat mencapai target.

* **🔊 Efek Suara (SFX) Prosedural Tanpa File Luar**:
  * Menggunakan sintesis gelombang audio murni Python (`struct` & `math`) menjadi format WAV PCM 16-bit.
  * Nada langkah ganda ceria, *chirp* robot saat berputar, bunyi lucu *"Duk!"* saat menabrak, dan melodi *fanfare* kemenangan *C5–E5–G5–C6* 🎉.
  * Dilengkapi tombol **Tes Suara** dan toggle bisu di sidebar.

* **👶 Dual-Mode Usia Fleksibel**:
  * **Mode Langsung (Usia 3 Tahun)**: Tiap tombol panah langsung menggerakkan robot 1 langkah (eksplorasi sebab-akibat instan).
  * **Mode Susun Kartu (Usia 4–6 Tahun)**: Anak menyusun rangkaian kartu perintah (hingga 12 kartu), lalu menekan tombol **▶️ JALAN!** dengan simulasi langkah demi langkah.

* **🔧 Konsep Debugging Ramah Anak**:
  * Tidak ada status "Game Over" yang menakutkan. Jika robot meleset, sistem akan memberi tahu nomor kartu yang perlu diganti.

* **👨‍👩‍👧 Panel Pendampingan Orang Tua**:
  * Panduan membatasi sesi bermain sehat (10–15 menit).
  * Tips mengajarkan anak menganalisis kartu program yang keliru.

---

## 🎯 5 Level Kurikulum Bertahap

| Level | Nama Level | Ukuran Grid | Fokus Pembelajaran | Rintangan |
| :---: | :--- | :---: | :--- | :---: |
| **1** | **Maju Terus** | 4x4 | Gerak linier lurus ke depan | Tidak ada |
| **2** | **Belok Satu Kali** | 4x4 | Orientasi tubuh robot (belok kiri/kanan) | Tidak ada |
| **3** | **Rencana Panjang** | 5x5 | Perencanaan sekuensial banyak kartu | Tidak ada |
| **4** | **Awas Batu!** | 5x5 | Menghindari rintangan batu (*pathfinding*) | 🪨 3 Batu |
| **5** | **Gawang!** | 5x5 | Menyelesaikan labirin rintangan kompleks | 🪨 5 Batu |

---

## 💻 Cara Menjalankan Secara Lokal

1. **Clone repository ini:**
   ```bash
   git clone https://github.com/jevinsyatir007-glitch/GAMESQU.git
   cd GAMESQU
   ```

2. **Buat virtual environment (opsional tapi disarankan):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi:**
   ```bash
   streamlit run app.py
   ```
   Buka browser di `http://localhost:8501`.

---

## 📄 Dokumen Spesifikasi Produk (PRD)

Dokumentasi lengkap mengenai visi produk, arsitektur teknis, persona pengguna, dan rencana roadmap masa depan dapat dibaca pada file **[PRD.md](PRD.md)**.

---

## 🌐 Landing Page Interaktif

Tersedia halaman landing page modern interaktif pada file **[index.html](index.html)** yang dapat diakses langsung via browser atau dideploy ke GitHub Pages.

---

### ❤️ Kontribusi & Lisensi
Dibuat dengan penuh cinta untuk edukasi anak-anak Indonesia. Lisensi terbuka untuk digunakan bagi keperluan pendidikan dan non-komersial.
