"""
Pydantic schemas for structured outputs in the grading system.

These schemas force the LLM to return valid JSON that can be parsed
and validated, preventing the "string instead of tool call" problem.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CriterionGrade(BaseModel):
    """Result of grading a single criterion."""
    
    criterion_name: str = Field(description="Name of the criterion being evaluated")
    max_score: int = Field(description="Maximum possible score for this criterion")
    score: float = Field(ge=0, description="Score awarded (0 to max_score)")
    evaluation_notes: str = Field(description="Detailed justification for the score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "criterion_name": "Code Quality",
                "max_score": 30,
                "score": 25,
                "evaluation_notes": "Good naming conventions, follows PEP 8..."
            }
        }


class GradeDetail(BaseModel):
    """Individual grade detail for aggregation."""
    
    criterion: str = Field(description="Criterion name")
    score: float = Field(ge=0, description="Score awarded")
    max_score: float = Field(gt=0, description="Maximum possible score")
    justification: str = Field(description="Brief justification")


class AggregationResult(BaseModel):
    """Final aggregated grading result."""
    
    total_score: float = Field(description="Sum of all criterion scores")
    max_possible: float = Field(description="Sum of all max scores")
    percentage: float = Field(ge=0, le=100, description="Score as percentage")
    letter_grade: str = Field(description="Letter grade (A, B, C, D, F)")
    grade_details: List[GradeDetail] = Field(description="Individual criterion grades")
    requires_human_approval: bool = Field(description="Whether human review is needed")
    approval_reason: Optional[str] = Field(default=None, description="Reason for requiring approval")


class FinalFeedback(BaseModel):
    """Structured feedback for the student."""
    
    strengths: List[str] = Field(description="What the student did well")
    areas_for_improvement: List[str] = Field(description="Specific areas to improve")
    suggestions: List[str] = Field(description="Actionable improvement suggestions")
    encouragement: str = Field(description="Encouraging closing message")
    overall_summary: str = Field(description="Brief overall assessment")


class GradingError(BaseModel):
    """Structured error response."""
    
    error_type: str = Field(description="Type of error (validation, grading, aggregation)")
    error_message: str = Field(description="Human-readable error description")
    recoverable: bool = Field(description="Whether the error can be retried")
    suggestion: Optional[str] = Field(default=None, description="How to fix the error")
