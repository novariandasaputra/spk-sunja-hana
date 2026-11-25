"""
critic_topsis.py — Mesin kalkulasi CRITIC + TOPSIS
====================================================
CRITIC  : Criteria Importance Through Intercriteria Correlation
TOPSIS  : Technique for Order Preference by Similarity to Ideal Solution

Kriteria yang digunakan (4 kriteria):
  C1 – Total Qty      (benefit : lebih tinggi lebih baik)
  C2 – Total Amount   (benefit)
  C3 – Bulan Aktif    (benefit : berapa bulan ada data)
  C4 – CV Qty         (cost    : koefisien variasi → lebih rendah = lebih stabil)
"""

import numpy as np
import pandas as pd
from database import get_connection

# ── Kriteria metadata ──────────────────────────────────────────────────────────
CRITERIA_SHORT  = ["C1", "C2", "C3", "C4"]
CRITERIA_LABELS = ["C1: Qty", "C2: Amount (Rp)", "C3: Bulan Aktif", "C4: CV Qty"]
CRITERIA_TYPES  = ["benefit", "benefit", "benefit", "cost"]

MONTH_NAMES = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}

# ── 1. Bangun Matriks Keputusan dari SQLite ────────────────────────────────────

def build_decision_matrix(tahun: int, bulan_awal: int, bulan_akhir: int) -> pd.DataFrame:
    """
    Ambil data penjualan dari SQLite dan hitung nilai keempat kriteria
    untuk setiap kategori aktif dalam periode yang diminta.

    Returns DataFrame kolom: kode, nama, C1, C2, C3, C4
    """
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT id, kode, nama FROM categories WHERE status='Aktif' ORDER BY kode")
    categories = [dict(r) for r in cur.fetchall()]

    rows = []
    for cat in categories:
        cur.execute("""
            SELECT bulan, qty, amount FROM monthly_sales
            WHERE category_id = ? AND tahun = ?
              AND bulan BETWEEN ? AND ?
            ORDER BY bulan
        """, (cat["id"], tahun, bulan_awal, bulan_akhir))
        monthly = [dict(r) for r in cur.fetchall()]

        if not monthly:
            rows.append({"kode": cat["kode"], "nama": cat["nama"],
                         "C1": 0, "C2": 0, "C3": 0, "C4": 0})
            continue

        qtys    = [m["qty"]    for m in monthly]
        amounts = [m["amount"] for m in monthly]

        c1 = sum(qtys)
        c2 = sum(amounts)
        c3 = len(monthly)   # jumlah bulan yang ada datanya

        mean_qty = np.mean(qtys)
        if mean_qty > 0 and len(qtys) > 1:
            c4 = round(float(np.std(qtys, ddof=1) / mean_qty), 4)
        else:
            c4 = 0.0

        rows.append({"kode": cat["kode"], "nama": cat["nama"],
                     "C1": c1, "C2": c2, "C3": c3, "C4": c4})

    conn.close()
    return pd.DataFrame(rows)


# ── 2. CRITIC : Bobot Objektif ─────────────────────────────────────────────────

def compute_critic(matrix: np.ndarray, criteria_types: list) -> dict:
    """
    Hitung bobot CRITIC.

    Langkah:
      1. Normalisasi min-max (sesuai tipe kriteria)
      2. Standar deviasi tiap kolom ternormalisasi
      3. Matriks korelasi antar kolom
      4. C_j = σ_j · Σ_k(1 − r_jk)   ← information measure
      5. w_j = C_j / Σ C_j

    Returns dict dengan: normalized, std_dev, correlation,
                         conflict, information, weights
    """
    m, n = matrix.shape

    # Langkah 1 – normalisasi
    norm = np.zeros_like(matrix, dtype=float)
    for j in range(n):
        col  = matrix[:, j].astype(float)
        cmin, cmax = col.min(), col.max()
        if cmax == cmin:
            norm[:, j] = 1.0
        elif criteria_types[j] == "benefit":
            norm[:, j] = (col - cmin) / (cmax - cmin)
        else:
            norm[:, j] = (cmax - col) / (cmax - cmin)

    # Langkah 2 – standar deviasi
    std_dev = norm.std(axis=0, ddof=(1 if m > 1 else 0))

    # Langkah 3 – korelasi
    if m > 1:
        with np.errstate(divide="ignore", invalid="ignore"):
            corr = np.corrcoef(norm.T)
        corr = np.nan_to_num(corr, nan=0.0)   # std=0 → NaN → ganti 0
    else:
        corr = np.ones((n, n))

    # Langkah 4 – information measure
    conflict    = np.sum(1 - corr, axis=1)   # Σ_k (1-r_jk)
    information = std_dev * conflict

    # Langkah 5 – bobot
    # Jika semua information = 0 (semua kriteria identik), gunakan bobot rata-rata
    total = information.sum()
    if total > 0:
        weights = information / total
    else:
        weights = np.ones(n) / n

    # Jika ada kriteria dengan information = 0 tapi yang lain tidak,
    # berikan bobot minimum 0.01 agar kriteria tersebut tetap dipertimbangkan
    if total > 0 and (weights == 0).any():
        min_w = 0.01
        zero_mask = weights == 0
        weights[zero_mask] = min_w
        # Re-normalize
        weights = weights / weights.sum()

    return {
        "normalized":   norm,
        "std_dev":      std_dev,
        "correlation":  corr,
        "conflict":     conflict,
        "information":  information,
        "weights":      weights,
    }


# ── 3. TOPSIS ──────────────────────────────────────────────────────────────────

def compute_topsis(matrix: np.ndarray, weights: np.ndarray,
                   criteria_types: list) -> dict:
    """
    Hitung TOPSIS.

    Langkah:
      1. Normalisasi vektor   r_ij = x_ij / ||x_j||
      2. Matriks terbobot     v_ij = w_j · r_ij
      3. Solusi ideal positif (A+) dan negatif (A-)
      4. Jarak D+ dan D-
      5. Nilai preferensi V_i = D- / (D+ + D-)

    Returns dict dengan semua hasil antara.
    """
    m, n = matrix.shape

    # Langkah 1
    vec_norms = np.sqrt((matrix.astype(float) ** 2).sum(axis=0))
    vec_norms[vec_norms == 0] = 1.0
    r = matrix.astype(float) / vec_norms

    # Langkah 2
    v = r * weights

    # Langkah 3
    pis = np.zeros(n)
    nis = np.zeros(n)
    for j in range(n):
        if criteria_types[j] == "benefit":
            pis[j] = v[:, j].max()
            nis[j] = v[:, j].min()
        else:
            pis[j] = v[:, j].min()
            nis[j] = v[:, j].max()

    # Langkah 4
    d_plus  = np.sqrt(((v - pis) ** 2).sum(axis=1))
    d_minus = np.sqrt(((v - nis) ** 2).sum(axis=1))

    # Langkah 5
    denom = d_plus + d_minus
    denom[denom == 0] = 1e-12
    preference = d_minus / denom

    return {
        "r_matrix":   r,
        "v_matrix":   v,
        "pis":        pis,
        "nis":        nis,
        "d_plus":     d_plus,
        "d_minus":    d_minus,
        "preference": preference,
    }


# ── 4. Pipeline utama ──────────────────────────────────────────────────────────

def run_analysis(tahun: int, bulan_awal: int, bulan_akhir: int) -> dict:
    """
    Jalankan seluruh pipeline CRITIC-TOPSIS.

    Returns dict lengkap berisi semua langkah perhitungan dan peringkat.
    Jika ada error, dict akan memiliki key "error".
    """
    # 1. Matriks keputusan
    df = build_decision_matrix(tahun, bulan_awal, bulan_akhir)

    if df.empty or len(df) < 2:
        return {"error": "Minimal 2 kategori aktif dibutuhkan. Periksa data penjualan."}

    raw = df[["C1", "C2", "C3", "C4"]].values.astype(float)

    # Validasi: semua kolom tidak boleh semua-nol
    if (raw == 0).all():
        return {"error": "Tidak ada data penjualan untuk periode yang dipilih."}

    # 2. CRITIC
    critic = compute_critic(raw, CRITERIA_TYPES)
    weights = critic["weights"]

    # 3. TOPSIS
    topsis = compute_topsis(raw, weights, CRITERIA_TYPES)
    preference = topsis["preference"]

    # 4. Peringkat (descending)
    ranking_idx = np.argsort(preference)[::-1]
    rankings = []
    for rank, idx in enumerate(ranking_idx, start=1):
        rankings.append({
            "rank":            rank,
            "kode":            df.iloc[idx]["kode"],
            "nama":            df.iloc[idx]["nama"],
            "d_plus":          round(float(topsis["d_plus"][idx]),  6),
            "d_minus":         round(float(topsis["d_minus"][idx]), 6),
            "nilai_preferensi": round(float(preference[idx]),       4),
        })

    # 5. Kembalikan semua hasil
    result = {
        "tahun":              tahun,
        "bulan_awal":         bulan_awal,
        "bulan_akhir":        bulan_akhir,
        "periode_label": (
            f"{MONTH_NAMES.get(bulan_awal, '')} – "
            f"{MONTH_NAMES.get(bulan_akhir, '')} {tahun}"
        ),
        "jumlah_alternatif":  len(df),
        "jumlah_kriteria":    4,
        "alternatif":         df[["kode", "nama"]].to_dict("records"),

        # Matriks keputusan awal
        "decision_matrix": {
            "data":    raw.tolist(),
            "index":   df["nama"].tolist(),
            "columns": CRITERIA_SHORT,
            "labels":  CRITERIA_LABELS,
            "types":   CRITERIA_TYPES,
        },

        # CRITIC
        "critic": {
            "normalized":   critic["normalized"].tolist(),
            "std_dev":      [round(x, 6) for x in critic["std_dev"].tolist()],
            "correlation":  [[round(v, 4) for v in row]
                             for row in critic["correlation"].tolist()],
            "conflict":     [round(x, 6) for x in critic["conflict"].tolist()],
            "information":  [round(x, 6) for x in critic["information"].tolist()],
            "weights":      [round(x, 6) for x in weights.tolist()],
        },

        # TOPSIS
        "topsis": {
            "r_matrix":   [[round(v, 6) for v in row]
                           for row in topsis["r_matrix"].tolist()],
            "v_matrix":   [[round(v, 6) for v in row]
                           for row in topsis["v_matrix"].tolist()],
            "pis":        [round(x, 6) for x in topsis["pis"].tolist()],
            "nis":        [round(x, 6) for x in topsis["nis"].tolist()],
            "d_plus":     [round(x, 6) for x in topsis["d_plus"].tolist()],
            "d_minus":    [round(x, 6) for x in topsis["d_minus"].tolist()],
            "preference": [round(x, 4) for x in preference.tolist()],
        },

        # Peringkat final
        "rankings": rankings,
    }

    return result


# ── 5. Validasi cepat sebelum analisis ────────────────────────────────────────

def validate_data(tahun: int, bulan_awal: int, bulan_akhir: int) -> dict:
    """
    Periksa kelayakan data sebelum analisis dijalankan.
    Returns dict: { ok: bool, messages: list[str], stats: dict }
    """
    df = build_decision_matrix(tahun, bulan_awal, bulan_akhir)
    messages = []
    stats    = {}

    if df.empty:
        return {"ok": False, "messages": ["Tidak ada kategori aktif."], "stats": {}}

    n_alt = len(df)
    no_data = df[(df["C1"] == 0) & (df["C3"] == 0)]["nama"].tolist()
    partial  = df[(df["C3"] > 0) &
                  (df["C3"] < (bulan_akhir - bulan_awal + 1))]["nama"].tolist()

    stats = {
        "jumlah_alternatif": n_alt,
        "jumlah_kriteria":   4,
        "tanpa_data":        no_data,
        "data_parsial":      partial,
    }

    if n_alt < 2:
        messages.append("⚠ Minimal 2 kategori diperlukan untuk analisis.")
    if no_data:
        messages.append(f"⚠ Kategori tanpa data: {', '.join(no_data)}")
    if partial:
        messages.append(f"ℹ Data tidak lengkap (sebagian bulan): {', '.join(partial)}")
    if not messages:
        messages.append("✅ Semua data valid dan siap dianalisis.")

    return {
        "ok":       n_alt >= 2 and not no_data,
        "messages": messages,
        "stats":    stats,
        "df":       df,
    }
