# Vitalyx
# VitalCare – Streamlit Health Companion

A realistic health-care dashboard built with Streamlit, NumPy, Pandas, Matplotlib, Seaborn and SciPy.

## Features
- **Dashboard** – health score, today's vitals, 30-day trends
- **Vitals Tracker** – log heart rate, BP, glucose, SpO2, weight; Seaborn charts, SciPy trend + anomaly (z-score) detection
- **BMI & Body Metrics** – BMI, BMR, daily calories, ideal weight range
- **Symptom Checker** – rule-based guidance (not a diagnosis)
- **Medications** – schedule, adherence tracking and chart
- **Appointments** – book and view visits
- **Sleep & Hydration** – logs, correlation (SciPy Pearson) between sleep and mood
- **Mental Wellness** – mood log and weekly heatmap
- **Fun Zone** – guided breathing, health trivia quiz, step challenge dice game, hydration "catch the drops" tap game, daily health tip

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Push to GitHub, then deploy at share.streamlit.io pointing at `app.py`.

## Disclaimer
Educational demo using simulated data. Not a substitute for professional medical advice, diagnosis or treatment. In an emergency call your local emergency number.
