
from pathlib import Path
from datetime import date
import base64
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
DATA = APP_DIR / "data"
ASSETS = APP_DIR / "assets" / "exercises"
DATA.mkdir(exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)
WORKOUTS = DATA / "workouts.csv"
LOG = DATA / "workout_log.csv"
MAP = DATA / "exercise_image_map.csv"

st.set_page_config(page_title="Brian Fitness Tracker 2.0", page_icon="🏋️", layout="wide")

def ensure_log():
    if not LOG.exists():
        pd.DataFrame(columns=['date','day','exercise','set_number','weight_lbs','reps','rpe','pain','notes','volume']).to_csv(LOG,index=False)
ensure_log()

def load_workouts():
    if not WORKOUTS.exists():
        st.error("Missing data/workouts.csv")
        return pd.DataFrame(columns=['day','muscle_group','exercise','target_sets','target_reps','base_weight','image_file'])
    df = pd.read_csv(WORKOUTS)
    required = ['day','muscle_group','exercise','target_sets','target_reps','base_weight','image_file']
    for c in required:
        if c not in df.columns: df[c] = ''
    return df

def load_log():
    ensure_log()
    try: return pd.read_csv(LOG)
    except Exception: return pd.DataFrame(columns=['date','day','exercise','set_number','weight_lbs','reps','rpe','pain','notes','volume'])

def save_log(rows):
    ensure_log()
    old = load_log()
    new = pd.DataFrame(rows)
    pd.concat([old,new], ignore_index=True).to_csv(LOG,index=False)

def image_path(row):
    f = str(row.get('image_file','')).strip()
    p = ASSETS / f
    if f and p.exists(): return p
    # try map file
    if MAP.exists():
        try:
            m = pd.read_csv(MAP)
            hit = m[m['exercise'].astype(str).str.lower()==str(row.get('exercise','')).lower()]
            if not hit.empty:
                p = ASSETS / str(hit.iloc[0]['image_file'])
                if p.exists(): return p
        except Exception: pass
    fallback = ASSETS / 'image_coming_soon.png'
    return fallback if fallback.exists() else None

def img_tag(path):
    if path and Path(path).exists():
        mime = 'image/png' if str(path).lower().endswith('png') else 'image/jpeg'
        data = base64.b64encode(Path(path).read_bytes()).decode()
        return f'<img src="data:{mime};base64,{data}" class="exercise-photo" />'
    return '<div class="no-image">Image Coming Soon</div>'

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: Inter, sans-serif;}
.stApp {background: #07111f; color:#f8fafc;}
[data-testid="stHeader"] {background: rgba(7,17,31,.85);}
section[data-testid="stSidebar"] {background: linear-gradient(180deg,#06111f,#08213b); border-right:1px solid #1d3655;}
section[data-testid="stSidebar"] * {color:#f8fafc !important;}
.hero {border:1px solid #254264; background:linear-gradient(135deg,#0e2138,#0a1728); border-radius:24px; padding:28px; margin:12px 0 22px 0;}
.kicker {letter-spacing:.25em; font-size:.82rem; color:#22c55e; font-weight:900; text-transform:uppercase;}
.title {font-size:2.1rem; font-weight:900; line-height:1.1; margin-top:8px;}
.sub {color:#9cc7ff; margin-top:10px;}
.metric-card {background:#0f1f34; border:1px solid #254264; border-radius:18px; padding:18px; min-height:95px;}
.metric-label {color:#9cc7ff; font-size:.85rem;}
.metric-value {font-size:1.7rem; font-weight:900; color:white;}
.exercise-card {background:linear-gradient(135deg,#0f1f34,#0a1728); border:1px solid #254264; border-radius:22px; padding:18px; margin:18px 0; box-shadow: 0 8px 28px rgba(0,0,0,.2);}
.exercise-head {display:flex; align-items:center; gap:12px; margin-bottom:12px;}
.num {background:#1d7cff; color:#fff; border-radius:999px; width:34px; height:34px; display:flex; align-items:center; justify-content:center; font-weight:900;}
.ex-title {font-size:1.35rem; font-weight:900;}
.badge {display:inline-block; padding:6px 10px; margin-right:8px; border-radius:999px; border:1px solid #1d7cff; color:#86c5ff; background:#0b2b4f; font-weight:800; font-size:.8rem;}
.badge.green {border-color:#22c55e; color:#7cff9d; background:#07351f;}
.exercise-photo-wrap {background:#081322; border:1px solid #1d3655; border-radius:16px; padding:8px; min-height:245px; display:flex; align-items:center; justify-content:center; overflow:hidden;}
.exercise-photo {width:100%; height:245px; object-fit:contain; border-radius:12px; background:#06111f;}
.no-image {width:100%; height:245px; display:flex; align-items:center; justify-content:center; border-radius:12px; background:#0b1e33; color:#9cc7ff; font-weight:800;}
.set-header, .set-row {display:grid; grid-template-columns: 55px 1fr 1fr 1fr 1.3fr 90px; gap:10px; align-items:center;}
.set-header {color:#9cc7ff; font-weight:900; font-size:.76rem; border-bottom:1px solid #1d3655; padding:8px 0;}
.set-row {padding:8px 0; border-bottom:1px solid rgba(37,66,100,.45);}
.volume {color:#2cff88; font-weight:900;}
.side-card {background:#0f1f34; border:1px solid #254264; border-radius:18px; padding:18px; margin-bottom:16px;}
.side-title {font-weight:900; color:white; font-size:1.05rem; margin-bottom:12px;}
.safe {background:#063326; border:1px solid #157a51; color:#b8ffd5; padding:16px; border-radius:16px; margin-top:24px;}
.small {font-size:.86rem; color:#9cc7ff;}
.stButton>button {background:#12375f; color:white; border:1px solid #2b70bb; border-radius:12px; font-weight:800;}
.stDownloadButton>button {background:#12375f; color:white; border:1px solid #2b70bb; border-radius:12px; font-weight:800;}
input, textarea, select {border-radius:10px !important;}
@media (max-width: 900px) {.set-header, .set-row {grid-template-columns: 36px 1fr 1fr;}.hide-mobile{display:none}.exercise-photo{height:210px}.exercise-photo-wrap{min-height:210px}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🏋️ Brian Fit 2.0")
st.sidebar.caption("Professional Edition")
page = st.sidebar.radio("Navigation", ["Dashboard","Today's Workout","Weekly Plan","Exercise Library","History","Data Safety"], index=0)
st.sidebar.markdown('<div class="safe"><b>✅ Data safe</b><br><br><span class="small">Workout history saves to</span><br><b>data/workout_log.csv</b></div>', unsafe_allow_html=True)

workouts = load_workouts()
log = load_log()
days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

if page == "Dashboard":
    today = date.today().strftime('%A')
    today_df = workouts[workouts.day==today]
    total_sessions = log['date'].nunique() if not log.empty and 'date' in log else 0
    total_volume = int(pd.to_numeric(log.get('volume', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not log.empty else 0
    installed = len(list(ASSETS.glob('*.png'))) + len(list(ASSETS.glob('*.jpg')))
    st.markdown(f'<div class="hero"><div class="kicker">Brian Fitness Tracker 2.0</div><div class="title">Commercial Dashboard</div><div class="sub">Today is {today} • {today_df.muscle_group.iloc[0] if not today_df.empty else "Rest / Recovery"}</div></div>', unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    for c,label,val in [(c1,'Sessions',total_sessions),(c2,'Total Volume',f'{total_volume:,} lbs'),(c3,'Exercises Today',len(today_df)),(c4,'Images Installed',installed)]:
        c.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)
    st.markdown("## Weekly Schedule")
    cols=st.columns(7)
    for col,day in zip(cols,days):
        d=workouts[workouts.day==day]
        group=d.muscle_group.iloc[0] if not d.empty else 'Rest'
        col.markdown(f'<div class="metric-card"><div class="metric-value" style="font-size:1.1rem">{day[:3]}</div><div class="badge">{group}</div><div class="small">{len(d)} exercises</div></div>', unsafe_allow_html=True)

elif page == "Today's Workout":
    day = st.selectbox("Workout Day", days, index=date.today().weekday() if date.today().weekday()<7 else 0)
    active = workouts[workouts.day==day].reset_index(drop=True)
    group = active.muscle_group.iloc[0] if not active.empty else 'Recovery / Rest'
    st.markdown(f'<div class="hero"><div class="kicker">Brian Fitness Tracker 2.0</div><div class="title">{day} — {group}</div><div><span class="badge green">{len(active)} exercises</span><span class="badge">Protect knee • controlled form</span></div></div>', unsafe_allow_html=True)
    if active.empty:
        st.info("No exercises scheduled for this day.")
    right = st.container()
    total_live = 0
    for i,row in active.iterrows():
        sets = int(row.target_sets) if str(row.target_sets).isdigit() else 3
        st.markdown('<div class="exercise-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="exercise-head"><div class="num">{i+1}</div><div><div class="ex-title">{row.exercise}</div><span class="badge">Target: {row.target_sets} × {row.target_reps}</span><span class="badge green">{row.muscle_group}</span></div></div>', unsafe_allow_html=True)
        col_img, col_sets = st.columns([.9,1.45])
        with col_img:
            st.markdown(f'<div class="exercise-photo-wrap">{img_tag(image_path(row))}</div>', unsafe_allow_html=True)
            st.caption(f"Previous best: {row.base_weight} lbs")
        with col_sets:
            st.markdown('<div class="set-header"><div>SET</div><div>WEIGHT</div><div>REPS</div><div>RPE</div><div>NOTES</div><div>VOLUME</div></div>', unsafe_allow_html=True)
            save_rows=[]; ex_vol=0
            for s in range(1, sets+1):
                cols=st.columns([.35,1,1,1,1.4,.8])
                cols[0].markdown(f'<div class="num" style="width:28px;height:28px;font-size:.85rem">{s}</div>', unsafe_allow_html=True)
                wt = cols[1].number_input('Weight', min_value=0.0, value=float(row.base_weight), step=5.0, key=f'w_{i}_{s}', label_visibility='collapsed')
                reps_default = 12
                try:
                    reps_default = int(str(row.target_reps).split('-')[-1].split()[0])
                except: pass
                reps = cols[2].number_input('Reps', min_value=0, value=reps_default, step=1, key=f'r_{i}_{s}', label_visibility='collapsed')
                rpe = cols[3].number_input('RPE', min_value=0.0, max_value=10.0, value=7.0, step=.5, key=f'rpe_{i}_{s}', label_visibility='collapsed')
                notes = cols[4].text_input('Notes', value='felt good' if s==1 else '', key=f'n_{i}_{s}', label_visibility='collapsed')
                vol = int(wt*reps); ex_vol += vol; total_live += vol
                cols[5].markdown(f'<div class="volume">{vol:,} lbs</div>', unsafe_allow_html=True)
                save_rows.append({'date':str(date.today()),'day':day,'exercise':row.exercise,'set_number':s,'weight_lbs':wt,'reps':reps,'rpe':rpe,'pain':0,'notes':notes,'volume':vol})
            if st.button(f"💾 Save {row.exercise}", key=f'save_{i}'):
                save_log(save_rows)
                st.success(f"Saved {row.exercise}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="side-card"><div class="side-title">Workout Summary</div><div>Total exercises: <b>{len(active)}</b></div><div>Live volume: <b class="volume">{total_live:,} lbs</b></div></div>', unsafe_allow_html=True)

elif page == "Weekly Plan":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.0</div><div class="title">Weekly Plan</div><div class="sub">Days, muscle groups, and exercise count</div></div>', unsafe_allow_html=True)
    for day in days:
        d=workouts[workouts.day==day]
        group=d.muscle_group.iloc[0] if not d.empty else 'Rest'
        st.markdown(f'<div class="side-card"><div class="side-title">{day} — {group}</div><div class="small">{len(d)} exercises</div></div>', unsafe_allow_html=True)

elif page == "Exercise Library":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.0</div><div class="title">Exercise Image Library</div><div class="sub">Checks assets/exercises and data/exercise_image_map.csv</div></div>', unsafe_allow_html=True)
    files = sorted(list(ASSETS.glob('*.png')) + list(ASSETS.glob('*.jpg')) + list(ASSETS.glob('*.jpeg')))
    st.write(f"Images folder: `{ASSETS}`")
    st.write(f"Image files found: **{len(files)}**")
    if MAP.exists():
        m=pd.read_csv(MAP)
        st.dataframe(m, use_container_width=True)
    else:
        st.warning('No exercise_image_map.csv found.')
    if files:
        cols=st.columns(4)
        for idx,p in enumerate(files[:60]):
            with cols[idx%4]:
                st.image(str(p), use_container_width=True)
                st.caption(p.name)

elif page == "History":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.0</div><div class="title">Workout History</div><div class="sub">Saved completed sets</div></div>', unsafe_allow_html=True)
    log=load_log()
    if log.empty: st.info('No workouts saved yet.')
    else: st.dataframe(log.tail(200), use_container_width=True)

elif page == "Data Safety":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.0</div><div class="title">Data Safety</div><div class="sub">Important files before updates</div></div>', unsafe_allow_html=True)
    st.code('data/workout_log.csv\ndata/workouts.csv\ndata/exercise_image_map.csv\nassets/exercises/')
    if LOG.exists():
        st.download_button('Export workout_log.csv', LOG.read_bytes(), file_name='workout_log.csv')
