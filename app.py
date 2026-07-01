import base64
from pathlib import Path
from datetime import date, datetime
import pandas as pd
import streamlit as st

BASE = Path(__file__).parent
DATA = BASE / 'data'
ASSETS = BASE / 'assets'
EXDIR = ASSETS / 'exercises'
WORKOUTS = DATA / 'workouts.csv'
LOG = DATA / 'workout_log.csv'
MAP = DATA / 'exercise_image_map.csv'

st.set_page_config(page_title='Brian Fitness Tracker 2.0 Recovery', layout='wide', initial_sidebar_state='expanded')

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
html, body, [class*='css'] {font-family: Inter, sans-serif;}
.stApp {background:#07111f;color:#f8fafc;}
[data-testid='stSidebar'] {background: linear-gradient(180deg,#061326,#09223d); border-right:1px solid #203650;}
[data-testid='stSidebar'] * {color:#f8fafc !important;}
.block-container {padding-top:1.2rem; max-width:1400px;}
.hero {background:#0f1d31;border:1px solid #263e5e;border-radius:22px;padding:26px 30px;margin-bottom:18px;}
.hero small {color:#36f77b;font-weight:900;letter-spacing:3px;}
.hero h1 {font-size:38px;margin:8px 0 8px 0;color:#fff;}
.pill {display:inline-block;background:#0b3b73;border:1px solid #2e8cff;color:#bfdbfe;border-radius:999px;padding:8px 14px;font-weight:800;font-size:13px;margin-right:8px;}
.pill.green {background:#063d24;border-color:#18a34a;color:#84f5a6;}
.card {background:#0f1d31;border:1px solid #263e5e;border-radius:18px;padding:18px;margin:0 0 18px 0;box-shadow:0 10px 24px rgba(0,0,0,.18);}
.exercise-grid {display:grid;grid-template-columns: 320px 1fr; gap:22px; align-items:start;}
.ex-img-wrap {background:#0a1627;border:1px solid #2b4667;border-radius:16px;padding:10px;height:250px;display:flex;align-items:center;justify-content:center;overflow:hidden;}
.ex-img {max-width:100%;max-height:230px;object-fit:contain;border-radius:12px;}
.no-img {height:230px;display:flex;align-items:center;justify-content:center;color:#93c5fd;text-align:center;}
.ex-title {font-size:25px;font-weight:900;margin:0 0 8px;color:#fff;}
.meta {color:#9cc3f0;font-weight:700;margin:6px 0;}
.table-head {display:grid;grid-template-columns:60px 150px 130px 120px 1fr 100px;gap:10px;color:#9cc3f0;font-size:12px;font-weight:900;text-transform:uppercase;margin-top:16px;padding-bottom:8px;border-bottom:1px solid #263e5e;}
.set-row {display:grid;grid-template-columns:60px 150px 130px 120px 1fr 100px;gap:10px;align-items:center;margin-top:9px;}
.set-badge {background:#1d74ff;color:white;border-radius:999px;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-weight:900;}
.vol {color:#36f77b;font-weight:900;}
.side-card {background:#0f1d31;border:1px solid #263e5e;border-radius:18px;padding:20px;margin-bottom:16px;}
.side-card h3 {margin-top:0;color:#fff;}
.metric {font-size:28px;font-weight:900;color:#fff;}
.small-muted {color:#9cc3f0;}
.stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb='select'] {background:#07111f !important;color:#fff !important;border-color:#35587f !important;}
.stButton button {background:#0e63ff;color:#fff;border:1px solid #4c91ff;border-radius:10px;font-weight:800;}
@media (max-width:900px){.exercise-grid{grid-template-columns:1fr}.table-head,.set-row{grid-template-columns:38px 1fr 1fr}.hide-mobile{display:none}.ex-img-wrap{height:220px}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# sidebar
st.sidebar.markdown('## 🏋️ Brian Fit 2.0')
st.sidebar.markdown('**Recovery Build**')
page = st.sidebar.radio('Navigation', ['Dashboard','Today Workout','Weekly Plan','Image Library','History','Data Safety'])
st.sidebar.markdown('---')
st.sidebar.success('Workout history saves to\n\n`data/workout_log.csv`')

# helpers
def ensure_files():
    DATA.mkdir(exist_ok=True)
    EXDIR.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        pd.DataFrame(columns=['timestamp','date','day','workout','exercise','set_number','weight_lbs','reps','rpe','notes','volume_lbs']).to_csv(LOG,index=False)

@st.cache_data(ttl=5)
def load_data():
    ensure_files()
    if not WORKOUTS.exists():
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    workouts = pd.read_csv(WORKOUTS)
    img_map = pd.read_csv(MAP) if MAP.exists() else pd.DataFrame(columns=['exercise_name','image_file'])
    log = pd.read_csv(LOG) if LOG.exists() else pd.DataFrame()
    return workouts, img_map, log

def img_path(exercise, img_map):
    if img_map.empty: return None
    hit = img_map[img_map['exercise_name'].astype(str).str.lower().str.strip()==str(exercise).lower().strip()]
    if hit.empty:
        return None
    fname = str(hit.iloc[0]['image_file']).replace('\\','/')
    p = EXDIR / fname
    if p.exists(): return p
    p2 = EXDIR / Path(fname).name
    return p2 if p2.exists() else None

def img_html(path):
    if path and path.exists():
        b64 = base64.b64encode(path.read_bytes()).decode()
        return f"<img class='ex-img' src='data:image/png;base64,{b64}' />"
    return "<div class='no-img'>Image coming soon<br><span class='small-muted'>assets/exercises</span></div>"

def save_rows(rows):
    ensure_files()
    old = pd.read_csv(LOG) if LOG.exists() else pd.DataFrame()
    new = pd.DataFrame(rows)
    pd.concat([old,new], ignore_index=True).to_csv(LOG,index=False)

workouts, img_map, log = load_data()

def dashboard():
    today_name = date.today().strftime('%A')
    todays = workouts[workouts['day'].eq(today_name)] if not workouts.empty else pd.DataFrame()
    total_vol = int(log['volume_lbs'].sum()) if not log.empty and 'volume_lbs' in log.columns else 0
    st.markdown(f"""<div class='hero'><small>BRIAN FITNESS TRACKER 2.0</small><h1>Commercial Dashboard</h1><p class='small-muted'>Today is {today_name} • {todays['workout'].iloc[0] if not todays.empty else 'Rest / Recovery'}</p></div>""", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.markdown(f"<div class='side-card'><div class='small-muted'>Sessions</div><div class='metric'>{log['date'].nunique() if not log.empty and 'date' in log else 0}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='side-card'><div class='small-muted'>Total Volume</div><div class='metric'>{total_vol:,} lbs</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='side-card'><div class='small-muted'>Exercises Today</div><div class='metric'>{len(todays)}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='side-card'><div class='small-muted'>Images Installed</div><div class='metric'>{len(list(EXDIR.glob('*.png')))}</div></div>", unsafe_allow_html=True)
    st.subheader('Weekly Schedule')
    cols=st.columns(7)
    for i,d in enumerate(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']):
        dd=workouts[workouts['day'].eq(d)] if not workouts.empty else pd.DataFrame()
        title=dd['workout'].iloc[0] if not dd.empty else 'Rest'
        cols[i].markdown(f"<div class='card'><b>{d[:3]}</b><br><span class='pill'>{title}</span><br><span class='small-muted'>{len(dd)} exercises</span></div>", unsafe_allow_html=True)

def today_workout():
    if workouts.empty:
        st.error('Missing data/workouts.csv')
        return
    days = list(workouts['day'].dropna().unique())
    default_day = date.today().strftime('%A') if date.today().strftime('%A') in days else days[0]
    day = st.selectbox('Workout Day', days, index=days.index(default_day))
    active = workouts[workouts['day'].eq(day)].reset_index(drop=True)
    if active.empty:
        st.info('No workout for this day.')
        return
    workout_name = active['workout'].iloc[0]
    st.markdown(f"""<div class='hero'><small>BRIAN FITNESS TRACKER 2.0 RECOVERY</small><h1>{day} — {workout_name}</h1><span class='pill'>{workout_name}</span><span class='pill green'>{len(active)} exercises</span></div>""", unsafe_allow_html=True)
    total_volume=0; rows=[]
    main, side = st.columns([4,1.1])
    with main:
        wdate = st.text_input('Workout date', value=str(date.today()).replace('-','/'))
        for idx, ex in active.iterrows():
            name=str(ex['exercise']); sets=int(ex['target_sets']) if str(ex['target_sets']).isdigit() else 3
            reps_default = 12
            try:
                reps_default=int(str(ex['target_reps']).split('-')[-1].split()[0])
            except Exception: reps_default=0
            weight_default=float(ex.get('starting_weight_lbs',0) or 0)
            p=img_path(name,img_map)
            st.markdown(f"<div class='card'><div class='exercise-grid'><div class='ex-img-wrap'>{img_html(p)}</div><div><div class='ex-title'>{idx+1}. {name}</div><span class='pill'>Target: {ex['target_sets']} x {ex['target_reps']}</span><span class='pill green'>{workout_name}</span><div class='meta'>Previous Best: 0 lbs</div><div class='table-head'><div>Set</div><div>Weight</div><div>Reps</div><div>RPE</div><div class='hide-mobile'>Notes</div><div>Volume</div></div>", unsafe_allow_html=True)
            for s in range(1, sets+1):
                c0,c1,c2,c3,c4,c5=st.columns([.45,1.4,1.1,1.1,1.7,.9])
                c0.markdown(f"<div class='set-badge'>{s}</div>", unsafe_allow_html=True)
                wt=c1.number_input('wt', value=weight_default, step=5.0, key=f'{name}_{s}_wt', label_visibility='collapsed')
                rp=c2.number_input('reps', value=reps_default, step=1, key=f'{name}_{s}_rp', label_visibility='collapsed')
                rpe=c3.number_input('rpe', value=7.0, step=.5, min_value=0.0, max_value=10.0, key=f'{name}_{s}_rpe', label_visibility='collapsed')
                note=c4.text_input('note', value='felt good' if s==1 else '', key=f'{name}_{s}_note', label_visibility='collapsed')
                vol=int(wt*rp); total_volume += vol
                c5.markdown(f"<div class='vol'>{vol:,} lbs</div>", unsafe_allow_html=True)
                if wt>0 or rp>0:
                    rows.append({'timestamp':datetime.now().isoformat(timespec='seconds'),'date':wdate,'day':day,'workout':workout_name,'exercise':name,'set_number':s,'weight_lbs':wt,'reps':rp,'rpe':rpe,'notes':note,'volume_lbs':vol})
            if st.button(f'💾 Save {name}', key=f'save_{idx}'):
                exrows=[r for r in rows if r['exercise']==name]
                save_rows(exrows)
                st.success(f'Saved {name}')
            st.markdown('</div></div></div>', unsafe_allow_html=True)
    with side:
        st.markdown(f"<div class='side-card'><h3>📋 Workout Summary</h3><p>Exercises</p><div class='metric'>{len(active)}</div><p>Total Volume</p><div class='metric'>{total_volume:,} lbs</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='side-card'><h3>💪 Muscle Focus</h3><div class='metric' style='font-size:22px'>{workout_name}</div><p class='small-muted'>Controlled form first. Protect the knee.</p></div>", unsafe_allow_html=True)
        if st.button('✅ Save Full Workout'):
            save_rows(rows)
            st.success('Full workout saved')

def weekly():
    st.markdown("<div class='hero'><small>BRIAN FITNESS TRACKER 2.0</small><h1>Weekly Plan</h1><p class='small-muted'>Days, muscle groups, and exercise count</p></div>", unsafe_allow_html=True)
    for d in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:
        dd=workouts[workouts['day'].eq(d)] if not workouts.empty else pd.DataFrame()
        title=dd['workout'].iloc[0] if not dd.empty else 'Rest'
        st.markdown(f"<div class='card'><h3>{d} — {title}</h3><p class='small-muted'>{len(dd)} exercises</p></div>", unsafe_allow_html=True)

def images():
    st.markdown("<div class='hero'><small>BRIAN FITNESS TRACKER 2.0</small><h1>Image Library Test</h1><p class='small-muted'>Checks assets/exercises and data/exercise_image_map.csv</p></div>", unsafe_allow_html=True)
    st.write('Images folder:', str(EXDIR))
    st.write('Image files found:', len(list(EXDIR.glob('*.png'))))
    if img_map.empty:
        st.warning('No exercise_image_map.csv found.')
    else:
        for _,r in img_map.iterrows():
            p=img_path(r['exercise_name'], img_map)
            status='✅' if p else '❌'
            st.write(status, r['exercise_name'], '→', r['image_file'])

def history():
    st.markdown("<div class='hero'><small>BRIAN FITNESS TRACKER 2.0</small><h1>Workout History</h1><p class='small-muted'>Saved completed sets</p></div>", unsafe_allow_html=True)
    if log.empty:
        st.info('No workouts saved yet.')
    else:
        st.dataframe(log.tail(200), use_container_width=True)
        st.download_button('Download workout_log.csv', LOG.read_bytes(), file_name='workout_log.csv')

def safety():
    st.markdown("<div class='hero'><small>BRIAN FITNESS TRACKER 2.0</small><h1>Data Safety</h1><p class='small-muted'>Important files before updates</p></div>", unsafe_allow_html=True)
    st.code('data/workout_log.csv\ndata/workouts.csv\ndata/exercise_image_map.csv\nassets/exercises/')
    if LOG.exists(): st.download_button('Export workout_log.csv', LOG.read_bytes(), 'workout_log.csv')

if page=='Dashboard': dashboard()
elif page=='Today Workout': today_workout()
elif page=='Weekly Plan': weekly()
elif page=='Image Library': images()
elif page=='History': history()
else: safety()
