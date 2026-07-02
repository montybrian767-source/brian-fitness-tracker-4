# Brian Fitness Tracker 2.2 — Nutrition Engine

Adds a nutrition system on top of 2.1 Workout Engine.

## New in 2.2
- Nutrition Tracker page
- Calories, protein, carbs, fat, water tracking
- Body Stats page
- Supplement checklist page
- Dashboard nutrition totals
- Export buttons for nutrition/body/supplement logs
- Keeps workout engine, images, and `data/workout_log.csv`

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Important data files
- `data/workout_log.csv`
- `data/nutrition_log.csv`
- `data/body_stats.csv`
- `data/supplement_log.csv`
- `data/workouts.csv`
- `data/exercise_image_map.csv`
