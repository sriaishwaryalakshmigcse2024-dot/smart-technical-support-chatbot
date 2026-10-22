
import csv
from pathlib import Path
from datetime import datetime

FEEDBACK_FILE = Path("data") / "feedback.csv"


def save_feedback(question, answer, rating):
    """Save chatbot feedback to a CSV file."""

    FEEDBACK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_exists = FEEDBACK_FILE.exists()

    with FEEDBACK_FILE.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "question",
                "answer",
                "rating",
            ])

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            question,
            answer,
            rating,
        ])
