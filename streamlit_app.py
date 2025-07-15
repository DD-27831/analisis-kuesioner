import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go

# =========================
# Metadata & Judul Aplikasi
# =========================
st.set_page_config(
    page_title="Kalkulator Alpha Cronbach (Dual DB)",
    page_icon="📊",
    layout="wide"
)
st.title("📊 Kalkulator Alpha Cronbach (Dual Database)")

# =========================
# Koneksi ke Database
# =========================
# DB1: Data Kuesioner Mentah
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

# DB2: Hasil Analisis
conn2 = sqlite3.connect('hasil_analisis.db')
c2 = conn2.cursor()
c2.execute('''
    CREATE TABLE IF NOT EXISTS hasil_analisis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cronbach_alpha REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn2.commit()

# =========================
# Upload File Excel
# =========================
st.subheader("📥 Upload Data Kuesioner")
uploaded_file = st.file_uploader("Unggah file Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("📄 Data yang diunggah:")
    st.dataframe(df)

    # Simpan data mentah ke DB1
    question_cols = [f'Q{i}' for i in range(1, 14)]
    df[question_cols].to_sql('respon_kuesioner', conn1, if_exists='append', index=False)

    # Hitung Cronbach’s Alpha
    def cronbach_alpha(items_scores):
        items_scores = np.array(items_scores)
        item_vars = items_scores.var(axis=0, ddof=1)
        total_var = items_scores.sum(axis=1).var(ddof=1)
        n_items = items_scores.shape[1]
        return (n_items / (n_items - 1)) * (1 - item_vars.sum() / total_var)

    alpha = round(cronbach_alpha(df[question_cols]), 3)

    # Simpan hasil analisis ke DB2
    c2.execute('''
        INSERT INTO hasil_analisis (cronbach_alpha)
        VALUES (?)
    ''', (alpha,))
    conn2.commit()

    st.success("✅ Data berhasil disimpan ke Database dan Cronbach’s Alpha telah dihitung.")

    # Tampilkan Hasil Analisis
    st.subheader("📈 Hasil Analisis")
    st.metric("Cronbach’s Alpha", alpha)

    # Gauge Meter
    st.subheader("📟 Visualisasi Cronbach’s Alpha")
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=alpha,
        title={'text': "Cronbach’s Alpha"},
        gauge={
            'axis': {'range': [0, 1]},
            'steps': [
                {'range': [0, 0.6], 'color': "#FF4C4C"},
                {'range': [0.6, 0.7], 'color': "#FFA500"},
                {'range': [0.7, 1.0], 'color': "#4CAF50"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': alpha
            }
        }
    ))
    st.plotly_chart(gauge, use_container_width=True)

# =========================
# Riwayat Analisis
# =========================
st.subheader("📜 Riwayat Hasil Analisis (Database 2)")
riwayat = pd.read_sql_query("SELECT * FROM hasil_analisis ORDER BY timestamp DESC", conn2)
st.dataframe(riwayat)

# =========================
# Tutup koneksi DB
# =========================
conn1.close()
conn2.close()
