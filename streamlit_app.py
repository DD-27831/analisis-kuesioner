import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# =====================
# Metadata & Judul
# =====================
st.set_page_config(
    page_title="Kalkulator Alpha Cronbach",
    page_icon="📊",
    layout="wide"
)
st.title("Kalkulator Alpha Cronbach")

# =====================
# Deskripsi Aplikasi
# =====================
st.write("""
Selamat datang di **Kalkulator Alpha Cronbach** 🎓  
Aplikasi ini membantu Anda menghitung **nilai Cronbach’s Alpha** untuk mengevaluasi reliabilitas kuesioner.  
*Silahkan unggah file Excel (.xlsx) berisi data jawaban responden*, dan sistem akan:
- Menghitung rata-rata dimensi
- Menampilkan nilai Cronbach’s Alpha
- Menyajikan grafik interaktif dan hasil yang dapat diunduh
""")

# =====================
# File Uploader
# =====================
uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx"])

if uploaded_file is not None:
    # =====================
    # Baca & Tampilkan Data
    # =====================
    df = pd.read_excel(uploaded_file)
    st.subheader("Data Jawaban Kuesioner")
    st.dataframe(df)

    # Hitung rata-rata dimensi
    df['Content'] = df[['Q1', 'Q2']].mean(axis=1)
    df['Accuracy'] = df[['Q3', 'Q4']].mean(axis=1)
    content_avg = round(df['Content'].mean(), 2)
    accuracy_avg = round(df['Accuracy'].mean(), 2)

    # =====================
    # Hitung Cronbach’s Alpha
    # =====================
    def cronbach_alpha(items_scores):
        items_scores = np.array(items_scores)
        item_vars = items_scores.var(axis=0, ddof=1)
        total_var = items_scores.sum(axis=1).var(ddof=1)
        n_items = items_scores.shape[1]
        return (n_items / (n_items - 1)) * (1 - item_vars.sum() / total_var)

    alpha = round(cronbach_alpha(df[['Q1', 'Q2', 'Q3', 'Q4', 'Q5']]), 3)

    # =====================
    # Hasil Analisis
    # =====================
    st.subheader("Hasil Analisis")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rata-rata Content", content_avg)
    col2.metric("Rata-rata Accuracy", accuracy_avg)
    col3.metric("Cronbach’s Alpha", alpha)

    # =====================
    # Grafik Bar Chart
    # =====================
    st.subheader("Grafik Rata-rata Dimensi")
    bar_chart = go.Figure(data=[
        go.Bar(name='Dimensi', x=['Content', 'Accuracy'], y=[content_avg, accuracy_avg],
               marker_color=['#4CAF50', '#2196F3'])
    ])
    bar_chart.update_layout(title="Rata-rata Dimensi", yaxis_title="Skor Rata-rata")
    st.plotly_chart(bar_chart, use_container_width=True)

    # =====================
    # Gauge Meter Cronbach’s Alpha
    # =====================
    st.subheader("Visualisasi Cronbach’s Alpha")
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

    # =====================
    # Tombol Download Hasil
    # =====================
    st.subheader("Download Hasil Analisis")
    hasil = pd.DataFrame({
        'Dimensi': ['Content', 'Accuracy'],
        'Rata-rata': [content_avg, accuracy_avg],
        'Cronbach_Alpha': [alpha, alpha]
    })

    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Hasil Analisis")
        processed_data = output.getvalue()
        return processed_data

    excel_data = convert_df_to_excel(hasil)

    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name='hasil_analisis.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
