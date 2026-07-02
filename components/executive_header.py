# Brian Fitness Tracker X
# Executive Header Component

import streamlit as st


def executive_header():
    st.markdown(
        """
        <div style="
            padding: 34px;
            border-radius: 26px;
            background: linear-gradient(135deg, #0B1220, #102A4C);
            border: 1px solid rgba(59,130,246,.45);
            box-shadow: 0 20px 50px rgba(0,0,0,.45);
            margin-bottom: 24px;
        ">
            <div style="color:#22C55E; font-size:13px; font-weight:800; letter-spacing:4px;">
                BRIAN FITNESS TRACKER X
            </div>

            <h1 style="color:white; font-size:46px; margin:14px 0 6px 0;">
                Good Morning Brian
            </h1>

            <div style="color:#B8C2D1; font-size:18px;">
                Today’s mission is built around performance, recovery, and consistency.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
