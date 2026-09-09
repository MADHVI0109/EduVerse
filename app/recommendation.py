"""
Core scoring logic for EduVerse.

Two responsibilities:
1. confidence_flag() — turns raw quiz behavior (time taken, whether the
   student switched their answer, correctness) into a confidence label.
   This is the "response-time / answer-switching" signal from the pitch,
   not just correctness.
2. score_content() — content-based ranking of candidate resources against
   a student's weak subtopics + format/difficulty preference. Deliberately
   simple (weighted feature matching via scikit-learn's cosine similarity)
   so it works with zero historical student data — see the cold-start
   design decision from the research phase.
"""
from typing import List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

from . import models


def confidence_flag(time_taken: float, expected_time: float, switched: bool, is_correct: bool) -> str:
    """
    Classify a single quiz response's confidence level.

    - "guess": answered far faster than the question's expected time.
      A fast WRONG answer suggests a real gap. A fast CORRECT answer is
      still treated cautiously — could be a lucky guess, not mastery.
    - "shaky": switched the answer before submitting, or took noticeably
      longer than expected — suggests real but incomplete knowledge.
    - "confident": answered correctly, in a reasonable time, without
      switching.
    """
    fast_threshold = expected_time * 0.4  # answered in <40% of expected time
    slow_threshold = expected_time * 1.6  # answered in >160% of expected time

    if time_taken <= fast_threshold:
        return "guess"
    if switched or time_taken >= slow_threshold:
        return "shaky"
    if is_correct:
        return "confident"
    return "shaky"


def compute_weak_subtopics(responses: List[models.QuizResponse], questions_by_id: Dict[int, models.QuizQuestion]) -> List[str]:
    """
    Aggregate per-subtopic performance, weighted by confidence — a subtopic
    only counts as "known" if the student was actually confident about it,
    not just technically correct (e.g. a "guess" that happened to be right
    doesn't count as mastery).
    """
    subtopic_scores: Dict[str, List[float]] = {}

    weight_by_flag = {"confident": 1.0, "shaky": 0.5, "guess": 0.1}

    for r in responses:
        q = questions_by_id[r.question_id]
        weight = weight_by_flag[r.confidence_flag]
        score = weight if r.is_correct else 0.0
        subtopic_scores.setdefault(q.subtopic, []).append(score)

    weak = [
        subtopic
        for subtopic, scores in subtopic_scores.items()
        if (sum(scores) / len(scores)) < 0.6  # threshold: below 60% confident-correct = weak
    ]
    return weak


def score_content(
    candidates: List[models.Content],
    weak_subtopics: List[str],
    format_preference: str,
    difficulty_preference: str,
    top_n: int = 5,
) -> List[dict]:
    """
    Rank candidate content for a student. Uses simple, explainable weighted
    scoring rather than a black-box model — every point added to a score
    has a plain-language reason, which feeds directly into the
    "Recommended because..." UI line.
    """
    if not candidates:
        return []

    # Vectorize subtopics with a bag-of-words style match so partial /
    # multi-word subtopic overlaps still register as similarity, not just
    # exact string equality.
    all_subtopics = list({c.subtopic for c in candidates} | set(weak_subtopics))
    vectorizer = CountVectorizer().fit(all_subtopics) if all_subtopics else None

    scored = []
    for c in candidates:
        reasons = []
        score = 0.0

        # 1. Subtopic relevance to a detected weak area
        if weak_subtopics:
            if vectorizer is not None:
                content_vec = vectorizer.transform([c.subtopic])
                weak_vecs = vectorizer.transform(weak_subtopics)
                similarity = float(np.max(cosine_similarity(content_vec, weak_vecs)))
            else:
                similarity = 1.0 if c.subtopic in weak_subtopics else 0.0
            if similarity > 0.3:
                score += 3.0 * similarity
                reasons.append(f"matches your gap in {c.subtopic}")
        else:
            # No weak subtopics detected (e.g. beginner / never-studied path)
            # — treat all foundational content as equally relevant.
            score += 1.0

        # 2. Format preference match
        if c.content_type == format_preference:
            score += 1.5
            reasons.append(f"matches your {format_preference.replace('_', ' ')} preference")

        # 3. Difficulty match
        if c.difficulty == difficulty_preference:
            score += 1.0
            reasons.append("matches your current level")

        # 4. General content quality signal
        score += c.engagement_score * 0.5

        reason_text = ", ".join(reasons) if reasons else "matches this topic"
        scored.append({"content": c, "score": score, "reason": f"Recommended because: {reason_text}"})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
