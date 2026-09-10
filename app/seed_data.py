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
    # --- Thermodynamics --- (all URLs below are real, verified working pages)
    dict(title="18.1 The Laws of Thermodynamics", content_type="video",
         url="https://www.youtube.com/watch?v=mNnmcXUJQGE", topic="Thermodynamics",
         subtopic="Laws of Thermodynamics", difficulty="beginner",
         source="Chad's Prep", duration_minutes=18, engagement_score=0.8),
    dict(title="First and Second Laws of Thermodynamics", content_type="video",
         url="https://www.khanacademy.org/science/hs-chemistry/x2613d8165d88df5e:thermochemistry/x2613d8165d88df5e:thermal-energy-and-equilibrium/v/first-and-second-laws-of-thermodynamics",
         topic="Thermodynamics", subtopic="Entropy", difficulty="intermediate",
         source="Khan Academy", duration_minutes=12, engagement_score=0.85),
    dict(title="Thermochemistry — Notes & Reference", content_type="pdf",
         url="https://www.khanacademy.org/science/hs-chemistry/x2613d8165d88df5e:thermochemistry",
         topic="Thermodynamics", subtopic="Laws of Thermodynamics", difficulty="beginner",
         source="Khan Academy", duration_minutes=None, engagement_score=0.7),
    dict(title="Carnot Cycle — Explained with Problems", content_type="question_bank",
         url="https://byjus.com/physics/carnot-cycle/", topic="Thermodynamics",
         subtopic="Carnot Cycle", difficulty="advanced",
         source="BYJU'S", duration_minutes=None, engagement_score=0.65),

    # --- Data Structures --- (all URLs below are real, verified working pages)
    dict(title="Data Structures and Algorithms in Hindi — Linked List", content_type="video",
         url="https://archive.codewithharry.com/videos/data-structures-and-algorithms-in-hindi-13/",
         topic="Data Structures", subtopic="Linked Lists", difficulty="beginner",
         source="CodeWithHarry", duration_minutes=22, engagement_score=0.85),
    dict(title="Abdul Bari — Data Structures & Algorithms (Trees playlist)", content_type="video",
         url="https://www.youtube.com/@abdul_bari/videos", topic="Data Structures",
         subtopic="Trees", difficulty="intermediate",
         source="Abdul Bari", duration_minutes=35, engagement_score=0.9),
    dict(title="Linked List Data Structure — Notes", content_type="pdf",
         url="https://www.geeksforgeeks.org/dsa/linked-list-data-structure/",
         topic="Data Structures", subtopic="Linked Lists", difficulty="beginner",
         source="GeeksforGeeks", duration_minutes=None, engagement_score=0.75),
    dict(title="Tree Traversals — Inorder, Preorder, Postorder", content_type="question_bank",
         url="https://www.geeksforgeeks.org/dsa/tree-traversals-inorder-preorder-and-postorder/",
         topic="Data Structures", subtopic="Trees", difficulty="intermediate",
         source="GeeksforGeeks", duration_minutes=None, engagement_score=0.75),
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
    """
    Content and quiz questions are reference/catalog data, not user data —
    so we fully refresh them on every startup rather than only seeding once.
    This means updating CONTENT or QUIZ_QUESTIONS above and redeploying is
    enough to push new data live, without needing to manually clear the
    database each time.

    Student records, quiz responses, and feedback are untouched — only
    Content and QuizQuestion get reset.
    """
    db.query(models.Content).delete()
    db.query(models.QuizQuestion).delete()
    db.commit()

    for item in CONTENT:
        db.add(models.Content(**item))
    for item in QUIZ_QUESTIONS:
        db.add(models.QuizQuestion(**item))
    db.commit()