import streamlit as st
import asyncio
from logic.destinations import DESTINATIONS
from views.home import render_home
from views.takeoff import render_takeoff
from views.chat import render_chat

async def main():
    # ---- Initialize session state ----
    if "view" not in st.session_state:
        st.session_state.view = "home"  # "home", "takeoff", "chat"

    if "current_destination" not in st.session_state:
        st.session_state.current_destination = DESTINATIONS[1]  # default Berlin

    if st.session_state.view == "home":
        render_home()
        return

    if st.session_state.view == "takeoff":
        render_takeoff()
        return

    render_chat()


asyncio.run(main())
