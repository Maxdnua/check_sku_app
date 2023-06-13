import streamlit as st
import pandas as pd

option = st.selectbox('Выберите модуль:',('Retur Toni', 'Retur Amazon'))


if option == 'Retur Amazon':
    top_novart = pd.read_csv('Novart_top.csv',sep=';', dtype={'EAN':'str'})

    def clear_text():
        st.session_state["sku"] = ""

    if 'data' not in st.session_state:
        st.session_state['data'] = pd.DataFrame(columns = ['SKU', 'Part'])

    if 'merged' not in st.session_state:
        st.session_state['merged'] = pd.DataFrame(columns = ['SKU','Part','remain','count'])
        
    module = st.radio('Choose what to scan', ['SKU','EAN'])

    if module == 'SKU':

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
            to_print = merged[(merged['remain'] != 0) & (merged['SKU'].isin(data[data['TOP']]['SKU'].unique()))][['SKU','Part','remain']].rename(columns={'remain':'Print'})
            st.session_state['merged'] = merged
            st.write(to_print)

        completed = st.session_state['merged'].groupby('SKU', as_index=False)['count'].agg(min)
        completed = completed[completed['count'] > 0]
        completed['Lager'] = completed['SKU'].isin(top_novart['SKU'])

        oxo = st.session_state['merged'][(st.session_state['merged']['remain'] != 0) & (st.session_state['merged']['SKU'].isin(top_novart['SKU']))][['SKU','Part','remain']].rename(columns={'remain':'Print'})

        col1, col2 = st.columns(2)
        col1.download_button("Download OXO", data= oxo.to_csv(index=False),file_name='retur_sku.csv',mime='text/csv')
        col2.download_button("Download Completed", data= completed.to_csv(index=False),file_name='ready_pictures.csv',mime='text/csv')
        
    else:
        ean = st.text_input('Scan Image', value="")
        if ean in top_novart['EAN'].tolist():
            st.success('SKU is TOP', icon="✅")
        else:
            st.error('SKU in Müll', icon="🚨")
elif option == 'Retur Toni':
    reture = pd.read_csv('Return Status.csv',sep=';', dtype={'EAN':'str'})

    st.header('Reture Toni')

    ean = st.text_input('Scan ean', key='ean')

    reture_scaned = reture[reture['EAN'] == ean]

    st.write(reture_scaned)

    for i, r in reture_scaned.iterrows():
        if r['Destination'] == 'Lager':
            st.success(r['Destination'] + " " + r['Lagerort'] + " - MHD: " + r['MHD'] + " - " + r['Good Status'] + "St.")
        elif r['Destination'] == 'Lager New':
            st.success("Lager  - внести в новое место - " + r['Good Status'] + "St.")
        elif r['Destination'] == 'Zapas':
            st.warning(r['Destination'] + " - " + r['Good Status'] + "St.")
        elif r['Destination'] == 'Prime':
            st.info(r['Destination'] + " - " + r['Good Status'] + "St.")
        elif r['Destination'] == 'Recycling':
            st.error(r['Destination'])
