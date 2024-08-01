import streamlit as st

def Navbar():
    st.logo("images/Oracle.png")
    st.sidebar.page_link('main.py', label='Home')
    st.sidebar.page_link('pages/myosearch.py', label='MyOracleSearch')
    st.sidebar.page_link('pages/agent.py', label='GenAI Agent (beta)')