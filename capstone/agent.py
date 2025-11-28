"""
Smart Grading Assistant - Main Agent

A multi-agent system for automated academic grading with human oversight.
This capstone project demonstrates key concepts from the Google ADK course:

1. Multi-agent system (Sequential + Parallel)
2. Custom Tools (validate_rubric, grade_criterion, calculate_score)
3. Human-in-the-Loop (approval for edge cases)
4. Sessions & Memory (DatabaseSessionService)
5. Observability (LoggingPlugin)
6. Gemini model (bonus points)

Author: Rafael Ventura
Course: 5-Day AI Agents Intensive Course with Google
"""

import asyncio
import json
import logging
import os
import uuid

from dotenv import load_dotenv
from google.genai import types

from google.adk.agents import Agent, LlmAgent, SequentialAgent, ParallelAgent
from google.adk.apps.app import App, ResumabilityConfig
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.adk.plugins.logging_plugin import LoggingPlugin

try:
    from .tools.validate_rubric import validate_rubric
    from .tools.grade_criterion import grade_criterion
    from .tools.calculate_score import calculate_final_score
except ImportError:  # When running `python agent.py` directly inside capstone/
    from tools.validate_rubric import validate_rubric
    from tools.grade_criterion import grade_criterion
    from tools.calculate_score import calculate_final_score

# Load environment variables
load_dotenv()

# Configure logging for observability
logging.basicConfig(
    filename="grading_agent.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s",
)

print("✅ Smart Grading Assistant - Loading...")

# =============================================================================
# CONFIGURATION
# =============================================================================

APP_NAME = "capstone"
USER_ID = "teacher_01"

# Retry configuration for API calls
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Score thresholds for human approval
FAILING_THRESHOLD = 50  # Below this requires approval
EXCEPTIONAL_THRESHOLD = 90  # Above this requires approval

print("✅ Configuration loaded")

# =============================================================================
# HUMAN-IN-THE-LOOP TOOL
# Concept: Day 2 - Long-running operations (pause/resume agents)
# =============================================================================

def request_grade_approval(
    final_score: float,
    max_score: float,
    percentage: float,
    letter_grade: str,
    reason: str,
    grade_summary: str,
    tool_context: ToolContext
) -> dict:
    """Request human approval for edge case grades.
    
    This tool pauses the agent and requests teacher confirmation
    for grades that are either failing (<50%) or exceptional (>90%).
    
    Args:
        final_score: The calculated final score
        max_score: Maximum possible score
        percentage: Score as percentage
        letter_grade: Letter grade (A, B, C, D, F)
        reason: Why approval is needed
        grade_summary: Summary of all criterion grades
        tool_context: ADK tool context for confirmation flow
    
    Returns:
        Approval status and message
    """
    
    # SCENARIO 1: First call - request confirmation
    if not tool_context.tool_confirmation:
        tool_context.request_confirmation(
            hint=f"""
⚠️ GRADE APPROVAL REQUIRED

Final Score: {final_score}/{max_score} ({percentage}%) - Grade: {letter_grade}

Reason: {reason}

Grade Summary:
{grade_summary}

Do you approve this grade?
            """,
            payload={
                "final_score": final_score,
                "percentage": percentage,
                "letter_grade": letter_grade,
            },
        )
        return {
            "status": "pending",
            "message": f"Awaiting teacher approval for grade {letter_grade} ({percentage}%)",
        }
    
    # SCENARIO 2: Resumed - handle approval response
    if tool_context.tool_confirmation.confirmed:
        return {
            "status": "approved",
            "approved_by": "human",
            "message": f"Grade {letter_grade} ({percentage}%) has been APPROVED by teacher",
        }
    else:
        return {
            "status": "rejected",
            "message": f"Grade {letter_grade} ({percentage}%) was REJECTED by teacher. Please review.",
        }


print("✅ Human-in-the-Loop tool defined")

# =============================================================================
# AGENT 1: RUBRIC VALIDATOR
# Concept: Day 1 - Single Agent with Tools
# =============================================================================

rubric_validator_agent = LlmAgent(
    name="RubricValidatorAgent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    description="Validates the structure and completeness of grading rubrics",
    instruction="""You are a rubric validation specialist. Your job is to validate 
    grading rubrics before they are used for evaluation.
    
    When you receive a rubric:
    1. Use the validate_rubric tool to check its structure
    2. If valid, confirm the rubric is ready and list the criteria
    3. If invalid, explain what needs to be fixed
    
    Always be precise and helpful in your feedback.""",
    tools=[validate_rubric],
    output_key="validation_result",
)

print("✅ RubricValidatorAgent created")

# =============================================================================
# AGENT 2: CRITERION GRADERS (Created dynamically based on rubric)
# Concept: Day 1 - Parallel Agents
# =============================================================================

def create_criterion_grader(criterion_name: str, criterion_description: str, max_score: int) -> LlmAgent:
    """Factory function to create a grader agent for a specific criterion.
    
    This allows us to create parallel graders dynamically based on the rubric.
    """
    return LlmAgent(
        name=f"Grader_{criterion_name.replace(' ', '_')}",
        model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
        description=f"Evaluates submissions for: {criterion_name}",
        instruction=f"""You are an expert evaluator for the criterion: "{criterion_name}"
        
        Criterion Description: {criterion_description}
        Maximum Score: {max_score} points
        
        When evaluating a submission:
        1. Carefully read the submission content
        2. Evaluate it against this specific criterion
        3. Determine a score from 0 to {max_score}
        4. Use the grade_criterion tool to record your evaluation
        5. Provide detailed justification for your score
        
        Be fair, consistent, and constructive in your feedback.
        Focus ONLY on this criterion - other aspects will be evaluated by other agents.""",
        tools=[grade_criterion],
        output_key=f"grade_{criterion_name.replace(' ', '_').lower()}",
    )


# Default graders for Python code rubric (will be replaced dynamically)
code_quality_grader = create_criterion_grader(
    "Code Quality", 
    "Evaluate code readability, naming conventions, and PEP 8 adherence",
    30
)

functionality_grader = create_criterion_grader(
    "Functionality",
    "Evaluate if the code correctly solves the problem",
    40
)

documentation_grader = create_criterion_grader(
    "Documentation",
    "Evaluate docstrings, comments, and code explanation",
    30
)

# Parallel agent to run all graders simultaneously
parallel_graders = ParallelAgent(
    name="ParallelGraders",
    sub_agents=[code_quality_grader, functionality_grader, documentation_grader],
)

print("✅ ParallelGraders created (3 criterion graders)")

# =============================================================================
# AGENT 3: SCORE AGGREGATOR
# Concept: Day 1 - Sequential Agent coordination
# =============================================================================

aggregator_agent = LlmAgent(
    name="AggregatorAgent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    description="Aggregates individual criterion grades into a final score",
    instruction="""You are a grade aggregator. Your job is to:
    
    1. Collect all the individual criterion grades from the previous evaluation step
    2. Use the calculate_final_score tool to compute the final grade
    3. Summarize the evaluation results
    
    Read the grades from the session state:
    - grade_code_quality
    - grade_functionality  
    - grade_documentation
    
    Format the grades as JSON and call calculate_final_score.
    
    After calculating, report:
    - Final score and letter grade
    - Whether human approval is required
    - Summary of strengths and areas for improvement""",
    tools=[calculate_final_score],
    output_key="aggregation_result",
)

print("✅ AggregatorAgent created")

# =============================================================================
# AGENT 4: APPROVAL HANDLER
# Concept: Day 2 - Human-in-the-Loop (pause/resume)
# =============================================================================

approval_agent = LlmAgent(
    name="ApprovalAgent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    description="Handles human approval for edge case grades",
    instruction="""You are the approval coordinator. Your job is to:
    
    1. Check if the aggregation result requires human approval
    2. If approval is needed (score < 50% or > 90%), use request_grade_approval tool
    3. If no approval needed, confirm the grade is finalized
    
    Read the aggregation_result from session state to get:
    - Final score and percentage
    - Whether approval is required
    - The reason for approval
    
    Be clear and professional in your communication.""",
    tools=[FunctionTool(request_grade_approval)],
    output_key="approval_result",
)

print("✅ ApprovalAgent created")

# =============================================================================
# AGENT 5: FEEDBACK GENERATOR
# Concept: Day 1 - Final agent in sequence
# =============================================================================

feedback_agent = LlmAgent(
    name="FeedbackGeneratorAgent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    description="Generates comprehensive feedback for the student",
    instruction="""You are a feedback specialist. Your job is to create 
    constructive, encouraging feedback for the student.
    
    Based on all the evaluation data in the session state:
    1. Start with positive aspects (what the student did well)
    2. Identify specific areas for improvement
    3. Provide actionable suggestions
    4. End with encouragement
    
    Your feedback should be:
    - Specific (reference actual parts of the submission)
    - Constructive (focus on improvement, not criticism)
    - Encouraging (motivate continued learning)
    - Clear (easy for the student to understand)
    
    Format your feedback in a clear, readable structure.""",
    output_key="final_feedback",
)

print("✅ FeedbackGeneratorAgent created")

# =============================================================================
# ROOT AGENT: ORCHESTRATOR
# Concept: Day 1 - Sequential Agent combining all steps
# =============================================================================

# The main grading pipeline
grading_pipeline = SequentialAgent(
    name="GradingPipeline",
    sub_agents=[
        rubric_validator_agent,
        parallel_graders,
        aggregator_agent,
        approval_agent,
        feedback_agent,
    ],
)

# Root agent that coordinates the entire process
root_agent = LlmAgent(
    name="SmartGradingAssistant",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    description="Main coordinator for the Smart Grading Assistant",
    instruction="""You are the Smart Grading Assistant, an AI-powered system 
    for evaluating academic submissions.
    
    When a user provides a submission and rubric:
    1. Acknowledge the submission
    2. Delegate to the GradingPipeline for evaluation
    3. Present the final results clearly
    
    Be professional, helpful, and thorough in your responses.
    
    If the user asks about the grading process, explain:
    - Rubric validation
    - Parallel criterion evaluation
    - Score aggregation
    - Human approval for edge cases
    - Constructive feedback generation""",
    sub_agents=[grading_pipeline],
)

print("✅ Root Agent (SmartGradingAssistant) created")

# =============================================================================
# APP CONFIGURATION
# Concept: Day 2 - Resumability for Human-in-the-Loop
# =============================================================================

grading_app = App(
    name=APP_NAME,
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)

print("✅ Resumable App configured")

# =============================================================================
# SESSION & RUNNER SETUP
# Concept: Day 3 - DatabaseSessionService for persistence
# =============================================================================

# Use SQLite for persistent sessions
db_url = "sqlite:///grading_sessions.db"
session_service = DatabaseSessionService(db_url=db_url)

# Create runner with observability plugin
runner = Runner(
    app=grading_app,
    session_service=session_service,
)

print("✅ Runner created with DatabaseSessionService")
print(f"   Database: grading_sessions.db")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def grade_submission(
    submission: str,
    rubric: dict,
    session_id: str = None
) -> dict:
    """Main function to grade a submission.
    
    Args:
        submission: The student's submission text
        rubric: The grading rubric as a dictionary
        session_id: Optional session ID for persistence
    
    Returns:
        Dictionary with grading results
    """
    if session_id is None:
        session_id = f"grading_{uuid.uuid4().hex[:8]}"
    
    # Create session
    try:
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )
    except:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )
    
    # Prepare the grading request
    rubric_json = json.dumps(rubric, indent=2)
    query = f"""Please evaluate the following submission using the provided rubric.

RUBRIC:
{rubric_json}

SUBMISSION:
{submission}

Please proceed with the evaluation."""

    query_content = types.Content(
        role="user",
        parts=[types.Part(text=query)]
    )
    
    # Run the grading pipeline
    results = []
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=query_content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    results.append(part.text)
    
    return {
        "session_id": session_id,
        "results": results,
    }


async def demo():
    """Demo function to test the grading system."""
    
    print("\n" + "=" * 60)
    print("🎓 SMART GRADING ASSISTANT - DEMO")
    print("=" * 60)
    
    # Load sample rubric
    with open("examples/rubrics/python_code_rubric.json", "r") as f:
        rubric = json.load(f)
    
    # Load sample submission
    with open("examples/submissions/sample_code.py", "r") as f:
        submission = f.read()
    
    print(f"\n📋 Rubric: {rubric['name']}")
    print(f"📝 Submission: Fibonacci Calculator")
    print("\n⏳ Starting evaluation...\n")
    
    result = await grade_submission(submission, rubric)
    
    print("\n" + "=" * 60)
    print("📊 EVALUATION RESULTS")
    print("=" * 60)
    
    for text in result["results"]:
        if text and text.strip():
            print(f"\n{text}")
    
    print("\n" + "=" * 60)
    print(f"✅ Session ID: {result['session_id']}")
    print("=" * 60)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("\n🚀 Starting Smart Grading Assistant...")
    asyncio.run(demo())
