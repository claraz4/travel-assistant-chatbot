import base64

def pilot_styles():
    with open("pictures/pilot.png", "rb") as f:
        pilot_data = f.read()
    pilot_base64 = base64.b64encode(pilot_data).decode()

    return  f"""
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