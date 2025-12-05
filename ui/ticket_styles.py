from ui.common_styles import dark_blue, light_blue

ticket_styles = f"""
    <style>
    .ticket-wrapper {{
        margin-top: 2rem;
        display: flex;
        justify-content: center;
    }}
    .ticket {{
        background: {dark_blue};
        color: #f5f5f5;
        border-radius: 18px;
        box-shadow: 0 18px 40px rgba(0,0,0,0.6);
        width: 420px;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        overflow: hidden;
    }}
    .ticket-main {{
        padding: 18px 22px;
        position: relative;
    }}
    .ticket-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .ticket-col {{
        display: flex;
        flex-direction: column;
        gap: 2px;
    }}
    .ticket-label {{
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #aaaaaa;
    }}
    .ticket-city {{
        font-size: 32px;
        font-weight: 700;
    }}
    .ticket-sub {{
        font-size: 12px;
        color: #cccccc;
    }}
    .ticket-middle {{
        font-size: 18px;
        opacity: 0.9;
    }}
    .ticket-footer {{
        margin-top: 16px;
        display: flex;
        justify-content: space-between;
        font-size: 11px;
        color: #cccccc;
    }}
    .ticket-footer strong {{
        color: #ffffff;
    }}
    .ticket-stub {{
        background: #000;
        padding: 14px 16px;
        display: flex;
        justify-content: center;
        background-color: {dark_blue};
        border-top: white dashed 2px
    }}
    .ticket-barcode {{
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
    }}
    </style>
"""