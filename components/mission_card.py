import streamlit as st


def mission_card(
    workout="Shoulders + Abs",
    recovery="94%",
    readiness="Ready To Train",
    time="58 min",
):
    st.markdown(
        f"""
        <div style="
            padding: 30px;
            border-radius: 26px;
            background: linear-gradient(135deg, #111827, #172554);
            border: 1px solid rgba(255,255,255,.08);
            box-shadow: 0 18px 45px rgba(0,0,0,.40);
            margin-bottom: 24px;
        ">
            <div style="color:#93C5FD; font-size:14px; font-weight:800; letter-spacing:3px;">
                TODAY'S MISSION
            </div>

            <h2 style="color:white; font-size:38px; margin:12px 0;">
                {workout}
            </h2>

            <div style="display:flex; gap:18px; flex-wrap:wrap; margin-top:20px;">
                <div style="color:white; background:rgba(34,197,94,.18); padding:14px 18px; border-radius:18px;">
                    Recovery: <b>{recovery}</b>
                </div>
                <div style="color:white; background:rgba(59,130,246,.18); padding:14px 18px; border-radius:18px;">
                    Status: <b>{readiness}</b>
                </div>
                <div style="color:white; background:rgba(245,158,11,.18); padding:14px 18px; border-radius:18px;">
                    Time: <b>{time}</b>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
