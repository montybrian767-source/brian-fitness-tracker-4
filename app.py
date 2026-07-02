
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
NUTRITION = DATA / "nutrition_log.csv"
BODY = DATA / "body_stats.csv"
SUPPLEMENTS = DATA / "supplement_log.csv"
SUPPLEMENT_PLAN = DATA / "supplement_plan.csv"

st.set_page_config(page_title="Brian Fitness Tracker 2.0", page_icon="🏋️", layout="wide")

def ensure_log():
    if not LOG.exists():
        pd.DataFrame(columns=['date','day','exercise','set_number','weight_lbs','reps','rpe','pain','notes','volume']).to_csv(LOG,index=False)
ensure_log()

def ensure_csv(path, columns):
    if not path.exists():
        pd.DataFrame(columns=columns).to_csv(path, index=False)

def ensure_health_logs():
    ensure_csv(NUTRITION, ['date','meal','calories','protein_g','carbs_g','fat_g','water_oz','notes'])
    ensure_csv(BODY, ['date','body_weight_lbs','goal_weight_lbs','waist_in','notes'])
    ensure_csv(SUPPLEMENTS, ['date','creatine','protein_powder','multivitamin','fish_oil','pre_workout','magnesium','vitamin_d','electrolytes','notes'])
    ensure_csv(SUPPLEMENT_PLAN, ['supplement','category','default_time','target_days_per_week','notes'])
ensure_health_logs()

def read_csv_safe(path, columns):
    ensure_csv(path, columns)
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=columns)

def append_csv(path, row, columns):
    df = read_csv_safe(path, columns)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False)

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

/* brighter Streamlit sidebar collapse arrows / menu controls */
[data-testid="collapsedControl"] {
    background: #22c55e !important;
    color: #04111f !important;
    border: 2px solid #60a5fa !important;
    box-shadow: 0 0 18px rgba(34,197,94,.75) !important;
    border-radius: 12px !important;
}
[data-testid="collapsedControl"] svg {stroke:#04111f !important; fill:#04111f !important;}
button[kind="header"] {
    background: #22c55e !important;
    color: #04111f !important;
    border-radius: 10px !important;
    box-shadow: 0 0 12px rgba(34,197,94,.55) !important;
}
button[kind="header"] svg {stroke:#04111f !important; fill:#04111f !important;}
/* make sidebar radio selection more obvious */
section[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child {border-color:#22c55e !important;}

.goalbar {height:12px;background:#132940;border-radius:999px;overflow:hidden;border:1px solid #254264}.goalfill{height:100%;background:linear-gradient(90deg,#22c55e,#60a5fa);border-radius:999px}.macro-card{background:#0f1f34;border:1px solid #254264;border-radius:18px;padding:16px;margin:8px 0}.macro-value{font-size:1.45rem;font-weight:900;color:#fff}.macro-good{color:#22c55e;font-weight:900}.macro-warn{color:#fbbf24;font-weight:900}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🏋️ Brian Fit 2.3")
st.sidebar.caption("2.3 Supplement Engine")
page = st.sidebar.radio("Navigation", ["Dashboard","Today's Workout","Workout Builder","Weekly Plan","Nutrition","Supplements","Body Stats","Exercise Library","History","Data Safety"], index=0)
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
    nut = read_csv_safe(NUTRITION, ['date','meal','calories','protein_g','carbs_g','fat_g','water_oz','notes'])
    today_s = str(date.today())
    nt = nut[nut['date'].astype(str)==today_s] if not nut.empty else nut
    cal_today = int(pd.to_numeric(nt.get('calories', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not nt.empty else 0
    protein_today = int(pd.to_numeric(nt.get('protein_g', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not nt.empty else 0
    water_today = int(pd.to_numeric(nt.get('water_oz', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not nt.empty else 0
    st.markdown(f'<div class="hero"><div class="kicker">Brian Fitness Tracker 2.3</div><div class="title">Nutrition + Workout Dashboard</div><div class="sub">Today is {today} • {today_df.muscle_group.iloc[0] if not today_df.empty else "Rest / Recovery"}</div></div>', unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    for c,label,val in [(c1,'Sessions',total_sessions),(c2,'Total Volume',f'{total_volume:,} lbs'),(c3,'Protein Today',f'{protein_today}g'),(c4,'Calories Today',cal_today)]:
        c.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)
    c5,c6=st.columns(2)
    c5.markdown(f'<div class="macro-card"><div class="metric-label">Water Today</div><div class="metric-value">{water_today} oz</div><div class="goalbar"><div class="goalfill" style="width:{min(100, water_today/100*100):.0f}%"></div></div><div class="small">Goal: 100 oz</div></div>', unsafe_allow_html=True)
    c6.markdown(f'<div class="macro-card"><div class="metric-label">Image Library</div><div class="metric-value">{installed}</div><div class="small">Exercise images installed</div></div>', unsafe_allow_html=True)
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


elif page == "Workout Builder":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.3</div><div class="title">Workout Builder</div><div class="sub">Add exercises to your weekly plan without editing CSV files.</div></div>', unsafe_allow_html=True)
    st.info("Use this page to add a new exercise to the weekly schedule. It updates data/workouts.csv.")
    library = workouts.copy()
    search = st.text_input("Search current exercise library", placeholder="lat pulldown, chest press, row...")
    if search:
        shown = library[library['exercise'].astype(str).str.contains(search, case=False, na=False)]
    else:
        shown = library
    st.markdown("### Current Plan / Exercise Library")
    st.dataframe(shown[['day','muscle_group','exercise','target_sets','target_reps','base_weight','image_file']], use_container_width=True)

    st.markdown("### Add Exercise to Plan")
    c1,c2,c3 = st.columns(3)
    with c1:
        new_day = st.selectbox("Workout Day", days, key="builder_day")
        new_group = st.text_input("Muscle Group", value="Custom")
    with c2:
        new_ex = st.text_input("Exercise Name", placeholder="Example: Cable Curl")
        new_img = st.text_input("Image file", placeholder="example: bicep_curl.png")
    with c3:
        new_sets = st.number_input("Target sets", min_value=1, max_value=10, value=3, step=1)
        new_reps = st.text_input("Target reps", value="10-12")
        new_weight = st.number_input("Starting weight", min_value=0.0, value=0.0, step=5.0)
    if st.button("➕ Add exercise to workouts.csv"):
        if not new_ex.strip():
            st.error("Enter an exercise name first.")
        else:
            df = load_workouts()
            row = {
                'day': new_day,
                'muscle_group': new_group.strip() or 'Custom',
                'exercise': new_ex.strip(),
                'target_sets': int(new_sets),
                'target_reps': new_reps.strip() or '10-12',
                'base_weight': float(new_weight),
                'image_file': new_img.strip()
            }
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            df.to_csv(WORKOUTS, index=False)
            st.success(f"Added {new_ex} to {new_day}. Reopen the page or refresh to see it in the workout.")

    st.markdown("### Image Filename Helper")
    st.caption("Use lowercase filenames with underscores. Example: Shoulder Press Machine → shoulder_press_machine.png")
    if new_ex.strip():
        suggested = ''.join(ch.lower() if ch.isalnum() else '_' for ch in new_ex.strip()).strip('_')
        while '__' in suggested: suggested = suggested.replace('__','_')
        st.code(f"{suggested}.png")

elif page == "Weekly Plan":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.3</div><div class="title">Weekly Plan</div><div class="sub">Days, muscle groups, and exercise count</div></div>', unsafe_allow_html=True)
    for day in days:
        d=workouts[workouts.day==day]
        group=d.muscle_group.iloc[0] if not d.empty else 'Rest'
        names = ', '.join(d['exercise'].astype(str).head(6).tolist()) if not d.empty else 'Recovery / Rest day'
        if len(d) > 6: names += ', ...'
        st.markdown(f'<div class="side-card"><div class="side-title">{day} — {group}</div><div class="small">{len(d)} exercises</div><div style="margin-top:8px;color:#c8ddff">{names}</div></div>', unsafe_allow_html=True)


elif page == "Nutrition":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.3</div><div class="title">Nutrition Engine</div><div class="sub">Track calories, protein, macros, water, and meals.</div></div>', unsafe_allow_html=True)
    cols = ['date','meal','calories','protein_g','carbs_g','fat_g','water_oz','notes']
    nut = read_csv_safe(NUTRITION, cols)
    today_s = str(date.today())
    left, right = st.columns([1.15,.85])
    with left:
        st.markdown('### Add meal / nutrition entry')
        c1,c2,c3 = st.columns(3)
        entry_date = c1.text_input('Date', value=today_s, key='nut_date')
        meal = c2.selectbox('Meal', ['Breakfast','Lunch','Dinner','Snack','Post-workout','Other'], key='meal')
        calories = c3.number_input('Calories', min_value=0, value=0, step=50, key='cal')
        c4,c5,c6,c7 = st.columns(4)
        protein = c4.number_input('Protein g', min_value=0, value=0, step=5, key='protein')
        carbs = c5.number_input('Carbs g', min_value=0, value=0, step=5, key='carbs')
        fat = c6.number_input('Fat g', min_value=0, value=0, step=5, key='fat')
        water = c7.number_input('Water oz', min_value=0, value=0, step=8, key='water')
        notes = st.text_input('Notes', placeholder='Chicken, rice, protein shake, etc.', key='nut_notes')
        if st.button('💾 Save nutrition entry'):
            append_csv(NUTRITION, {'date':entry_date,'meal':meal,'calories':calories,'protein_g':protein,'carbs_g':carbs,'fat_g':fat,'water_oz':water,'notes':notes}, cols)
            st.success('Nutrition entry saved.')
    with right:
        today_df = nut[nut['date'].astype(str)==today_s] if not nut.empty else nut
        cal = int(pd.to_numeric(today_df.get('calories', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not today_df.empty else 0
        pro = int(pd.to_numeric(today_df.get('protein_g', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not today_df.empty else 0
        carb = int(pd.to_numeric(today_df.get('carbs_g', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not today_df.empty else 0
        fatg = int(pd.to_numeric(today_df.get('fat_g', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not today_df.empty else 0
        wat = int(pd.to_numeric(today_df.get('water_oz', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not today_df.empty else 0
        st.markdown('<div class="side-card"><div class="side-title">Today\'s Nutrition</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{cal:,} calories</div><div class="small">Protein: <b>{pro}g</b> • Carbs: <b>{carb}g</b> • Fat: <b>{fatg}g</b></div><br><div class="metric-label">Water</div><div class="goalbar"><div class="goalfill" style="width:{min(100, wat)}%"></div></div><div class="small">{wat} / 100 oz</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="side-card"><div class="side-title">Simple Goals</div><div class="small">Protein: 150g/day<br>Water: 100 oz/day<br>Calories: set based on goal weight</div></div>', unsafe_allow_html=True)
    st.markdown('### Nutrition History')
    if nut.empty: st.info('No nutrition entries saved yet.')
    else: st.dataframe(nut.tail(100), use_container_width=True)
    if NUTRITION.exists(): st.download_button('Export nutrition_log.csv', NUTRITION.read_bytes(), file_name='nutrition_log.csv')

elif page == "Supplements":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.3</div><div class="title">Supplement Engine</div><div class="sub">Track supplement consistency, timing, and weekly completion. Not medical advice.</div></div>', unsafe_allow_html=True)
    cols=['date','creatine','protein_powder','multivitamin','fish_oil','pre_workout','magnesium','vitamin_d','electrolytes','notes']
    plan_cols=['supplement','category','default_time','target_days_per_week','notes']
    sup=read_csv_safe(SUPPLEMENTS, cols)
    plan=read_csv_safe(SUPPLEMENT_PLAN, plan_cols)
    if plan.empty:
        default_plan = pd.DataFrame([
            {'supplement':'Creatine','category':'Performance','default_time':'Anytime','target_days_per_week':7,'notes':'Common daily consistency supplement.'},
            {'supplement':'Protein Powder','category':'Protein','default_time':'Post workout / meal gap','target_days_per_week':5,'notes':'Use when food protein is low.'},
            {'supplement':'Multivitamin','category':'General','default_time':'Morning with meal','target_days_per_week':7,'notes':'Optional daily check.'},
            {'supplement':'Fish Oil','category':'General','default_time':'With meal','target_days_per_week':7,'notes':'Optional daily check.'},
            {'supplement':'Pre-workout','category':'Workout','default_time':'Before workout','target_days_per_week':3,'notes':'Only when needed; track timing.'},
            {'supplement':'Magnesium','category':'Recovery','default_time':'Evening','target_days_per_week':7,'notes':'Optional recovery/sleep habit.'},
            {'supplement':'Vitamin D','category':'General','default_time':'Morning with meal','target_days_per_week':7,'notes':'Optional daily check.'},
            {'supplement':'Electrolytes','category':'Hydration','default_time':'Training / sauna','target_days_per_week':4,'notes':'Useful for sweating days.'},
        ])
        default_plan.to_csv(SUPPLEMENT_PLAN, index=False)
        plan=default_plan

    today_s=str(date.today())
    today_sup = sup[sup['date'].astype(str)==today_s] if not sup.empty else pd.DataFrame(columns=cols)
    completed_today=0
    if not today_sup.empty:
        last=today_sup.iloc[-1]
        for field in cols[1:-1]:
            if str(last.get(field,'')).lower() in ['true','1','yes']:
                completed_today += 1
    c1,c2,c3=st.columns(3)
    c1.markdown(f'<div class="metric-card"><div class="metric-label">Today Completed</div><div class="metric-value">{completed_today}/8</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><div class="metric-label">Plan Items</div><div class="metric-value">{len(plan)}</div></div>', unsafe_allow_html=True)
    streak_days = sup['date'].nunique() if not sup.empty else 0
    c3.markdown(f'<div class="metric-card"><div class="metric-label">Days Logged</div><div class="metric-value">{streak_days}</div></div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(['Daily Checklist','Supplement Plan','History & Export'])
    with tab1:
        entry_date=st.text_input('Date', value=today_s, key='sup_date')
        st.markdown('### Today\'s Supplements')
        a,b,c,d=st.columns(4)
        creatine=a.checkbox('Creatine')
        protein=b.checkbox('Protein Powder')
        multi=c.checkbox('Multivitamin')
        fish=d.checkbox('Fish Oil')
        e,f,g,h=st.columns(4)
        pre=e.checkbox('Pre-workout')
        magnesium=f.checkbox('Magnesium')
        vitamin_d=g.checkbox('Vitamin D')
        electrolytes=h.checkbox('Electrolytes')
        notes=st.text_input('Supplement notes', placeholder='Example: took creatine post workout; no pre-workout today')
        if st.button('💾 Save supplement day'):
            append_csv(SUPPLEMENTS, {'date':entry_date,'creatine':creatine,'protein_powder':protein,'multivitamin':multi,'fish_oil':fish,'pre_workout':pre,'magnesium':magnesium,'vitamin_d':vitamin_d,'electrolytes':electrolytes,'notes':notes}, cols)
            st.success('Supplement day saved.')
    with tab2:
        st.markdown('### Supplement Plan')
        st.dataframe(plan, use_container_width=True)
        with st.expander('Add supplement to plan'):
            sname=st.text_input('Supplement name')
            cat=st.selectbox('Category', ['Performance','Protein','General','Workout','Recovery','Hydration','Other'])
            timing=st.text_input('Default time', value='Morning / Workout / Evening')
            target=st.number_input('Target days per week', min_value=0, max_value=7, value=7)
            pnotes=st.text_input('Plan notes')
            if st.button('Add to supplement plan') and sname.strip():
                plan = pd.concat([plan, pd.DataFrame([{'supplement':sname,'category':cat,'default_time':timing,'target_days_per_week':target,'notes':pnotes}])], ignore_index=True)
                plan.to_csv(SUPPLEMENT_PLAN, index=False)
                st.success('Supplement added to plan. Refresh page to see updated list.')
    with tab3:
        if sup.empty:
            st.info('No supplement entries yet.')
        else:
            st.dataframe(sup.tail(90), use_container_width=True)
            # Weekly consistency summary
            calc=sup.copy()
            for field in cols[1:-1]:
                calc[field]=calc[field].astype(str).str.lower().isin(['true','1','yes']).astype(int)
            totals=calc[cols[1:-1]].sum().sort_values(ascending=False).reset_index()
            totals.columns=['supplement','times_taken']
            st.markdown('### Consistency Summary')
            st.dataframe(totals, use_container_width=True)
            st.download_button('Export supplement_log.csv', SUPPLEMENTS.read_bytes(), file_name='supplement_log.csv')

elif page == "Body Stats":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.3</div><div class="title">Body Stats</div><div class="sub">Track body weight, goal weight, waist, and notes.</div></div>', unsafe_allow_html=True)
    cols=['date','body_weight_lbs','goal_weight_lbs','waist_in','notes']
    body=read_csv_safe(BODY, cols)
    c1,c2,c3,c4=st.columns(4)
    entry_date=c1.text_input('Date', value=str(date.today()), key='body_date')
    bw=c2.number_input('Current weight lbs', min_value=0.0, value=0.0, step=0.5)
    gw=c3.number_input('Goal weight lbs', min_value=0.0, value=0.0, step=0.5)
    waist=c4.number_input('Waist inches', min_value=0.0, value=0.0, step=0.25)
    notes=st.text_input('Notes', placeholder='Energy, soreness, progress photo note')
    if st.button('💾 Save body stats'):
        append_csv(BODY, {'date':entry_date,'body_weight_lbs':bw,'goal_weight_lbs':gw,'waist_in':waist,'notes':notes}, cols)
        st.success('Body stats saved.')
    if body.empty: st.info('No body stats saved yet.')
    else:
        st.dataframe(body.tail(100), use_container_width=True)
        chart = body.copy()
        chart['body_weight_lbs'] = pd.to_numeric(chart['body_weight_lbs'], errors='coerce')
        chart = chart.dropna(subset=['body_weight_lbs'])
        if not chart.empty:
            st.line_chart(chart.set_index('date')['body_weight_lbs'])

elif page == "Exercise Library":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.3</div><div class="title">Exercise Image Library</div><div class="sub">Checks assets/exercises and data/exercise_image_map.csv</div></div>', unsafe_allow_html=True)
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
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.3</div><div class="title">Workout History</div><div class="sub">Saved completed sets</div></div>', unsafe_allow_html=True)
    log=load_log()
    if log.empty: st.info('No workouts saved yet.')
    else: st.dataframe(log.tail(200), use_container_width=True)

elif page == "Data Safety":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker 2.3</div><div class="title">Data Safety</div><div class="sub">Important files before updates</div></div>', unsafe_allow_html=True)
    st.code('data/workout_log.csv\ndata/workouts.csv\ndata/exercise_image_map.csv\ndata/nutrition_log.csv\ndata/body_stats.csv\ndata/supplement_log.csv\ndata/supplement_plan.csv\nassets/exercises/')
    if LOG.exists():
        st.download_button('Export workout_log.csv', LOG.read_bytes(), file_name='workout_log.csv')
    if NUTRITION.exists():
        st.download_button('Export nutrition_log.csv', NUTRITION.read_bytes(), file_name='nutrition_log.csv')
    if BODY.exists():
        st.download_button('Export body_stats.csv', BODY.read_bytes(), file_name='body_stats.csv')
    if SUPPLEMENTS.exists():
        st.download_button('Export supplement_log.csv', SUPPLEMENTS.read_bytes(), file_name='supplement_log.csv')
    if SUPPLEMENT_PLAN.exists():
        st.download_button('Export supplement_plan.csv', SUPPLEMENT_PLAN.read_bytes(), file_name='supplement_plan.csv')
