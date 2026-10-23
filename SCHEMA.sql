-- ============================================================================
-- SCHEMA DATABASE: ROBOT MINI 3D (GAME EDUKASI CODING ANAK)
-- Kompatibel: PostgreSQL 14+ / Supabase / Neon / SQLite 3
-- ============================================================================

-- Ekstensi UUID (opsional untuk PostgreSQL)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------------------------
-- 1. Tabel Akun Pengguna (Orang Tua / Wali)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    nama_orang_tua VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255),
    role VARCHAR(20) DEFAULT 'parent' CHECK (role IN ('parent', 'educator', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------------
-- 2. Tabel Profil Anak (Pemain)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS child_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nama_anak VARCHAR(50) NOT NULL,
    usia_tahun INT NOT NULL CHECK (usia_tahun BETWEEN 2 AND 12),
    avatar_karakter VARCHAR(20) DEFAULT '🤖',
    mode_default_langsung BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_child_profiles_user_id ON child_profiles(user_id);

-- ---------------------------------------------------------------------------
-- 3. Tabel Master Level Permainan
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS levels (
    id INT PRIMARY KEY,
    nomor_level INT NOT NULL UNIQUE,
    nama VARCHAR(100) NOT NULL,
    petunjuk TEXT NOT NULL,
    ukuran_grid INT NOT NULL CHECK (ukuran_grid IN (4, 5, 6)),
    start_r INT NOT NULL,
    start_c INT NOT NULL,
    start_arah INT NOT NULL CHECK (start_arah BETWEEN 0 AND 3), -- 0: Atas, 1: Kanan, 2: Bawah, 3: Kiri
    target_r INT NOT NULL,
    target_c INT NOT NULL,
    target_icon VARCHAR(10) DEFAULT '⚽',
    is_active BOOLEAN DEFAULT TRUE
);

-- ---------------------------------------------------------------------------
-- 4. Tabel Rintangan Level (Batu / Dinding)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS level_obstacles (
    id SERIAL PRIMARY KEY,
    level_id INT NOT NULL REFERENCES levels(id) ON DELETE CASCADE,
    pos_r INT NOT NULL,
    pos_c INT NOT NULL,
    jenis_rintangan VARCHAR(30) DEFAULT 'batu',
    CONSTRAINT uq_level_obstacle_pos UNIQUE (level_id, pos_r, pos_c)
);

CREATE INDEX IF NOT EXISTS idx_obstacles_level_id ON level_obstacles(level_id);

-- ---------------------------------------------------------------------------
-- 5. Tabel Progres & Bintang Level Anak
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS level_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES child_profiles(id) ON DELETE CASCADE,
    level_id INT NOT NULL REFERENCES levels(id) ON DELETE CASCADE,
    selesai BOOLEAN DEFAULT FALSE,
    bintang INT DEFAULT 0 CHECK (bintang BETWEEN 0 AND 3),
    percobaan_terbaik_kartu INT,
    total_percobaan INT DEFAULT 1,
    tanggal_selesai TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_profile_level_progress UNIQUE (profile_id, level_id)
);

CREATE INDEX IF NOT EXISTS idx_progress_profile ON level_progress(profile_id);

-- ---------------------------------------------------------------------------
-- 6. Tabel Sesi Permainan (Monitoring Sesi 10-15 Menit)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS game_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES child_profiles(id) ON DELETE CASCADE,
    level_id INT NOT NULL REFERENCES levels(id) ON DELETE CASCADE,
    mode_permainan VARCHAR(20) NOT NULL CHECK (mode_permainan IN ('langsung', 'kartu')),
    durasi_detik INT DEFAULT 0,
    status_berhasil BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_sessions_profile_started ON game_sessions(profile_id, started_at DESC);

-- ---------------------------------------------------------------------------
-- 7. Tabel Rangkaian Kartu Program (Langkah yang Disusun Anak)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS program_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
    urutan_langkah INT NOT NULL CHECK (urutan_langkah BETWEEN 1 AND 20),
    perintah VARCHAR(20) NOT NULL CHECK (perintah IN ('maju', 'kiri', 'kanan')),
    sukses_dieksekusi BOOLEAN DEFAULT TRUE,
    CONSTRAINT uq_session_card_step UNIQUE (session_id, urutan_langkah)
);

-- ---------------------------------------------------------------------------
-- 8. Tabel Log Peristiwa Debugging (Insiden Tabrakan)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS debugging_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
    kartu_ke INT NOT NULL,
    perintah_gagal VARCHAR(20) NOT NULL,
    jenis_error VARCHAR(50) NOT NULL, -- 'tabrak_batu', 'tabrak_pinggir'
    waktu_kejadian TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_debugging_session ON debugging_events(session_id);

-- ============================================================================
-- SEED DATA: 5 LEVEL RESMI & RINTANGAN ROBOT MINI 3D
-- ============================================================================

INSERT INTO levels (id, nomor_level, nama, petunjuk, ukuran_grid, start_r, start_c, start_arah, target_r, target_c, target_icon)
VALUES
(1, 1, 'Level 1 - Maju Terus', 'Bola ada di depan robot. Tekan MAJU sampai robot ketemu bola!', 4, 3, 1, 0, 1, 1, '⚽'),
(2, 2, 'Level 2 - Belok Satu Kali', 'Robot harus belok untuk sampai ke bola.', 4, 3, 0, 0, 1, 2, '⚽'),
(3, 3, 'Level 3 - Rencana Panjang', 'Susun beberapa kartu dulu, baru tekan JALAN.', 5, 4, 0, 1, 0, 4, '⚽'),
(4, 4, 'Level 4 - Awas Batu!', 'Jangan tabrak batu. Cari jalan memutar.', 5, 4, 0, 0, 0, 2, '⚽'),
(5, 5, 'Level 5 - Gawang!', 'Bawa robot ke gawang. Hati-hati banyak batu.', 5, 4, 4, 3, 0, 0, '🥅')
ON CONFLICT (id) DO UPDATE SET
    nama = EXCLUDED.nama,
    petunjuk = EXCLUDED.petunjuk,
    ukuran_grid = EXCLUDED.ukuran_grid,
    start_r = EXCLUDED.start_r,
    start_c = EXCLUDED.start_c,
    start_arah = EXCLUDED.start_arah,
    target_r = EXCLUDED.target_r,
    target_c = EXCLUDED.target_c,
    target_icon = EXCLUDED.target_icon;

-- Rintangan Level 4 (3 Batu)
INSERT INTO level_obstacles (level_id, pos_r, pos_c, jenis_rintangan)
VALUES
(4, 2, 0, 'batu'),
(4, 2, 1, 'batu'),
(4, 1, 3, 'batu')
ON CONFLICT (level_id, pos_r, pos_c) DO NOTHING;

-- Rintangan Level 5 (5 Batu)
INSERT INTO level_obstacles (level_id, pos_r, pos_c, jenis_rintangan)
VALUES
(5, 3, 1, 'batu'),
(5, 3, 2, 'batu'),
(5, 1, 1, 'batu'),
(5, 1, 2, 'batu'),
(5, 2, 4, 'batu')
ON CONFLICT (level_id, pos_r, pos_c) DO NOTHING;

-- ============================================================================
-- VIEW ANALITIK: REKAP PRESTASI DAN EVALUASI BELAJAR ANAK
-- ============================================================================

CREATE OR REPLACE VIEW v_rekap_kemajuan_anak AS
SELECT 
    cp.id AS profile_id,
    cp.nama_anak,
    cp.usia_tahun,
    COUNT(lp.id) FILTER (WHERE lp.selesai = TRUE) AS level_terselesaikan,
    COALESCE(SUM(lp.bintang), 0) AS total_bintang,
    COALESCE(SUM(gs.durasi_detik) / 60, 0) AS total_menit_bermain,
    COUNT(de.id) AS total_debugging_dilakukan
FROM child_profiles cp
LEFT JOIN level_progress lp ON cp.id = lp.profile_id
LEFT JOIN game_sessions gs ON cp.id = gs.profile_id
LEFT JOIN debugging_events de ON gs.id = de.session_id
GROUP BY cp.id, cp.nama_anak, cp.usia_tahun;
