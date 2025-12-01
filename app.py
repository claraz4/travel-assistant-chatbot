import streamlit as st
from agent.chat import GeminiChat
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import asyncio
import base64

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
        if msg.tool_calls:
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


async def main():
    file_path = "pictures/dCXxwH.jpg" 
    with open(file_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()

    dark_blue = "rgb(0, 51, 102)"
    light_blue = "rgb(4 89 173)"
    styles = f"""
    <style>
        h1 {{
            color: black !important;
            text-shadow: none !important;
        }}

        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded}");
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


    st.markdown(styles, unsafe_allow_html=True)

    if "llm" not in st.session_state:
        st.session_state.llm = GeminiChat()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render history
    for msg in st.session_state.messages:
        render_message(msg)

    # Get user input
    prompt = st.chat_input("Your message")

    if not prompt:
        return

    # Render user message
    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)
    render_message(user_msg)

    # Generate response
    new_messages = st.session_state.llm.send_message(prompt)

    # Append and render new messages only
    for msg in new_messages:
        st.session_state.messages.append(msg)
        render_message(msg)


asyncio.run(main())