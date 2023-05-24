import streamlit as st
import pandas as pd
top_novart = pd.read_csv('C:/Users/Work Runa Art/Downloads/Novart_top.csv',sep=';')

def clear_text():
    st.session_state["sku"] = ""

if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns = ['SKU', 'Part'])

if 'merged' not in st.session_state:
    st.session_state['merged'] = pd.DataFrame(columns = ['SKU','Part','remain','count'])

sku = st.text_input('Scan Image', value="", key='sku')
if sku[:8] in top_novart['SKU'].tolist():
    st.success('SKU is TOP', icon="✅")
    Lager = True
else:
    st.error('SKU in Müll', icon="🚨")
    Lager = False

if sku != "":
    new_row = {"SKU": sku[:8], 'Part':int(sku[9:]), 'TOP':Lager}
    st.session_state['data'] = pd.concat([st.session_state['data'], pd.DataFrame(new_row, index=[0])], ignore_index=True)



if st.button("Calculate_parts", on_click=clear_text):
    data = st.session_state['data']
    data['n'] = data['SKU'].str[5].astype(int)
    counts = data.groupby(['SKU', 'Part']).size().reset_index(name='count')
    all_parts = pd.DataFrame({'SKU': data['SKU'].unique()})
    all_parts['key'] = 1
    part_numbers = pd.DataFrame({'Part': range(1, data['n'].max() + 1)})
    part_numbers['key'] = 1
    combined = all_parts.merge(part_numbers, on='key').drop('key', axis=1)
    combined = combined[combined['SKU'].str[5].astype(int) >= combined['Part']]
    merged = combined.merge(counts, how='left', on=['SKU', 'Part']).fillna(0)
    merged['Max'] = merged.groupby('SKU')['count'].transform('max')
    merged['remain'] = merged['Max'] - merged['count']
    to_print = merged[merged['remain'] != 0][['SKU','Part','remain']].rename(columns={'remain':'Print'})
    st.session_state['merged'] = merged
    st.write(to_print)

completed = st.session_state['merged'].groupby('SKU', as_index=False)['count'].agg(min)
completed = completed[completed['count'] > 0]
completed['Lager'] = completed['SKU'].isin(top_novart['SKU'])

col1, col2 = st.columns(2)
col1.download_button("Download OXO", data= st.session_state['merged'][st.session_state['merged']['remain'] != 0][['SKU','Part','remain']].rename(columns={'remain':'Print'}).to_csv(index=False),file_name='retur_sku.csv',mime='text/csv')
col2.download_button("Download Completed", data= completed.to_csv(index=False),file_name='ready_pictures.csv',mime='text/csv')