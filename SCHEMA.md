# 📐 Dokumentasi Skema (SCHEMA)
## Robot Mini 3D — Arsitektur Data Relasional & Format JSON

Dokumen ini memuat detail spesifikasi skema data relasional (SQL), skema data pertukaran JSON (*JSON Schema*), serta model validasi Python (*Pydantic Models*) untuk game **Robot Mini 3D**.

---

## 1. Skema Basis Data Relasional (SQL)

Skema database lengkap tersedia pada file [SCHEMA.sql](file:///Users/jevin/game/bolaa/SCHEMA.sql).

### 1.1 Ringkasan Struktur Tabel & Kunci

| Tabel | Deskripsi | Primary Key | Foreign Key | Indeks Kunci |
| :--- | :--- | :--- | :--- | :--- |
| **`users`** | Akun orang tua / pendidik | `id` (UUID) | - | `email` (UNIQUE) |
| **`child_profiles`** | Profil anak (pemain) | `id` (UUID) | `user_id -> users(id)` | `idx_child_profiles_user_id` |
| **`levels`** | Definisi master 5 level | `id` (INT) | - | `nomor_level` (UNIQUE) |
| **`level_obstacles`** | Posisi batu/rintangan tiap level | `id` (SERIAL) | `level_id -> levels(id)` | `idx_obstacles_level_id`, `(level_id, pos_r, pos_c)` UNIQUE |
| **`level_progress`** | Catatan bintang dan status lulus | `id` (UUID) | `profile_id`, `level_id` | `(profile_id, level_id)` UNIQUE |
| **`game_sessions`** | Log sesi bermain & durasi layar | `id` (UUID) | `profile_id`, `level_id` | `idx_sessions_profile_started` |
| **`program_cards`** | Kartu algoritma yang disusun | `id` (UUID) | `session_id -> game_sessions(id)` | `(session_id, urutan_langkah)` UNIQUE |
| **`debugging_events`** | Log peristiwa tabrakan robot | `id` (UUID) | `session_id -> game_sessions(id)` | `idx_debugging_session` |

---

## 2. Skema Format JSON (*JSON Schema*)

### 2.1 JSON Schema: Definisi Level Permainan (`level.schema.json`)
Skema ini digunakan untuk membaca, menyimpan, atau mengekspor level (*Level Editor*):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RobotMiniLevel",
  "type": "object",
  "required": ["nama", "petunjuk", "ukuran", "start", "arah", "target", "rintangan"],
  "properties": {
    "nama": {
      "type": "string",
      "description": "Judul nama level"
    },
    "petunjuk": {
      "type": "string",
      "description": "Instruksi petunjuk ramah anak"
    },
    "ukuran": {
      "type": "integer",
      "enum": [4, 5, 6],
      "description": "Dimensi grid matrix N x N"
    },
    "start": {
      "type": "array",
      "items": { "type": "integer", "minimum": 0 },
      "minItems": 2,
      "maxItems": 2,
      "description": "Koordinat awal [baris, kolom]"
    },
    "arah": {
      "type": "integer",
      "enum": [0, 1, 2, 3],
      "description": "0: Atas, 1: Kanan, 2: Bawah, 3: Kiri"
    },
    "target": {
      "type": "array",
      "items": { "type": "integer", "minimum": 0 },
      "minItems": 2,
      "maxItems": 2,
      "description": "Koordinat target [baris, kolom]"
    },
    "rintangan": {
      "type": "array",
      "items": {
        "type": "array",
        "items": { "type": "integer", "minimum": 0 },
        "minItems": 2,
        "maxItems": 2
      },
      "description": "Daftar koordinat rintangan batu [[r, c], ...]"
    }
  }
}
```

---

### 2.2 JSON Schema: Sesi Game & Progress (`game_state.schema.json`)
Digunakan untuk sinkronisasi simpanan permainan (*Cloud Save / LocalStorage*):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RobotMiniGameState",
  "type": "object",
  "required": ["level_aktif", "mode_langsung", "bintang", "level_selesai"],
  "properties": {
    "level_aktif": {
      "type": "integer",
      "minimum": 0,
      "maximum": 4
    },
    "mode_langsung": {
      "type": "boolean"
    },
    "suara_aktif": {
      "type": "boolean",
      "default": true
    },
    "tampilan_kamera": {
      "type": "string",
      "enum": ["🌟 3D Isometrik", "📐 3D Miring Ringan", "📋 2D Datar"]
    },
    "bintang": {
      "type": "integer",
      "minimum": 0,
      "maximum": 5
    },
    "level_selesai": {
      "type": "array",
      "items": { "type": "boolean" },
      "minItems": 5,
      "maxItems": 5
    },
    "program_tersimpan": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["maju", "kiri", "kanan"]
      },
      "maxItems": 12
    }
  }
}
```

---

## 3. Skema Python Typed (Pydantic / Dataclasses)

Untuk memvalidasi data di layer aplikasi Python:

```python
from enum import Enum
from typing import List, Tuple
from pydantic import BaseModel, Field

class ArahRobot(int, Enum):
    ATAS = 0
    KANAN = 1
    BAWAH = 2
    KIRI = 3

class PerintahKartu(str, Enum):
    MAJU = "maju"
    KIRI = "kiri"
    KANAN = "kanan"

class LevelSchema(BaseModel):
    nama: str
    petunjuk: str
    ukuran: int = Field(ge=4, le=6)
    start: Tuple[int, int]
    arah: ArahRobot
    target: Tuple[int, int]
    rintangan: List[Tuple[int, int]] = []

class GameSessionSchema(BaseModel):
    level_index: int = Field(ge=0, le=4)
    program: List[PerintahKartu] = Field(default_factory=list, max_length=12)
    mode_langsung: bool = True
    bintang_terkumpul: int = Field(default=0, ge=0, le=5)
    selesai_per_level: List[bool] = Field(default=[False] * 5)
```
