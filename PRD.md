# 📋 Product Requirements Document (PRD)
## Robot Mini — Permainan Coding Sederhana untuk Anak

---

## 1. Ringkasan Eksekutif & Visi Produk

### 1.1 Visi Produk
**Robot Mini** adalah platform edukasi berbasis web interaktif yang memperkenalkan fondasi *Computational Thinking* (algoritma, sekuensial, orientasi spasial, dan debugging) kepada anak usia dini (3–6 tahun) melalui konsep permainan robot bola yang ceria, bebas stres, dan aman.

### 1.2 Masalah yang Diselesaikan
* **Over-stimulasi pada game anak modern**: Banyak game edukasi anak yang terlalu bising, penuh iklan, dan membingungkan.
* **Kurangnya pengenalan logika pemrograman ramah balita**: Sebagian besar platform coding (seperti Scratch) dirancang untuk usia 7+ tahun yang sudah lancar membaca dan mengetik.
* **Kebutuhan pendampingan orang tua**: Orang tua sering kesulitan menemukan media belajar digital yang interaktif sekaligus menyediakan panduan pendampingan konkret (*parental guidance*).

---

## 2. Target Pengguna & Persona

| Persona | Rentang Usia | Karakteristik Belajar | Mode yang Digunakan |
| :--- | :--- | :--- | :--- |
| **Eksplorer Cilik** | 3 tahun | Belum lancar membaca, memahami sebab-akibat langsung (*direct cause-and-effect*), membutuhkan respons audio-visual instan. | **Mode Langsung** (*Direct Mode*) |
| **Pemikir Algoritmik** | 4–6 tahun | Mampu merencanakan 2–5 langkah ke depan, memahami konsep urutan kartu, siap belajar konsep *debugging*. | **Mode Susun Kartu** (*Batch Mode*) |
| **Orang Tua / Pendidik** | Dewasa | Menginginkan aktivitas screen-time bernilai edukatif, membatasi waktu layar (10–15 menit/sesi), mendampingi saat anak menemui kendala. | **Sidebar Fasilitator** |

---

## 3. Filosofi Desain & UX

1. **Ergonomi Ramah Sentuhan Anak**:
   * Tombol panah ekstra besar (tinggi 86px) dengan sudut membulat (*radius 20px*).
   * Ikon arah kontras dan kode warna konsisten (Hijau = Maju, Biru = Kiri, Oranye = Kanan).
2. **Umpan Balik Positif Tanpa Hukuman (*No Frustration Policy*)**:
   * Menabrak batu/tepi papan tidak memicu status "Game Over" yang menakutkan, melainkan feedback ramah dan suara lucu (*"Duk!"*), mengajak anak menganalisis kartu mana yang perlu diganti.
3. **Multi-Sensory Engagement (Audio-Visual)**:
   * Efek suara sintetis prosedural untuk setiap langkah, belokan, tabrakan, dan melodi kemenangan (*fanfare*).
   * Animasi balon (*balloons*) dan bintang perayaan saat menyelesaikan level.

---

## 4. Spesifikasi Fungsional

### 4.1 Papan Permainan Dinamis (Grid Engine)
* Grid berukuran fleksibel (4x4 untuk level pemula, 5x5 untuk level menengah).
* Komponen grid:
  * 🤖 **Robot**: Menampilkan posisi koordinat dan arah hadap (`⬆️`, `➡️`, `⬇️`, `⬅️`).
  * ⚽ / 🥅 **Target**: Bola atau gawang tujuan dengan latar sorot kuning cerah.
  * 🪨 **Rintangan**: Batu statis yang tidak dapat dilalui robot.

### 4.2 Mode Permainan Ganda (*Dual-Mode Engine*)

#### A. Mode Langsung (Usia 3 Tahun)
* Setiap kali tombol arah ditekan (`MAJU`, `KIRI`, `KANAN`), robot **langsung bergerak 1 langkah**.
* Cocok untuk mengenalkan konsep orientasi tubuh robot (arah relatif robot vs arah pandang anak).

#### B. Mode Susun Kartu & Jalan (Usia 4–6 Tahun)
* Anak menyusun deretan kartu perintah (maksimal 12 kartu).
* Kartu menampilkan nomor urut, ikon arah, dan warna pembeda.
* Tombol kontrol program:
  * **▶️ JALAN!**: Menjalankan simulasi animasi kartu satu per satu (delay 0.6 detik per langkah).
  * **⌫ Hapus**: Menghapus kartu terakhir yang salah.
  * **🔄 Ulang**: Mengosongkan susunan kartu dan mengembalikan robot ke posisi awal.
* **Fitur Debugging Visual**: Kartu yang sedang aktif dieksekusi diberi bingkai tebal kuning menyala (`#ffd400`). Jika menabrak, pesan akan mengidentifikasi kartu nomor berapa yang harus diperbaiki.

### 4.3 Kurikulum & Desain Level

| Level | Judul | Ukuran | Konsep Coding | Rintangan |
| :--- | :--- | :--- | :--- | :--- |
| **Level 1** | Maju Terus | 4x4 | Gerak Linier (*Linear Sequence*) | Tidak ada |
| **Level 2** | Belok Satu Kali | 4x4 | Orientasi Spasial (*Turning Logic*) | Tidak ada |
| **Level 3** | Rencana Panjang | 5x5 | Sekuens Panjang (*Multi-step Planning*) | Tidak ada |
| **Level 4** | Awas Batu! | 5x5 | Penghindaran Rintangan (*Pathfinding*) | 3 Batu |
| **Level 5** | Gawang! | 5x5 | Navigasi Labirin Kompleks (*Complex Maze*) | 5 Batu |

### 4.4 Engine Audio Sintetis Prosedural
* Dibuat menggunakan modul bawaan Python (`struct` & `math`) menghasilkan gelombang suara WAV mono 16-bit PCM tanpa memerlukan file eksternal (anti *broken audio*):
  * **Maju**: 2 nada *triangle* naik (480 Hz & 720 Hz).
  * **Belok**: Nada *chirp* berputar (380 Hz & 540 Hz).
  * **Tabrak**: Gelombang *square* berfrekuensi rendah (160 Hz ke 75 Hz).
  * **Menang**: Melodi *arpeggio* 4 nada perayaan C5–E5–G5–C6.
  * **Klik/Hapus/Ulang**: Nada pop lembut.

### 4.5 Panel Pendamping Orang Tua (Sidebar)
* Pengaturan mode (Toggle Mode Langsung vs Mode Kartu).
* Pengaturan suara (Toggle Suara & tombol Tes Suara).
* Pemilih level bebas dan papan skor bintang (0 / 5 bintang).
* Catatan edukasi pendamping (*tips batasan waktu 10-15 menit dan cara memfasilitasi debugging*).

---

## 5. Arsitektur & Teknologi

* **Bahasa & Framework**: Python 3.10+ & Streamlit
* **State Management**: `st.session_state` (posisi robot, arah hadap, program kartu, status bintang, antrean audio)
* **Kompilasi Suara**: *Zero-dependency in-memory WAV byte generator*
* **Deployment & CI/CD**:
  * GitHub Repository: `jevinsyatir007-glitch/bolaa`
  * Cloud Hosting: Streamlit Community Cloud (`https://gamesku.streamlit.app/`)
  * Auto-redeploy saat ada `git push` ke cabang `main`

---

## 6. Metrik Keberhasilan (KPI)

1. **Completion Rate**: Anak mampu menyelesaikan Level 1 dan 2 secara mandiri setelah 1 sesi pendampingan.
2. **Debugging Understanding**: Anak usia 4+ dapat mengenali kartu yang salah ketika eksekusi gagal tanpa mereset seluruh program dari nol.
3. **Usability**: Nol delay audio (>100ms) dan tata letak tidak bergeser saat kartu ditambahkan di layar tablet/ponsel.

---

## 7. Rencana Pengembangan Selanjutnya (Roadmap)

* [ ] **Fase 2**: Penambahan suara narasi instruksi dalam Bahasa Indonesia ("Ayo maju!", "Belok kanan!").
* [ ] **Fase 3**: Fitur blok perulangan sederhana (*Loop / Repeat block* 2x, 3x).
* [ ] **Fase 4**: *Level Maker / Labirin Kreatif* (anak dan orang tua dapat meletakkan batu dan target sendiri).
