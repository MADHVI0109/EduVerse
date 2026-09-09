"""
Seed data for the prototype demo. Covers two topics (as agreed — better to
have 2-3 topics working with real-feeling data than many topics with none).

To pull real YouTube data instead of these placeholders, replace the
CONTENT list below with results from the YouTube Data API + your transcript
matching step. Everything downstream (scoring, recommendations) already
works against this same Content shape, so swapping the data source doesn't
require touching recommendation.py.
"""
from sqlalchemy.orm import Session
from . import models

CONTENT = [
    # --- Thermodynamics ---
    dict(title="Laws of Thermodynamics Explained Simply", content_type="video",
         url="https://www.youtube.com/watch?v=example1", topic="Thermodynamics",
         subtopic="Laws of Thermodynamics", difficulty="beginner",
         source="Physics Wallah", duration_minutes=18, engagement_score=0.8),
    dict(title="Entropy and the Second Law — Deep Dive", content_type="video",
         url="https://www.youtube.com/watch?v=example2", topic="Thermodynamics",
         subtopic="Entropy", difficulty="intermediate",
         source="NPTEL", duration_minutes=42, engagement_score=0.7),
    dict(title="Thermodynamics Formula Sheet (PDF)", content_type="pdf",
         url="https://example.com/thermo-formulas.pdf", topic="Thermodynamics",
         subtopic="Laws of Thermodynamics", difficulty="beginner",
         source="MIT OpenCourseWare", duration_minutes=None, engagement_score=0.6),
    dict(title="Carnot Cycle Practice Problems", content_type="question_bank",
         url="https://example.com/carnot-qbank", topic="Thermodynamics",
         subtopic="Carnot Cycle", difficulty="advanced",
         source="GATE Question Bank", duration_minutes=None, engagement_score=0.65),

    # --- Data Structures ---
    dict(title="Arrays and Linked Lists — Visual Guide", content_type="video",
         url="https://www.youtube.com/watch?v=example3", topic="Data Structures",
         subtopic="Linked Lists", difficulty="beginner",
         source="CodeWithHarry", duration_minutes=22, engagement_score=0.85),
    dict(title="Binary Trees Deep Dive", content_type="video",
         url="https://www.youtube.com/watch?v=example4", topic="Data Structures",
         subtopic="Trees", difficulty="intermediate",
         source="Abdul Bari", duration_minutes=35, engagement_score=0.9),
    dict(title="Data Structures Cheat Sheet (PDF)", content_type="pdf",
         url="https://example.com/ds-cheatsheet.pdf", topic="Data Structures",
         subtopic="Linked Lists", difficulty="beginner",
         source="GeeksforGeeks", duration_minutes=None, engagement_score=0.7),
    dict(title="Tree Traversal Practice Set", content_type="question_bank",
         url="https://example.com/tree-qbank", topic="Data Structures",
         subtopic="Trees", difficulty="intermediate",
         source="LeetCode-style Bank", duration_minutes=None, engagement_score=0.75),
]

QUIZ_QUESTIONS = [
    dict(topic="Thermodynamics", subtopic="Laws of Thermodynamics",
         question_text="Which law states that energy cannot be created or destroyed?",
         options=["Zeroth Law", "First Law", "Second Law", "Third Law"],
         correct_option_index=1, difficulty="beginner", expected_time_seconds=15),
    dict(topic="Thermodynamics", subtopic="Entropy",
         question_text="Entropy of an isolated system tends to:",
         options=["Decrease", "Stay constant", "Increase", "Become zero"],
         correct_option_index=2, difficulty="intermediate", expected_time_seconds=20),
    dict(topic="Thermodynamics", subtopic="Carnot Cycle",
         question_text="A Carnot engine's efficiency depends on:",
         options=["Only the working substance", "Only the hot reservoir temperature",
                   "Temperatures of both reservoirs", "The engine's size"],
         correct_option_index=2, difficulty="advanced", expected_time_seconds=25),

    dict(topic="Data Structures", subtopic="Linked Lists",
         question_text="What is the time complexity of inserting at the head of a linked list?",
         options=["O(1)", "O(n)", "O(log n)", "O(n^2)"],
         correct_option_index=0, difficulty="beginner", expected_time_seconds=15),
    dict(topic="Data Structures", subtopic="Trees",
         question_text="In a binary search tree, an in-order traversal visits nodes:",
         options=["Randomly", "In sorted order", "Right-to-left only", "Level by level"],
         correct_option_index=1, difficulty="intermediate", expected_time_seconds=20),
]


def seed_if_empty(db: Session):
    if db.query(models.Content).count() == 0:
        for item in CONTENT:
            db.add(models.Content(**item))
    if db.query(models.QuizQuestion).count() == 0:
        for item in QUIZ_QUESTIONS:
            db.add(models.QuizQuestion(**item))
    db.commit()
