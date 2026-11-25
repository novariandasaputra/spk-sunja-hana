import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "spk_sunja_hana.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # ── Users ──────────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            role     TEXT    NOT NULL DEFAULT 'USER',
            status   TEXT    NOT NULL DEFAULT 'Aktif',
            created_at TEXT  DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Categories ─────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            kode   TEXT    NOT NULL UNIQUE,
            nama   TEXT    NOT NULL,
            status TEXT    NOT NULL DEFAULT 'Aktif'
        )
    """)

    # ── Monthly Sales ──────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS monthly_sales (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            tahun       INTEGER NOT NULL,
            bulan       INTEGER NOT NULL,
            qty         INTEGER NOT NULL DEFAULT 0,
            amount      REAL    NOT NULL DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            UNIQUE(category_id, tahun, bulan)
        )
    """)

    # ── Analysis History ───────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id     TEXT    NOT NULL UNIQUE,
            tanggal         TEXT    NOT NULL,
            periode_awal    TEXT    NOT NULL,
            periode_akhir   TEXT    NOT NULL,
            jumlah_alternatif INTEGER NOT NULL DEFAULT 0,
            jumlah_kriteria   INTEGER NOT NULL DEFAULT 0,
            status          TEXT    NOT NULL DEFAULT 'Selesai',
            created_by      TEXT,
            result_json     TEXT
        )
    """)

    conn.commit()

    # ── Seed data ──────────────────────────────────────────────────────────────
    _seed_users(cur)
    _seed_categories(cur)
    _seed_monthly_sales(cur)
    _seed_analysis_history(cur)

    conn.commit()
    conn.close()


# ─────────────────────────── Seed helpers ─────────────────────────────────────

def _seed_users(cur):
    users = [
        ("Administrator", "admin",  hash_password("admin123"), "ADMIN",   "Aktif"),
        ("Budi Santoso",  "budi",   hash_password("budi123"),  "ADMIN",   "Aktif"),
        ("Siti Nurhayati","siti",   hash_password("siti123"),  "PEMILIK", "Aktif"),
    ]
    for name, uname, pwd, role, status in users:
        cur.execute("""
            INSERT OR IGNORE INTO users (name, username, password, role, status)
            VALUES (?, ?, ?, ?, ?)
        """, (name, uname, pwd, role, status))


def _seed_categories(cur):
    cats = [
        ("001", "Rokok"),
        ("002", "Alat Tulis"),
        ("003", "Minuman Instan"),
        ("004", "Snack"),
        ("005", "Aneka Susu"),
    ]
    for kode, nama in cats:
        cur.execute("""
            INSERT OR IGNORE INTO categories (kode, nama, status)
            VALUES (?, ?, 'Aktif')
        """, (kode, nama))


def _seed_monthly_sales(cur):
    # qty and amount data for Jan(1)–Nov(11) 2026, per category
    # Format: (kode, [(qty_jan, amt_jan), (qty_feb, amt_feb), ...up to Nov])
    sales_data = {
        "001": [  # Rokok
            (120, 1_200_000), (115, 1_150_000), (130, 1_300_000),
            (125, 1_250_000), (140, 1_400_000), (135, 1_350_000),
            (145, 1_450_000), (150, 1_500_000), (138, 1_380_000),
            (155, 1_550_000), (120, 1_200_000),
        ],
        "002": [  # Alat Tulis
            (85,  850_000),  (90,  900_000),  (80,  800_000),
            (95,  950_000),  (88,  880_000),  (92,  920_000),
            (87,  870_000),  (93,  930_000),  (89,  890_000),
            (96,  960_000),  (85,  850_000),
        ],
        "003": [  # Minuman Instan
            (75,  750_000),  (80,  800_000),  (78,  780_000),
            (82,  820_000),  (85,  850_000),  (79,  790_000),
            (83,  830_000),  (86,  860_000),  (77,  770_000),
            (88,  880_000),  (75,  750_000),
        ],
        "004": [  # Snack
            (60,  600_000),  (65,  650_000),  (62,  620_000),
            (68,  680_000),  (70,  700_000),  (64,  640_000),
            (66,  660_000),  (72,  720_000),  (63,  630_000),
            (74,  740_000),  (60,  600_000),
        ],
        "005": [  # Aneka Susu
            (45,  450_000),  (48,  480_000),  (47,  470_000),
            (50,  500_000),  (52,  520_000),  (49,  490_000),
            (51,  510_000),  (54,  540_000),  (46,  460_000),
            (55,  550_000),  (45,  450_000),
        ],
    }

    # get category ids
    cur.execute("SELECT id, kode FROM categories")
    cat_map = {row["kode"]: row["id"] for row in cur.fetchall()}

    for kode, months in sales_data.items():
        cat_id = cat_map.get(kode)
        if cat_id is None:
            continue
        for bulan_idx, (qty, amount) in enumerate(months, start=1):
            cur.execute("""
                INSERT OR IGNORE INTO monthly_sales (category_id, tahun, bulan, qty, amount)
                VALUES (?, 2026, ?, ?, ?)
            """, (cat_id, bulan_idx, qty, amount))


def _seed_analysis_history(cur):
    histories = [
        ("AN-005", "24 Nov 2024", "Januari", "November", 63, 4, "Selesai", "admin"),
        ("AN-004", "10 Okt 2024", "Januari", "Oktober",  61, 4, "Selesai", "admin"),
        ("AN-003", "15 Sep 2024", "Januari", "September",60, 4, "Selesai", "budi"),
    ]
    for aid, tgl, pa, pakhir, jalt, jkrit, status, by in histories:
        cur.execute("""
            INSERT OR IGNORE INTO analysis_history
                (analysis_id, tanggal, periode_awal, periode_akhir,
                 jumlah_alternatif, jumlah_kriteria, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (aid, tgl, pa, pakhir, jalt, jkrit, status, by))


# ─────────────────────────── Query helpers ────────────────────────────────────

def get_user(username: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM users WHERE username = ? AND password = ? AND status = 'Aktif'
    """, (username, hash_password(password)))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM categories ORDER BY kode")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_monthly_sales(tahun: int = 2026):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.kode, c.nama, ms.bulan, ms.qty, ms.amount
        FROM monthly_sales ms
        JOIN categories c ON ms.category_id = c.id
        WHERE ms.tahun = ?
        ORDER BY c.kode, ms.bulan
    """, (tahun,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_analysis_history():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analysis_history ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_dashboard_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM categories WHERE status='Aktif'")
    total_cat = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(DISTINCT bulan) as total FROM monthly_sales WHERE tahun=2026")
    total_months = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) as total FROM analysis_history")
    total_analysis = cur.fetchone()["total"]
    conn.close()
    return {
        "total_categories": total_cat,
        "total_months": total_months,
        "total_analysis": total_analysis,
        "last_analysis": "24 Nov 2026, 14:30",
    }


MONTH_NAMES_DB = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}


def get_sales_for_analysis(tahun: int, bulan_awal: int, bulan_akhir: int) -> list:
    """Return per-category monthly sales rows for the requested period."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id as category_id, c.kode, c.nama,
               ms.bulan, ms.qty, ms.amount
        FROM categories c
        LEFT JOIN monthly_sales ms
               ON ms.category_id = c.id
              AND ms.tahun        = ?
              AND ms.bulan BETWEEN ? AND ?
        WHERE c.status = 'Aktif'
        ORDER BY c.kode, ms.bulan
    """, (tahun, bulan_awal, bulan_akhir))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def save_analysis_result(analysis_data: dict) -> str:
    """Persist analysis result to history. Returns the new analysis_id."""
    import json as _json
    conn = get_connection()
    cur  = conn.cursor()

    # Next sequential analysis ID (find highest numerical suffix)
    cur.execute("SELECT analysis_id FROM analysis_history")
    rows = cur.fetchall()
    max_num = 0
    for r in rows:
        aid_str = str(r["analysis_id"])
        if aid_str.startswith("AN-"):
            try:
                val = int(aid_str.replace("AN-", ""))
                if val > max_num:
                    max_num = val
            except ValueError:
                pass
    analysis_id = f"AN-{(max_num + 1):03d}"

    tanggal      = datetime.now().strftime("%d %b %Y, %H:%M")
    periode_awal  = MONTH_NAMES_DB.get(analysis_data.get("bulan_awal", 1), "?")
    periode_akhir = MONTH_NAMES_DB.get(analysis_data.get("bulan_akhir", 12), "?")

    cur.execute("""
        INSERT OR IGNORE INTO analysis_history
            (analysis_id, tanggal, periode_awal, periode_akhir,
             jumlah_alternatif, jumlah_kriteria, status, created_by, result_json)
        VALUES (?, ?, ?, ?, ?, ?, 'Selesai', ?, ?)
    """, (
        analysis_id,
        tanggal,
        periode_awal,
        periode_akhir,
        analysis_data.get("jumlah_alternatif", 0),
        analysis_data.get("jumlah_kriteria", 4),
        analysis_data.get("created_by", "admin"),
        _json.dumps(analysis_data, ensure_ascii=False),
    ))
    conn.commit()
    conn.close()
    return analysis_id


def get_analysis_by_id(analysis_id: str) -> dict:
    """Load a full analysis record (including parsed result_json)."""
    import json as _json
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM analysis_history WHERE analysis_id = ?", (analysis_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    record = dict(row)
    if record.get("result_json"):
        record["result_data"] = _json.loads(record["result_json"])
    return record


def get_latest_analysis() -> dict:
    """Return the most recently saved analysis record that has full result_json."""
    import json as _json
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM analysis_history WHERE result_json IS NOT NULL ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    record = dict(row)
    if record.get("result_json"):
        record["result_data"] = _json.loads(record["result_json"])
    return record


def get_dashboard_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM categories WHERE status='Aktif'")
    total_cat = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(DISTINCT bulan) as total FROM monthly_sales WHERE tahun=2026")
    total_months = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) as total FROM analysis_history")
    total_analysis = cur.fetchone()["total"]
    # Last analysis timestamp
    cur.execute("SELECT tanggal FROM analysis_history ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    last_analysis = row["tanggal"] if row else "—"
    conn.close()
    return {
        "total_categories": total_cat,
        "total_months": total_months,
        "total_analysis": total_analysis,
        "last_analysis": last_analysis,
    }


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
