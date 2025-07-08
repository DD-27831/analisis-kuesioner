import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analisis Kuesioner", layout="wide")
st.title("📊 Kalkulator Alpha Cronbach")

uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("📄 Data yang diunggah:")
    st.dataframe(df)

    df['Content'] = df[['Q1', 'Q2']].mean(axis=1)
    df['Accuracy'] = df[['Q3', 'Q4']].mean(axis=1)

    def cronbach_alpha(items_scores):
        items_scores = np.array(items_scores)
        item_vars = items_scores.var(axis=0, ddof=1)
        total_var = items_scores.sum(axis=1).var(ddof=1)
        n_items = items_scores.shape[1]
        return (n_items / (n_items - 1)) * (1 - item_vars.sum() / total_var)

    alpha = cronbach_alpha(df[['Q1', 'Q2', 'Q3', 'Q4', 'Q5']])

    st.subheader("📈 Hasil Analisis")
    st.metric("Rata-rata Content", round(df['Content'].mean(), 2))
    st.metric("Rata-rata Accuracy", round(df['Accuracy'].mean(), 2))
    st.metric("Cronbach’s Alpha", round(alpha, 3))
