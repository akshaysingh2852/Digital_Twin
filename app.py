import streamlit as st
from copy import deepcopy

from twin import chat, history as initial_history


# --------------------------------------------------
# Streamlit page
# --------------------------------------------------

st.set_page_config(
    page_title="My Digital Twin",
    page_icon="🤖",
)

st.title("My Digital Twin")
st.caption("Ask me about my career, skills, and experience.")


# --------------------------------------------------
# Initialize conversation history
# --------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = deepcopy(initial_history)

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# Display previous messages
# --------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# --------------------------------------------------
# Handle new user message
# --------------------------------------------------

if prompt := st.chat_input("Ask my digital twin..."):

    # Display user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.write(prompt)

    # Get response from Gemini
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = chat(
                    prompt,
                    st.session_state.history,
                )

                st.write(answer)

            except Exception as e:
                answer = "Sorry, something went wrong."
                st.error(f"{answer}\n\nError: {e}")

    # Save assistant response for display
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )