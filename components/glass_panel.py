import streamlit as st


def glass_panel(title, body, icon="✨"):
    st.markdown(
        f"""
        <div style="
            background:rgba(18,28,46,0.92);
            border:1px solid rgba(255,255,255,.08);
            border-radius:20px;
            padding:24px;
            margin-bottom:20px;
            box-shadow:0 10px 30px rgba(0,0,0,.35);
        ">

            <div style="
                font-size:22px;
                font-weight:700;
                color:white;
                margin-bottom:12px;
            ">
                {icon} {title}
            </div>

            <div style="
                color:#C7D3E6;
                font-size:16px;
                line-height:1.6;
            ">
                {body}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )
