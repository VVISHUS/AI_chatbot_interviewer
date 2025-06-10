from pydantic import BaseModel 
from openai import OpenAI
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import asyncio
import aiofiles
from utils.custom_tools import tools
from utils.custom_classes_and_prompts import ScreeningQuestion, ScreeningQuestionsResponse, TestEvaluation, FinalCandidateReport,CandidateProfile


load_dotenv()


class HiringAgent:
    def __init__(self,  resume_details:dict,candidate_details: dict, jd_details: dict, primary_llm="gemini", fallback_llm="hyperbolic", add_details: dict = None):
        self.primary_llm = primary_llm
        self.fallback_llm = fallback_llm
        self.primary_url = os.getenv("primary_url")
        self.fallback_url = os.getenv("fallback_url")
        self.primary_llm_key = os.getenv("GEMINI_API_KEY")
        self.fallback_llm_key = os.getenv("HYPERBOLIC")
        self.analysis_done=False
        # Validate and handle empty candidate_details
        if not candidate_details or not isinstance(candidate_details, dict):
            candidate_details = {}

        self.cand_details = candidate_details
        self.resume_details = resume_details['resume_details'] or ""
        if not add_details:
            self.add_details = {}
        self.jd_details = jd_details or {}

        self.profile = self.filter_relevant_fields(candidate_details)



        # Get JD content for the applied position
        self.current_jd = self.get_current_jd_content()

        # Validate final profile has required fields with defaults
        required_fields = ['first_name', 'position_applied']
        for field in required_fields:
            if field not in self.profile or not self.profile[field]:
                if field == 'first_name':
                    self.profile[field] = "Candidate"
                elif field == 'position_applied':
                    self.profile[field] = "General Position"
                print(f"[WARNING] Missing required field '{field}', using default: {self.profile[field]}")

        # Initialize OpenAI client with error handling
        try:
            self.client = self.create_openai_client(self.primary_llm_key, self.primary_url)
        except Exception as e:
            print(f"[ERROR] Failed to initialize OpenAI client: {e}")
            raise ValueError(f"Failed to initialize AI client. Please check your API configuration: {e}")

        # UNIFIED SYSTEM: Initialize conversation state
        self.interview_started = False
        self.resume_summary=None
        self.questions_asked = 0
        self.max_questions = 5
        self.interview_intents= ["casual_chat", "structured_questions", "post_interview"]
        self.interview_phase = self.interview_intents[0]
        self.formal_interactions_count = 0

        # UNIFIED SYSTEM: Initialize test system  
        self.screening_questions = []
        self.current_question_index = 0
        self.test_responses = []
        self.test_scores = []
        self.questions_generated = False
        self.casual_chat_count = 0
        self.max_casual_chats = 2
        
    async def init_func(self):
        await self.generate_screening_questions_async()
        await self.save_questions_to_file_async()
        self.questions_generated = True
        await self.get_resume_summary()

    async def get_resume_summary(self):
        try:
            if (self.resume_details is not None ) and len(self.resume_details)>100:
                user_message = f"""
                Please extract the candidate's information from the following resume text. 
                If any field is missing or unclear, just set it as `None`.

                Resume:{self.resume_details}
                """
                self.resume_summary=self.chat_with_llm(user_message=user_message,chat_history=None,get_common_system_prompt=False,response_format=CandidateProfile,temp=0.5)
                print(f"\n\n Resume_summary:{self.resume_summary}\n\n")
            else:
                print("Unable to read th resume provided")
        except Exception as e:
            print(f"Unable to summarize the resume due to: {e}")


    async def generate_screening_questions_async(self):
        """Asynchronously generate 5 screening questions with structured output validation"""
        try:
            prompt = f"""Generate exactly 5 screening test questions based on the candidate's profile and job requirements.

    CANDIDATE PROFILE:
    - Name: {self.profile.get('first_name', '')} {self.profile.get('last_name', '')}
    - Position Applied: {self.profile.get('position_applied', '')}
    - Experience: {self.profile.get('years_experience', 0)} years
    - Tech Stack: {self.profile.get('tech_stack', '')}
    - Current Company: {self.profile.get('current_company', '')}
    - Major/Education: {self.profile.get('major', '')}

    RESUME DETAILS:
    {json.dumps(self.resume_details, indent=2) if self.resume_details else 'No resume details provided'}

    JOB DESCRIPTION:
    {self.current_jd if self.current_jd else 'General technical role'}

    Generate 5 questions divided into 5 sections (1 questions each):
    1. Technical Skills
    2. Problem Solving  
    3. Experience & Projects
    4. Behavioral
    5. Role-Specific

    Each question should have clear evaluation criteria and expected answer points."""

            messages = [
                {"role": "system", "content": "You are an expert technical recruiter creating screening questions."},
                {"role": "user", "content": prompt}
            ]

            response = self.client.beta.chat.completions.parse(
                model="gemini-2.0-flash",
                messages=messages,
                response_format=ScreeningQuestionsResponse,
                temperature=0.7
            )

            questions_data = response.choices[0].message.parsed
            self.screening_questions = questions_data.screening_questions
            print(f"[DEBUG] Generated {len(self.screening_questions)} screening questions with validation")

        except Exception as e:
            print(f"[ERROR] Failed to generate screening questions: {e}")


    async def save_questions_to_file_async(self):
        """Asynchronously save generated questions to JSON file"""
        try:          
            # Improved version
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join("screening_questions")  # Better than raw string path
            os.makedirs(output_dir, exist_ok=True)  # Creates directory if doesn't exist

            filename = os.path.join(
                output_dir,
                f"screening_questions_{self.profile.get('first_name', 'candidate')}_{timestamp}.json"
            )

            questions_data = {
                "candidate_info": {
                    "name": f"{self.profile.get('first_name', '')} {self.profile.get('last_name', '')}",
                    "position": self.profile.get('position_applied', '') ,
                    "experience": self.profile.get('years_experience', 0),
                    "generated_at": timestamp
                },
                "questions": [q.dict() if isinstance(q, ScreeningQuestion) else q for q in self.screening_questions]
            }

            async with aiofiles.open(filename, 'w') as f:
                await f.write(json.dumps(questions_data, indent=2))

            print(f"[DEBUG] Questions saved to {filename}")

        except Exception as e:
            print(f"[ERROR] Failed to save questions to file: {e}")

    def get_current_jd_content(self) -> str:
        """Get JD content for the position candidate applied for"""
        position = self.profile.get('position_applied', '')
        if position and position in self.jd_details:
            return self.jd_details[position]
        return ""

    def filter_relevant_fields(self, data: dict) -> dict:
        relevant_keys = [
            "first_name", "last_name", "email", "phone", "institute", "major", "current_company",
            "current_title", "years_experience", "linkedin", "github", "portfolio",
            "position_applied", "expected_salary", "tech_stack", "current_location", "ready_to_relocate"
        ]
        
        filtered = {k: v for k, v in data.items() if k in relevant_keys and v}
        
        # Debug filtered results
        print("\n[DEBUG] Filtered fields:")
        print(f"Original keys: {list(data.keys())}")
        print(f"Filtered keys: {list(filtered.keys())}")
        print(f"Missing expected keys: {set(relevant_keys) - set(filtered.keys())}")
        
        return filtered

    def create_openai_client(self, api_key: str, base_url: str):
        """Create OpenAI client with the specified API key and base URL"""
        return OpenAI(api_key=api_key, base_url=base_url)
        
    def get_common_system_prompt(self, include_jd: bool = True, include_resume: bool = True) -> str:
        """Common system prompt used across all interactions with optional JD and Resume inclusion"""
        
        # Assemble candidate resume info only if flag is True
        candidate_info = f"""
    CANDIDATE RESUME INFORMATION:
    - Name: {self.profile.get('first_name', '')} {self.profile.get('last_name', '')}
    - Position Applied: {self.profile.get('position_applied', 'Not specified')}
    - Experience: {self.profile.get('years_experience', 0)} years
    - Current Company: {self.profile.get('current_company', 'Not specified')}
    - Current Location: {self.profile.get('current_location', 'Not specified')}
    - Ready to Relocate: {self.profile.get('ready_to_relocate', 'Not specified')}
    - Tech Stack: {self.profile.get('tech_stack', 'Not specified')}
    - Expected Salary: {self.profile.get('expected_salary', 'Not specified')} LPA
    """
        resume_info=f"""Resume Summary of the Candidate: {self.resume_summary}""" if include_resume else ""

        jd_info = f"""
    JOB DESCRIPTION:
    {self.current_jd[:1000] if self.current_jd else 'No JD available'}
    """ if include_jd else ""

        return f"""You are a professional Technical Recruiter and Interviewer for TalenScout conducting a structured interview/screening process.

    ⚙️ CHATBOT FLOW OVERVIEW:
    1. **Phase 1: Casual Chat** – Ask up to 2–3 resume-based casual questions while the structured questions are being generated.
    2. **Phase 2: Structured Questions** – Ask the candidate screening questions one by one in a human, professional tone using the provided format (Section, Question Number, and Question).
    3. **Phase 3: Post-Interview** – After all questions are done, allow candidate to request an **analysis**, **recommendation**, or to **exit**.

    {candidate_info}
    {resume_info}
    {jd_info}
    INTERVIEW GUIDELINES:
    1. Stay focused on the interview/screening process ONLY
    2. Do NOT answer questions outside the interview context
    3. Do NOT provide information about the company, role details, or general career advice
    4. Only respond to: question clarifications, question repeats, basic acknowledgments
    5. If candidate asks irrelevant questions, politely redirect to the interview
    6. Maintain professional, structured interview flow
    7. Ask one question at a time and wait for complete answers
    8. Current interview phase: {self.interview_phase}
    9. Formal interactions completed: {self.formal_interactions_count}/4
    10. Total interactions limit: {self.max_questions}

    STRICT BOUNDARIES:
    - No discussions about salary negotiations, company policies, or role responsibilities
    - No answering "What questions do you have for us?" until interview completion
    - No providing hints or answers to technical questions
    - No going back to previous questions unless for clarification
    - No casual conversation outside interview context

    You are the interviewer. The candidate should answer YOUR questions, not the other way around.
    """

    def chat_with_llm(
        self,
        user_message: str,
        chat_history: list,
        get_common_system_prompt: bool = True,
        get_common_system_prompt_args: list[bool, bool] = [True, True],
        custom_system_prompt: str = None,
        response_format=None,
        temp: float = 0.7,
        max_chat_history: int = 6
    ) -> str:
        """
        Send message to LLM with proper context and optional structured output.

        Parameters:
        - user_message: str → user’s current input
        - chat_history: list → full session history in Streamlit style (list of dicts with 'role' and 'content')
        - get_common_system_prompt: bool → whether to use common system prompt
        - get_common_system_prompt_args: list[bool, bool] → whether to include resume & JD respectively
        - custom_system_prompt: str → override the system prompt completely if provided
        - response_format: Optional BaseModel → for structured LLM outputs
        - temp: float → sampling temperature
        - max_chat_history: int → number of most recent history turns to include
        """

        try:
            # System prompt logic
            if custom_system_prompt:
                system_prompt = custom_system_prompt
            elif get_common_system_prompt:
                system_prompt = self.get_common_system_prompt(*get_common_system_prompt_args)
            else:
                system_prompt = (
                    "You are a help bot. Respond appropriately to user queries. "
                    "These may involve extracting relevant information or simple Q&A."
                )
            if(chat_history is not None):
                max_chat_history=max_chat_history if max_chat_history<len(chat_history) else int(len(chat_history)-1)
            # Trim chat history to the last `max_chat_history` items
            trimmed_history = chat_history[-max_chat_history:] if chat_history else []

            # Convert chat history (already formatted with {"role": ..., "content": ...})
            formatted_history = [{"role": msg["role"], "content": msg["content"]} for msg in trimmed_history]

            # Compose final message list
            messages = [{"role": "system", "content": system_prompt}] + formatted_history + [
                {"role": "user", "content": user_message}
            ]

            # Call LLM with or without structured output
            if response_format:
                response = self.client.beta.chat.completions.parse(
                    model="gemini-2.0-flash",
                    messages=messages,
                    response_format=response_format,
                    temperature=temp
                )
                return response.choices[0].message.parsed
            else:
                response = self.client.chat.completions.create(
                    model="gemini-2.5-flash-preview-05-20",
                    messages=messages,
                    temperature=temp
                )
                return response.choices[0].message.content

        except Exception as e:
            print(f"[LLM ERROR]: {e}")
            return "I apologize, but I encountered a technical issue. Let's continue with the interview. Could you please repeat your last response?"


    def take_interview(self, chat_history: list) -> str:
        """Handle the flow between casual chat and structured questions"""

        # Phase 1: Casual chat while questions generate
        if self.interview_phase == "casual_chat":
            if self.casual_chat_count <= self.max_casual_chats:
                self.casual_chat_count += 1

                prompt = f"""Have a casual, professional conversation with the candidate while I prepare their structured questions.

    Casual chat #{self.casual_chat_count}/{self.max_casual_chats}
    Topics you can discuss:
    - What excites them about this role
    - Willingness to relocate if required 
    - Their learning goals or career aspirations
    - Based on resume projects/experience that align with this role
    - Any initial questions they might have about the process

    Keep it natural, friendly, and professional. Questions are being prepared in the background."""

                response = self.chat_with_llm(user_message=prompt, chat_history=chat_history,max_chat_history=2)

                # Check if we should transition
                if self.casual_chat_count >= self.max_casual_chats:
                    if self.questions_generated:
                        self.interview_phase = "structured_questions"
                        return response 
                    else:
                        return response + "\n\nI'm still preparing your customized questions. Let's chat a bit more!"

                return response

            # Transition if ready
            elif self.questions_generated:
                self.interview_phase = "structured_questions"
                return """
                Perfect! Your customized questions are ready. Let's begin the structured assessment.\n
                INTERVIEW RULES & FAIRNESS GUIDELINES:\n
                - Answer questions honestly based on your own knowledge and experience\n
                - No external assistance, AI tools, or reference materials allowed\n
                - Keep responses concise: 3-4 lines maximum or under 500 characters\n
                - If you don't know something, simply say "I don't know" rather than guessing\n
                - Each question will be asked once - clarification available only if truly needed\n
                - This is a fair assessment designed to evaluate your genuine technical understanding\n

                Ready to start? Your first question is coming up next."""

            else:
                return "I'm still preparing your personalized questions. How about we discuss what interests you most about this role?"

        # Phase 2: Structured Q&A
        elif self.interview_phase == "structured_questions":
            if not self.questions_generated or not self.screening_questions:
                return "I'm still preparing your questions. Please wait a moment."

            # All questions done
            if self.current_question_index >= len(self.screening_questions):
                self.interview_phase = "post_interview"

                # Trigger analysis just once upon finishing all Qs
                self.analysis_result = self.analyze_candidate_performance(chat_history)

                return """🎉 **All screening questions completed!**

    What would you like to do next?
    - Analysis of the session?
            \nOR\n
    - Type 'exit' to conclude the interview"""

        # Ask next structured question with strict rules enforced
        q = self.screening_questions[self.current_question_index]

        # The prompt sent to LLM (as user message)
        prompt = f"""Ask the following structured question in a human conversational way but quoting all 3 below info as it is:
        - Section: {q.section}
        - Question Number: {q.question_number}
        - Question: {q.question}
        """

        # The strict instruction passed in the custom system prompt

        custom_system_prompt = """
        You are an AI Technical Interviewer for TalenScout conducting a formal screening.

        **CORE BEHAVIOR:**
        - Never provide hints, help, or guidance
        - Maintain professional, neutral tone
        - Present questions in exact format provided
        - Log responses silently (no evaluation during interview)

        **RESPONSE RULES:**
        1. If candidate asks for clarification: Simplify ONCE only
        2. If they ask again: "Cannot be simplified further."
        3. If candidate says "I don't know" or asks for help: Issue formal warning

        **QUESTION PRESENTATION:**
        Present each question conversationally but quote these exact elements and don't forget to include /n and "`" in the output response:
        - Section: [section name]\n
        - Question Number: [number]\n\n 
        - Question: [question text]
        
        Stick to this structured format to ensure fairness and consistency. The candidate's answers will be evaluated after the interview.
        """

        self.current_question_index += 1

        # Send to LLM
        return self.chat_with_llm(
            user_message=prompt,
            chat_history=chat_history,
            get_common_system_prompt=False,
            max_chat_history=2,
            custom_system_prompt=custom_system_prompt
        )

            
    def analyze_candidate_performance(self,chat_history:list) -> TestEvaluation:
        """Evaluate structured interview responses and return structured feedback"""
        self.analysis_done=True
        custom_system_prompt = f"""
        You are a professional Technical Recruiter and Interviewer for TalenScout conducting a structured interview screening process. You have just completed the structured phase of the interview consisting of 5-7 questions. You are now tasked with evaluating the candidate's answers.

        You will be given:
        - The full chat history between the candidate and the interviewer during the structured questions phase by user
        - The original structured questions with expected answer points and evaluation criteria which is {self.screening_questions}

        Please evaluate the candidate's performance using the following structure:

        **EVALUATION METRICS:**
        - Total Score: [X/100]
        - AI Cheat Probability Score: [X/100] (Based on response patterns, timing, complexity of answers relative to question difficulty, and signs of potential AI assistance)

        **DETAILED ASSESSMENT:**
        - Clear strengths based on the answers given by candidate and based on Total Score
        - Areas for improvement on the answers given by candidate and based on Total Score
        - Overall feedback in a professional, friendly, and constructive tone with mention and remarks on **AI Cheat Probability** 

        **AI CHEAT PROBABILITY FACTORS TO CONSIDER:**
        - Unusually perfect or overly comprehensive answers
        - Responses that seem copied/pasted or unnaturally formatted
        - Answers that exceed expected depth for the candidate's stated experience level
        - Inconsistent knowledge patterns across different topics
        - Responses that include information not directly asked for in suspicious ways

        Provide honest, fair evaluation while being constructive and professional.
        """
        try:
            # Request structured evaluation
            evaluation = self.chat_with_llm(
                custom_system_prompt=custom_system_prompt,
                user_message="Evaluate the candidate's structured interview performance.",
                chat_history=chat_history,
                max_chat_history=50,
                response_format=TestEvaluation
            )

            score = evaluation.AI_Cheat_probability
            if score > 1.0:
                score = score / 100.0  

            percentage = min(score * 100, 100.0)

            formatted_evaluation = f"""
            📊 EVALUATION METRICS\n
            {'─' * 80}
            • Overall Score: {evaluation.score}/100\n
            • AI Assistance Probability: {percentage:.2f}%
            💪 STRENGTHS
            {'─' * 80}
            {evaluation.strengths}

            🔧 AREAS FOR IMPROVEMENT
            {'─' * 80}
            {evaluation.areas_for_improvement}

            📝 OVERALL FEEDBACK
            {'─' * 80}
            {evaluation.feedback}

            {'═' * 80}
            Report Generated: {self._get_timestamp()}
            Interviewer: TalenScout AI Screening System
            {'═' * 80}\n\n
            You can now procees to final recommendation section where you may ask to get your final recommendation.
                    """
                    
            return formatted_evaluation
        
        except Exception as e:
            print("Evaluation failed:", e)
            raise

    def _get_timestamp(self):
        """Helper method to get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")       


    def generate_final_recommendation(
        self,
        chat_history: list,
    ) -> FinalCandidateReport:
        """Analyze the candidate's overall profile and test performance to generate a final hiring report."""
        
        custom_system_prompt = f"""
    You are a professional Technical Recruiter and Interviewer at TalenScout.

    You are tasked with generating a final hiring recommendation report for a candidate, based on:

    1.Resume Summary:
    {self.resume_summary}

    2. Job Description (JD):
    {self.current_jd}

    3. Candidate Profile:
    - Name: {self.profile.get('first_name', '')} {self.profile.get('last_name', '')}
    - Experience: {self.profile.get('years_experience', 'Not Specified')} years
    - Current Company: {self.profile.get('current_company', 'Not Specified')}
    - Location: {self.profile.get('current_location', 'Not Specified')}
    - Ready to Relocate: {self.profile.get('ready_to_relocate', 'Not Specified')}
    - Tech Stack: {self.profile.get('tech_stack', 'Not Specified')}
    - Expected Salary: {self.profile.get('expected_salary', 'Not Specified')} LPA

    4. Structured Interview Evaluation Summary:
        -This is the summary based on 5 total questions asked from candidate
        {self.analysis_result}


    Your objective is to analyze the above information and return a detailed hiring recommendation using the following structure (conform to the class `FinalCandidateReport`):

    - jd_requirements_match: Skill-wise fit between resume and JD
    - screening_test_performance: Total test score and insights
    - specific_scores: Inferred technical and communication score buckets
    - location_logistics: Candidate's location and relocation readiness
    - salary_expectations: Fit between expected salary and general market/budget
    - final_decision: One of ['Recommended', 'On Hold', 'Not Recommended']
    - overall_score: Normalized score out of 100 for hiring consideration
    - test_performance_impact: How much test result influenced the decision
    - overall_assessment: Summary and fit-level description
    - top_strengths: List of top 3–5 strengths
    - concerns: Any risks or red flags
    - recommendations: What the candidate should work on
    - next_steps: Suggestions like "Move to Tech Round", "Needs Portfolio", etc.
    - timeline_recommendation: When they can join or timelines to note

    Be comprehensive and use professional language and if you don't find anything to include just give None there.
    """

        try:
            final_report = self.chat_with_llm(
                user_message="Generate the final candidate recommendation based on all provided information.",
                chat_history=chat_history,
                custom_system_prompt=custom_system_prompt,
                response_format=FinalCandidateReport,
                max_chat_history=2,
                temp=0.5,
            )
            return f"""

    🎯 FINAL DECISION: {final_report.final_decision.upper()}
    Overall Score: {final_report.overall_score}/100

    📋 JOB REQUIREMENTS MATCH
    {'─' * 80}
    {chr(10).join([f"• {item}" for item in final_report.jd_requirements_match]) if final_report.jd_requirements_match else "No data available"}

    📊 SCREENING TEST PERFORMANCE
    {'─' * 80}
    {chr(10).join([f"• {item}" for item in final_report.screening_test_performance]) if final_report.screening_test_performance else "No data available"}

    📈 SPECIFIC SCORES BREAKDOWN
    {'─' * 80}
    {chr(10).join([f"• {item}" for item in final_report.specific_scores]) if final_report.specific_scores else "No data available"}

    🌍 LOCATION & LOGISTICS
    {'─' * 80}
    {chr(10).join([f"• {item}" for item in final_report.location_logistics]) if final_report.location_logistics else "No data available"}

    💰 SALARY EXPECTATIONS
    {'─' * 80}
    {chr(10).join([f"• {item}" for item in final_report.salary_expectations]) if final_report.salary_expectations else "No data available"}

    🔍 OVERALL ASSESSMENT
    {'─' * 80}
    {chr(10).join([f"• {item}" for item in final_report.overall_assessment]) if final_report.overall_assessment else "No data available"}

    Test Performance Impact: {final_report.test_performance_impact}

    💪 TOP STRENGTHS
    {'─' * 80}
    {chr(10).join([f"• {item}" for item in final_report.top_strengths]) if final_report.top_strengths else "None identified"}

    ⚠️  AREAS OF CONCERN
    {'─' * 80}
    {chr(10).join([f"• {item}" for item in final_report.concerns]) if final_report.concerns else "None identified"}

    💡 RECOMMENDATIONS
    {'─' * 80}
    {chr(10).join([f"• {item}" for item in final_report.recommendations]) if final_report.recommendations else "None identified"}

    🚀 SUGGESTED NEXT STEPS
    {'─' * 80}
    {chr(10).join([f"• {item}" for item in final_report.next_steps]) if final_report.next_steps else "None identified"}

    ⏰ TIMELINE RECOMMENDATION
    {'─' * 80}
    {final_report.timeline_recommendation}

    {'═' * 80}

    🎉 PROCESS COMPLETION NOTICE
    {'─' * 80}

    **Next Steps:**
    1. You are now formally released from this evaluation process.

    2. For your final report and feedback on next rounds, please contact:
    📧 careers@talentscout.com
    📞 +1 (555) 123-4567

    3. To officially conclude this session, type `end_chat` or `end_conversation`
    (Session may end automatically in a while)

    {'═' * 80}
    Thank you for your participation! We appreciate your time and effort.
    Report Generated: {self._get_timestamp()}
    {'═' * 80}
        """.strip()

        except Exception as e:
            print("Failed to generate final recommendation:", e)
            raise


    def greet_candidate(self) -> str:
        """Professional interview greeting"""
        return f"""Hello {self.profile.get('first_name', '')}! Welcome to TalenScout.

    I'm conducting your interview for the {self.profile.get('position_applied', 'position')} role today. This will be a structured interview covering your background, technical skills, and experience relevant to the job requirements.

    ⚠️ **IMPORTANT INTERVIEW RULES & FAIRNESS GUIDELINES**:
    - Total interaction limit: 15 exchanges only
    - After 2–3 formal questions, you must take a technical test
    - Only after completing the test can you get analysis or recommendations
    - Please manage your responses efficiently — total session time is ~10 minutes
    - This will be a **straight Q&A session**: every message you send will move the conversation forward
    - **There is no going back** to previous questions
    - **Each question is well-curated** and written in **simple, clear language**
    - You are expected to:
    - Answer honestly based on your own knowledge and experience
    - Use no external help — AI tools, browsers, or reference materials are strictly prohibited
    - Keep answers concise: about 3–4 lines or under 500 characters
    - If unsure, respond with _"I don't know"_ — guessing is discouraged
    - Clarification is allowed only once if truly necessary

    ⏳ Make sure to complete the session within 10 minutes for fairness.

    ❗ In case of any technical issues or confusion, reach out to: **careers@talentscout.com** with a **screenshot attached**.

    ---

    Let’s begin. Are you ready to start the interview?
    """

    
    def end_conversation(self):
        """
        Handles conversation termination when user explicitly requests to end the session.
        This should only be called when user clearly indicates they want to stop/end the conversation.
        """
        try:
            # Add any cleanup logic here if needed
            # For example: save conversation, update database, etc.
            
            return "Thank you for using TalenScout Interview Assistant. The conversation has been ended. Have a great day!"
        
        except Exception as e:
            return f"⚠️ Error ending conversation: {e}"
        
    def get_response(self, chat_history: list):
        system_prompt = f"""
You are an advanced AI Interview Assistant for TalenScout.

You are conducting and managing intelligent, structured screening interviews. You have access to the following tools:

🔹 `take_interview`: Use this to begin or continue an interview (either casual or structured questions phase). This is your default tool during any question-asking stage.
→ Trigger Keywords: "start interview", "next question", "continue", "ask me", "ready"

🔹 `analyze_candidate_performance`: Use this **only after** structured questions are completed and user asks for performance, analysis, score, evaluation, or feedback.
→ Trigger Keywords: "analyze", "analysis"

🔹 `generate_final_recommendation`: Use when user wants a summary, hiring decision, final recommendation, or report based on everything.
→ Trigger Keywords: "recommendation", "final recommendation", "summary", "report"

🔹 `end_conversation`: Use only when the user explicitly says "stop", "end", "quit", "no more questions", etc.

💡 Use the current phase and context from `chat_history` to decide which tool to use:
- interview_phase: {self.interview_phase}
- analysis_done: {self.analysis_done}

❗ RULES:
- You MUST select one tool every time.
- Never respond directly to the user without selecting a tool.
- If analysis_done=True, do not use analyze_candidate_performance again.
- Use end_conversation only when user clearly requests to stop.

You will now continue the session using the correct tool.

chat_history:
"""
        def _make_llm_call(messages, is_retry=False):
            """Helper function to make LLM call with retry logic"""
            retry_suffix = """

    CRITICAL: You MUST select one tool from the available tools list. Do not respond without selecting a tool. Choose the most appropriate tool based on the conversation context.""" if is_retry else ""
            
            if is_retry and messages:
                # Add explicit instruction for retry
                messages[-1]["content"] += retry_suffix

            response = self.client.beta.chat.completions.parse(
                model="gemini-2.0-flash",
                messages=messages,
                tools=tools,
                tool_choice="required"
            )
            return response

        try:
            max_chat_history = 4
            if chat_history is not None:
                max_chat_history = max_chat_history if max_chat_history < len(chat_history) else int(len(chat_history) - 1)
            
            # Add actual chat history here
            messages = [{"role": "system", "content": system_prompt}] + chat_history[-max_chat_history:]

            # Add optional message if needed
            messages.append({"role": "user", "content": "Please continue the interview based on the previous conversation."})

            # First attempt
            response = _make_llm_call(messages, is_retry=False)

            # Defensive check
            if not response.choices:
                return "⚠️ No response choices returned from the model."

            message = response.choices[0].message
            tool_calls = getattr(message, "tool_calls", [])

            # If no tool was called, retry with explicit instructions
            if not tool_calls:
                print("⚠️ No tool selected on first attempt. Retrying with explicit instructions...")
                try:
                    response = _make_llm_call(messages, is_retry=True)
                    message = response.choices[0].message
                    tool_calls = getattr(message, "tool_calls", [])
                    
                    if not tool_calls:
                        return "⚠️ Model failed to select a tool even after retry. Please try again."
                except Exception as retry_error:
                    return f"⚠️ Retry failed: {retry_error}"

            print(f"\ntool called by LLM: {tool_calls}\n")
            tool_call = tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Handle tool execution
            if tool_name == "take_interview":
                result = self.take_interview(chat_history=chat_history)
            elif tool_name == "analyze_candidate_performance":
                result = self.analyze_candidate_performance(chat_history=chat_history)
            elif tool_name == "generate_final_recommendation":
                result = self.generate_final_recommendation(chat_history=chat_history)
            elif tool_name == "end_conversation":
                result = self.end_conversation()
            else:
                result = f"⚠️ Unknown tool selected: {tool_name}. Available tools: take_interview, analyze_candidate_performance, generate_final_recommendation, end_conversation"

            return result

        except Exception as e:
            return f"⚠️ Internal Error in get_response: {e}"
