import streamlit as st

def hero_banner(
    workout_name="Shoulders + Abs",
    recovery="94%",
    readiness="Excellent",
    duration="61 min"
):

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg,#1d4ed8,#2563eb);
        padding:32px;
        border-radius:22px;
        color:white;
        margin-bottom:25px;
    ">

    <h1 style="margin:0;">
    Brian Fitness Tracker X
    </h1>

    <p style="font-size:22px;margin-top:10px;">
    Good Morning Brian
    </p>

    <hr>

    <div style="display:flex;justify-content:space-between;">

        <div>
        <h3>Today's Workout</h3>
        <h2>{workout_name}</h2>
        </div>

        <div>
        <h3>Recovery</h3>
        <h2>{recovery}</h2>
        </div>

        <div>
        <h3>Readiness</h3>
        <h2>{readiness}</h2>
        </div>

        <div>
        <h3>Time</h3>
        <h2>{duration}</h2>
        </div>

    </div>

    </div>
    """, unsafe_allow_html=True)
