from __future__ import annotations
import os
from datetime import date, datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).parent
DATA = APP_DIR / 'data'
ASSETS = APP_DIR / 'assets'
EX = ASSETS / 'exercises'
WORKOUTS = DATA / 'workouts.csv'
LOG = DATA / 'workout_log.csv'
NUTRITION = DATA / 'nutrition_log.csv'
SUPPS = DATA / 'supplement_log.csv'
SUPP_PLAN = DATA / 'supplement_plan.csv'
BODY = DATA / 'body_stats.csv'

st.set_page_config(page_title='Brian Fitness Tracker 2.5', page_icon='🏋️', layout='wide', initial_sidebar_state='expanded')

st.markdown('''
<style>
:root{--bg:#07111f;--panel:#0f172a;--panel2:#111827;--card:#111827;--text:#f8fafc;--muted:#94a3b8;--blue:#38bdf8;--green:#22c55e;--orange:#f59e0b;--purple:#a78bfa;--red:#ef4444;--border:#1f2a44;}
html,body,[data-testid="stAppViewContainer"]{background:linear-gradient(135deg,#050b16,#0b1220 55%,#0f172a);color:var(--text)}
.block-container{padding-top:1rem;max-width:1400px}.main-card{background:rgba(15,23,42,.86);border:1px solid var(--border);border-radius:22px;padding:18px;box-shadow:0 20px 45px rgba(0,0,0,.25)}
.hero{background:linear-gradient(135deg,#0f172a,#10233f);border:1px solid #1e3a5f;border-radius:26px;padding:24px;margin-bottom:18px}.hero h1{margin:0;font-size:2rem}.sub{color:var(--muted)}
.metric-card{background:#0f172a;border:1px solid #213452;border-radius:20px;padding:16px}.metric-label{color:#94a3b8;font-size:.86rem;font-weight:800;text-transform:uppercase}.metric-value{font-size:1.7rem;font-weight:950;color:white}.badge{display:inline-block;border-radius:999px;padding:6px 10px;font-weight:900;font-size:.82rem}.blue{background:#083344;color:#67e8f9}.green{background:#052e16;color:#86efac}.orange{background:#451a03;color:#fdba74}.purple{background:#2e1065;color:#d8b4fe}.red{background:#450a0a;color:#fca5a5}
.exercise-card{background:#0f172a;border:1px solid #22324c;border-radius:24px;padding:16px;margin:14px 0;box-shadow:0 14px 30px rgba(0,0,0,.25)}.exercise-title{font-size:1.35rem;font-weight:950}.exercise-img{width:100%;height:230px;object-fit:contain;background:#07111f;border-radius:18px;border:1px solid #1f2a44;padding:10px}.setbox{background:#111827;border:1px solid #253554;border-radius:16px;padding:12px}.big-button button{height:3.5rem!important;border-radius:18px!important;font-weight:950!important;background:linear-gradient(135deg,#2563eb,#38bdf8)!important;color:white!important;border:0!important}.complete button{background:linear-gradient(135deg,#16a34a,#22c55e)!important;color:white!important;border:0!important}.danger button{background:linear-gradient(135deg,#dc2626,#ef4444)!important;color:white!important;border:0!important}
.supp-card{border-radius:20px;padding:18px;margin-bottom:14px;color:white;border:1px solid rgba(255,255,255,.12);box-shadow:0 12px 26px rgba(0,0,0,.25)}.supp-Performance{background:linear-gradient(135deg,#075985,#2563eb)}.supp-Recovery{background:linear-gradient(135deg,#14532d,#16a34a)}.supp-Health{background:linear-gradient(135deg,#581c87,#9333ea)}.supp-Daily{background:linear-gradient(135deg,#7c2d12,#f97316)}
.stTabs [data-baseweb="tab"]{font-weight:900;color:#e2e8f0}.stTabs [aria-selected="true"]{color:#38bdf8!important;border-bottom:3px solid #38bdf8}.stButton>button{border-radius:14px;font-weight:900}.stNumberInput input,.stTextInput input{background:#0b1220;color:#f8fafc;border:1px solid #1f2a44}.stSelectbox div{color:#f8fafc}
@media(max-width:850px){.exercise-img{height:190px}.hero h1{font-size:1.45rem}.block-container{padding-left:.55rem;padding-right:.55rem}}
</style>
''', unsafe_allow_html=True)

def ensure_files():
    DATA.mkdir(exist_ok=True); EX.mkdir(parents=True, exist_ok=True)
    if not LOG.exists(): LOG.write_text('date,day,workout,exercise,set_number,weight_lbs,reps,rpe,pain,notes,volume,saved_at\n')
    if not NUTRITION.exists(): NUTRITION.write_text('date,meal,calories,protein_g,carbs_g,fat_g,water_oz,notes\n')
    if not SUPPS.exists(): SUPPS.write_text('date,supplement,category,taken,notes\n')
    if not BODY.exists(): BODY.write_text('date,body_weight,waist,notes\n')
ensure_files()

def read_csv(path, cols=None):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=cols or [])

def save_append(path, rows):
    df = pd.DataFrame(rows)
    exists = path.exists() and path.stat().st_size > 0
    df.to_csv(path, mode='a', header=not exists, index=False)

def img_path(file):
    p = EX / str(file)
    return p if p.exists() else None

workouts = read_csv(WORKOUTS)
log = read_csv(LOG)
nut = read_csv(NUTRITION)
sup_log = read_csv(SUPPS)

with st.sidebar:
    st.markdown('## ⚡ BrianFit 2.5')
    st.caption('Gym Mode + Professional UI')
    page = st.radio('Navigation', ['Dashboard','Gym Mode','Workout','Weekly Plan','Nutrition','Supplements','Progress','History','Image Test'], label_visibility='collapsed')
    st.markdown('---')
    st.markdown('**Today**')
    st.markdown(f'<span class="badge blue">{date.today().strftime("%A")}</span>', unsafe_allow_html=True)

if workouts.empty:
    st.error('Missing data/workouts.csv. Upload the data folder to GitHub.')
    st.stop()

today_name = date.today().strftime('%A')
if today_name not in set(workouts['day']): today_name='Monday'

if page == 'Dashboard':
    st.markdown('<div class="hero"><h1>🏋️ Brian Fitness Tracker 2.5</h1><div class="sub">Gym Mode, Nutrition, Supplements, and Progress in one professional dashboard.</div></div>', unsafe_allow_html=True)
    sessions = log['date'].nunique() if not log.empty and 'date' in log else 0
    volume = log['volume'].sum() if not log.empty and 'volume' in log else 0
    protein = nut[nut['date'].astype(str)==str(date.today())]['protein_g'].sum() if not nut.empty else 0
    calories = nut[nut['date'].astype(str)==str(date.today())]['calories'].sum() if not nut.empty else 0
    c1,c2,c3,c4 = st.columns(4)
    for c,label,val,cls in [(c1,'Sessions',sessions,'blue'),(c2,'Total Volume',f'{volume:,.0f} lbs','green'),(c3,'Protein Today',f'{protein:.0f}g','purple'),(c4,'Calories Today',f'{calories:.0f}','orange')]:
        c.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)
    st.markdown('### Weekly Plan')
    days = workouts.groupby(['day','muscle_group']).size().reset_index(name='exercises')
    cols = st.columns(7)
    order=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    for i,d in enumerate(order):
        row = days[days['day']==d]
        mg = row['muscle_group'].iloc[0] if not row.empty else 'Recovery'
        n = int(row['exercises'].iloc[0]) if not row.empty else 0
        color='green' if d==today_name else 'blue'
        cols[i].markdown(f'<div class="metric-card"><span class="badge {color}">{d[:3]}</span><br><b>{mg}</b><br><span class="sub">{n} exercises</span></div>', unsafe_allow_html=True)

elif page in ['Workout','Gym Mode']:
    gym = page=='Gym Mode'
    st.markdown(f'<div class="hero"><h1>{"📱 Gym Mode" if gym else "🏋️ Today’s Workout"}</h1><div class="sub">Large controls, rest timer, pain score, and clean save flow.</div></div>', unsafe_allow_html=True)
    day = st.selectbox('Choose workout day', ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], index=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].index(today_name))
    daydf = workouts[workouts['day']==day].reset_index(drop=True)
    if daydf.empty:
        st.info('No workout for this day.')
    else:
        workout_name = daydf['workout'].iloc[0]
        if gym:
            idx = st.number_input('Exercise #', min_value=1, max_value=len(daydf), value=1, step=1) - 1
            daydf = daydf.iloc[[idx]].reset_index(drop=True)
        rows=[]
        for i,r in daydf.iterrows():
            with st.container():
                st.markdown('<div class="exercise-card">', unsafe_allow_html=True)
                col_img, col_main, col_side = st.columns([1.05,1.7,.85])
                p = img_path(r.get('image_file',''))
                with col_img:
                    if p: st.image(str(p), use_container_width=True)
                    else: st.markdown('<div class="exercise-img" style="display:flex;align-items:center;justify-content:center;color:#94a3b8;">Image coming soon</div>', unsafe_allow_html=True)
                with col_main:
                    st.markdown(f'<div class="exercise-title">{r.exercise}</div><span class="badge blue">{r.muscle_group}</span> <span class="badge green">Target {r.target_sets} × {r.target_reps}</span>', unsafe_allow_html=True)
                    note = st.text_input('Notes', key=f'note_{day}_{i}', placeholder='How did it feel?')
                    pain = st.slider('Pain score',0,10,0,key=f'pain_{day}_{i}')
                    sets = int(r.target_sets)
                    for s in range(1, sets+1):
                        st.markdown(f'<div class="setbox"><b>Set {s}</b></div>', unsafe_allow_html=True)
                        a,b,c,d = st.columns([1,1,1,1])
                        w = a.number_input('lbs', min_value=0.0, value=float(r.default_weight), step=2.5, key=f'w_{day}_{i}_{s}')
                        reps = b.number_input('reps', min_value=0, value=0, step=1, key=f'reps_{day}_{i}_{s}')
                        rpe = c.number_input('RPE', min_value=0, max_value=10, value=7, key=f'rpe_{day}_{i}_{s}')
                        complete = d.checkbox('Done', key=f'done_{day}_{i}_{s}')
                        if complete and reps>0:
                            rows.append({'date':str(date.today()),'day':day,'workout':workout_name,'exercise':r.exercise,'set_number':s,'weight_lbs':w,'reps':reps,'rpe':rpe,'pain':pain,'notes':note,'volume':w*reps,'saved_at':datetime.now().isoformat(timespec='seconds')})
                with col_side:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Volume if target met</div><div class="metric-value">{float(r.default_weight)*int(r.target_sets)*12:,.0f}</div><span class="sub">lbs estimate</span></div>', unsafe_allow_html=True)
                    st.markdown('<br>', unsafe_allow_html=True)
                    rest = st.selectbox('Rest Timer', ['60 sec','90 sec','120 sec'], key=f'rest_{day}_{i}')
                    st.markdown(f'<span class="badge orange">⏱ {rest}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="big-button complete">', unsafe_allow_html=True)
        if st.button('✅ Save Completed Sets'):
            if rows:
                save_append(LOG, rows)
                st.success(f'Saved {len(rows)} completed sets.')
                st.balloons()
            else:
                st.warning('Check Done and enter reps for at least one set.')
        st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Weekly Plan':
    st.markdown('<div class="hero"><h1>📅 Weekly Plan</h1><div class="sub">Muscle groups and exercises by day.</div></div>', unsafe_allow_html=True)
    for d,df in workouts.groupby('day', sort=False):
        st.markdown(f'### {d} — {df.muscle_group.iloc[0]}')
        st.dataframe(df[['exercise','target_sets','target_reps','default_weight']], use_container_width=True, hide_index=True)

elif page == 'Nutrition':
    st.markdown('<div class="hero"><h1>🍎 Nutrition Engine</h1><div class="sub">Calories, protein, carbs, fat, water, and daily notes.</div></div>', unsafe_allow_html=True)
    with st.form('nutrition'):
        c1,c2,c3=st.columns(3)
        meal=c1.text_input('Meal', 'Meal')
        cal=c2.number_input('Calories',0,5000,0)
        protein=c3.number_input('Protein g',0,500,0)
        c4,c5,c6=st.columns(3)
        carbs=c4.number_input('Carbs g',0,500,0)
        fat=c5.number_input('Fat g',0,300,0)
        water=c6.number_input('Water oz',0,300,0)
        notes=st.text_input('Notes')
        if st.form_submit_button('Save Nutrition'):
            save_append(NUTRITION,[{'date':str(date.today()),'meal':meal,'calories':cal,'protein_g':protein,'carbs_g':carbs,'fat_g':fat,'water_oz':water,'notes':notes}])
            st.success('Nutrition saved.')
    st.dataframe(read_csv(NUTRITION), use_container_width=True)

elif page == 'Supplements':
    st.markdown('<div class="hero"><h1>💊 Supplement Engine</h1><div class="sub">Bright category cards for easy visibility.</div></div>', unsafe_allow_html=True)
    plan = read_csv(SUPP_PLAN)
    rows=[]
    for _,r in plan.iterrows():
        cls = 'supp-Daily' if 'Daily' in r.category else f'supp-{r.category}'
        st.markdown(f'<div class="supp-card {cls}"><h3>{r.supplement}</h3><b>{r.category}</b> · {r.time}<br>{r.notes}</div>', unsafe_allow_html=True)
        taken = st.checkbox(f'Taken — {r.supplement}', key=f'supp_{r.supplement}')
        note = st.text_input(f'Note — {r.supplement}', key=f'supp_note_{r.supplement}', label_visibility='collapsed')
        if taken: rows.append({'date':str(date.today()),'supplement':r.supplement,'category':r.category,'taken':True,'notes':note})
    if st.button('Save Supplement Check-In'):
        if rows:
            save_append(SUPPS, rows); st.success(f'Saved {len(rows)} supplements.')
        else: st.warning('Check at least one supplement.')
    st.dataframe(read_csv(SUPPS), use_container_width=True)

elif page == 'Progress':
    st.markdown('<div class="hero"><h1>📈 Progress Engine</h1><div class="sub">Volume, PRs, nutrition, and supplement consistency.</div></div>', unsafe_allow_html=True)
    log=read_csv(LOG)
    if log.empty: st.info('No workout history yet.')
    else:
        daily=log.groupby('date',as_index=False)['volume'].sum()
        st.plotly_chart(px.bar(daily,x='date',y='volume',title='Daily Workout Volume'), use_container_width=True)
        prs=log.groupby('exercise',as_index=False)['weight_lbs'].max().sort_values('weight_lbs',ascending=False)
        st.dataframe(prs.rename(columns={'weight_lbs':'personal_record_lbs'}), use_container_width=True, hide_index=True)

elif page == 'History':
    st.markdown('<div class="hero"><h1>📜 History</h1><div class="sub">Your saved workout data.</div></div>', unsafe_allow_html=True)
    df=read_csv(LOG)
    st.dataframe(df, use_container_width=True)
    st.download_button('Download workout_log.csv', df.to_csv(index=False), 'workout_log.csv')

elif page == 'Image Test':
    st.markdown('<div class="hero"><h1>🖼️ Image Test</h1><div class="sub">Verify exercise images in assets/exercises.</div></div>', unsafe_allow_html=True)
    imgs=list(EX.glob('*.*'))
    st.write(f'Image files found: {len(imgs)}')
    cols=st.columns(4)
    for i,p in enumerate(imgs[:40]):
        with cols[i%4]:
            st.image(str(p), use_container_width=True)
            st.caption(p.name)
