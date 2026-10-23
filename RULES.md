# 📜 Pedoman & Aturan Permainan (RULES)
## Robot Mini 3D — Aturan Game & Standar Pengembangan

---

## 1. Aturan Mekanika Permainan (Game Rules)

### 1.1 Aturan Papan & Koordinat Grid
1. Papan permainan berupa kisi dua dimensi berukuran $N \times N$:
   * **Level 1–2**: Grid $4 \times 4$ (indeks baris `0..3`, indeks kolom `0..3`).
   * **Level 3–5**: Grid $5 \times 5$ (indeks baris `0..4`, indeks kolom `0..4`).
2. Posisi dinyatakan dalam pasangan koordinat `(baris, kolom)`, di mana koordinat `(0, 0)` adalah sudut kiri atas.
3. Arah orientasi robot memiliki 4 kemungkinan hadap:
   * `0`: **Atas** (`⬆️`, $-1$ baris)
   * `1`: **Kanan** (`➡️`, $+1$ kolom)
   * `2`: **Bawah** (`⬇️`, $+1$ baris)
   * `3`: **Kiri** (`⬅️`, $-1$ kolom)

---

### 1.2 Aturan Perintah Kartu
Setiap langkah robot dikontrol oleh 3 jenis kartu aksi:
* ⬆️ **MAJU**:
  * Menggerakkan robot 1 petak ke depan sesuai arah hadapnya saat ini.
  * Orientasi hadap tidak berubah.
* ↩️ **KIRI**:
  * Robot berputar $90^\circ$ berlawanan arah jarum jam di tempat.
  * Posisi koordinat `(baris, kolom)` **tidak berubah**, arah baru: `(arah - 1) % 4`.
* ↪️ **KANAN**:
  * Robot berputar $90^\circ$ searah jarum jam di tempat.
  * Posisi koordinat `(baris, kolom)` **tidak berubah**, arah baru: `(arah + 1) % 4`.

---

### 1.3 Batasan Kartu & Buffer Algoritma
* Pada **Mode Susun Kartu**, anak dapat menyusun maksimal **12 kartu** dalam satu sesi program.
* Jika batas 12 kartu tercapai, tombol kartu dinonaktifkan untuk mencegah loop tanpa akhir dan melatih efisiensi algoritma berpikir anak.

---

### 1.4 Aturan Tabrakan & Feedback (*Kid-Friendly Collision Rules*)
1. **Tabrakan Pinggir Papan**:
   * Terjadi jika perintah `MAJU` membawa robot ke luar batas grid ($r < 0$, $r \ge N$, $c < 0$, atau $c \ge N$).
   * Efek: Robot tertahan di petak terakhir, bergetar (*wobble shake*), memainkan suara *"Duk!"*, dan memberi tahu nomor kartu yang keliru.
2. **Tabrakan Batu (Rintangan 🪨)**:
   * Terjadi jika petak tujuan `MAJU` berisi rintangan batu.
   * Efek: Robot tidak menembus batu, tetap di posisinya, dan simulasi berhenti seketika (*early termination*).
3. **Prinsip Tanpa Hukuman (*No Frustration Policy*)**:
   * **TIDAK ADA** status *"Game Over"* atau pengurangan poin/nyawa.
   * Anak langsung diajak melakukan **debugging**: kartu yang menyebabkan tabrakan disorot sehingga anak cukup menghapus atau mengganti kartu tersebut.

---

### 1.5 Aturan Kemenangan & Bintang
1. **Kondisi Menang**: Robot mendarat tepat di petak target (Bola ⚽ pada Level 1–4, Gawang 🥅 pada Level 5).
2. **Reward Kemenangan**:
   * Suara melodi kemenangan *fanfare* $C5 \to E5 \to G5 \to C6$.
   * Robot melakukan lompatan dan putaran perayaan 360° (*victory flip*).
   * Animasi balon terbang (*balloons effect*).
   * Menambahkan bintang (⭐) pada papan skor (maksimal 1 bintang per level, total 5 bintang).

---

### 1.6 Aturan Pendampingan Orang Tua (*Screen-Time Rules*)
1. **Rekomendasi Durasi**: Sesi bermain dibatasi maksimal **10–15 menit per hari** untuk menjaga kesehatan mata anak.
2. **Peran Orang Tua**: Sebagai fasilitator refleksi saat robot meleset:
   * *"Kira-kira robotnya tadi beloknya kepagian atau kemalaman ya, Dik?"*
   * *"Coba kita lihat kartu nomor berapa yang bikin robot nabrak batu?"*

---

## 2. Aturan Rekayasa Perangkat Lunak (Development Rules)

### 2.1 Efisiensi Audio Tanpa Aset Eksternal (*Zero-External Asset Audio*)
* **Wajib**: Semua efek suara (SFX) dihasilkan secara komputasi prosedural menggunakan pustaka standar Python (`struct` & `math`) menghasilkan gelombang suara 16-bit PCM mono WAV.
* **Dilarang**: Menggunakan file suara dari URL eksternal (hosting luar) yang rentan mengalami *broken link*, pemblokiran CORS, atau latency jaringan.

### 2.2 Keamanan Secret & Token (*Strict Token Security*)
* **Dilarang keras**: Menyimpan token akses GitHub (`ghp_...`), password, atau kunci API dalam kode sumber (`app.py`, `PRD.md`, `RULES.md`, atau commit git).
* **Wajib**: Menggunakan autentikasi berbasis environment variable atau OAuth credential manager (`gh auth login`).

### 2.3 Standar Desain Sentuhan Anak (*Kid Ergonomics Standards*)
* Tombol aksi harus memiliki tinggi minimal **86 piksel** dengan sudut membulat (*border-radius $\ge$ 20px*).
* Ukuran font ikon minimal **30 piksel** agar mudah ditekan jari balita pada layar sentuh ponsel dan tablet.
* Tata letak wajib stabil (*zero layout shift*) saat kartu ditambah atau dihapus.

### 2.4 Kompatibilitas Multi-Platform
* Aplikasi harus dapat berjalan mulus pada:
  * Streamlit Community Cloud (`https://gamesku.streamlit.app/`).
  * Web modern pada peramban seluler (Chrome Mobile, Safari iOS).
  * Menjalankan secara lokal via perintah: `streamlit run app.py`.
