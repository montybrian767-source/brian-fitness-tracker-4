import streamlit as st

from components.executive_header import executive_header
from components.mission_card import mission_card
from components.action_button import start_workout_button
from components.hero_banner import hero_banner
from components.stat_card import stat_card
from components.ai_card import ai_card
from components.glass_panel import glass_panel
executive_header()

mission_card()

start_workout_button()

st.divider()

def render_dashboard():
    hero_banner(
        workout_name="Today’s Focus",
        recovery="94%",
        readiness="Excellent",
        duration="60 min",
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        stat_card("Sessions", "0", "#3B82F6")

    with c2:
        stat_card("Total Volume", "0 lbs", "#22C55E")

    with c3:
        stat_card("Protein Today", "0g", "#8B5CF6")

    with c4:
        stat_card("Calories Today", "0", "#F59E0B")

    ai_card()

    glass_panel(
        "Weekly Focus",
        "Stay consistent. Complete today’s workout, hit your protein goal, and keep hydration above 100 oz.",
        "🔥",
    )


render_dashboard()
