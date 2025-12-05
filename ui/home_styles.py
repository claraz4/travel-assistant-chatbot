from ui.common_styles import dark_blue, light_blue
import base64

def home_styles():
    file_path = "pictures/dCXxwH.jpg"
    with open(file_path, "rb") as f:
        data = f.read()
    encoded_bg = base64.b64encode(data).decode()

    return f"""
    <style>
        h1 {{
            color: black !important;
            text-shadow: none !important;
        }}

        [data-testid="stMainBlockContainer"] {{
            padding: 0;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: center;
            height: 100%;
        }}

        [data-testid="stVerticalBlock"] {{
            align-items: center;
            padding: 30px;
            border-radius: 20px;
            background-color: rgba(0,51,102,0.4);
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

        [data-testid="stSidebar"] {{
            background: rgba(255,255,255,0.8);
        }}

        div[data-baseweb="select"] > div {{
            background-color: {dark_blue};
        }}

        div.stButton button {{
            background-color: {dark_blue};
        }}

        div.stButton button:hover {{
            background-color: rgb(0,51,142);
        }}

        .stSelectbox > div > div:focus-within {{
            border-color: transparent !important;
            box-shadow: none !important;
        }}

        [data-testid="stSelectboxVirtualDropdown"] {{
            background-color: {dark_blue} !important;   
            color: white !important;                 
        }}
    </style>
    """