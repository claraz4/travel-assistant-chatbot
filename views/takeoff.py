import streamlit as st
import time
from logic.destinations import country_flag
from ui.takeoff_styles import takeoff_styles
from ui.plane_styles import plane_styles


def render_takeoff():
    dest = st.session_state.current_destination
    code = dest["code"]

    # simple flag: have we already started the timer on this screen?
    if "takeoff_timer_started" not in st.session_state:
        st.session_state.takeoff_timer_started = False

    st.markdown(takeoff_styles(), unsafe_allow_html=True)

    st.subheader(
        f"Taking off to {dest['city']}, {dest['country']} {country_flag(code)}"
    )
    st.caption("Fasten your seatbelt… we’re taking off! ✈️")

    # show the plane overlay
    try:
        st.markdown(plane_styles(), unsafe_allow_html=True)
    except FileNotFoundError:
        pass

    # first time we arrive on takeoff: wait then go to chat
    if not st.session_state.takeoff_timer_started:
        st.session_state.takeoff_timer_started = True
        time.sleep(3)

        st.session_state.view = "chat"
        st.session_state.takeoff_timer_started = False  # reset for next trip
        st.rerun()
