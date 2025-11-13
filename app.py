import streamlit as st
from agent.chat import GeminiChat
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import asyncio
import base64

async def main():
    st.title("Your Travel Buddy")
    
    
    file_path = "/Users/gaelletohme/travel-assistant-chatbot/pictures/dCXxwH.jpg" 
    with open(file_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()

    page_bg = f"""
    <style>
    h1 {{
    color: black !important;
    text-shadow: none !important;
}}
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
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
    
   /*  User message (slightly stronger blue bubble) */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background: rgba(135, 206, 250, 1); 
    border-radius: 18px;
    padding: 10px 16px;
    margin-bottom: 10px;
}}

/*  Assistant message (stronger navy bubble) */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
    background: rgba(0, 51, 102, 1); 
    border-radius: 18px;
    padding: 10px 16px;
    margin-bottom: 10px;
   
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) span,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) div {{
    color: white !important;      
}}
    </style>
    """

    st.markdown(page_bg, unsafe_allow_html=True)

    if "llm" not in st.session_state:
        st.session_state.llm = GeminiChat()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        if isinstance(msg, SystemMessage):
            continue
        with st.chat_message("assistant" if isinstance(msg, AIMessage) else "user"):
            st.markdown(msg.content)

    prompt = st.chat_input("Your message")

    if prompt:
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        new_messages = st.session_state.llm.send_message(prompt)
        
        for msg in new_messages:
            if isinstance(msg, AIMessage) and getattr(msg, "text", None):
                st.session_state.messages.append(AIMessage(content=msg.text))
                with st.chat_message("assistant"):
                    st.markdown(msg.text)

asyncio.run(main())
