from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initializing FastMCP Server
mcp = FastMCP("hiring_assistant")


# 🔹 Master Prompt (Entry Point)
@mcp.prompt()
def master_prompt(text):
    """Main prompt to guide candidate through the hiring process."""
    return f"""{{% set profile = memory.get("candidate_profile") or dict() %}}
👋 Hi {{ profile.get("first_name", "there") }}! Welcome to the Hiring Assistant. 
How can I assist you today in your hiring journey?

Options:
- Take a technical test
- Analyze your profile
- Get interview questions
- End the conversation
"""


# 🔹 Take Test
@mcp.prompt()
def take_test_prompt():
    return "📝 You are now starting the technical test. The link has been sent to your email."


# 🔹 End Conversation
@mcp.prompt()
def end_convo_prompt():
    return "✅ Thank you for your time! This concludes our conversation."


# 🔹 Generate Recommendation
@mcp.prompt()
def recommendation_prompt():
    return """{{% set candidate = memory.get("candidate_profile") %}}
📋 Recommendation for {{ candidate.get("first_name", "the candidate") }}:
- Skills match: {{ candidate.get("skills_match", 0) }}/10
- Culture fit: {{ candidate.get("culture_fit", 0) }}/10

{{%- set avg = ((candidate.get("skills_match", 0) + candidate.get("culture_fit", 0)) / 2) %}}
{{%- if avg >= 8 %}}
Strong candidate - recommend proceeding to next stage.
{{%- elif avg >= 6 %}}
Good candidate - consider for interview.
{{%- else %}}
May need further evaluation.
{{%- endif %}}

**Overall Score:** {{ '%.1f' % avg }}/10
"""


# 🔹 Generate Interview Questions
@mcp.prompt()
def interview_questions_prompt():
    return """{{% set candidate = memory.get("candidate_profile") %}}
Here are some questions you can ask {{ candidate.get("first_name", "the candidate") }}:
1. Tell me about your experience at {{ candidate.get("current_company", "your current company") }}.
2. How do you handle challenging projects?
3. What excites you about the {{ candidate.get("position_applied", "role") }} position?
"""


# 🧪 Placeholder Tool: Analyze Salary
@mcp.tool()
def analyze_salary(data: dict) -> Any:
    """Tool to analyze candidate's expected salary."""
    return {"insight": f"Expected salary is ₹{data.get('expected_salary', 'not provided')}"}


# 🧪 Placeholder Tool: Analyze GitHub
@mcp.tool()
def analyze_github(data: dict) -> Any:
    """Tool to analyze GitHub profile."""
    return {"summary": f"GitHub analysis complete for {data.get('github', 'N/A')}"}


# 🧪 Placeholder Tool: Analyze LinkedIn
@mcp.tool()
def analyze_linkedin(data: dict) -> Any:
    """Tool to analyze LinkedIn profile."""
    return {"summary": f"LinkedIn review complete for {data.get('linkedin', 'N/A')}"}


# Example Utility Tool
@mcp.tool()
def get_doc_data():
    """Stub tool for document data extraction (not implemented)."""
    return {"status": "Not implemented yet"}

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')