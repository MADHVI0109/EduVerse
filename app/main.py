from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, recommendation, seed_data
from .database import engine, get_db, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="EduVerse API")

# Wide-open CORS for the hackathon prototype — restrict this before any
# real deployment beyond the demo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    db = next(get_db())
    seed_data.seed_if_empty(db)


@app.post("/students", response_model=schemas.StudentOut)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get("/students/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.post("/topics/start")
def start_topic(req: schemas.TopicStartRequest, db: Session = Depends(get_db)):
    """
    Branch point from the pitch: 'never studied' skips the quiz entirely and
    goes straight to beginner content. 'studied before' returns quiz
    questions for the diagnostic assessment.
    """
    student = db.query(models.Student).get(req.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if req.prior_knowledge == "never_studied":
        candidates = (
            db.query(models.Content)
            .filter(models.Content.topic == req.topic, models.Content.difficulty == "beginner")
            .all()
        )
        results = recommendation.score_content(
            candidates, weak_subtopics=[],
            format_preference=student.format_preference,
            difficulty_preference="beginner",
        )
        return {
            "path": "beginner_no_quiz",
            "recommendations": [
                schemas.RecommendationOut(
                    content_id=r["content"].id, title=r["content"].title,
                    content_type=r["content"].content_type, url=r["content"].url,
                    source=r["content"].source, duration_minutes=r["content"].duration_minutes,
                    difficulty=r["content"].difficulty, reason=r["reason"],
                ) for r in results
            ],
        }

    elif req.prior_knowledge == "studied_before":
        questions = db.query(models.QuizQuestion).filter(models.QuizQuestion.topic == req.topic).all()
        if not questions:
            raise HTTPException(status_code=404, detail=f"No quiz questions found for topic '{req.topic}'")
        return {
            "path": "diagnostic_quiz",
            "disclaimer": (
                "Answer as honestly as you can, even if you're unsure or want to guess. "
                "There's no right or wrong answer here, and this isn't graded — your "
                "responses just help us understand exactly where you need support."
            ),
            "questions": [schemas.QuizQuestionOut.model_validate(q) for q in questions],
        }

    raise HTTPException(status_code=400, detail="prior_knowledge must be 'never_studied' or 'studied_before'")


@app.post("/quiz/submit", response_model=schemas.QuizSubmitResponse)
def submit_quiz(req: schemas.QuizSubmitRequest, db: Session = Depends(get_db)):
    student = db.query(models.Student).get(req.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    questions = db.query(models.QuizQuestion).filter(models.QuizQuestion.topic == req.topic).all()
    questions_by_id = {q.id: q for q in questions}

    saved_responses = []
    for r in req.responses:
        q = questions_by_id.get(r.question_id)
        if not q:
            continue
        is_correct = r.final_option_index == q.correct_option_index
        switched = r.initial_option_index is not None and r.initial_option_index != r.final_option_index
        flag = recommendation.confidence_flag(
            time_taken=r.time_taken_seconds,
            expected_time=q.expected_time_seconds,
            switched=switched,
            is_correct=is_correct,
        )
        db_response = models.QuizResponse(
            student_id=req.student_id, question_id=r.question_id, topic=req.topic,
            initial_option_index=r.initial_option_index, final_option_index=r.final_option_index,
            time_taken_seconds=r.time_taken_seconds, switched_answer=switched,
            is_correct=is_correct, confidence_flag=flag,
        )
        db.add(db_response)
        saved_responses.append(db_response)
    db.commit()

    weak_subtopics = recommendation.compute_weak_subtopics(saved_responses, questions_by_id)

    candidates = db.query(models.Content).filter(models.Content.topic == req.topic).all()
    results = recommendation.score_content(
        candidates, weak_subtopics=weak_subtopics,
        format_preference=student.format_preference,
        difficulty_preference=student.difficulty_preference,
    )

    return schemas.QuizSubmitResponse(
        weak_subtopics=weak_subtopics,
        recommendations=[
            schemas.RecommendationOut(
                content_id=r["content"].id, title=r["content"].title,
                content_type=r["content"].content_type, url=r["content"].url,
                source=r["content"].source, duration_minutes=r["content"].duration_minutes,
                difficulty=r["content"].difficulty, reason=r["reason"],
            ) for r in results
        ],
    )


@app.post("/feedback")
def submit_feedback(req: schemas.FeedbackIn, db: Session = Depends(get_db)):
    db.add(models.Feedback(**req.model_dump()))
    db.commit()
    return {"status": "recorded"}


@app.get("/topics")
def list_topics(db: Session = Depends(get_db)):
    topics = db.query(models.Content.topic).distinct().all()
    return {"topics": [t[0] for t in topics]}
