import streamlit as st
import nav

st.set_page_config(
    page_title="OCI Agent Platform (beta) - DEMO",
    page_icon="images/o.png",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items=None)

nav.Navbar()
st.sidebar.info("Check out ..")

st.session_state.current_page = st.session_state.get("page", "home")

if st.session_state.get("page", "Home") != st.session_state.current_page:
    # Clear all session state data
    st.session_state.clear()

    # Store the current page for the next comparison
    st.session_state.current_page = st.session_state.get("page", "Home")


st.markdown(
    """
    ## What can I do here?
    - Use **RAG Agent** to chat with an AI that has specialized knowledge of Oracle Cloud for US Government. 
        - Ask it things like `How can Oracle Cloud support my agency's zero trust journey?`
    """
)
