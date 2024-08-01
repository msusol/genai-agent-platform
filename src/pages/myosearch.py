import streamlit as st
import nav

nav.Navbar()
st.sidebar.info("..")

if st.session_state.get("page", "MyOracleSearch") != st.session_state.current_page:
    # Clear all session state data
    st.session_state.clear()

    # Store the current page for the next comparison
    st.session_state.current_page = st.session_state.get("page", "MyOracleSearch")

# TODO: Connect to myosearch-dev API
