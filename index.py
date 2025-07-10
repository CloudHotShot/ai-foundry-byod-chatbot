import streamlit as st
from chat_completion_your_own_data import chat_completion_oyd_studio_viewcode
import time
import os

st.set_page_config(page_title="Azure OpenAI BYOD Chatbot", layout="centered")
st.title("Azure OpenAI BYOD Chatbot")

# Display environment variables in small text at the top left
env_vars = {
    "Model Deployment": os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "Not set"),
    "AI Search Index": os.environ.get("AZURE_OPENAI_SEARCH_INDEX", "Not set"),
    "AI Search Endpoint": os.environ.get("AZURE_OPENAI_SEARCH_ENDPOINT", "Not set"),
    "AI Endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT", "Not set"),
}

env_html = "<div style='position:fixed; top:10px; left:10px; z-index:1000; font-size:0.8em; color:#fff; background:none; border-radius:8px; padding:8px 16px;'>"
for k, v in env_vars.items():
    env_html += f"<div><b>{k}:</b> {v}</div>"
env_html += "</div>"
st.markdown(env_html, unsafe_allow_html=True)

st.write("Ask questions about your data using Azure OpenAI and Azure AI Search.")

# Initialize session state for chat history
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'pending' not in st.session_state:
    st.session_state['pending'] = False
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ""

# Use a form for chat input to support CTRL+ENTER
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area(
        "Your question:",
        "",
        height=100,
        key="user_input_box",
    )
    ask_clicked = st.form_submit_button("Ask")

bubble_styles = {
    'user': "background: #009966; color: #fff; border-radius: 20px; padding: 12px 18px; margin: 8px 0 8px auto; max-width: 70%; text-align: right; display: block; box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
    'agent': "background: #005a9e; color: #fff; border-radius: 20px; padding: 12px 18px; margin: 8px auto 8px 0; max-width: 70%; text-align: left; display: block; box-shadow: 0 2px 8px rgba(0,0,0,0.08);"
}

# Only allow one pending request at a time
if (ask_clicked or (user_input and st.session_state.get('pending') is False and st.session_state.get('last_input') != user_input)) and user_input.strip() and not st.session_state['pending']:
    st.session_state['pending'] = True
    st.session_state['last_input'] = user_input
    # Immediately display the user's question
    st.session_state['history'].append({"role": "user", "content": user_input})
    # Display chat history so far (including the new question)
    for msg in st.session_state['history']:
        if msg['role'] == 'user':
            st.markdown(f"<div style='{bubble_styles['user']}'><b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='{bubble_styles['agent']}'><b>Agent:</b> {msg['content']}</div>", unsafe_allow_html=True)
    # Now stream the agent's answer below the question
    with st.spinner("Agent is thinking..."):
        try:
            response = ""
            full_response = chat_completion_oyd_studio_viewcode(user_input)
            response_placeholder = st.empty()
            for word in full_response.split():
                response += word + " "
                response_placeholder.markdown(f"<div style='{bubble_styles['agent']}'><b>Agent:</b> {response}</div>", unsafe_allow_html=True)
                time.sleep(0.05)
            # Add agent message to history (only after streaming)
            st.session_state['history'].append({"role": "agent", "content": full_response})
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            st.session_state['pending'] = False
elif (ask_clicked or (user_input and st.session_state.get('pending') is False and st.session_state.get('last_input') != user_input)) and not user_input.strip():
    st.warning("Please enter a question.")
else:
    # Show chat history in order
    for msg in st.session_state['history']:
        if msg['role'] == 'user':
            st.markdown(f"<div style='{bubble_styles['user']}'><b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='{bubble_styles['agent']}'><b>Agent:</b> {msg['content']}</div>", unsafe_allow_html=True)