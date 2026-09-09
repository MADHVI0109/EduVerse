from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from .database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    college = Column(String, nullable=True)
    course_branch = Column(String, nullable=True)
    year = Column(String, nullable=True)
    # Preferences, stored as simple lists/dicts — fine for prototype scale.
    format_preference = Column(String, default="video")  # video | pdf | question_bank
    difficulty_preference = Column(String, default="beginner")
    learning_goals = Column(JSON, default=list)  # e.g. ["exam_prep", "concept_building"]

    responses = relationship("QuizResponse", back_populates="student")
    feedback = relationship("Feedback", back_populates="student")


class Content(Base):
    """
    A piece of external content (YouTube video / PDF / question bank).
    In Phase 1, this table is populated by seed_data.py with a small curated
    set. Later, this is where content pulled from the YouTube Data API would
    land instead of hand-entered rows.
    """
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # video | pdf | question_bank
    url = Column(String, nullable=False)
    topic = Column(String, nullable=False, index=True)
    subtopic = Column(String, nullable=False)  # what specific gap this addresses
    difficulty = Column(String, nullable=False)  # beginner | intermediate | advanced
    source = Column(String, nullable=True)  # channel name, publisher, etc.
    duration_minutes = Column(Integer, nullable=True)
    engagement_score = Column(Float, default=0.5)  # 0-1, from views/likes/etc.


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False, index=True)
    subtopic = Column(String, nullable=False)
    question_text = Column(String, nullable=False)
    options = Column(JSON, nullable=False)  # ["A text", "B text", "C text", "D text"]
    correct_option_index = Column(Integer, nullable=False)
    difficulty = Column(String, default="intermediate")
    # A rough expected time (seconds) a student who genuinely knows the
    # material would take — used to flag suspiciously fast "guesses".
    expected_time_seconds = Column(Integer, default=20)


class QuizResponse(Base):
    __tablename__ = "quiz_responses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    question_id = Column(Integer, ForeignKey("quiz_questions.id"))
    topic = Column(String, nullable=False)
    initial_option_index = Column(Integer, nullable=True)
    final_option_index = Column(Integer, nullable=False)
    time_taken_seconds = Column(Float, nullable=False)
    switched_answer = Column(Boolean, default=False)
    is_correct = Column(Boolean, nullable=False)
    confidence_flag = Column(String, nullable=False)  # "confident" | "shaky" | "guess"

    student = relationship("Student", back_populates="responses")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    helpful = Column(Boolean, nullable=False)

    student = relationship("Student", back_populates="feedback")
