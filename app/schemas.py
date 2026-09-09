from pydantic import BaseModel
from typing import List, Optional


class StudentCreate(BaseModel):
    name: str
    email: Optional[str] = None
    college: Optional[str] = None
    course_branch: Optional[str] = None
    year: Optional[str] = None
    format_preference: str = "video"
    difficulty_preference: str = "beginner"
    learning_goals: List[str] = []


class StudentOut(StudentCreate):
    id: int

    class Config:
        from_attributes = True


class TopicStartRequest(BaseModel):
    student_id: int
    topic: str
    prior_knowledge: str  # "never_studied" | "studied_before"


class QuizQuestionOut(BaseModel):
    id: int
    question_text: str
    options: List[str]

    class Config:
        from_attributes = True


class QuizResponseIn(BaseModel):
    question_id: int
    initial_option_index: Optional[int] = None
    final_option_index: int
    time_taken_seconds: float


class QuizSubmitRequest(BaseModel):
    student_id: int
    topic: str
    responses: List[QuizResponseIn]


class RecommendationOut(BaseModel):
    content_id: int
    title: str
    content_type: str
    url: str
    source: Optional[str]
    duration_minutes: Optional[int]
    difficulty: str
    reason: str  # the "Recommended because..." explainability line


class QuizSubmitResponse(BaseModel):
    weak_subtopics: List[str]
    recommendations: List[RecommendationOut]


class FeedbackIn(BaseModel):
    student_id: int
    content_id: int
    helpful: bool
