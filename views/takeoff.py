import streamlit as st
import base64
import time
from logic.destinations import country_flag
from ui.takeoff_styles import takeoff_styles
from ui.plane_styles import plane_styles

def render_takeoff():
    dest = st.session_state.current_destination
    code = dest["code"]

    st.markdown(takeoff_styles(), unsafe_allow_html=True)

    # ---- Text ----
    st.subheader(
        f"Taking off to {dest['city']}, {dest['country']} {country_flag(code)}"
    )

    # ---- Plane Animation ----
    try:
        st.markdown(plane_styles(), unsafe_allow_html=True)

    except FileNotFoundError:
        pass

    st.caption("Fasten your seatbelt… we’re taking off! ✈️")

    # ---- Transition After 3 Seconds ----
    if "takeoff_timer_started" not in st.session_state:
        st.session_state.takeoff_timer_started = True
        time.sleep(3)
        st.session_state.view = "chat"
        del st.session_state.takeoff_timer_started
        st.rerun()
