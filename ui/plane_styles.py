import base64

def plane_styles():
    with open("pictures/airplane.png", "rb") as f:
            plane_data = f.read()
    plane_base64 = base64.b64encode(plane_data).decode()

    return f"""
    <style>
    .plane-overlay {{
        position: fixed;
        top: 55%;
        left: -340px;
        width: 400px;
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