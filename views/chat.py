import streamlit as st
import base64
from pathlib import Path

from agent.chat import GeminiChat
from langchain_core.messages import HumanMessage

from logic.destinations import country_flag, FLAG_NAME
from logic.render_messages import render_message
from ui.chat_styles import chat_styles
from ui.pilot_styles import pilot_styles


def render_chat():
    # ---------------- CHAT VIEW ---------------- #
    dest = st.session_state.current_destination
    code = dest["code"]

    # ---- Flag-based background from /pictures/flags ----
    flag_style = "background: linear-gradient(to bottom, #87CEFA, #ffffff);"

    base_name = FLAG_NAME.get(code.upper())
    if base_name is not None:
        flags_dir = Path("pictures") / "flags"
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            candidate = flags_dir / f"{base_name}{ext}"
            if candidate.exists():
                with open(candidate, "rb") as f:
                    flag_data = f.read()
                flag_encoded = base64.b64encode(flag_data).decode()

                # correct MIME types
                ext_no_dot = ext[1:].lower()
                if ext_no_dot in ("jpg", "jpeg"):
                    mime = "jpeg"
                elif ext_no_dot == "png":
                    mime = "png"
                elif ext_no_dot == "webp":
                    mime = "webp"
                else:
                    mime = ext_no_dot

                flag_style = f"""
                background-image: url("data:image/{mime};base64,{flag_encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                """
                break
    
    st.markdown(chat_styles(flag_style), unsafe_allow_html=True)

    st.caption(
        f"Destination: {country_flag(code)} {dest['city']}, {dest['country']}"
    )

    st.markdown(pilot_styles(), unsafe_allow_html=True)

    # ---- LLM + message state ----
    if "llm" not in st.session_state:
        st.session_state.llm = GeminiChat()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render chat history
    for msg in st.session_state.messages:
        render_message(msg)

    # User input
    prompt = st.chat_input("Your message")
    if not prompt:
        return

    # User message
    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)
    render_message(user_msg)

    # Inject destination context for the model
    context_prefix = (
        f"The current destination is {dest['city']}, {dest['country']} "
        f"({country_flag(code)}). "
        "Answer specifically for this destination.\n\n"
    )
    full_prompt = context_prefix + prompt

    # Ask the LLM
    new_messages = st.session_state.llm.send_message(full_prompt)

    # Append and render new messages
    for msg in new_messages:
        st.session_state.messages.append(msg)
        render_message(msg)
