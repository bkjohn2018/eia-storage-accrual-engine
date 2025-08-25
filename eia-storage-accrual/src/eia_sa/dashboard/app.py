import streamlit as st
from pathlib import Path

st.set_page_config(page_title='EIA Storage Accrual Engine', page_icon='', layout='wide')

def main():
    st.title(' EIA Storage Accrual Engine')
    st.caption('Silver  Gold  Accruals  Narratives')
    st.success('Dashboard created successfully! ')
    st.write('This is a minimal working version.')

if __name__ == '__main__':
    main()
