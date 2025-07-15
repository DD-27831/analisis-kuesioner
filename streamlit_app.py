import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
import os

# =========================
# Metadata & Judul Aplikasi
# =========================
st.set_page_config(
    page_title="Kalkulator Cronbach Alpha per Dimensi (EUCS)",
    page_icon="📊",
    layout="wide"
)
st.title("📊 Kalkulator Cronbach Alpha per Dimensi (EUCS)")

# =========================
# Hapus DB lama jika ingin reset (opsional)
if not os.path.exists('data_kuesioner.db'):
    conn1 = sqlite3.connect('data_kuesioner.db')
    c1 = conn1.cursor()
    c1.execute('''
        CREATE TABLE IF NOT EXISTS respon_kuesioner (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ''' + ', '.join([f'Q{i} REAL' for i in range(1,14)]) + ''',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn1.commit()
    conn1.close()

if not os.path.exists('hasil_analisis.db'):
    conn2 = sqlite3.connect('hasil_analisis.db')
    c2 = conn2.cursor()
    c2.execute('''
        CREATE TABLE IF NOT EXISTS hasil_analisis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dimensi TEXT,
            cronbach_alpha REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn2.commit()
    conn2.close()

# =========================
# Upload File Excel
# =========================
st.subheader("📥 Upload Data Kuesioner")
uploaded_file = st.file_uploader("Unggah file Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Baca Excel
    df = pd.read_excel(uploaded_file)
    st.write("📄 Data yang diunggah:")
    st.dataframe(df)

    # Koneksi ke Database
    conn1 = sqlite3.connect('data_kuesioner.db')
    conn2 = sqlite3.connect('hasil_analisis.db')
    c1 = conn1.cursor()
    c2 = conn2.cursor()

    # Simpan data mentah ke DB1
    question_cols = [f'Q{i}' for i in range(1, 14)]
    df[question_cols].to_sql('respon_kuesioner', conn1, if_exists='append', index=False)

    # Definisi Dimensi EUCS
    dimensi_dict = {
        'Content': ['Q1', 'Q2', 'Q3'],
        'Accuracy': ['Q4', 'Q5', 'Q6'],
        'Format': ['Q7', 'Q8', 'Q9'],
        'Ease of Use': ['Q10', 'Q11'],
        'Timeliness': ['Q12', 'Q13']
    }

    # Hitung Cronbach Alpha per Dimensi
    hasil_alpha = {}
    for dimensi, pertanyaan in dimensi_dict.items():
        def cronbach_alpha(items_scores):
            items_scores = np.array(items_scores)
            item_vars = items_scores.var(axis=0, ddof=1)
            total_var = items_scores.sum(axis=1).var(ddof=1)
            n_items = items_scores.shape[1]
            return (n_items / (n_items - 1)) * (1 - item_vars.sum() / total_var)

        alpha = round(cronbach_alpha(df[pertanyaan]), 3)
        hasil_alpha[dimensi] = alpha

        # Simpan ke DB2
        c2.execute('''
            INSERT INTO hasil_analisis (dimensi, cronbach_alpha)
            VALUES (?, ?)
        ''', (dimensi, alpha))
        conn2.commit()

    st.success("✅ Hasil Cronbach Alpha per Dimensi telah disimpan ke Database.")

    # =========================
    # Tampilkan Hasil Analisis
    # =========================
    st.subheader("📈 Hasil Cronbach Alpha per Dimensi")
    hasil_df = pd.DataFrame(list(hasil_alpha.items()), columns=['Dimensi', 'Cronbach Alpha'])
    st.dataframe(hasil_df)

    # =========================
    # Grafik Bar Chart Warna-warni
    # =========================
    st.subheader("📊 Visualisasi Cronbach Alpha per Dimensi")
    colors = ['#4CAF50', '#2196F3', '#FFC107', '#9C27B0', '#FF5722']  # Warna per dimensi
    bar_chart = go.Figure(data=[
        go.Bar(
            name='Cronbach Alpha',
            x=list(hasil_alpha.keys()),
            y=list(hasil_alpha.values()),
            marker_color=colors
        )
    ])
    bar_chart.update_layout(
        title="Cronbach Alpha per Dimensi",
        yaxis_title="Nilai Alpha"
    )
    st.plotly_chart(bar_chart, use_container_width=True)

    # Tutup koneksi DB
    conn1.close()
    conn2.close()

# =========================
# Riwayat Analisis
# =========================
st.subheader("📜 Riwayat Hasil Analisis (Database 2)")
conn2 = sqlite3.connect('hasil_analisis.db')
riwayat = pd.read_sql_query("SELECT * FROM hasil_analisis ORDER BY timestamp DESC", conn2)
st.dataframe(riwayat)
conn2.close()
