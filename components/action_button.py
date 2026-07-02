import streamlit as st


def start_workout_button():
    st.markdown(
        """
        <style>
        div.stButton > button:first-child {
            width:100%;
            height:72px;
            border-radius:22px;
            border:none;
            font-size:24px;
            font-weight:700;
            color:white;
            background:linear-gradient(135deg,#2563EB,#3B82F6);
            box-shadow:0 14px 35px rgba(37,99,235,.45);
            transition:all .25s ease;
        }

        div.stButton > button:first-child:hover{
            transform:translateY(-2px);
            box-shadow:0 20px 45px rgba(37,99,235,.65);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    return st.button("💪 START TODAY'S WORKOUT")
