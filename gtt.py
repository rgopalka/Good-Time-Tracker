import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date


# ---------- Adaptive Aesthetic Styling ----------
st.markdown("""
<style>
/* General layout */
.main {
    padding: 2rem;
}

/* Rounded containers */
div.block-container {
    border-radius: 12px;
}

/* Typography: use system color so it works in light/dark */
h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: inherit !important;
    font-family: "Georgia", serif;
}

/* Expander (adaptive) */
[data-testid="stExpander"] {
    border-radius: 10px;
    margin-top: 0.5rem;
    margin-bottom: 1rem;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

[data-testid="stExpander"] > div:first-child {
    background-color: rgba(255, 255, 255, 0.05);
    padding: 0.75rem 1rem;
    font-weight: 600;
    color: #ffcc00 !important;
}

[data-testid="stExpander"] > div:nth-child(2) {
    background-color: rgba(255, 255, 255, 0.03);
    padding: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Adapt to light theme automatically */
@media (prefers-color-scheme: light) {
    [data-testid="stAppViewContainer"] {
        background-color: #faf9f6;
        color: #222;
    }
    [data-testid="stExpander"] > div:first-child {
        background-color: #f0f0f0;
        color: #cc6600 !important;
    }
    [data-testid="stExpander"] > div:nth-child(2) {
        background-color: #f9f9f9;
        color: #222;
    }
}
</style>
""", unsafe_allow_html=True)


st.set_page_config(page_title="Good Time Tracker 🪷", page_icon="🪷", layout="centered")
st.title("🌿 Good Time Tracker (GTT)")
st.subheader("Rohin Gopalka (+ AI) for DYL F2025")
DATA_FILE = "entries.csv"
TODAY = str(date.today())

# ---------- Load or initialize data ----------
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)

    # If old file has no Date column, add one
    if "Date" not in df.columns:
        df["Date"] = "Before Update"
        df.to_csv(DATA_FILE, index=False)
else:
    df = pd.DataFrame(columns=["Date", "Scale", "Feeling", "Entry"])

# Filter today's data
today_df = df[df["Date"] == TODAY].copy()

# ---------- New Day Button ----------
if st.button("🌞 Start New Day"):
    # Only create a new day if current day already exists
    if TODAY in df["Date"].values:
        st.success(f"New day started! Today is {TODAY}.")
    else:
        st.success(f"Starting your reflection log for {TODAY}.")
    # No need to clear file—entries are stored with Date tags

# ---------- Add New Entry ----------
st.write(f"### Add Reflection for {TODAY}")

scales = ["Engagement", "Energy", "Joy", "Purpose"]
scale = st.selectbox("Choose a scale:", scales)
feeling = st.radio("How did you feel?", ["Good", "Bad"])
entry = st.text_area("Optional reflection:")

if st.button("Add Entry"):
    new_entry = pd.DataFrame(
        [[TODAY, scale, feeling, entry]],
        columns=["Date", "Scale", "Feeling", "Entry"]
    )
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("Entry added! 🌼")
    st.rerun()  # Refresh page to show updates immediately

# ---------- Visualization (soft balance style) ----------
if not today_df.empty:
    st.write(f"### 🌞 Today's Feeling Balance")

    counts = today_df.groupby(["Scale", "Feeling"]).size().unstack(fill_value=0)

    # Soft colors
    good_color = "#b7e4c7"
    bad_color = "#f8d7da"

    for scale in ["Engagement", "Energy", "Joy", "Purpose"]:
        good = counts["Good"][scale] if "Good" in counts.columns and scale in counts.index else 0
        bad = counts["Bad"][scale] if "Bad" in counts.columns and scale in counts.index else 0


        balance = good - bad
        if balance > 0:
            emoji = "🌿"
            message = f"More good {scale.lower()} than bad ({good} good vs {bad} bad)"
            bar = "🟩" * good + " | " + "🟥" * bad
        elif balance < 0:
            emoji = "💨"
            message = f"More bad {scale.lower()} than good ({bad} bad vs {good} good)"
            bar = "🟩" * good + " | " + "🟥" * bad
        else:
            emoji = "⚖️"
            message = f"Balanced {scale.lower()}"
            bar = "🟩" * good + " | " + "🟥" * bad


        st.markdown(f"**{emoji} {scale}:** {message}")
        st.markdown(f"<div style='text-align:center;font-size:1.3rem;'>{bar}</div>", unsafe_allow_html=True)


    st.markdown("---")

# ---------- Review today's reflections ----------
if not today_df.empty:
    with st.expander("🕯 Review today's reflections"):
        st.dataframe(today_df)

        # Optional day summary for today
        counts = today_df.groupby(["Scale", "Feeling"]).size().unstack(fill_value=0)
        for col in ["Good", "Bad"]:
            if col not in counts.columns:
                counts[col] = 0
        st.write("### 💭 Today’s Summary")

        summary = []
        for scale in ["Engagement", "Energy", "Joy", "Purpose"]:
            good = counts.loc[scale, "Good"] if scale in counts.index else 0
            bad = counts.loc[scale, "Bad"] if scale in counts.index else 0
            if good > bad:
                summary.append(f"more *good* {scale.lower()} than bad {scale.lower()}")
            elif bad > good:
                summary.append(f"more *bad* {scale.lower()} than good {scale.lower()}")
            else:
                summary.append(f"balanced {scale.lower()}")
        summary_text = ", ".join(summary[:-1]) + f", and {summary[-1]}."
        st.markdown(f"> So far today, you’ve felt {summary_text}.")

# ---------- Past Days Section ----------
st.write("### 📅 Past Days Archive")

past_dates = sorted(df["Date"].unique(), reverse=True)
past_dates = [d for d in past_dates if d != TODAY]

if len(past_dates) == 0:
    st.info("No past days yet — start logging and come back tomorrow!")
else:
    selected_date = st.selectbox("Select a past day to view:", past_dates)
    selected_df = df[df["Date"] == selected_date]

    if not selected_df.empty:
        counts = selected_df.groupby(["Scale", "Feeling"]).size().unstack(fill_value=0)
        for col in ["Good", "Bad"]:
            if col not in counts.columns:
                counts[col] = 0
        for scale in ["Engagement", "Energy", "Joy", "Purpose"]:
            if scale not in counts.index:
                counts.loc[scale] = {"Good": 0, "Bad": 0}
        counts = counts.loc[["Engagement", "Energy", "Joy", "Purpose"]]

        plt.figure(figsize=(8, 5))
        y = range(len(counts))
        plt.barh(y, -counts["Bad"], color="#ff9999", label="Bad")
        plt.barh(y, counts["Good"], color="#90ee90", label="Good")
        plt.yticks(y, counts.index)
        plt.axvline(0, color="gray", linewidth=1)
        plt.xlabel("Count of Entries (Good vs Bad)")
        plt.title(f"Feeling Balance for {selected_date}")
        plt.legend(loc="upper right")
        limit = max(counts["Good"].max(), counts["Bad"].max()) + 1
        plt.xlim(-limit, limit)
        plt.tight_layout()
        st.pyplot(plt)

            # ---------- Day Summary ----------
    st.write("### 💭 Day Summary")

    summary = []
    for scale in ["Engagement", "Energy", "Joy", "Purpose"]:
        good = counts.loc[scale, "Good"]
        bad = counts.loc[scale, "Bad"]
        if good > bad:
            summary.append(f"more *good* {scale.lower()} than bad {scale.lower()}")
        elif bad > good:
            summary.append(f"more *bad* {scale.lower()} than good {scale.lower()}")
        else:
            summary.append(f"balanced {scale.lower()}")

    summary_text = ", ".join(summary[:-1]) + f", and {summary[-1]}."
    st.markdown(
        f"> On **{selected_date}**, you felt {summary_text.capitalize()}"
    )

# ---------- Reset / Clear All Data ----------
st.markdown("### ⚠️ Reset Tracker")

with st.expander("⚠️ Danger Zone: Reset Tracker"):
    st.warning("This will permanently delete all your past entries and graphs.")
    confirm_reset = st.checkbox("Yes, I understand this will erase all data")

    if st.button("🧹 Clear All Data"):
        if confirm_reset:
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            df = pd.DataFrame(columns=["Date", "Scale", "Feeling", "Entry"])
            st.success("All data cleared! Starting fresh 🌱")
            st.rerun()
        else:
            st.warning("Please check the box to confirm.")
