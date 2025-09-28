import streamlit as st
from llm_query import ask_llm

st.set_page_config(page_title="Music Knowledge Graph Chat", page_icon="🎵")

st.title("🎵 Music Knowledge Graph Chat")
st.write("Ask questions about artists, albums, tracks, and genres.")

# Keep chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get answer
    answer = ask_llm(prompt)
    st.session_state["messages"].append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
