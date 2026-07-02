# Brian Fitness Tracker 3.2.3 — Workout Database Repair

This build repairs the master workout database and keeps the weekly plan synchronized.

## Fixes
- Removes Standing Calf Raise from Wednesday — Shoulders + Abs
- Adds Plank to Wednesday — Shoulders + Abs
- Keeps calf work on leg / rehab day
- Adds automatic workout database repair on app startup
- Keeps top navigation contrast fix
- Preserves workout logging to data/workout_log.csv

## Important
Upload the complete `data/` folder to GitHub. The app also auto-repairs older `workouts.csv` files if they still contain the Wednesday calf raise mistake.
