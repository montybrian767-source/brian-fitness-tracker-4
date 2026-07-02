
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

st.set_page_config(page_title="Brian Fitness Tracker X", page_icon="🏋️", layout="wide", initial_sidebar_state="expanded")

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

def repair_workout_database(df):
    """Keep the weekly plan clean even if an older workouts.csv is uploaded."""
    required = ['day','muscle_group','exercise','target_sets','target_reps','base_weight','image_file']
    for c in required:
        if c not in df.columns:
            df[c] = ''

    # Normalize text fields
    df['day'] = df['day'].astype(str).str.strip()
    df['muscle_group'] = df['muscle_group'].astype(str).str.strip()
    df['exercise'] = df['exercise'].astype(str).str.strip()

    changed = False

    # Remove calf work from Wednesday / Shoulder Day
    wrong = (df['day'].str.lower() == 'wednesday') & (df['exercise'].str.lower().str.contains('calf', na=False))
    if wrong.any():
        df = df.loc[~wrong].copy()
        changed = True

    # Add Plank to Wednesday if missing
    wed = df[df['day'].str.lower() == 'wednesday']
    has_plank = wed['exercise'].str.lower().eq('plank').any()
    if not has_plank:
        df = pd.concat([df, pd.DataFrame([{
            'day':'Wednesday',
            'muscle_group':'Shoulders + Abs',
            'exercise':'Plank',
            'target_sets':3,
            'target_reps':'45 sec',
            'base_weight':0,
            'image_file':'plank.png'
        }])], ignore_index=True)
        changed = True

    # Ensure Standing Calf Raise lives on leg/recovery day, not shoulders.
    has_calf = df['exercise'].str.lower().eq('standing calf raise').any()
    if not has_calf:
        df = pd.concat([df, pd.DataFrame([{
            'day':'Thursday',
            'muscle_group':'Leg Rehab Day',
            'exercise':'Standing Calf Raise',
            'target_sets':3,
            'target_reps':15,
            'base_weight':30,
            'image_file':'standing_calf_raise.png'
        }])], ignore_index=True)
        changed = True

    # Deduplicate exact same day/exercise rows
    before = len(df)
    df = df.drop_duplicates(subset=['day','exercise'], keep='first').reset_index(drop=True)
    if len(df) != before:
        changed = True

    if changed:
        try:
            df.to_csv(WORKOUTS, index=False)
        except Exception:
            pass
    return df[required]

def load_workouts():
    if not WORKOUTS.exists():
        st.error("Missing data/workouts.csv")
        return pd.DataFrame(columns=['day','muscle_group','exercise','target_sets','target_reps','base_weight','image_file'])
    df = pd.read_csv(WORKOUTS)
    return repair_workout_database(df)

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

/* 2.5.1 repair: brighter supplement cards */
.supp-bright-card{border-radius:18px;padding:16px;margin:10px 0;color:white;border:1px solid rgba(255,255,255,.18);box-shadow:0 10px 24px rgba(0,0,0,.22)}
.supp-performance{background:linear-gradient(135deg,#075985,#2563eb)}
.supp-protein{background:linear-gradient(135deg,#064e3b,#10b981)}
.supp-recovery{background:linear-gradient(135deg,#14532d,#22c55e)}
.supp-general{background:linear-gradient(135deg,#581c87,#a855f7)}
.supp-workout{background:linear-gradient(135deg,#7c2d12,#f97316)}
.supp-hydration{background:linear-gradient(135deg,#164e63,#06b6d4)}
.supp-title{font-size:1.12rem;font-weight:950;margin-bottom:4px}.supp-meta{font-size:.86rem;opacity:.95}.supp-pill{display:inline-block;margin-top:8px;background:rgba(255,255,255,.18);padding:5px 8px;border-radius:999px;font-weight:850;font-size:.78rem}



/* 3.1 Professional UI polish */
.stApp {background: radial-gradient(circle at top left, #10284a 0%, #07111f 34%, #050b14 100%) !important;}
.block-container {padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1480px;}
[data-testid="stToolbar"] {display:none;}
.hero {box-shadow: 0 18px 45px rgba(0,0,0,.28); border:1px solid rgba(96,165,250,.32) !important;}
.metric-card, .side-card, .exercise-card, .macro-card {box-shadow: 0 14px 34px rgba(0,0,0,.22);}
.metric-card {background:linear-gradient(145deg,#10263f,#0c1a2d) !important;}
.metric-card:hover, .side-card:hover, .exercise-card:hover {border-color:#60a5fa !important;}
.stTabs [data-baseweb="tab-list"] {gap:10px; background:#081322; padding:8px; border-radius:18px; border:1px solid #1d3655;}
.stTabs [data-baseweb="tab"] {border-radius:14px; padding:10px 14px; color:#c8ddff; font-weight:900;}
.stTabs [aria-selected="true"] {background:#2563eb !important; color:white !important;}
.stSelectbox div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input, .stTextArea textarea {background:#0b1e33 !important; color:#f8fafc !important; border:1px solid #2b527a !important;}
.stCheckbox label span {color:#f8fafc !important; font-weight:700;}
.stDataFrame {border:1px solid #254264; border-radius:16px; overflow:hidden;}
div[data-testid="stMetric"] {background:#0f1f34; border:1px solid #254264; border-radius:18px; padding:14px;}
section[data-testid="stSidebar"] [role="radiogroup"] label {background:rgba(255,255,255,.035); border:1px solid rgba(96,165,250,.10); border-radius:14px; padding:8px 10px; margin:5px 0;}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {background:rgba(37,99,235,.20); border-color:#60a5fa;}
section[data-testid="stSidebar"] h2 {font-size:1.45rem !important;}
.professional-chip {display:inline-flex;align-items:center;gap:6px;padding:7px 11px;border-radius:999px;background:#0b2b4f;border:1px solid #60a5fa;color:#c8ddff;font-weight:900;font-size:.78rem;margin-right:6px;}

/* 3.2 Mobile navigation fix */
.mobile-nav-title{display:none;}
div[role="radiogroup"]{gap:8px; flex-wrap:wrap;}
div[role="radiogroup"] label{background:#0f1f34 !important; border:1px solid #254264 !important; border-radius:14px !important; padding:8px 12px !important; margin:4px 2px !important; color:#f8fafc !important; font-weight:900 !important;}
div[role="radiogroup"] label:hover{border-color:#60a5fa !important; background:#12375f !important;}
div[role="radiogroup"] label[data-checked="true"], div[role="radiogroup"] label:has(input:checked){background:linear-gradient(135deg,#2563eb,#22c55e) !important; border-color:#22c55e !important; color:white !important; box-shadow:0 0 18px rgba(34,197,94,.35) !important;}
@media (max-width: 900px){
  section[data-testid="stSidebar"]{display:none !important;}
  .mobile-nav-title{display:block; position:sticky; top:0; z-index:999; background:#07111f; border:1px solid #254264; border-radius:14px; padding:10px 12px; margin-bottom:8px; font-weight:950; color:#22c55e;}
  div[role="radiogroup"]{position:sticky; top:48px; z-index:998; background:#07111f; padding:8px; border:1px solid #254264; border-radius:16px; margin-bottom:14px; box-shadow:0 12px 30px rgba(0,0,0,.3);}
  div[role="radiogroup"] label{font-size:.82rem !important; padding:8px 10px !important;}
  .hero{padding:18px !important;}
  .title{font-size:1.55rem !important;}
}



/* 3.2.2 TOP NAV CONTRAST FIX */
/* Make horizontal top navigation readable on dark background */
div[role="radiogroup"] label,
div[role="radiogroup"] label *,
div[role="radiogroup"] label p,
div[role="radiogroup"] label span {
    color: #f8fafc !important;
    opacity: 1 !important;
    font-weight: 900 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,.55) !important;
}

div[role="radiogroup"] label {
    background: linear-gradient(135deg, #10263f, #0b1e33) !important;
    border: 1.5px solid #3b82f6 !important;
    box-shadow: 0 4px 14px rgba(0,0,0,.28) !important;
}

div[role="radiogroup"] label:hover {
    background: linear-gradient(135deg, #1d4ed8, #0f766e) !important;
    border-color: #60a5fa !important;
}

div[role="radiogroup"] label[data-checked="true"],
div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg, #2563eb, #22c55e) !important;
    border: 2px solid #86efac !important;
    box-shadow: 0 0 18px rgba(34,197,94,.55) !important;
}

div[role="radiogroup"] label[data-checked="true"] *,
div[role="radiogroup"] label:has(input:checked) * {
    color: #ffffff !important;
    opacity: 1 !important;
}

/* Make the small radio dots visible but not distracting */
div[role="radiogroup"] input[type="radio"] + div,
div[role="radiogroup"] [data-testid="stMarkdownContainer"] {
    color: #f8fafc !important;
    opacity: 1 !important;
}


/* X.4.1 Executive Dashboard - stable Streamlit-safe HTML */
.x-hero {position:relative; overflow:hidden; border:1px solid rgba(59,130,246,.45); background: radial-gradient(circle at 75% 30%, rgba(37,99,235,.35), transparent 32%), linear-gradient(135deg,#08111F 0%,#0B1B35 55%,#0B1220 100%); border-radius:28px; padding:38px 42px; margin:18px 0 26px 0; box-shadow:0 25px 70px rgba(0,0,0,.45);}
.x-kicker {letter-spacing:.30em; color:#22C55E; font-size:.78rem; font-weight:950; text-transform:uppercase;}
.x-title {font-size:3.05rem; font-weight:950; color:#fff; line-height:1.02; margin:14px 0 10px 0;}
.x-subtitle {font-size:1.08rem; color:#BFD7FF; max-width:690px; line-height:1.55;}
.x-recovery {position:absolute; right:42px; top:34px; text-align:right;}
.x-recovery .big {font-size:4rem; line-height:1; color:#22C55E; font-weight:950;}
.x-recovery .label {letter-spacing:.18em; color:#fff; font-weight:900; margin-top:8px;}
.x-recovery .status {color:#7CFF9B; font-weight:900; margin-top:8px;}
.x-mission {display:grid; grid-template-columns: 1.2fr .9fr; gap:22px; align-items:center; border:1px solid rgba(59,130,246,.45); background:linear-gradient(135deg,#0D1B2F,#0B1424); border-radius:26px; padding:30px 34px; margin:0 0 22px 0; box-shadow:0 16px 45px rgba(0,0,0,.38);}
.x-mission-label {color:#60A5FA; font-weight:950; letter-spacing:.20em; text-transform:uppercase; font-size:.78rem;}
.x-mission-title {font-size:2.35rem; font-weight:950; color:white; margin:10px 0 20px;}
.x-pills {display:flex; flex-wrap:wrap; gap:14px;}
.x-pill {background:#10243C; border:1px solid #254264; color:#EAF2FF; border-radius:18px; padding:12px 16px; font-weight:850;}
.x-pill.green {background:rgba(34,197,94,.13); border-color:rgba(34,197,94,.55);}
.x-pill.blue {background:rgba(59,130,246,.14); border-color:rgba(59,130,246,.58);}
.x-pill.amber {background:rgba(245,158,11,.12); border-color:rgba(245,158,11,.55);}
.x-start {background:linear-gradient(135deg,#0EA5E9,#2563EB); border-radius:22px; padding:28px; text-align:center; color:white; font-size:1.35rem; font-weight:950; box-shadow:0 18px 55px rgba(37,99,235,.45); border:1px solid rgba(147,197,253,.65);}
.x-stat {background:linear-gradient(145deg,#0F1F34,#0A1728); border:1px solid rgba(59,130,246,.30); border-radius:22px; padding:22px; min-height:150px; box-shadow:0 16px 40px rgba(0,0,0,.28);}
.x-stat-icon {font-size:2rem; margin-bottom:12px;}
.x-stat-label {color:#B8C2D1; font-size:.82rem; letter-spacing:.10em; text-transform:uppercase; font-weight:900;}
.x-stat-value {font-size:2rem; font-weight:950; color:white; margin-top:6px;}
.x-stat-sub {color:#9CC7FF; font-size:.9rem; margin-top:8px;}
.x-progress {height:9px; background:#142842; border-radius:999px; overflow:hidden; margin-top:15px; border:1px solid #24334A;}
.x-progress-fill {height:100%; border-radius:999px; background:linear-gradient(90deg,#2563EB,#22C55E);}
.x-ai {display:grid; grid-template-columns: 1fr .55fr .55fr; gap:18px; background:linear-gradient(135deg,rgba(139,92,246,.18),rgba(15,31,52,.96)); border:1px solid rgba(139,92,246,.45); border-radius:24px; padding:24px 28px; margin:24px 0; box-shadow:0 16px 45px rgba(0,0,0,.32);}
.x-ai-kicker {color:#A78BFA; font-size:.78rem; letter-spacing:.18em; font-weight:950; text-transform:uppercase;}
.x-ai-title {font-size:1.65rem; font-weight:950; color:#fff; margin-top:8px;}
.x-ai-sub {color:#C8D3E6; margin-top:6px;}
.x-ai-mini {border-left:1px solid rgba(255,255,255,.12); padding-left:18px;}
.x-ai-mini .ok {color:#22C55E; font-weight:950; font-size:1.1rem;}
.x-ai-mini .warn {color:#F59E0B; font-weight:950; font-size:1.1rem;}
.x-week {background:#0F1F34; border:1px solid #254264; border-radius:20px; padding:18px; min-height:150px; box-shadow:0 12px 32px rgba(0,0,0,.22);}
.x-week.today {border-color:#22C55E; box-shadow:0 0 28px rgba(34,197,94,.18);}
.x-week-day {font-size:1.1rem; font-weight:950; color:white;}
.x-week-badge {display:inline-block; margin:12px 0 8px; color:#93C5FD; border:1px solid #2563EB; border-radius:999px; padding:7px 10px; font-size:.78rem; font-weight:900;}
@media(max-width: 850px){.x-hero{padding:28px 22px}.x-title{font-size:2.2rem}.x-recovery{position:relative; right:auto; top:auto; text-align:left; margin-top:24px}.x-recovery .big{font-size:3rem}.x-mission{grid-template-columns:1fr}.x-ai{grid-template-columns:1fr}.x-ai-mini{border-left:none; padding-left:0; border-top:1px solid rgba(255,255,255,.12); padding-top:14px}}


/* Sprint X.5 Smart Workout Experience */
.smart-shell{background:linear-gradient(135deg,#08111F,#0B1B35);border:1px solid rgba(96,165,250,.45);border-radius:28px;padding:28px;margin:18px 0 24px;box-shadow:0 24px 70px rgba(0,0,0,.45)}
.smart-top{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;flex-wrap:wrap}.smart-kicker{letter-spacing:.25em;color:#22C55E;font-size:.78rem;font-weight:950;text-transform:uppercase}.smart-title{font-size:2.7rem;font-weight:950;color:#fff;margin:10px 0 8px}.smart-sub{color:#BFD7FF;font-size:1rem}.smart-score{font-size:3.2rem;font-weight:950;color:#22C55E;text-align:right}.smart-score-label{color:#fff;font-weight:900;letter-spacing:.16em;text-align:right}.smart-card{background:linear-gradient(145deg,#0F1F34,#0A1728);border:1px solid rgba(96,165,250,.32);border-radius:24px;padding:22px;margin:16px 0;box-shadow:0 16px 45px rgba(0,0,0,.32)}
.smart-photo-box{background:#081322;border:1px solid #1d3655;border-radius:22px;padding:10px;display:flex;align-items:center;justify-content:center;min-height:330px}.smart-photo{width:100%;height:330px;object-fit:contain;border-radius:16px;background:#06111f}.smart-exercise-title{font-size:2rem;color:white;font-weight:950;margin-bottom:8px}.smart-chip{display:inline-block;background:#0B2B4F;border:1px solid #60A5FA;color:#C8DDFF;border-radius:999px;padding:8px 12px;font-weight:900;font-size:.82rem;margin-right:8px;margin-bottom:8px}.smart-chip.green{background:rgba(34,197,94,.13);border-color:#22C55E;color:#B7FFCE}.smart-chip.purple{background:rgba(139,92,246,.16);border-color:#8B5CF6;color:#DDD6FE}.smart-control{background:#0B1E33;border:1px solid #254264;border-radius:18px;padding:16px}.smart-big-value{font-size:2rem;font-weight:950;color:white}.smart-complete{background:linear-gradient(135deg,#22C55E,#16A34A);border-radius:20px;padding:18px;text-align:center;color:white;font-size:1.2rem;font-weight:950;margin-top:14px;box-shadow:0 15px 40px rgba(34,197,94,.35)}
.smart-timer{background:radial-gradient(circle at center,rgba(34,197,94,.20),rgba(15,31,52,.95));border:1px solid rgba(34,197,94,.50);border-radius:24px;padding:24px;text-align:center}.smart-timer-number{font-size:3.6rem;line-height:1;color:white;font-weight:950}.smart-timer-label{color:#86EFAC;font-weight:950;letter-spacing:.15em;margin-top:8px}.smart-progress{height:14px;background:#132940;border:1px solid #24334A;border-radius:999px;overflow:hidden;margin:14px 0}.smart-progress-fill{height:100%;background:linear-gradient(90deg,#2563EB,#22C55E);border-radius:999px}.smart-ai{background:linear-gradient(135deg,rgba(139,92,246,.22),rgba(15,31,52,.98));border:1px solid rgba(139,92,246,.55);border-radius:22px;padding:20px;color:white}.smart-muted{color:#B8C2D1}.smart-nav-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}@media(max-width:900px){.smart-title{font-size:2rem}.smart-score{text-align:left;font-size:2.5rem}.smart-score-label{text-align:left}.smart-photo,.smart-photo-box{height:250px;min-height:250px}}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Navigation — desktop sidebar + phone-friendly top menu
nav_options = ["Dashboard","Today's Workout","Gym Mode","AI Coach","Workout Builder","Weekly Plan","System Check","Nutrition","Supplements","Body Stats","Progress Analytics","Exercise Library","History","Data Safety"]
st.sidebar.markdown("## 🏋️ Brian Fit 3.3")
st.sidebar.caption("X.5.1 Workout Command Center")
st.sidebar.markdown('<div class="safe"><b>✅ Data safe</b><br><br><span class="small">Workout history saves to</span><br><b>data/workout_log.csv</b></div>', unsafe_allow_html=True)

st.markdown('<div class="mobile-nav-title">📱 Quick Navigation</div>', unsafe_allow_html=True)
page = st.radio("Mobile / Desktop Navigation", nav_options, horizontal=True, key="main_nav", label_visibility="collapsed")

workouts = load_workouts()
log = load_log()
days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

if page == "Dashboard":
    today = date.today().strftime('%A')
    today_df = workouts[workouts.day == today]
    focus = today_df.muscle_group.iloc[0] if not today_df.empty else "Recovery / Rest"
    total_sessions = log['date'].nunique() if not log.empty and 'date' in log else 0
    total_volume = int(pd.to_numeric(log.get('volume', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not log.empty else 0
    installed = len(list(ASSETS.glob('*.png'))) + len(list(ASSETS.glob('*.jpg')))
    nut = read_csv_safe(NUTRITION, ['date','meal','calories','protein_g','carbs_g','fat_g','water_oz','notes'])
    today_s = str(date.today())
    nt = nut[nut['date'].astype(str) == today_s] if not nut.empty else nut
    cal_today = int(pd.to_numeric(nt.get('calories', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not nt.empty else 0
    protein_today = int(pd.to_numeric(nt.get('protein_g', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not nt.empty else 0
    water_today = int(pd.to_numeric(nt.get('water_oz', pd.Series(dtype=float)), errors='coerce').fillna(0).sum()) if not nt.empty else 0
    protein_pct = min(100, int((protein_today / 160) * 100)) if protein_today else 0
    water_pct = min(100, int((water_today / 100) * 100)) if water_today else 0
    calorie_pct = min(100, int((cal_today / 2800) * 100)) if cal_today else 0
    recovery_score = 94
    status = "Excellent" if recovery_score >= 85 else "Good"
    ai_weight_tip = "+5 lb" if total_sessions > 0 else "Build consistency"

    st.markdown(f'''
    <div class="x-hero">
        <div class="x-kicker">Brian Fitness Tracker X</div>
        <div class="x-title">Good Morning Brian</div>
        <div class="x-subtitle">You are building consistency. Today is <b>{today}</b> • <b>{focus}</b>. Make the next action obvious and keep moving forward.</div>
        <div class="x-recovery">
            <div class="big">{recovery_score}%</div>
            <div class="label">RECOVERY</div>
            <div class="status">● {status}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="x-mission">
        <div>
            <div class="x-mission-label">Today's Mission</div>
            <div class="x-mission-title">{focus}</div>
            <div class="x-pills">
                <div class="x-pill green">Recovery: <b>{recovery_score}%</b></div>
                <div class="x-pill blue">Status: <b>Ready To Train</b></div>
                <div class="x-pill amber">Estimated Time: <b>58 min</b></div>
            </div>
        </div>
        <div class="x-start">💪 START TODAY'S WORKOUT</div>
    </div>
    ''', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "🔥", "Calories", f"{cal_today:,}", "/ 2,800 kcal", calorie_pct, "#A855F7"),
        (c2, "💪", "Protein", f"{protein_today}g", "/ 160g", protein_pct, "#22C55E"),
        (c3, "💧", "Water", f"{water_today} oz", "/ 100 oz", water_pct, "#3B82F6"),
        (c4, "⚡", "Streak", f"{total_sessions}", "sessions", min(100,total_sessions*10), "#F59E0B"),
        (c5, "🏋️", "Volume", f"{total_volume:,}", "lbs lifted", 70 if total_volume else 0, "#8B5CF6"),
    ]
    for col, icon, label, value, sub, pct, color in cards:
        col.markdown(f'''
        <div class="x-stat">
            <div class="x-stat-icon">{icon}</div>
            <div class="x-stat-label">{label}</div>
            <div class="x-stat-value">{value}</div>
            <div class="x-stat-sub">{sub}</div>
            <div class="x-progress"><div class="x-progress-fill" style="width:{pct}%; background:linear-gradient(90deg,{color},#60A5FA);"></div></div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="x-ai">
        <div>
            <div class="x-ai-kicker">AI Coach Recommendation</div>
            <div class="x-ai-title">{('Increase Shoulder Press ' + ai_weight_tip) if total_sessions else 'Complete today’s workout and log every set'}</div>
            <div class="x-ai-sub">Focus on controlled reps, protect the knee, and finish with clean notes so the coach gets smarter.</div>
        </div>
        <div class="x-ai-mini">
            <div class="x-ai-kicker">Protein Intake</div>
            <div class="ok">{'On Track' if protein_pct >= 80 else 'Below Goal'}</div>
        </div>
        <div class="x-ai-mini">
            <div class="x-ai-kicker">Hydration</div>
            <div class="{'ok' if water_pct >= 80 else 'warn'}">{'On Track' if water_pct >= 80 else 'Below Goal'}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("## Weekly Schedule")
    cols = st.columns(7)
    for col, day in zip(cols, days):
        d = workouts[workouts.day == day]
        group = d.muscle_group.iloc[0] if not d.empty else 'Rest'
        today_class = ' today' if day == today else ''
        col.markdown(f'''
        <div class="x-week{today_class}">
            <div class="x-week-day">{day[:3]}</div>
            <div class="x-week-badge">{group}</div>
            <div class="small">{len(d)} exercises</div>
        </div>
        ''', unsafe_allow_html=True)

elif page == "Today's Workout":
    today = date.today().strftime('%A')
    day = st.selectbox("Workout Day", days, index=date.today().weekday() if date.today().weekday()<7 else 0, key="smart_day")
    active = workouts[workouts.day == day].reset_index(drop=True)
    group = active.muscle_group.iloc[0] if not active.empty else "Recovery / Rest"
    log_now = load_log()
    completed_today = 0
    if not log_now.empty and 'date' in log_now.columns and 'day' in log_now.columns:
        completed_today = len(log_now[(log_now['date'].astype(str) == str(date.today())) & (log_now['day'].astype(str) == day)])
    progress_pct = 0 if active.empty else min(100, int((completed_today / max(1, len(active) * 3)) * 100))
    recovery_score = 94

    st.markdown(f'''
    <div class="smart-shell">
      <div class="smart-top">
        <div>
          <div class="smart-kicker">Brian Fitness Tracker X • Workout Command Center</div>
          <div class="smart-title">{day} — {group}</div>
          <div class="smart-sub">Live training command center: image, set logging, rest timer, progress, and coach notes.</div>
        </div>
        <div>
          <div class="smart-score">{recovery_score}%</div>
          <div class="smart-score-label">READY</div>
        </div>
      </div>
      <div class="smart-progress"><div class="smart-progress-fill" style="width:{progress_pct}%;"></div></div>
      <div class="smart-muted">Workout progress: {progress_pct}% • Completed sets today: {completed_today}</div>
    </div>
    ''', unsafe_allow_html=True)

    if active.empty:
        st.success("Recovery day. Use mobility, walking, sauna, swimming, or rest.")
    else:
        if 'smart_idx' not in st.session_state:
            st.session_state.smart_idx = 0
        st.session_state.smart_idx = max(0, min(int(st.session_state.smart_idx), len(active)-1))
        pick = st.number_input("Exercise", min_value=1, max_value=len(active), value=st.session_state.smart_idx+1, step=1, key="smart_pick") - 1
        st.session_state.smart_idx = int(pick)
        row = active.iloc[st.session_state.smart_idx]
        sets = int(row.target_sets) if str(row.target_sets).isdigit() else 3
        target_reps_display = str(row.target_reps)
        try:
            reps_default = int(target_reps_display.split('-')[-1].split()[0])
        except Exception:
            reps_default = 12

        photo_html = img_tag(image_path(row)).replace('class="exercise-photo"', 'class="smart-photo"')
        left, right = st.columns([1.05, 1.15])
        with left:
            st.markdown(f'<div class="smart-card"><div class="smart-photo-box">{photo_html}</div></div>', unsafe_allow_html=True)
            st.markdown(f'''
            <div class="smart-ai">
              <div class="smart-kicker">AI Coach</div>
              <div style="font-size:1.35rem;font-weight:950;margin-top:8px;">Today’s Focus</div>
              <div class="smart-muted" style="margin-top:8px;">Use controlled reps. If pain rises above 3/10, stop the set and reduce load. If all reps feel clean under RPE 8, consider adding weight next time.</div>
            </div>
            ''', unsafe_allow_html=True)
        with right:
            st.markdown(f'''
            <div class="smart-card">
              <div class="smart-exercise-title">{st.session_state.smart_idx+1}. {row.exercise}</div>
              <span class="smart-chip">Target: {row.target_sets} × {row.target_reps}</span>
              <span class="smart-chip green">{row.muscle_group}</span>
              <span class="smart-chip purple">Base: {row.base_weight} lbs</span>
            </div>
            ''', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                wt = st.number_input("Weight", min_value=0.0, value=float(row.base_weight), step=5.0, key=f"smart_w_{st.session_state.smart_idx}")
            with c2:
                reps = st.number_input("Reps", min_value=0, value=reps_default, step=1, key=f"smart_r_{st.session_state.smart_idx}")
            with c3:
                rpe = st.number_input("RPE", min_value=0.0, max_value=10.0, value=7.0, step=.5, key=f"smart_rpe_{st.session_state.smart_idx}")
            pain = st.slider("Pain check", 0, 10, 0, key=f"smart_pain_{st.session_state.smart_idx}")
            notes = st.text_input("Quick notes", value="", placeholder="Form, difficulty, pain, etc.", key=f"smart_notes_{st.session_state.smart_idx}")
            set_number = st.number_input("Set number", min_value=1, max_value=max(sets, 8), value=1, step=1, key=f"smart_set_{st.session_state.smart_idx}")
            vol = int(wt * reps)
            st.markdown(f'''
            <div class="smart-control">
              <div class="smart-muted">Current Set Volume</div>
              <div class="smart-big-value">{vol:,} lbs</div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("✅ Complete Set", key="smart_complete", use_container_width=True):
                save_log([{'date':str(date.today()),'day':day,'exercise':row.exercise,'set_number':set_number,'weight_lbs':wt,'reps':reps,'rpe':rpe,'pain':pain,'notes':notes,'volume':vol}])
                st.success(f"Saved set {set_number} for {row.exercise}. Start your rest timer.")

            st.markdown('<div class="smart-timer"><div class="smart-timer-number">60</div><div class="smart-timer-label">SECONDS REST</div></div>', unsafe_allow_html=True)
            rest_cols = st.columns(3)
            rest_cols[0].button("Start 60s", use_container_width=True, key="smart_60")
            rest_cols[1].button("Start 90s", use_container_width=True, key="smart_90")
            rest_cols[2].button("Reset", use_container_width=True, key="smart_reset")

        nav1, nav2, nav3 = st.columns(3)
        with nav1:
            if st.button("← Previous Exercise", use_container_width=True, disabled=st.session_state.smart_idx <= 0):
                st.session_state.smart_idx -= 1
                st.rerun()
        with nav2:
            st.download_button("Export Workout Log", LOG.read_bytes(), file_name="workout_log.csv", use_container_width=True)
        with nav3:
            if st.button("Next Exercise →", use_container_width=True, disabled=st.session_state.smart_idx >= len(active)-1):
                st.session_state.smart_idx += 1
                st.rerun()

        st.markdown("## Today’s Exercise List")
        for idx, ex in active.iterrows():
            status = "✅" if idx < st.session_state.smart_idx else ("▶️" if idx == st.session_state.smart_idx else "○")
            st.markdown(f'<div class="smart-card" style="padding:14px 18px;margin:8px 0;"><b>{status} {idx+1}. {ex.exercise}</b> <span class="smart-muted">• {ex.target_sets} × {ex.target_reps} • {ex.muscle_group}</span></div>', unsafe_allow_html=True)




elif page == "Gym Mode":
    day = st.selectbox("Workout Day", days, index=date.today().weekday() if date.today().weekday()<7 else 0, key="gym_day")
    active = workouts[workouts.day==day].reset_index(drop=True)
    group = active.muscle_group.iloc[0] if not active.empty else 'Recovery / Rest'
    st.markdown(f'<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">Gym Mode</div><div class="sub">{day} — {group}. One exercise at a time with larger controls.</div></div>', unsafe_allow_html=True)
    if active.empty:
        st.success("Recovery day. Mobility, walking, sauna, swimming, or rest.")
    else:
        idx = st.number_input("Exercise number", min_value=1, max_value=len(active), value=1, step=1) - 1
        row = active.iloc[int(idx)]
        st.markdown(f'<div class="exercise-card"><div class="exercise-head"><div class="num">{idx+1}</div><div><div class="ex-title">{row.exercise}</div><span class="badge">Target: {row.target_sets} × {row.target_reps}</span><span class="badge green">{row.muscle_group}</span></div></div>', unsafe_allow_html=True)
        cimg, ctrack = st.columns([1,1])
        with cimg:
            st.markdown(f'<div class="exercise-photo-wrap">{img_tag(image_path(row))}</div>', unsafe_allow_html=True)
            st.caption(f"Previous/base weight: {row.base_weight} lbs")
        with ctrack:
            st.markdown("### Log Current Set")
            wt = st.number_input("Weight (lbs)", min_value=0.0, value=float(row.base_weight), step=5.0, key="gym_wt")
            reps = st.number_input("Reps", min_value=0, value=12, step=1, key="gym_reps")
            rpe = st.slider("Effort RPE", 0.0, 10.0, 7.0, 0.5, key="gym_rpe")
            pain = st.slider("Pain 0-10", 0, 10, 0, key="gym_pain")
            notes = st.text_input("Quick note", value="", key="gym_notes")
            vol = int(wt*reps)
            st.markdown(f'<div class="metric-card"><div class="metric-label">Set Volume</div><div class="metric-value">{vol:,} lbs</div></div>', unsafe_allow_html=True)
            if st.button("✅ Complete Set", key="gym_complete"):
                save_log([{'date':str(date.today()),'day':day,'exercise':row.exercise,'set_number':1,'weight_lbs':wt,'reps':reps,'rpe':rpe,'pain':pain,'notes':notes,'volume':vol}])
                st.success("Set saved. Start your rest timer.")
            st.markdown("### Rest Timer")
            t = st.selectbox("Timer", [45,60,75,90,120], index=1, key="gym_timer")
            st.info(f"Rest {t} seconds, then move to the next set/exercise.")
        n1,n2=st.columns(2)
        with n1:
            if idx > 0: st.caption(f"Previous: {active.iloc[idx-1].exercise}")
        with n2:
            if idx < len(active)-1: st.caption(f"Next: {active.iloc[idx+1].exercise}")
        st.markdown('</div>', unsafe_allow_html=True)


elif page == "AI Coach":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">AI Coach</div><div class="sub">Rule-based coaching recommendations from your workout, recovery, nutrition, and supplement data. No API key needed.</div></div>', unsafe_allow_html=True)

    log = load_log()
    workouts_df = load_workouts()
    nut = read_csv_safe(NUTRITION, ['date','meal','calories','protein_g','carbs_g','fat_g','water_oz','notes'])
    body = read_csv_safe(BODY, ['date','body_weight_lbs','goal_weight_lbs','waist_in','notes'])
    sup = read_csv_safe(SUPPLEMENTS, ['date','creatine','protein_powder','multivitamin','fish_oil','pre_workout','magnesium','vitamin_d','electrolytes','notes'])

    if log.empty:
        st.info('Save a few workouts first. The AI Coach will start making recommendations after it has workout history.')
    else:
        # Normalize numbers
        coach_log = log.copy()
        for col in ['weight_lbs','reps','rpe','pain','volume']:
            if col in coach_log.columns:
                coach_log[col] = pd.to_numeric(coach_log[col], errors='coerce').fillna(0)
        coach_log['date'] = coach_log['date'].astype(str)

        total_sessions = coach_log['date'].nunique() if 'date' in coach_log.columns else 0
        total_volume = int(coach_log['volume'].sum()) if 'volume' in coach_log.columns else 0
        avg_rpe = float(coach_log['rpe'].mean()) if 'rpe' in coach_log.columns else 0
        avg_pain = float(coach_log['pain'].mean()) if 'pain' in coach_log.columns else 0
        recent_dates = sorted(coach_log['date'].dropna().unique())[-7:]
        recent = coach_log[coach_log['date'].isin(recent_dates)] if recent_dates else coach_log
        recent_volume = int(recent['volume'].sum()) if not recent.empty else 0
        comeback_score = max(0, min(100, int((total_sessions * 6) + (recent_volume / 1200) - (avg_pain * 4) - max(0, avg_rpe - 8) * 5)))

        c1,c2,c3,c4 = st.columns(4)
        c1.markdown(f'<div class="metric-card"><div class="metric-label">Comeback Score</div><div class="metric-value">{comeback_score}/100</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="metric-label">Sessions Logged</div><div class="metric-value">{total_sessions}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="metric-label">Recent Volume</div><div class="metric-value">{recent_volume:,}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-card"><div class="metric-label">Avg Pain</div><div class="metric-value">{avg_pain:.1f}/10</div></div>', unsafe_allow_html=True)

        st.markdown('## Today’s Coach Read')
        if avg_pain >= 4:
            st.markdown('<div class="supp-bright-card supp-workout"><div class="supp-title">⚠️ Knee / Pain Alert</div><div class="supp-meta">Average pain is elevated. Keep weights conservative, avoid lower-body loading, and stop any movement that causes knee pain.</div></div>', unsafe_allow_html=True)
        elif comeback_score >= 75:
            st.markdown('<div class="supp-bright-card supp-recovery"><div class="supp-title">✅ Strong Training Readiness</div><div class="supp-meta">Your recent consistency and pain scores look good. Stay controlled and consider small weight increases only on exercises where you completed all reps.</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="supp-bright-card supp-performance"><div class="supp-title">📈 Build Momentum</div><div class="supp-meta">Focus on completing target reps, clean form, and consistent logging. The coach will get smarter as your history grows.</div></div>', unsafe_allow_html=True)

        st.markdown('## Suggested Weight Changes')
        suggestions = []
        for exercise, ex in coach_log.groupby('exercise'):
            ex = ex.sort_values('date')
            latest_date = ex['date'].iloc[-1]
            latest = ex[ex['date'] == latest_date]
            best_w = float(ex['weight_lbs'].max())
            latest_w = float(latest['weight_lbs'].max())
            avg_reps = float(latest['reps'].mean()) if not latest.empty else 0
            latest_rpe = float(latest['rpe'].mean()) if 'rpe' in latest.columns else 0
            latest_pain = float(latest['pain'].max()) if 'pain' in latest.columns else 0
            # Target lookup
            target_reps = 12
            hit = workouts_df[workouts_df['exercise'].astype(str).str.lower() == str(exercise).lower()]
            if not hit.empty:
                raw = str(hit.iloc[0].get('target_reps','12'))
                import re
                nums = re.findall(r'\d+', raw)
                if nums:
                    target_reps = int(nums[-1])
            if latest_pain >= 4:
                action = 'DECREASE / HOLD'
                next_w = max(0, latest_w - 5)
                reason = 'Pain was elevated. Protect the knee/joints and reduce load if needed.'
            elif avg_reps >= target_reps and latest_rpe <= 8:
                action = 'INCREASE'
                step = 2.5 if any(word in str(exercise).lower() for word in ['cable','curl','raise','wrist']) else 5
                next_w = latest_w + step
                reason = f'You averaged {avg_reps:.1f} reps at RPE {latest_rpe:.1f}. Small increase is reasonable.'
            elif latest_rpe >= 9:
                action = 'HOLD'
                next_w = latest_w
                reason = 'RPE was high. Stay at the same weight until reps feel cleaner.'
            elif avg_reps < max(6, target_reps - 3):
                action = 'DECREASE / BUILD REPS'
                next_w = max(0, latest_w - 5)
                reason = 'Reps were below target. Lower slightly or keep weight and build reps first.'
            else:
                action = 'HOLD'
                next_w = latest_w
                reason = 'Close to target. Repeat this weight and aim for more clean reps.'
            suggestions.append({'exercise':exercise, 'last_weight':latest_w, 'suggested_next_weight':next_w, 'action':action, 'reason':reason, 'best_weight':best_w, 'latest_avg_reps':round(avg_reps,1), 'latest_rpe':round(latest_rpe,1), 'latest_pain':round(latest_pain,1)})
        sug_df = pd.DataFrame(suggestions).sort_values(['action','exercise']) if suggestions else pd.DataFrame()
        if not sug_df.empty:
            st.dataframe(sug_df, use_container_width=True)
            st.download_button('Export AI coach recommendations', sug_df.to_csv(index=False).encode('utf-8'), file_name='ai_coach_recommendations.csv')

        st.markdown('## Muscle Group Balance')
        if 'day' in coach_log.columns:
            # Map each exercise back to muscle group from workout plan
            map_group = workouts_df[['exercise','muscle_group']].drop_duplicates() if not workouts_df.empty else pd.DataFrame(columns=['exercise','muscle_group'])
            mg = coach_log.merge(map_group, on='exercise', how='left')
            mg['muscle_group'] = mg['muscle_group'].fillna('Unmapped')
            group_vol = mg.groupby('muscle_group', as_index=False)['volume'].sum().sort_values('volume', ascending=False)
            if not group_vol.empty:
                st.bar_chart(group_vol.set_index('muscle_group')['volume'])
                top = group_vol.iloc[0]
                low = group_vol.iloc[-1]
                st.markdown(f'<div class="side-card"><div class="side-title">Balance Note</div><div class="small">Highest volume: <b>{top.muscle_group}</b> ({int(top.volume):,} lbs). Lowest mapped volume: <b>{low.muscle_group}</b> ({int(low.volume):,} lbs). Use this to avoid overtraining one area and neglecting another.</div></div>', unsafe_allow_html=True)

        st.markdown('## Nutrition / Recovery Coach')
        today_s = str(date.today())
        if not nut.empty:
            for col in ['calories','protein_g','water_oz']:
                if col in nut.columns:
                    nut[col] = pd.to_numeric(nut[col], errors='coerce').fillna(0)
            nt = nut[nut['date'].astype(str) == today_s]
            protein = int(nt['protein_g'].sum()) if not nt.empty else 0
            water = int(nt['water_oz'].sum()) if not nt.empty else 0
            if protein < 120:
                st.markdown('<div class="supp-bright-card supp-protein"><div class="supp-title">🍗 Protein Reminder</div><div class="supp-meta">Protein is under the suggested daily target. Aim for a protein-focused meal or shake if it fits your plan.</div></div>', unsafe_allow_html=True)
            if water < 80:
                st.markdown('<div class="supp-bright-card supp-hydration"><div class="supp-title">💧 Hydration Reminder</div><div class="supp-meta">Water is below target. Hydration matters especially on sauna, swim, and training days.</div></div>', unsafe_allow_html=True)
        else:
            st.info('Start logging nutrition to unlock protein, water, and recovery recommendations.')

        st.markdown('## Next Workout Advice')
        next_day = st.selectbox('Choose next workout day for advice', days, index=date.today().weekday() if date.today().weekday() < 7 else 0)
        nd = workouts_df[workouts_df['day'] == next_day]
        if nd.empty:
            st.success('Recovery day: swim, bike, sauna, mobility, and keep the knee pain-free.')
        else:
            st.markdown(f'<div class="side-card"><div class="side-title">{next_day} Focus</div><div class="small">Muscle group: <b>{nd.muscle_group.iloc[0]}</b><br>Exercises: <b>{len(nd)}</b><br>Coach goal: use controlled form, stop if pain rises, and only increase weight when target reps were completed.</div></div>', unsafe_allow_html=True)


elif page == "Workout Builder":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">Workout Builder</div><div class="sub">Add exercises to your weekly plan without editing CSV files.</div></div>', unsafe_allow_html=True)
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
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">Weekly Plan</div><div class="sub">Days, muscle groups, and exercise count</div></div>', unsafe_allow_html=True)
    for day in days:
        d=workouts[workouts.day==day]
        group=d.muscle_group.iloc[0] if not d.empty else 'Rest'
        names = ', '.join(d['exercise'].astype(str).head(6).tolist()) if not d.empty else 'Recovery / Rest day'
        if len(d) > 6: names += ', ...'
        st.markdown(f'<div class="side-card"><div class="side-title">{day} — {group}</div><div class="small">{len(d)} exercises</div><div style="margin-top:8px;color:#c8ddff">{names}</div></div>', unsafe_allow_html=True)


elif page == "System Check":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">System Check + Backup</div><div class="sub">Daily-use stability tools: validate workouts, images, files, and backups.</div></div>', unsafe_allow_html=True)
    issues=[]
    st.markdown("## Required Files")
    required_files=[WORKOUTS, LOG, MAP, NUTRITION, BODY, SUPPLEMENTS]
    for f in required_files:
        ok=f.exists()
        st.markdown(f"{'✅' if ok else '❌'} `{f.relative_to(APP_DIR)}`")
        if not ok: issues.append(f"Missing {f.relative_to(APP_DIR)}")
    st.markdown("## Workout Database Validator")
    df=load_workouts()
    if df.empty:
        st.error("No workout exercises found.")
        issues.append("No workout exercises found")
    else:
        # wrong muscle/day checks
        bad_wed=df[(df['day'].astype(str).str.lower()=='wednesday') & (df['exercise'].astype(str).str.lower().str.contains('calf', na=False))]
        if not bad_wed.empty:
            st.error("Standing/calf exercise still found on Wednesday.")
            issues.append("Calf exercise on Wednesday")
        else:
            st.success("Wednesday workout split is clean: no calf exercises found.")
        dup=df[df.duplicated(subset=['day','exercise'], keep=False)]
        if not dup.empty:
            st.warning(f"Duplicate day/exercise rows found: {len(dup)}")
            issues.append("Duplicate exercises")
        else:
            st.success("No duplicate day/exercise rows.")
        st.dataframe(df[['day','muscle_group','exercise','target_sets','target_reps','image_file']], use_container_width=True)
    st.markdown("## Image Validator")
    image_files=list(ASSETS.glob('*.png'))+list(ASSETS.glob('*.jpg'))+list(ASSETS.glob('*.jpeg'))
    st.write(f"Images installed: **{len(image_files)}**")
    missing=[]
    if not df.empty:
        for _,r in df.iterrows():
            img=str(r.get('image_file','')).strip()
            if img and not (ASSETS/img).exists():
                missing.append((r.get('exercise',''), img))
    if missing:
        st.warning(f"Missing mapped images: {len(missing)}")
        st.dataframe(pd.DataFrame(missing, columns=['exercise','image_file']), use_container_width=True)
        issues.append("Missing mapped images")
    else:
        st.success("All mapped workout images found.")
    st.markdown("## Backup / Export")
    bc1,bc2,bc3=st.columns(3)
    if LOG.exists():
        bc1.download_button("Export workout_log.csv", LOG.read_bytes(), file_name="workout_log.csv")
    if WORKOUTS.exists():
        bc2.download_button("Export workouts.csv", WORKOUTS.read_bytes(), file_name="workouts.csv")
    if MAP.exists():
        bc3.download_button("Export exercise_image_map.csv", MAP.read_bytes(), file_name="exercise_image_map.csv")
    if not issues:
        st.success("System status: ready for daily use.")
    else:
        st.error("System status: review issues above before adding more features.")


elif page == "Nutrition":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">Nutrition Engine</div><div class="sub">Track calories, protein, macros, water, and meals.</div></div>', unsafe_allow_html=True)
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
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">Supplement Engine</div><div class="sub">Track supplement consistency, timing, and weekly completion. Not medical advice.</div></div>', unsafe_allow_html=True)
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
        for _, r in plan.iterrows():
            cat = str(r.get('category','General'))
            css_cat = {
                'Performance':'supp-performance', 'Protein':'supp-protein', 'Recovery':'supp-recovery',
                'General':'supp-general', 'Workout':'supp-workout', 'Hydration':'supp-hydration'
            }.get(cat, 'supp-general')
            st.markdown(f'''<div class="supp-bright-card {css_cat}">
                <div class="supp-title">💊 {r.get('supplement','Supplement')}</div>
                <div class="supp-meta">{cat} • {r.get('default_time','Anytime')} • Goal: {r.get('target_days_per_week','')} days/week</div>
                <span class="supp-pill">{r.get('notes','')}</span>
            </div>''', unsafe_allow_html=True)
        with st.expander('View raw supplement plan table'):
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
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">Body Stats</div><div class="sub">Track body weight, goal weight, waist, and notes.</div></div>', unsafe_allow_html=True)
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


elif page == "Progress Analytics":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">Progress Engine</div><div class="sub">Personal records, volume trends, body stats, nutrition, and consistency analytics.</div></div>', unsafe_allow_html=True)
    log = load_log()
    nut = read_csv_safe(NUTRITION, ['date','meal','calories','protein_g','carbs_g','fat_g','water_oz','notes'])
    body = read_csv_safe(BODY, ['date','body_weight_lbs','goal_weight_lbs','waist_in','notes'])
    sup = read_csv_safe(SUPPLEMENTS, ['date','creatine','protein_powder','multivitamin','fish_oil','pre_workout','magnesium','vitamin_d','electrolytes','notes'])

    # Normalize numeric fields safely
    if not log.empty:
        for col in ['weight_lbs','reps','volume','rpe','pain']:
            if col in log.columns:
                log[col] = pd.to_numeric(log[col], errors='coerce').fillna(0)
        log['date'] = log['date'].astype(str)
    if not nut.empty:
        for col in ['calories','protein_g','carbs_g','fat_g','water_oz']:
            if col in nut.columns:
                nut[col] = pd.to_numeric(nut[col], errors='coerce').fillna(0)
        nut['date'] = nut['date'].astype(str)
    if not body.empty:
        for col in ['body_weight_lbs','goal_weight_lbs','waist_in']:
            if col in body.columns:
                body[col] = pd.to_numeric(body[col], errors='coerce')
        body['date'] = body['date'].astype(str)

    total_sessions = log['date'].nunique() if not log.empty and 'date' in log.columns else 0
    total_volume = int(log['volume'].sum()) if not log.empty and 'volume' in log.columns else 0
    avg_rpe = float(log['rpe'].mean()) if not log.empty and 'rpe' in log.columns else 0
    avg_pain = float(log['pain'].mean()) if not log.empty and 'pain' in log.columns else 0
    pr_count = log.groupby('exercise')['weight_lbs'].max().shape[0] if not log.empty and 'exercise' in log.columns else 0
    comeback_score = min(100, int((total_sessions * 5) + (min(total_volume, 50000) / 1000) + (pr_count * 2) - (avg_pain * 3))) if total_sessions else 0

    m1,m2,m3,m4 = st.columns(4)
    m1.markdown(f'<div class="metric-card"><div class="metric-label">Comeback Score</div><div class="metric-value">{comeback_score}/100</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="metric-label">Workout Sessions</div><div class="metric-value">{total_sessions}</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="metric-label">Total Volume</div><div class="metric-value">{total_volume:,} lbs</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div class="metric-label">Avg Knee Pain</div><div class="metric-value">{avg_pain:.1f}/10</div></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(['Strength', 'Body', 'Nutrition', 'Supplements'])
    with tab1:
        if log.empty:
            st.info('No workout history yet. Save workouts to unlock strength analytics.')
        else:
            st.markdown('### Volume by Day')
            daily = log.groupby('date', as_index=False)['volume'].sum().sort_values('date')
            st.line_chart(daily.set_index('date')['volume'])
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('### Personal Records')
                prs = log.groupby('exercise', as_index=False).agg(best_weight=('weight_lbs','max'), best_reps=('reps','max'), total_volume=('volume','sum')).sort_values(['best_weight','total_volume'], ascending=False)
                st.dataframe(prs, use_container_width=True)
            with c2:
                st.markdown('### Top Exercises by Volume')
                top = log.groupby('exercise', as_index=False)['volume'].sum().sort_values('volume', ascending=False).head(15)
                st.bar_chart(top.set_index('exercise')['volume'])
            st.markdown('### Coach Notes')
            st.markdown('<div class="side-card"><div class="side-title">Smart Progress Read</div><div class="small">If you complete all target reps with pain under 3/10 and RPE under 8, increase next week by 5 lb for upper-body machines or 2.5 lb for cable movements.</div></div>', unsafe_allow_html=True)
    with tab2:
        if body.empty:
            st.info('No body stats yet. Use Body Stats page to start tracking weight and waist.')
        else:
            st.markdown('### Body Weight Trend')
            bw = body.dropna(subset=['body_weight_lbs']).sort_values('date')
            if not bw.empty:
                st.line_chart(bw.set_index('date')['body_weight_lbs'])
            st.markdown('### Body Stats Table')
            st.dataframe(body.tail(100), use_container_width=True)
    with tab3:
        if nut.empty:
            st.info('No nutrition entries yet. Use Nutrition page to start tracking calories and protein.')
        else:
            st.markdown('### Daily Nutrition Totals')
            daily_nut = nut.groupby('date', as_index=False).agg(calories=('calories','sum'), protein_g=('protein_g','sum'), water_oz=('water_oz','sum')).sort_values('date')
            c1,c2 = st.columns(2)
            with c1:
                st.line_chart(daily_nut.set_index('date')['protein_g'])
                st.caption('Protein grams per day')
            with c2:
                st.line_chart(daily_nut.set_index('date')['calories'])
                st.caption('Calories per day')
            st.dataframe(daily_nut.tail(30), use_container_width=True)
    with tab4:
        if sup.empty:
            st.info('No supplement entries yet. Use Supplements page to start tracking consistency.')
        else:
            calc=sup.copy()
            fields=['creatine','protein_powder','multivitamin','fish_oil','pre_workout','magnesium','vitamin_d','electrolytes']
            for field in fields:
                if field in calc.columns:
                    calc[field]=calc[field].astype(str).str.lower().isin(['true','1','yes']).astype(int)
            totals=calc[[f for f in fields if f in calc.columns]].sum().sort_values(ascending=False).reset_index()
            totals.columns=['supplement','times_taken']
            st.markdown('### Supplement Consistency')
            st.bar_chart(totals.set_index('supplement')['times_taken'])
            st.dataframe(totals, use_container_width=True)

elif page == "Exercise Library":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">Exercise Image Library</div><div class="sub">Checks assets/exercises and data/exercise_image_map.csv</div></div>', unsafe_allow_html=True)
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
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">Workout History</div><div class="sub">Saved completed sets</div></div>', unsafe_allow_html=True)
    log=load_log()
    if log.empty: st.info('No workouts saved yet.')
    else: st.dataframe(log.tail(200), use_container_width=True)

elif page == "Data Safety":
    st.markdown('<div class="hero"><div class="kicker">Brian Fitness Tracker X</div><div class="title">Data Safety</div><div class="sub">Important files before updates</div></div>', unsafe_allow_html=True)
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
