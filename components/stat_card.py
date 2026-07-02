import streamlit as st

def stat_card(title, value, color="#3B82F6"):
    st.markdown(
        f"""
        <div style="
            background:#121C2E;
            border-left:6px solid {color};
            border-radius:18px;
            padding:18px;
            min-height:110px;
        ">
            <div style="
                color:#AAB4C5;
                font-size:14px;
            ">
                {title}
            </div>

            <div style="
                font-size:34px;
                color:white;
                font-weight:700;
                margin-top:8px;
            ">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
