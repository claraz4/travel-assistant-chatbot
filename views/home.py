import streamlit as st
from datetime import date
from logic.destinations import country_flag, DESTINATIONS
from ui.home_styles import home_styles
from ui.ticket_styles import ticket_styles

def render_home():
    st.markdown(home_styles(), unsafe_allow_html=True)

    st.subheader("Where do you want to fly today?")

    # Destination selector
    options = [
        f"{country_flag(d['code'])} {d['city']}, {d['country']}"
        for d in DESTINATIONS
    ]
    current = st.session_state.current_destination
    default_index = next(
        (i for i, d in enumerate(DESTINATIONS) if d["code"] == current["code"]),
        1,
    )

    selected_label = st.selectbox("Choose your destination", options, index=default_index)
    chosen = DESTINATIONS[options.index(selected_label)]
    st.session_state.current_destination = chosen

    st.caption(
        f"Selected destination: {country_flag(chosen['code'])} "
        f"{chosen['city']}, {chosen['country']}"
    )

    # ---------- BOARDING PASS / TICKET ---------- #
    today_str = date.today().strftime("%Y/%m/%d")
    origin_code = "BEY"
    origin_city = "Beirut"
    dest_code = chosen["code"]
    dest_city = chosen["city"]

    ticket_html = f"""
    <div class="ticket-wrapper">
        <div class="ticket">
        <div class="ticket-main">
            <div class="ticket-row">
            <div class="ticket-col">
                <div class="ticket-label">From</div>
                <div class="ticket-city">{origin_code}</div>
                <div class="ticket-sub">{origin_city}</div>
            </div>
            <div class="ticket-middle">✈</div>
            <div class="ticket-col">
                <div class="ticket-label">To</div>
                <div class="ticket-city">{dest_code}</div>
                <div class="ticket-sub">{dest_city}</div>
            </div>
            </div>
            <div class="ticket-footer">
            <div>Seat <strong>01F</strong></div>
            <div>Boarding <strong>Now</strong></div>
            <div>Date <strong>{today_str}</strong></div>
            </div>
        </div>
        <div class="ticket-stub">
            <div class="ticket-barcode"></div>
        </div>
        </div>
    </div>
    """

    st.markdown(ticket_styles + ticket_html, unsafe_allow_html=True)

    st.markdown("")

    # ---- Button: rip ticket & go to takeoff (plane animation) ----
    if st.button("✂️ Rip ticket & board"):
        st.session_state.view = "takeoff"
        st.rerun()

    return 