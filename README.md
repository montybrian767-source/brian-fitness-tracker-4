# Brian Fitness Tracker 2.4 — Progress Engine

This build keeps the 2.3 nutrition/supplement system and adds a new **Progress Analytics** page.

## Added in 2.4
- Comeback Score
- Personal Records table
- Total volume analytics
- Volume by day chart
- Top exercises by volume
- Body weight trend
- Nutrition progress charts
- Supplement consistency chart
- Coach progress notes

## Important data files
Do not delete these if you want to keep your history:

- `data/workout_log.csv`
- `data/nutrition_log.csv`
- `data/body_stats.csv`
- `data/supplement_log.csv`
- `data/workouts.csv`
- `assets/exercises/`

## Run locally
Double-click `run_app.bat`, or run:

```bash
python -m streamlit run app.py
```

## Streamlit Cloud
Upload all files and folders to GitHub, then reboot/redeploy your Streamlit app.
