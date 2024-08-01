import streamlit as st
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

def write_message(role, content, save = True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    if save:
        st.session_state.messages.append({"role": role, "content": content})

    with st.chat_message(role):
        st.markdown(content)

def get_session_id():
    return get_script_run_ctx().session_id