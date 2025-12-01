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
    </style>
    """