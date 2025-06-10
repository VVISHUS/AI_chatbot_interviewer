from pydantic import BaseModel
from typing import List, Optional


# Pydantic models
class ScreeningQuestion(BaseModel):
    section: str
    question_number: int
    question: str
    expected_answer_points: List[str]
    evaluation_criteria: str
    max_score: int

class ScreeningQuestionsResponse(BaseModel):
    screening_questions: List[ScreeningQuestion]

class TestEvaluation(BaseModel):
    score: int
    AI_Cheat_probability:float
    strengths: str
    areas_for_improvement: str
    feedback: str


class FinalCandidateReport(BaseModel):
    # Screening & Matching Analysis
    jd_requirements_match: List[str]  # e.g. {"Python": "Strong", "Django": "Moderate"}
    screening_test_performance: List[str]  # e.g. {"total_score": 37, "max_score": 50}
    specific_scores: List[str]  # e.g. {"Technical": 8, "Communication": 7}

    # Contextual Considerations
    location_logistics: List[str]  # e.g. {"current_location": "Bangalore", "relocation_ready": "Yes"}
    salary_expectations: List[str]  # e.g. {"expected": "18 LPA", "budget_fit": "Within range"}

    # Final Evaluation & Recommendations
    final_decision: str  # e.g. "Recommended", "On Hold", "Not Recommended"
    overall_score: int  # normalized score (0–100)
    test_performance_impact: str  # qualitative summary of test impact on decision
    overall_assessment: List[str]  # e.g. {"summary": "...", "fit_score": "High"}
    
    top_strengths: List[str]
    concerns: List[str]
    recommendations: List[str]  # action items or improvement suggestions
    next_steps: List[str]  # e.g. ["Schedule technical round", "Request portfolio"]
    timeline_recommendation: str  # e.g. "Can join within 30 days"



class CandidateProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    portfolio_url: Optional[str] = None

    institute: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None

    total_experience_years: Optional[float] = None
    experiences: Optional[List[str]] = None

    tech_stack: Optional[List[str]] = None
    programming_languages: Optional[List[str]] = None
    tools_frameworks: Optional[List[str]] = None

    projects: Optional[List[str]] = None

    certifications: Optional[List[str]] = None
    publications: Optional[List[str]] = None
    languages: Optional[List[str]] = None




"""
Modular prompt functions for resume processing and screening question generation.
This module contains all hardcoded prompts as reusable functions with variable injection.
"""

import json
from typing import Dict, Any, Optional


def get_resume_summary_prompt(resume_details: str) -> str:
    """
    Generate prompt for extracting candidate information from resume text.
    
    Args:
        resume_details (str): The raw resume text content
        
    Returns:
        str: Formatted prompt for resume summarization
    """
    return f"""
Please extract the candidate's information from the following resume text. 
If any field is missing or unclear, just set it as `None`.

Resume: {resume_details}
"""
