import os
from copy import deepcopy
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from twin import chat, history as initial_history


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

UNKNOWN_QUESTIONS_FILE = BASE_DIR / "unknown_questions.txt"
USER_DETAILS_FILE = BASE_DIR / "user_details.txt"

load_dotenv(BASE_DIR / ".env")


def get_admin_password():
    """
    Read the admin password from Streamlit secrets.
    If no secrets file exists, fall back to .env.
    """

    try:
        password = st.secrets.get("ADMIN_PASSWORD", "")
    except st.errors.StreamlitSecretNotFoundError:
        password = ""

    if not password:
        password = os.getenv("ADMIN_PASSWORD", "")

    return password


def read_saved_file(file_path: Path) -> str:
    """Read a saved text file, or return a message if it doesn't exist."""

    if file_path.exists():
        return file_path.read_text(encoding="utf-8")

    return "No records have been saved yet."


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
# Admin portal
# --------------------------------------------------

with st.sidebar:
    st.header("Admin Centre")

    admin_password = get_admin_password()

    if not admin_password:
        st.warning(
            "Admin password is not configured. "
            "Add ADMIN_PASSWORD to your .env or secrets.toml file."
        )

    entered_password = st.text_input(
        "Admin password",
        type="password",
        key="admin_password_input",
    )

    if st.button("Unlock Admin Portal"):
        if admin_password and entered_password == admin_password:
            st.session_state.admin_authenticated = True
        else:
            st.session_state.admin_authenticated = False
            st.error("Incorrect admin password.")

    if st.session_state.get("admin_authenticated", False):
        st.success("Admin access granted")

        st.divider()

        # ------------------------------------------
        # Unknown questions
        # ------------------------------------------

        st.subheader("Unknown Questions")

        unknown_questions = read_saved_file(
            UNKNOWN_QUESTIONS_FILE
        )

        st.text_area(
            "Saved questions",
            value=unknown_questions,
            height=220,
            disabled=True,
            key="admin_unknown_questions",
        )

        st.download_button(
            label="Download Unknown Questions",
            data=unknown_questions,
            file_name="unknown_questions.txt",
            mime="text/plain",
            disabled=not UNKNOWN_QUESTIONS_FILE.exists(),
            key="download_unknown_questions",
        )

        st.divider()

        # ------------------------------------------
        # Visitor contact details
        # ------------------------------------------

        st.subheader("Visitor Contact Details")

        user_details = read_saved_file(
            USER_DETAILS_FILE
        )

        st.text_area(
            "Saved visitor details",
            value=user_details,
            height=220,
            disabled=True,
            key="admin_user_details",
        )

        st.download_button(
            label="Download Visitor Details",
            data=user_details,
            file_name="user_details.txt",
            mime="text/plain",
            disabled=not USER_DETAILS_FILE.exists(),
            key="download_user_details",
        )

        st.divider()

        # ------------------------------------------
        # Lock admin portal
        # ------------------------------------------

        if st.button("Lock Admin Portal"):
            st.session_state.admin_authenticated = False
            st.rerun()


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

                st.error(
                    f"{answer}\n\nError: {e}"
                )

    # Save assistant response for display
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )