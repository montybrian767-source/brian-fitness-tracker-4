# Brian Fitness Tracker 2.3 — Supplement Engine

This build extends 2.2 with a more complete supplement tracking system.

## Added in 2.3
- Supplement Engine page
- Daily supplement checklist
- Magnesium, Vitamin D, and electrolytes added
- Supplement plan database: `data/supplement_plan.csv`
- Weekly consistency summary
- Export for supplement log and supplement plan
- Keeps nutrition, body stats, workout history, exercise images, and workout builder

## Important Data Files
- `data/workout_log.csv` — completed workouts
- `data/nutrition_log.csv` — nutrition entries
- `data/body_stats.csv` — body stats
- `data/supplement_log.csv` — supplement history
- `data/supplement_plan.csv` — supplement plan

## Run locally
```bash
python -m streamlit run app.py
```
