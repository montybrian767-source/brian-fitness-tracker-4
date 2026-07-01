from __future__ import annotations

import base64
import json
import shutil
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
ASSET_DIR = APP_DIR / "assets"
EXERCISE_DIR = ASSET_DIR / "exercises"
WORKOUTS_FILE = DATA_DIR / "workouts.csv"
LOG_FILE = DATA_DIR / "workout_log.csv"
PROFILE_FILE = DATA_DIR / "profile.json"
BACKUP_DIR = DATA_DIR / "backups"

DATA_DIR.mkdir(exist_ok=True)
EXERCISE_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

LOG_COLS = ["date", "saved_at", "day", "muscle_group", "exercise", "set_number", "weight_lbs", "reps", "rpe", "pain", "notes", "volume"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

st.set_page_config(page_title="Brian Fitness Tracker 2.0", page_icon="🏋️", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
:root {
  --bg:#07111f; --panel:#0f1b2d; --panel2:#111827; --card:#101828;
  --text:#f8fafc; --muted:#94a3b8; --line:#243145; --green:#22c55e;
  --blue:#38bdf8; --gold:#f59e0b; --red:#ef4444;
}
html, body, [data-testid="stAppViewContainer"] {background:var(--bg); color:var(--text);}
.block-container {padding-top:1rem; max-width:1500px;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#08111f,#0f1b2d); border-right:1px solid #1e293b;}
[data-testid="stSidebar"] * {color:#f8fafc;}
h1,h2,h3 {color:#f8fafc !important; letter-spacing:-.03em;}
.stButton>button {border-radius:14px; min-height:44px; font-weight:800; border:1px solid #334155; background:#142033; color:#f8fafc;}
.stButton>button:hover {border-color:#22c55e; color:#22c55e;}
[data-testid="stMetric"] {background:#0f1b2d; border:1px solid #243145; border-radius:18px; padding:14px;}
[data-testid="stMetricLabel"] {color:#94a3b8 !important; font-weight:800;}
[data-testid="stMetricValue"] {color:#f8fafc !important; font-weight:900;}
.stNumberInput input, .stTextInput input, textarea {background:#0b1220 !important; color:#f8fafc !important; border:1px solid #334155 !important; border-radius:12px !important;}
.bft-hero {background:linear-gradient(135deg,#0f1b2d,#101828); border:1px solid #243145; border-radius:26px; padding:24px; margin-bottom:18px; box-shadow:0 18px 44px rgba(0,0,0,.22);}
.bft-eyebrow {color:#22c55e; font-size:.82rem; font-weight:900; letter-spacing:.12em; text-transform:uppercase;}
.bft-title {font-size:2rem; font-weight:950; color:#f8fafc; margin:.1rem 0;}
.bft-muted {color:#94a3b8;}
.bft-card {background:#0f1b2d; border:1px solid #243145; border-radius:22px; padding:18px; margin-bottom:16px; box-shadow:0 10px 30px rgba(0,0,0,.18);}
.bft-card-title {font-size:1.18rem; font-weight:950; color:#f8fafc; margin-bottom:3px;}
.bft-pill {display:inline-block; padding:6px 10px; border-radius:999px; background:#12263a; color:#38bdf8; font-weight:900; font-size:.78rem; border:1px solid #21435f; margin-right:6px;}
.bft-imgbox {background:#07111f; border:1px solid #1f2a3a; border-radius:18px; padding:8px; height:230px; display:flex; align-items:center; justify-content:center; overflow:hidden;}
.bft-imgbox img {max-width:100%; max-height:100%; object-fit:contain; border-radius:14px;}
.bft-fallback {height:100%; width:100%; display:flex; align-items:center; justify-content:center; color:#64748b; font-weight:900; border:1px dashed #334155; border-radius:14px;}
.bft-volume {background:#07111f; border:1px solid #243145; border-radius:16px; padding:12px; text-align:center;}
.bft-volume strong {display:block; font-size:1.35rem; color:#22c55e;}
.bft-summary {position:sticky; top:1rem;}
.bft-safe {background:#11261d; border:1px solid #166534; color:#bbf7d0; border-radius:16px; padding:13px; font-weight:800;}
.bft-warn {background:#2a1b0c; border:1px solid #92400e; color:#fed7aa; border-radius:16px; padding:13px; font-weight:800;}
hr {border-color:#243145;}
@media (max-width: 900px) {.bft-summary{position:static}.bft-imgbox{height:190px}.bft-title{font-size:1.55rem}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def load_workouts() -> pd.DataFrame:
    if not WORKOUTS_FILE.exists():
        st.error("Missing data/workouts.csv")
        return pd.DataFrame(columns=["day", "muscle_group", "exercise", "target_sets", "target_reps", "image_file", "notes"])
    df = pd.read_csv(WORKOUTS_FILE)
    df.columns = [c.strip() for c in df.columns]
    return df


def load_log() -> pd.DataFrame:
    if LOG_FILE.exists():
        df = pd.read_csv(LOG_FILE)
        for c in LOG_COLS:
            if c not in df.columns:
                df[c] = "" if c in ["date", "saved_at", "day", "muscle_group", "exercise", "notes"] else 0
        return df[LOG_COLS]
    df = pd.DataFrame(columns=LOG_COLS)
    df.to_csv(LOG_FILE, index=False)
    return df


def backup_log() -> None:
    if LOG_FILE.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy(LOG_FILE, BACKUP_DIR / f"workout_log_backup_{stamp}.csv")


def save_log(rows: list[dict]) -> None:
    if not rows:
        return
    backup_log()
    current = load_log()
    updated = pd.concat([current, pd.DataFrame(rows)], ignore_index=True)
    updated.to_csv(LOG_FILE, index=False)


def img_data_uri(filename: str) -> str | None:
    if not filename or pd.isna(filename):
        return None
    path = EXERCISE_DIR / str(filename)
    if not path.exists():
        return None
    suffix = path.suffix.lower().replace(".", "")
    mime = "image/svg+xml" if suffix == "svg" else f"image/{suffix}"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def image_html(filename: str) -> str:
    uri = img_data_uri(filename)
    if uri:
        return f'<div class="bft-imgbox"><img src="{uri}" /></div>'
    return '<div class="bft-imgbox"><div class="bft-fallback">IMAGE MISSING<br/>assets/exercises</div></div>'


def last_for_exercise(log: pd.DataFrame, exercise: str) -> str:
    if log.empty:
        return "No previous workout"
    ex = log[log["exercise"].astype(str) == str(exercise)].copy()
    if ex.empty:
        return "No previous workout"
    ex["date"] = pd.to_datetime(ex["date"], errors="coerce")
    last_date = ex["date"].max()
    last = ex[ex["date"] == last_date]
    if last.empty:
        return "No previous workout"
    weights = last["weight_lbs"].fillna(0).astype(float)
    reps = last["reps"].fillna(0).astype(int).tolist()
    return f"Last: {weights.max():g} lbs • reps {', '.join(map(str, reps[:6]))}"


def header(title: str, subtitle: str = ""):
    st.markdown(f'''<div class="bft-hero"><div class="bft-eyebrow">Brian Fitness Tracker 2.0</div><div class="bft-title">{title}</div><div class="bft-muted">{subtitle}</div></div>''', unsafe_allow_html=True)


workouts = load_workouts()
log = load_log()

st.sidebar.markdown("## 🏋️ Brian Fit 2.0")
st.sidebar.caption("Fresh working build")
page = st.sidebar.radio("Navigation", ["Dashboard", "Today's Workout", "Weekly Plan", "Image Library", "History", "Data Safety"])
st.sidebar.markdown("---")
st.sidebar.success("Workout history saves to data/workout_log.csv")

if page == "Dashboard":
    today = date.today().strftime("%A")
    active = workouts[workouts["day"] == today]
    group = active["muscle_group"].iloc[0] if not active.empty else "Recovery / Rest"
    header("Commercial Dashboard", f"Today is {today} • {group}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sessions", log["date"].nunique() if not log.empty else 0)
    c2.metric("Total Volume", f"{pd.to_numeric(log['volume'], errors='coerce').fillna(0).sum():,.0f} lbs" if not log.empty else "0 lbs")
    c3.metric("Exercises Today", len(active))
    c4.metric("Images Installed", len(list(EXERCISE_DIR.glob('*.*'))))
    st.markdown("### Weekly Schedule")
    cols = st.columns(7)
    for i, day in enumerate(DAY_ORDER):
        ddf = workouts[workouts["day"] == day]
        grp = ddf["muscle_group"].iloc[0] if not ddf.empty else "Rest"
        with cols[i]:
            st.markdown(f'<div class="bft-card"><div class="bft-card-title">{day[:3]}</div><span class="bft-pill">{grp}</span><div class="bft-muted">{len(ddf)} exercises</div></div>', unsafe_allow_html=True)
    if not log.empty:
        daily = log.copy()
        daily["volume"] = pd.to_numeric(daily["volume"], errors="coerce").fillna(0)
        chart = daily.groupby("date", as_index=False)["volume"].sum()
        st.plotly_chart(px.line(chart, x="date", y="volume", title="Workout Volume"), use_container_width=True)

elif page == "Today's Workout":
    selected_day = st.selectbox("Workout Day", DAY_ORDER, index=DAY_ORDER.index(date.today().strftime("%A")) if date.today().strftime("%A") in DAY_ORDER else 0)
    active = workouts[workouts["day"] == selected_day].reset_index(drop=True)
    group = active["muscle_group"].iloc[0] if not active.empty else ""
    header(f"{selected_day} Workout", f"{group} • log weights, reps, RPE and knee pain")
    if selected_day == "Thursday":
        st.markdown('<div class="bft-warn">🦵 Leg Rehab Day: no downward loading. Stop anything that causes knee pain.</div>', unsafe_allow_html=True)
    if selected_day == "Sunday":
        st.markdown('<div class="bft-safe">Recovery day: swimming, bike, sauna, and easy movement.</div>', unsafe_allow_html=True)
    workout_date = st.date_input("Workout date", value=date.today())
    rows_to_save = []
    live_volume = 0.0
    complete_sets = 0
    left, right = st.columns([2.1, .9])
    with left:
        for idx, r in active.iterrows():
            exercise = str(r["exercise"])
            target_sets = int(r["target_sets"])
            target_reps = str(r["target_reps"])
            image_file = str(r.get("image_file", ""))
            st.markdown('<div class="bft-card">', unsafe_allow_html=True)
            cimg, cmain = st.columns([.85, 1.35])
            with cimg:
                st.markdown(image_html(image_file), unsafe_allow_html=True)
            with cmain:
                st.markdown(f'<div class="bft-card-title">{exercise}</div>', unsafe_allow_html=True)
                st.markdown(f'<span class="bft-pill">Target {target_sets} × {target_reps}</span><span class="bft-pill">{group}</span>', unsafe_allow_html=True)
                st.caption(last_for_exercise(log, exercise))
                pain = st.slider("Pain", 0, 10, 0, key=f"pain_{selected_day}_{idx}")
                note = st.text_input("Notes", key=f"note_{selected_day}_{idx}", placeholder="Form, knee, energy, etc.")
                for s in range(1, target_sets + 1):
                    sc1, sc2, sc3, sc4 = st.columns([1, 1, 1, 1])
                    weight = sc1.number_input(f"Set {s} lbs", min_value=0.0, step=2.5, value=0.0, key=f"w_{selected_day}_{idx}_{s}")
                    reps = sc2.number_input(f"Set {s} reps", min_value=0, step=1, value=0, key=f"r_{selected_day}_{idx}_{s}")
                    rpe = sc3.number_input(f"Set {s} RPE", min_value=0.0, max_value=10.0, step=0.5, value=0.0, key=f"rpe_{selected_day}_{idx}_{s}")
                    vol = weight * reps
                    sc4.markdown(f'<div class="bft-volume"><span>Volume</span><strong>{vol:,.0f}</strong></div>', unsafe_allow_html=True)
                    if reps > 0:
                        complete_sets += 1
                        live_volume += vol
                        rows_to_save.append({
                            "date": str(workout_date), "saved_at": datetime.now().isoformat(timespec="seconds"),
                            "day": selected_day, "muscle_group": group, "exercise": exercise,
                            "set_number": s, "weight_lbs": weight, "reps": reps, "rpe": rpe,
                            "pain": pain, "notes": note, "volume": vol,
                        })
            st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="bft-summary">', unsafe_allow_html=True)
        st.markdown('<div class="bft-card"><div class="bft-card-title">Workout Summary</div>', unsafe_allow_html=True)
        st.metric("Sets entered", complete_sets)
        st.metric("Live volume", f"{live_volume:,.0f} lbs")
        st.metric("Exercises", len(active))
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="bft-card"><div class="bft-card-title">Quick Rules</div><div class="bft-muted">Protect right knee<br/>Increase slowly<br/>Leave feeling like you could do more</div></div>', unsafe_allow_html=True)
        if st.button("💾 Save Workout", use_container_width=True):
            if rows_to_save:
                save_log(rows_to_save)
                st.success(f"Saved {len(rows_to_save)} sets.")
                st.balloons()
                st.rerun()
            else:
                st.warning("Enter reps for at least one set before saving.")
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Weekly Plan":
    header("Weekly Plan", "Days, muscle groups, and exercise count")
    for day in DAY_ORDER:
        ddf = workouts[workouts["day"] == day]
        grp = ddf["muscle_group"].iloc[0] if not ddf.empty else "Rest"
        st.markdown(f'<div class="bft-card"><div class="bft-card-title">{day} — {grp}</div><div class="bft-muted">{len(ddf)} exercises</div></div>', unsafe_allow_html=True)
        if not ddf.empty:
            st.dataframe(ddf[["exercise", "target_sets", "target_reps", "image_file"]], use_container_width=True, hide_index=True)

elif page == "Image Library":
    header("Image Library Test", "Verifies every exercise has an image file in assets/exercises")
    img_map = pd.read_csv(DATA_DIR / "exercise_image_map.csv") if (DATA_DIR / "exercise_image_map.csv").exists() else pd.DataFrame()
    if img_map.empty:
        st.warning("No exercise_image_map.csv found.")
    else:
        for _, r in img_map.iterrows():
            c1, c2, c3 = st.columns([.7, 1.4, .4])
            with c1:
                st.markdown(image_html(str(r["image_file"])), unsafe_allow_html=True)
            with c2:
                st.markdown(f'### {r["exercise"]}')
                st.caption(str(r.get("muscle_group", "")))
                st.code(str(EXERCISE_DIR / str(r["image_file"])))
            with c3:
                exists = (EXERCISE_DIR / str(r["image_file"])).exists()
                st.success("Found") if exists else st.error("Missing")
            st.markdown("---")

elif page == "History":
    header("Workout History", "Saved completed sets")
    log = load_log()
    if log.empty:
        st.info("No workouts saved yet.")
    else:
        st.dataframe(log.sort_values(["date", "saved_at"], ascending=False), use_container_width=True, hide_index=True)
        st.download_button("Download workout_log.csv", log.to_csv(index=False).encode("utf-8"), "workout_log.csv", "text/csv")
        vol = log.copy()
        vol["volume"] = pd.to_numeric(vol["volume"], errors="coerce").fillna(0)
        by_ex = vol.groupby("exercise", as_index=False)["volume"].sum().sort_values("volume", ascending=False).head(15)
        st.plotly_chart(px.bar(by_ex, x="exercise", y="volume", title="Volume by Exercise"), use_container_width=True)

elif page == "Data Safety":
    header("Data Safety", "Protect your workout history before updates")
    st.markdown('<div class="bft-card">', unsafe_allow_html=True)
    st.write("Important files:")
    st.code("data/workout_log.csv\ndata/workouts.csv\ndata/exercise_image_map.csv\nassets/exercises/")
    if LOG_FILE.exists():
        st.download_button("Export workout_log.csv", LOG_FILE.read_bytes(), "workout_log.csv", "text/csv")
    if st.button("Create Manual Backup"):
        backup_log()
        st.success("Backup created in data/backups/")
    backups = sorted(BACKUP_DIR.glob("*.csv"), reverse=True)
    st.write(f"Backups found: {len(backups)}")
    for b in backups[:10]:
        st.caption(b.name)
    st.markdown('</div>', unsafe_allow_html=True)
