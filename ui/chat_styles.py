from ui.common_styles import dark_blue, light_blue

def chat_styles(flag_style):
    return  f"""
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