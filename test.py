import streamlit as st
import pandas as pd
top_novart = pd.read_csv('C:/Users/Work Runa Art/Downloads/Novart_top.csv',sep=';')

ean = st.text_input('Scan Image', value="")[:8]
if ean in top_novart['SKU'].tolist():
    st.success('SKU is TOP', icon="✅")
else:
    st.error('SKU in Müll', icon="🚨")