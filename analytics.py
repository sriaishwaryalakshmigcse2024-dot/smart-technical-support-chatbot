
import csv
from pathlib import Path

import streamlit as st
import pandas as pd


FEEDBACK_FILE = Path("data") / "feedback.csv"


def load_feedback():
    """Load saved feedback from the CSV file."""

    if not FEEDBACK_FILE.exists():
        return pd.DataFrame(
            columns=["timestamp", "question", "answer", "rating"]
        )

    try:
        return pd.read_csv(FEEDBACK_FILE)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(
            columns=["timestamp", "question", "answer", "rating"]
        )


def show_feedback_dashboard():
    """Display feedback statistics and recent feedback."""

    st.header("📊 Feedback Analytics")

    feedback = load_feedback()

    if feedback.empty or "rating" not in feedback.columns:
        st.info("No feedback has been recorded yet.")
        return

    # Count helpful and unhelpful ratings.
    helpful_count = (
        feedback["rating"].astype(str).str.lower() == "helpful"
    ).sum()

    unhelpful_count = (
        feedback["rating"].astype(str).str.lower() == "not_helpful"
    ).sum()

    total_feedback = len(feedback)

    # Calculate the percentage of helpful ratings.
    satisfaction = (
        helpful_count / total_feedback * 100
        if total_feedback > 0
        else 0
    )

    # Display summary metrics.
    col1, col2, col3 = st.columns(3)

    col1.metric("Total feedback", total_feedback)
    col2.metric("Helpful", int(helpful_count))
    col3.metric("Helpful rate", f"{satisfaction:.1f}%")

    st.subheader("Rating breakdown")

    st.write(f"👍 Helpful: {int(helpful_count)}")
    st.write(f"👎 Not helpful: {int(unhelpful_count)}")

    st.subheader("Recent feedback")

    if "timestamp" in feedback.columns:
        feedback = feedback.sort_values(
            "timestamp", ascending=False
        )

    st.dataframe(
        feedback,
        use_container_width=True,
        hide_index=True,
    )
