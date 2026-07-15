import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats
from reportlab.pdfgen import canvas
import io

st.set_page_config(page_title="Data Health Analyzer", layout="wide")

# --- UI Header ---
st.title("📊 Dataset Health Analyzer: Professional Auditor")
st.markdown("Upload your CSV to perform a comprehensive data quality check.")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # 1. Dataset Overview
    st.subheader("1️⃣ Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB")
    col4.metric("Duplicates", df.duplicated().sum())

    # 2. Data Health Score Logic
    st.subheader("2️⃣ Data Health Score ⭐")
    missing_ratio = df.isnull().mean().mean()
    health_score = int(max(0, 100 - (missing_ratio * 100) - (df.duplicated().sum() / len(df) * 100)))
    
    st.progress(health_score / 100)
    st.write(f"Overall Health Score: **{health_score}/100**")

    # 4. Outlier Detection (IQR Method)
    st.subheader("4️⃣ Outlier Detection (Numeric Columns)")
    numeric_df = df.select_dtypes(include=[np.number])
    outliers = {}
    for col in numeric_df.columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers[col] = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
    st.write("Outliers per column:", outliers)

    # 5. One-Click Clean
    st.subheader("5️⃣ Automatic Cleaning")
    if st.button("🚀 Clean Dataset & Download"):
        df_cleaned = df.drop_duplicates().fillna(df.median(numeric_only=True))
        csv = df_cleaned.to_csv(index=False).encode('utf-8')
        st.download_button("Download Cleaned CSV", csv, "cleaned_data.csv", "text/csv")
        st.success("Duplicates removed and missing values imputed with median!")

    # 6. PDF Certificate
    if st.button("📄 Generate Quality Certificate"):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 800, "DATA QUALITY CERTIFICATE")
        c.drawString(100, 780, f"Dataset Score: {health_score}/100")
        c.save()
        st.download_button("Download PDF", buffer.getvalue(), "Quality_Cert.pdf", "application/pdf")