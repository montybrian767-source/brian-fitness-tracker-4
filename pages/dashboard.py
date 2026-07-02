import streamlit as st

from components.hero_banner import hero_banner

st.set_page_config(layout="wide")

hero_banner()

st.markdown("## AI Coach")

st.info(
    "Increase Shoulder Press by 5 lbs today.\n\n"
    "Protein goal is on track.\n\n"
    "Recovery looks excellent."
)

c1,c2,c3,c4=st.columns(4)

with c1:
    st.metric("Nutrition","91%","+2%")

with c2:
    st.metric("Supplements","6 / 7","+1")

with c3:
    st.metric("Workout Streak","18 Days","+1")

with c4:
    st.metric("Weekly Volume","82,400","+4%")

st.divider()

st.subheader("Quick Actions")

a,b,c=st.columns(3)

with a:
    st.button("💪 Start Workout",use_container_width=True)

with b:
    st.button("🤖 Open AI Coach",use_container_width=True)

with c:
    st.button("📅 Weekly Plan",use_container_width=True)
