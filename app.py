import streamlit as st
from agent.chat import GeminiChat
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import asyncio
import base64
from pathlib import Path
import time
from datetime import date


# ---------------- DESTINATION SELECTOR DATA ---------------- #

DESTINATIONS = [
    {"code": "FR", "country": "France", "city": "Paris"},
    {"code": "DE", "country": "Germany", "city": "Berlin"},
    {"code": "IT", "country": "Italy", "city": "Rome"},
    {"code": "GB", "country": "United Kingdom", "city": "London"},
    {"code": "ES", "country": "Spain", "city": "Barcelona"},
    {"code": "TR", "country": "Turkey", "city": "Istanbul"},
    {"code": "JP", "country": "Japan", "city": "Tokyo"},
    {"code": "US", "country": "United States", "city": "New York"},
]

# map country code -> flag file base name in /pictures/flags
FLAG_NAME = {
    "FR": "france",
    "DE": "germany",
    "IT": "italy",
    "GB": "england",   # your file name
    "ES": "spain",
    "TR": "turkey",
    "JP": "japan",
    "US": "usa",
}


def country_flag(code: str) -> str:
    """Return emoji flag from country code like 'DE'."""
    code = code.upper()
    return "".join(
        chr(ord(c) - 65 + 0x1F1E6) for c in code
        if "A" <= c <= "Z"
    )


# ---------------- CHAT RENDERING HELPERS ---------------- #

def extract_text(msg):
    if isinstance(msg.content, str):
        return msg.content

    if isinstance(msg.content, list):
        return "".join(
            item.get("text", "")
            for item in msg.content
            if isinstance(item, dict) and item.get("type") == "text"
        )
    return ""


def render_message(msg):
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)

    elif isinstance(msg, AIMessage):
        if getattr(msg, "tool_calls", None):
            tool_call = msg.tool_calls[0]
            with st.chat_message("assistant"):
                with st.status(f"Tool call: {tool_call['name']}"):
                    st.markdown(str(tool_call["args"]))
        else:
            text = extract_text(msg)
            with st.chat_message("assistant"):
                st.markdown(text)

    elif isinstance(msg, ToolMessage):
        with st.chat_message("assistant"):
            with st.status("Tool result:"):
                st.markdown(msg.content)


# ---------------- MAIN APP ---------------- #

async def main():
    dark_blue = "rgb(0,51,102)"
    light_blue = "rgb(4,89,173)"

    # ---- Initialize session state ----
    if "view" not in st.session_state:
        st.session_state.view = "home"  # "home", "takeoff", "chat"
    if "current_destination" not in st.session_state:
        st.session_state.current_destination = DESTINATIONS[1]  # default Berlin

    # ---------------- HOME VIEW ---------------- #
    if st.session_state.view == "home":
        
        # Sky / monuments background
        file_path = "pictures/dCXxwH.jpg"
        with open(file_path, "rb") as f:
            data = f.read()
        encoded_bg = base64.b64encode(data).decode()

        home_bg = f"""
    <style>
        h1 {{
            color: black !important;
            text-shadow: none !important;
        }}

        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded_bg}");
            background-size: cover;
            background-position: bottom;
            background-repeat: no-repeat;
        }}

        [data-testid="stHeader"] {{
            background: {dark_blue};
            padding: 10px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.2) !important;
        }}

        [data-testid="stSidebar"] {{
            background: rgba(255,255,255,0.8);
        }}

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
            background: {light_blue};
            border-radius: 18px;
            padding: 10px 16px;
            margin-bottom: 10px;
            margin-top: 20px;
            width: 65%;
            align-self: flex-end;
        }}

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
            background: {dark_blue};
            border-radius: 18px;
            padding: 10px 16px;
            margin-bottom: -10px;
        }}

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) span,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) div {{
            color: white !important;
        }}

        .st-emotion-cache-hzygls {{
            background: transparent;
            padding: 15px;
        }}

        [data-testid="stHeader"]::before {{
            content: "Your Travel Buddy";
            position: absolute;
            top: 50%;
            left: 20px;
            transform: translateY(-50%);
            font-size: 28px;
            font-weight: 900;
            color: white;
        }}

        [data-testid="stChatMessageAvatarUser"],
        [data-testid="stChatMessageAvatarAssistant"] {{
            display: none;
        }}

        .st-emotion-cache-6shykm {{
            padding: 0;
        }}

        .st-emotion-cache-x1bvup {{
            max-height: none;
            height: 50px;
            border-radius: 30px;
        }}

        .st-emotion-cache-6shykm,
         .st-emotion-cache-1cei9z1 {{
            max-width: 900px;
            width: 65%;
        }}

        textarea[placeholder="Your message"] {{
            min-height: unset;
            color: 
        }}

        .st-emotion-cache-sey4o0 {{
            align-items: center;
        }}

        .st-emotion-cache-x1bvup:focus-within {{
            border-color: transparent !important;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.2) !important;
        }}

        .st-emotion-cache-x1bvup *,
        .st-emotion-cache-x1bvup {{
            background-color: {light_blue};
        }}

        .st-emotion-cache-vsnu81:disabled, 
        .st-emotion-cache-vsnu81:disabled:hover, 
        .st-emotion-cache-vsnu81:disabled:active {{
            color: rgb(239 241 245);
        }}

        .st-emotion-cache-1cei9z1 {{
            padding-bottom: 5rem;
        }}
    </style>
    """
        st.markdown(home_bg, unsafe_allow_html=True)

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

        ticket_css = """
        <style>
        .ticket-wrapper {
            margin-top: 2rem;
            display: flex;
            justify-content: center;
        }
        .ticket {
            background: #111;
            color: #f5f5f5;
            border-radius: 18px;
            box-shadow: 0 18px 40px rgba(0,0,0,0.6);
            width: 420px;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            overflow: hidden;
        }
        .ticket-main {
            padding: 18px 22px;
            position: relative;
        }
        .ticket-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .ticket-col {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .ticket-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #aaaaaa;
        }
        .ticket-city {
            font-size: 32px;
            font-weight: 700;
        }
        .ticket-sub {
            font-size: 12px;
            color: #cccccc;
        }
        .ticket-middle {
            font-size: 18px;
            opacity: 0.9;
        }
        .ticket-footer {
            margin-top: 16px;
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #cccccc;
        }
        .ticket-footer strong {
            color: #ffffff;
        }
        .ticket-stub {
            background: #000;
            padding: 8px 16px 14px 16px;
            display: flex;
            justify-content: center;
        }
        .ticket-barcode {
            width: 80%;
            height: 32px;
            background: repeating-linear-gradient(
                90deg,
                #fff 0px,
                #fff 2px,
                #000 2px,
                #000 4px
            );
            border-radius: 6px;
        }
        </style>
        """

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

        st.markdown(ticket_css + ticket_html, unsafe_allow_html=True)

        st.markdown("")

        # ---- Button: rip ticket & go to takeoff (plane animation) ----
        if st.button("✂️ Rip ticket & board"):
            st.session_state.view = "takeoff"
            st.rerun()

        return  # stop here for home view

    # ---------------- TAKEOFF VIEW ---------------- #
    if st.session_state.view == "takeoff":
        dest = st.session_state.current_destination
        code = dest["code"]

        # Reuse sky background
        file_path = "pictures/dCXxwH.jpg"
        with open(file_path, "rb") as f:
            data = f.read()
        encoded_bg = base64.b64encode(data).decode()

        takeoff_bg = f"""
        <style>
        h1 {{
            color: black !important;
            text-shadow: none !important;
        }}
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded_bg}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}
        [data-testid="stSidebar"] {{
            background: rgba(255,255,255,0.8);
        }}
        </style>
        """
        st.markdown(takeoff_bg, unsafe_allow_html=True)

        st.subheader(
            f"Taking off to {dest['city']}, {dest['country']} {country_flag(code)}"
        )

        # Plane animation across the screen (one time)
        try:
            with open("pictures/airplane.png", "rb") as f:
                plane_data = f.read()
            plane_base64 = base64.b64encode(plane_data).decode()

            plane_css = f"""
            <style>
            .plane-overlay {{
                position: fixed;
                top: 35%;
                left: -340px;
                width: 1400px;
                z-index: 9998;
                animation: fly-home 3s linear 1 forwards;
                pointer-events: none;
            }}

            @keyframes fly-home {{
                0%   {{ left: -340px; }}
                100% {{ left: 110%; }}
            }}
            </style>

            <img src="data:image/png;base64,{plane_base64}" class="plane-overlay">
            """
            st.markdown(plane_css, unsafe_allow_html=True)
        except FileNotFoundError:
            pass

        st.caption("Fasten your seatbelt… we’re taking off! ✈️")

        # 3-second timer: when done, go to chat
        if "takeoff_timer_started" not in st.session_state:
            st.session_state.takeoff_timer_started = True
            time.sleep(3)
            st.session_state.view = "chat"
            del st.session_state.takeoff_timer_started
            st.rerun()

        return  # stop here for takeoff view

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

    dark_blue = "rgb(0,51,102)"
    light_blue = "rgb(4,89,173)"
    file_path = "pictures/dCXxwH.jpg"
    with open(file_path, "rb") as f:
        data = f.read()
    encoded_bg = base64.b64encode(data).decode()
    chat_bg = f"""
    <style>
        h1 {{
            color: black !important;
            text-shadow: none !important;
        }}

        [data-testid="stAppViewContainer"] {{
            {flag_style}
        }}

        [data-testid="stHeader"] {{
            background: {dark_blue};
            padding: 10px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.2) !important;
        }}

        [data-testid="stSidebar"] {{
            background: rgba(255,255,255,0.8);
        }}

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
            background: {light_blue};
            border-radius: 18px;
            padding: 10px 16px;
            margin-bottom: 10px;
            margin-top: 20px;
            width: 65%;
            align-self: flex-end;
        }}

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
            background: {dark_blue};
            border-radius: 18px;
            padding: 10px 16px;
            margin-bottom: -10px;
        }}

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) span,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) div {{
            color: white !important;
        }}

        .st-emotion-cache-hzygls {{
            background: transparent;
            padding: 15px;
        }}

        [data-testid="stHeader"]::before {{
            content: "Your Travel Buddy";
            position: absolute;
            top: 50%;
            left: 20px;
            transform: translateY(-50%);
            font-size: 28px;
            font-weight: 900;
            color: white;
        }}

        [data-testid="stChatMessageAvatarUser"],
        [data-testid="stChatMessageAvatarAssistant"] {{
            display: none;
        }}

        .st-emotion-cache-6shykm {{
            padding: 0;
        }}

        .st-emotion-cache-x1bvup {{
            max-height: none;
            height: 50px;
            border-radius: 30px;
        }}

        .st-emotion-cache-6shykm,
         .st-emotion-cache-1cei9z1 {{
            max-width: 900px;
            width: 65%;
        }}

        textarea[placeholder="Your message"] {{
            min-height: unset;
            color: 
        }}

        .st-emotion-cache-sey4o0 {{
            align-items: center;
        }}

        .st-emotion-cache-x1bvup:focus-within {{
            border-color: transparent !important;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.2) !important;
        }}

        .st-emotion-cache-x1bvup *,
        .st-emotion-cache-x1bvup {{
            background-color: {light_blue};
        }}

        .st-emotion-cache-vsnu81:disabled, 
        .st-emotion-cache-vsnu81:disabled:hover, 
        .st-emotion-cache-vsnu81:disabled:active {{
            color: rgb(239 241 245);
        }}

        .st-emotion-cache-1cei9z1 {{
            padding-bottom: 5rem;
        }}
    </style>
    """
    st.markdown(chat_bg, unsafe_allow_html=True)

    st.title("Your Travel Buddy")
    st.caption(
        f"Destination: {country_flag(code)} {dest['city']}, {dest['country']}"
    )

    # ---- Floating Pilot Mascot (bottom-right-ish) ----
    with open("pictures/pilot.png", "rb") as f:
        pilot_data = f.read()
    pilot_base64 = base64.b64encode(pilot_data).decode()

    pilot_css = f"""
    <style>
    .pilot-avatar {{
        position: fixed;
        bottom: 10%;
        left: 85%;
        width: 230px;
        z-index: 9999;
        animation: float 3s ease-in-out infinite;
    }}

    @keyframes float {{
        0%   {{ transform: translateY(0px); }}
        50%  {{ transform: translateY(-10px); }}
        100% {{ transform: translateY(0px); }}
    }}
    </style>

    <img src="data:image/png;base64,{pilot_base64}" class="pilot-avatar">
    """
    st.markdown(pilot_css, unsafe_allow_html=True)

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


asyncio.run(main())
