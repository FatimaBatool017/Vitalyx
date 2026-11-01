import time
import random
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import streamlit as st

# ---------------------------------------------------------------- setup
st.set_page_config(page_title="VitalCare", page_icon="🩺", layout="wide")
sns.set_theme(style="whitegrid", palette="viridis")
TEAL = "#0E9F8E"

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem;}
    .hero {background: linear-gradient(120deg,#0E9F8E,#2AA7D8); color:white;
           padding:22px 28px; border-radius:16px; margin-bottom:18px;}
    .hero h1 {margin:0; font-size:2rem;} .hero p {margin:4px 0 0 0; opacity:.9;}
    .card {background:white; border-radius:14px; padding:16px 18px;
           box-shadow:0 2px 10px rgba(0,0,0,.06); border-left:5px solid #0E9F8E;}
    .warn {background:#FFF4E5; border-left:5px solid #F59E0B; padding:12px 16px; border-radius:10px;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- data
@st.cache_data
def make_vitals(days: int = 30, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=date.today(), periods=days)
    df = pd.DataFrame(
        {
            "Date": dates,
            "Heart Rate": rng.normal(72, 6, days).round(0),
            "Systolic": rng.normal(120, 8, days).round(0),
            "Diastolic": rng.normal(80, 5, days).round(0),
            "Glucose": rng.normal(95, 10, days).round(0),
            "SpO2": np.clip(rng.normal(97.5, 1, days), 90, 100).round(1),
            "Weight": (72 + np.cumsum(rng.normal(-0.03, 0.2, days))).round(1),
            "Sleep (h)": np.clip(rng.normal(7, 1.1, days), 3, 10).round(1),
            "Water (L)": np.clip(rng.normal(2.2, 0.6, days), 0.3, 4).round(1),
            "Steps": rng.normal(7500, 2500, days).clip(800).round(0),
        }
    )
    df["Mood"] = np.clip((df["Sleep (h)"] - 3) * 0.7 + rng.normal(0, 0.8, days), 1, 5).round(0)
    return df


def init_state():
    if "vitals" not in st.session_state:
        st.session_state.vitals = make_vitals().copy()
    if "meds" not in st.session_state:
        st.session_state.meds = pd.DataFrame(
            {"Medicine": ["Vitamin D", "Metformin", "Omega-3"],
             "Dose": ["1000 IU", "500 mg", "1 capsule"],
             "Time": ["08:00", "13:00", "21:00"],
             "Taken today": [False, False, False]}
        )
    if "appts" not in st.session_state:
        st.session_state.appts = pd.DataFrame(
            {"Doctor": ["Dr. Ayesha Khan"], "Department": ["General Medicine"],
             "Date": [date.today() + timedelta(days=5)], "Time": ["10:30"]}
        )
    if "points" not in st.session_state:
        st.session_state.points = 0
    if "steps_game" not in st.session_state:
        st.session_state.steps_game = 0


init_state()
vit = st.session_state.vitals


def health_score(df: pd.DataFrame) -> int:
    last = df.iloc[-1]
    s = 100
    s -= min(abs(last["Heart Rate"] - 70) * 0.8, 15)
    s -= min(abs(last["Systolic"] - 118) * 0.6, 15)
    s -= min(abs(last["Glucose"] - 90) * 0.4, 15)
    s -= max(0, (97 - last["SpO2"]) * 4)
    s -= max(0, (7 - last["Sleep (h)"]) * 3)
    s -= max(0, (2 - last["Water (L)"]) * 4)
    s += min(last["Steps"] / 10000 * 5, 5)
    return int(np.clip(s, 0, 100))


# ---------------------------------------------------------------- sidebar
st.sidebar.title("🩺 VitalCare")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "❤️ Vitals Tracker", "⚖️ BMI & Body Metrics", "🤒 Symptom Checker",
     "💊 Medications", "📅 Appointments", "😴 Sleep & Hydration", "🧘 Mental Wellness",
     "🎮 Fun Zone"],
)
st.sidebar.markdown("---")
st.sidebar.metric("⭐ Wellness points", st.session_state.points)
st.sidebar.caption("Demo app with simulated data. Not medical advice.")

st.markdown(
    f"""<div class="hero"><h1>Hello, welcome back 👋</h1>
    <p>{datetime.now():%A, %d %B %Y} · Your health, at a glance</p></div>""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- pages
if page.startswith("🏠"):
    last, prev = vit.iloc[-1], vit.iloc[-2]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Health score", f"{health_score(vit)}/100")
    c2.metric("Heart rate", f"{last['Heart Rate']:.0f} bpm", f"{last['Heart Rate']-prev['Heart Rate']:+.0f}")
    c3.metric("Blood pressure", f"{last['Systolic']:.0f}/{last['Diastolic']:.0f}")
    c4.metric("SpO2", f"{last['SpO2']}%")
    c5.metric("Steps", f"{last['Steps']:.0f}")

    left, right = st.columns([2, 1])
    with left:
        fig, ax = plt.subplots(figsize=(8, 3.6))
        sns.lineplot(data=vit, x="Date", y="Heart Rate", marker="o", ax=ax, color=TEAL, label="Heart rate")
        sns.lineplot(data=vit, x="Date", y="Systolic", marker="s", ax=ax, color="#2AA7D8", label="Systolic BP")
        ax.set_title("30-day cardiovascular trend"); ax.set_ylabel("")
        plt.xticks(rotation=30); st.pyplot(fig)
    with right:
        st.markdown("#### Today's goals")
        st.progress(min(last["Steps"] / 10000, 1.0), text=f"Steps {last['Steps']:.0f}/10,000")
        st.progress(min(last["Water (L)"] / 2.5, 1.0), text=f"Water {last['Water (L)']} / 2.5 L")
        st.progress(min(last["Sleep (h)"] / 8, 1.0), text=f"Sleep {last['Sleep (h)']} / 8 h")
        taken = int(st.session_state.meds["Taken today"].sum())
        st.progress(taken / len(st.session_state.meds), text=f"Medicines {taken}/{len(st.session_state.meds)}")
    st.info("💡 " + random.choice([
        "A 10-minute walk after meals helps keep blood sugar steady.",
        "Aim for a consistent bedtime, even on weekends.",
        "Sip water through the day instead of all at once.",
        "Stand up and stretch every hour if you sit for work.",
    ]))

elif page.startswith("❤️"):
    st.subheader("Vitals Tracker")
    with st.expander("➕ Log today's reading", expanded=False):
        with st.form("vitals_form"):
            a, b, c = st.columns(3)
            hr = a.number_input("Heart rate (bpm)", 30, 220, 72)
            sy = b.number_input("Systolic BP", 70, 220, 120)
            di = c.number_input("Diastolic BP", 40, 140, 80)
            gl = a.number_input("Glucose (mg/dL)", 40, 400, 95)
            sp = b.number_input("SpO2 (%)", 70.0, 100.0, 98.0)
            wt = c.number_input("Weight (kg)", 20.0, 250.0, float(vit["Weight"].iloc[-1]))
            if st.form_submit_button("Save reading"):
                row = vit.iloc[-1].copy()
                row["Date"] = pd.Timestamp(date.today()) + pd.Timedelta(days=1)
                row[["Heart Rate", "Systolic", "Diastolic", "Glucose", "SpO2", "Weight"]] = [hr, sy, di, gl, sp, wt]
                st.session_state.vitals = pd.concat([vit, row.to_frame().T], ignore_index=True)
                st.session_state.vitals = st.session_state.vitals.astype({"Date": "datetime64[ns]"})
                st.session_state.points += 10
                st.success("Saved! +10 wellness points"); st.rerun()

    metric = st.selectbox("Metric", ["Heart Rate", "Systolic", "Diastolic", "Glucose", "SpO2", "Weight"])
    y = vit[metric].astype(float).values
    x = np.arange(len(y))
    slope, intercept, r, p, _ = stats.linregress(x, y)
    z = stats.zscore(y)
    vit_plot = vit.assign(Anomaly=np.abs(z) > 2)

    fig, ax = plt.subplots(figsize=(9, 4))
    sns.lineplot(x=vit_plot["Date"], y=y, ax=ax, color=TEAL, marker="o")
    ax.plot(vit_plot["Date"], intercept + slope * x, "--", color="gray", label="Trend")
    ax.scatter(vit_plot.loc[vit_plot.Anomaly, "Date"], y[vit_plot.Anomaly.values], color="red", s=90, zorder=5, label="Unusual")
    ax.set_title(f"{metric} over time"); ax.legend(); plt.xticks(rotation=30)
    st.pyplot(fig)

    c1, c2, c3 = st.columns(3)
    c1.metric("Average", f"{y.mean():.1f}")
    c2.metric("Trend per day", f"{slope:+.3f}", "significant" if p < 0.05 else "not significant")
    c3.metric("Unusual readings", int(vit_plot.Anomaly.sum()))

    st.markdown("#### Correlation between vitals")
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    sns.heatmap(vit[["Heart Rate", "Systolic", "Glucose", "SpO2", "Sleep (h)", "Steps"]].astype(float).corr(),
                annot=True, cmap="crest", fmt=".2f", ax=ax2)
    st.pyplot(fig2)

    sys_, dia_ = vit["Systolic"].iloc[-1], vit["Diastolic"].iloc[-1]
    if sys_ >= 140 or dia_ >= 90:
        st.error("Latest BP is in the high range. Consider consulting a doctor.")
    elif sys_ >= 130 or dia_ >= 80:
        st.warning("Latest BP is slightly elevated.")
    else:
        st.success("Latest BP is in a healthy range.")

elif page.startswith("⚖️"):
    st.subheader("BMI & Body Metrics")
    c1, c2, c3, c4 = st.columns(4)
    sex = c1.selectbox("Sex", ["Female", "Male"])
    age = c2.number_input("Age", 5, 100, 28)
    h = c3.number_input("Height (cm)", 100.0, 220.0, 170.0)
    w = c4.number_input("Weight (kg)", 20.0, 250.0, 70.0)
    act = st.select_slider("Activity level", ["Sedentary", "Light", "Moderate", "Active", "Very active"], "Moderate")
    mult = {"Sedentary": 1.2, "Light": 1.375, "Moderate": 1.55, "Active": 1.725, "Very active": 1.9}[act]

    bmi = w / (h / 100) ** 2
    bmr = 10 * w + 6.25 * h - 5 * age + (5 if sex == "Male" else -161)
    lo, hi = 18.5 * (h / 100) ** 2, 24.9 * (h / 100) ** 2
    cat = "Underweight" if bmi < 18.5 else "Healthy" if bmi < 25 else "Overweight" if bmi < 30 else "Obese range"
    a, b, c, d = st.columns(4)
    a.metric("BMI", f"{bmi:.1f}", cat)
    b.metric("BMR", f"{bmr:.0f} kcal")
    c.metric("Daily calories", f"{bmr*mult:.0f} kcal")
    d.metric("Healthy weight", f"{lo:.0f}-{hi:.0f} kg")

    fig, ax = plt.subplots(figsize=(8, 1.6))
    for (s, e), col in zip([(10, 18.5), (18.5, 25), (25, 30), (30, 40)], ["#60A5FA", "#34D399", "#FBBF24", "#F87171"]):
        ax.barh(0, e - s, left=s, color=col)
    ax.axvline(np.clip(bmi, 10, 40), color="black", lw=3)
    ax.set_yticks([]); ax.set_xlabel("BMI scale"); st.pyplot(fig)
    st.caption("BMI is a screening tool and does not account for muscle mass or body composition.")

elif page.startswith("🤒"):
    st.subheader("Symptom Checker")
    st.markdown('<div class="warn">This gives general guidance only and is <b>not</b> a diagnosis.</div>', unsafe_allow_html=True)
    rules = {
        "Fever": ["Common cold / flu", "Viral infection"],
        "Cough": ["Common cold", "Allergies", "Respiratory infection"],
        "Headache": ["Tension headache", "Dehydration", "Migraine"],
        "Sore throat": ["Common cold", "Strep throat"],
        "Fatigue": ["Poor sleep", "Anemia", "Stress"],
        "Nausea": ["Food-related upset", "Stomach bug"],
        "Shortness of breath": ["Asthma", "Respiratory infection"],
        "Chest pain": ["Muscle strain", "Heart-related issue"],
    }
    chosen = st.multiselect("Select your symptoms", list(rules))
    days = st.slider("How many days?", 1, 14, 2)
    if chosen:
        if {"Chest pain", "Shortness of breath"} & set(chosen):
            st.error("🚨 These can be serious. Seek urgent medical care or call emergency services.")
        counts = pd.Series([c for s in chosen for c in rules[s]]).value_counts()
        st.markdown("#### Possible general causes (most overlap first)")
        st.dataframe(counts.rename("Matching symptoms"))
        st.markdown("**Self-care:** rest, fluids, and monitor symptoms."
                    + (" Symptoms lasting more than a week should be checked by a doctor." if days > 7 else ""))

elif page.startswith("💊"):
    st.subheader("Medication Schedule")
    meds = st.session_state.meds
    for i, row in meds.iterrows():
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.markdown(f"**{row['Medicine']}** · {row['Dose']}")
        c2.write(f"⏰ {row['Time']}")
        new = c3.checkbox("Taken", value=row["Taken today"], key=f"med{i}")
        if new and not row["Taken today"]:
            st.session_state.points += 5
        meds.at[i, "Taken today"] = new
    with st.expander("➕ Add medicine"):
        with st.form("med_form"):
            n = st.text_input("Name"); d = st.text_input("Dose"); t = st.time_input("Time")
            if st.form_submit_button("Add") and n:
                st.session_state.meds = pd.concat(
                    [meds, pd.DataFrame([{"Medicine": n, "Dose": d, "Time": t.strftime("%H:%M"), "Taken today": False}])],
                    ignore_index=True)
                st.rerun()
    rng = np.random.default_rng(3)
    adh = pd.DataFrame({"Day": pd.date_range(end=date.today(), periods=14).strftime("%d %b"),
                        "Adherence %": rng.integers(60, 101, 14)})
    fig, ax = plt.subplots(figsize=(9, 3.2))
    sns.barplot(data=adh, x="Day", y="Adherence %", ax=ax, color=TEAL)
    ax.axhline(80, ls="--", color="gray"); plt.xticks(rotation=45); ax.set_title("14-day adherence")
    st.pyplot(fig)

elif page.startswith("📅"):
    st.subheader("Appointments")
    with st.form("appt"):
        c1, c2 = st.columns(2)
        doc = c1.selectbox("Doctor", ["Dr. Ayesha Khan", "Dr. Omar Siddiqui", "Dr. Sara Malik", "Dr. Bilal Ahmed"])
        dep = c2.selectbox("Department", ["General Medicine", "Cardiology", "Dermatology", "Pediatrics", "Dental"])
        d = c1.date_input("Date", date.today() + timedelta(days=1), min_value=date.today())
        t = c2.selectbox("Time slot", ["09:00", "10:30", "12:00", "14:00", "16:30"])
        if st.form_submit_button("Book appointment"):
            st.session_state.appts = pd.concat(
                [st.session_state.appts, pd.DataFrame([{"Doctor": doc, "Department": dep, "Date": d, "Time": t}])],
                ignore_index=True)
            st.session_state.points += 5
            st.success("Appointment booked!")
    st.dataframe(st.session_state.appts.sort_values("Date"), use_container_width=True)

elif page.startswith("😴"):
    st.subheader("Sleep & Hydration")
    r, p = stats.pearsonr(vit["Sleep (h)"].astype(float), vit["Mood"].astype(float))
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg sleep", f"{vit['Sleep (h)'].mean():.1f} h")
    c2.metric("Avg water", f"{vit['Water (L)'].mean():.1f} L")
    c3.metric("Sleep ↔ mood correlation", f"{r:.2f}", f"p={p:.3f}")
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    sns.histplot(vit["Sleep (h)"], kde=True, ax=axes[0], color="#6366F1"); axes[0].set_title("Sleep distribution")
    sns.regplot(data=vit, x="Sleep (h)", y="Mood", ax=axes[1], color=TEAL); axes[1].set_title("Better sleep, better mood?")
    st.pyplot(fig)
    fig2, ax2 = plt.subplots(figsize=(9, 3))
    sns.barplot(data=vit.tail(14), x=vit.tail(14)["Date"].dt.strftime("%d %b"), y="Water (L)", ax=ax2, color="#2AA7D8")
    ax2.axhline(2.5, ls="--", color="gray"); plt.xticks(rotation=45); ax2.set_title("Water intake, last 14 days")
    st.pyplot(fig2)

elif page.startswith("🧘"):
    st.subheader("Mental Wellness")
    mood = st.select_slider("How are you feeling right now?", [1, 2, 3, 4, 5], 3,
                            format_func=lambda x: ["😞", "😕", "😐", "🙂", "😄"][x - 1])
    note = st.text_area("Journal (optional)")
    if st.button("Save mood"):
        st.session_state.points += 5
        st.success("Mood saved. Taking time to check in matters.")
    wk = vit.tail(28).copy()
    wk["Week"] = np.arange(len(wk)) // 7 + 1
    wk["Day"] = wk["Date"].dt.day_name().str[:3]
    pivot = wk.pivot_table(index="Week", columns="Day", values="Mood")
    order = [d for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] if d in pivot.columns]
    fig, ax = plt.subplots(figsize=(8, 3))
    sns.heatmap(pivot[order], annot=True, cmap="YlGnBu", ax=ax, cbar_kws={"label": "Mood (1-5)"})
    ax.set_title("Mood heatmap (last 4 weeks)"); st.pyplot(fig)
    st.caption("If you feel persistently low or overwhelmed, please talk to someone you trust or a mental health professional.")

elif page.startswith("🎮"):
    st.subheader("Fun Zone 🎉")
    t1, t2, t3, t4 = st.tabs(["🌬️ Breathing", "🧠 Health Quiz", "🎲 Step Challenge", "💧 Catch the Drops"])

    with t1:
        st.write("Box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s.")
        rounds = st.slider("Rounds", 1, 4, 2)
        if st.button("Start session"):
            box = st.empty(); bar = st.progress(0)
            for _ in range(rounds):
                for phase, emoji in [("Inhale", "🌬️"), ("Hold", "⏸️"), ("Exhale", "😮‍💨"), ("Hold", "⏸️")]:
                    for s in range(4, 0, -1):
                        box.markdown(f"## {emoji} {phase}… {s}")
                        time.sleep(1)
            box.markdown("## ✅ Well done!"); bar.progress(100)
            st.session_state.points += 15; st.balloons()

    with t2:
        quiz = [
            ("How many hours of sleep do most adults need?", ["4-5", "7-9", "10-12"], "7-9"),
            ("Which vitamin do we get from sunlight?", ["Vitamin C", "Vitamin D", "Vitamin K"], "Vitamin D"),
            ("A normal resting heart rate for adults is about…", ["60-100 bpm", "120-160 bpm", "30-40 bpm"], "60-100 bpm"),
            ("Which is best for hydration?", ["Water", "Soda", "Energy drinks"], "Water"),
            ("How much moderate exercise per week is commonly recommended?", ["30 min", "150 min", "600 min"], "150 min"),
        ]
        score = 0
        with st.form("quiz"):
            answers = [st.radio(q, o, index=None, key=f"q{i}") for i, (q, o, _) in enumerate(quiz)]
            if st.form_submit_button("Submit"):
                score = sum(a == c for a, (_, _, c) in zip(answers, quiz))
                st.success(f"You scored {score}/{len(quiz)}")
                st.session_state.points += score * 4
                if score == len(quiz): st.balloons()

    with t3:
        st.write("Roll the dice to walk your virtual avatar to 10,000 steps!")
        if st.button("🎲 Roll"):
            roll = random.randint(1, 6)
            st.session_state.steps_game += roll * 400
            st.write(f"You rolled a **{roll}** → +{roll*400} steps")
        st.progress(min(st.session_state.steps_game / 10000, 1.0), text=f"{st.session_state.steps_game}/10000")
        if st.session_state.steps_game >= 10000:
            st.success("Goal reached! +25 points 🏆"); st.balloons()
            st.session_state.points += 25; st.session_state.steps_game = 0

    with t4:
        st.write("Click the 💧 buttons as fast as you can. Each tap is a glass of water towards your goal.")
        if "drops" not in st.session_state: st.session_state.drops = 0
        cols = st.columns(5)
        pos = random.randint(0, 4)
        for i, c in enumerate(cols):
            if i == pos:
                if c.button("💧", key=f"drop{random.random()}"):
                    st.session_state.drops += 1
            else:
                c.write("")
        st.metric("Drops caught", st.session_state.drops)
        if st.session_state.drops >= 8:
            st.success("Hydrated! +10 points"); st.session_state.points += 10; st.session_state.drops = 0
