# HiringAgent - AI-Powered Technical Interview System

An intelligent, automated interview system that conducts structured technical screenings with adaptive conversation flow, real-time question generation, and comprehensive candidate evaluation.
---
![Application Screenshot(Form Submission Page)](assets/ss_1.png)
---
![Application Screenshot(Chat Interface)](assets/ss_2.png)
---
## 🚀 Overview

The **HiringAgent** is a sophisticated AI interviewer that combines casual conversation with structured technical assessments. It dynamically generates personalized screening questions based on job descriptions and candidate profiles, then conducts fair, consistent interviews with built-in evaluation mechanisms.

## ✨ Key Features

### 🧠 **Intelligent Dual-LLM Architecture**
- **Primary LLM**: Gemini (default) for main interview operations
- **Fallback LLM**: Hyperbolic for redundancy and reliability
- Automatic failover ensures uninterrupted interview sessions

### 📋 **Multi-Phase Interview Flow**
1. **Casual Chat Phase**: Natural conversation while questions generate
2. **Structured Questions Phase**: Technical screening with strict fairness rules
3. **Post-Interview Phase**: Analysis and final recommendations

### 🎯 **Dynamic Question Generation**
- Asynchronous question generation based on JD requirements
- Personalized screening questions tailored to candidate profile
- Structured output with section categorization and difficulty levels

### 📊 **Comprehensive Evaluation System**
- Real-time response tracking and scoring
- Structured performance analysis with detailed feedback
- Final hiring recommendations with confidence ratings

### 🛡️ **Fairness & Integrity Controls**
- Strict interview rules enforcement
- No external assistance detection
- Consistent question presentation format
- Response length limitations (500 characters max)

### 🕒 **Session Management & Resource Controls***

- Time Limit: 3-minute maximum session duration with automatic timeout
- **Interaction Limit**: Maximum 15 chat interactions per session
- **Session Tracking**: Real-time elapsed time and interaction count monitoring
- **Automatic Restart**: Complete session reset on timeout or limit reached
- **Resource Protection**: Prevents excessive usage and ensures fair access

## 🏗️ System Architecture

### Core Components

```
HiringAgent
├── Interview Management
│   ├── Phase Controller (casual_chat → structured_questions → post_interview)
│   ├── Question Generator (async, JD-based)
│   └── Response Tracker
├── LLM Integration
│   ├── Primary/Fallback System
│   ├── Custom System Prompts
│   └── Tool Selection Logic
└── Evaluation Engine
    ├── Performance Analyzer
    ├── Score Calculator
    └── Report Generator
```

## 🔧 Installation & Setup

### Prerequisites
```bash
# Required environment variables
GEMINI_API_KEY=your_gemini_api_key
HYPERBOLIC=your_hyperbolic_api_key
primary_url=your_primary_llm_endpoint
fallback_url=your_fallback_llm_endpoint
```

### Initialization
```python
# Initialize HiringAgent
agent = HiringAgent(
    resume_details={"resume_details": "candidate_resume_text"},
    candidate_details={"first_name": "John", "position_applied": "Software Engineer"},
    jd_details={"role": "Backend Developer", "requirements": "Python, APIs"},
    primary_llm="gemini",
    fallback_llm="hyperbolic"
)

# Async initialization for question generation
await agent.init_func()
```

## 🌊 Interview Flow

### Phase 1: Casual Chat (2 interactions max)
- **Purpose**: Engage candidate while questions generate in background
- **Topics**: Role excitement, relocation willingness, career goals, project discussions
- **Transition**: Automatic when questions ready + chat limit reached

### Phase 2: Structured Questions (5 questions)
- **Format**: Section-based technical screening
- **Rules**: No hints, no help, single clarification allowed
- **Tracking**: Response logging with silent evaluation
- **Fairness**: Consistent question presentation with strict guidelines

### Phase 3: Post-Interview Analysis
- **Evaluation**: Comprehensive performance analysis
- **Scoring**: Technical competency + soft skills assessment
- **Recommendation**: Final hiring decision with detailed reasoning
### Note: **These number of question scan easily be changed in the prompt by the interviewer or admin**
## 🎛️ Core Functionalities

### 1. **Intelligent Question Generation**
```python
async def generate_screening_questions_async(self):
    """
    - Analyzes JD requirements and candidate profile
    - Generates 5 personalized technical questions
    - Categorizes by difficulty and technical area
    - Saves to file for consistency
    """
```

### 2. **Adaptive Interview Management**
```python
def take_interview(self, chat_history: list) -> str:
    """
    - Phase-aware conversation handling
    - Dynamic transition between casual and structured phases
    - Rule enforcement for structured questions
    - Progress tracking and state management
    """
```

### 3. **Performance Analysis**
```python
def analyze_candidate_performance(self, chat_history: list) -> TestEvaluation:
    """
    - Technical competency scoring
    - Communication skills evaluation
    - Response quality assessment
    - Detailed feedback generation
    """
```

### 4. **Final Recommendation Engine**
```python
def generate_final_recommendation(self, chat_history: list) -> FinalCandidateReport:
    """
    - Overall profile analysis
    - Test performance integration
    - Hiring decision with confidence rating
    - Detailed reasoning and next steps
    """
```

### 5. **Tool Selection Intelligence**
```python
def get_response(self, chat_history: list):
    """
    Available Tools:
    - take_interview: Main interview conductor
    - analyze_candidate_performance: Post-question evaluation
    - generate_final_recommendation: Final hiring decision
    - end_conversation: Session termination
    """
```

## 📊 Data Structures

### Input Requirements
- **resume_details**: Dictionary with candidate's resume text
- **candidate_details**: Personal info (name, position applied)
- **jd_details**: Job description and requirements
- **add_details**: Optional additional context

### Output Formats
- **CandidateProfile**: Structured resume summary
- **TestEvaluation**: Performance analysis results
- **FinalCandidateReport**: Comprehensive hiring recommendation

## ⚡ Advanced Features

### 🔄 **Async Operations**
- Non-blocking question generation
- Background resume processing
- Concurrent initialization tasks

### 🎯 **Context-Aware Responses**
- Chat history analysis (configurable length: 2-6 messages)
- Phase-appropriate system prompts
- Custom temperature settings for different scenarios

### 🛠️ **Error Handling & Resilience**
- Fallback LLM activation on primary failure
- Graceful handling of missing candidate data
- Default value assignment for required fields

### 📈 **Scalable Configuration**
- Adjustable question count (default: 5)
- Configurable casual chat limit (default: 2)
- Customizable response length limits
- Flexible LLM endpoint configuration

## 🎨 Usage Examples

### Basic Interview Session
```python
# Start interview
response = agent.get_response(chat_history=[])

# Continue conversation
chat_history.append({"role": "assistant", "content": response})
chat_history.append({"role": "user", "content": user_input})
next_response = agent.get_response(chat_history)
```

### Custom Configuration
```python
agent = HiringAgent(
    resume_details=resume_data,
    candidate_details=candidate_info,
    jd_details=job_requirements,
    primary_llm="gemini",
    fallback_llm="hyperbolic"
)

# Modify interview parameters
agent.max_questions = 7  # Extended screening
agent.max_casual_chats = 3  # Longer casual phase
```

## 🖥️ User Interface & Application Logic

### **Streamlit Web Application**
The HiringAgent is integrated into a comprehensive Streamlit web application that provides an intuitive interface for HR professionals and candidates.

#### **Application Structure**
```
Hiring Agent Portal
├── 📝 Candidate Form Tab
│   ├── Basic Information Collection
│   ├── Resume/Document Upload
│   ├── JD Selection & Matching
│   └── Form Validation & Submission
└── 🤖 AI Chat Tab
    ├── Interview Management
    ├── Real-time Conversation
    ├── Session Tracking
    └── Interaction Limits
```

#### **Tab 1: Candidate Form (📝)**
**Purpose**: Comprehensive candidate data collection and validation

**Key Features**:
- **Smart JD Integration**: Automatically loads available job descriptions from the `JDs/` folder
- **Resume Processing**: Supports PDF/DOCX uploads with automatic text extraction
- **Data Validation**: Prevents duplicate submissions and ensures required fields
- **Professional Details**: Captures experience, tech stack, education, and social profiles
- **Location Intelligence**: Tracks current location and relocation preferences

**Form Sections**:
1. **Basic Information**: Name, email, phone, current location
2. **Position Matching**: Dynamic JD selection from available positions
3. **Professional Profile**: Experience, company, tech stack, education
4. **Social Presence**: LinkedIn, GitHub, portfolio links
5. **Document Upload**: Resume (mandatory) and additional supporting documents

**Validation Logic**:
```python
# Duplicate Prevention
def is_duplicate(first_name, last_name, email, phone):
    # Checks existing submissions to prevent duplicates
    
# Required Field Validation
required_fields = [first_name, last_name, email, phone, uploaded_file, 
                  linkedin, github, position_applied, current_location, tech_stack]
```

#### **Tab 2: AI Chat Interface (🤖)**
**Purpose**: Interactive interview management and candidate assessment

**Session Management**:
- **Unique Session IDs**: Each submission gets a UUID for tracking
- **Interaction Limits**: Maximum 15 conversations per session to ensure fair usage
- **State Persistence**: Maintains chat history and agent state throughout session
- **Auto-disable**: Form locks after submission to prevent duplicate entries

**Chat Features**:
- **Smart Agent Initialization**: Loads candidate data, resume, and JD automatically
- **Async Question Generation**: Background processing while user interacts
- **Real-time Progress Tracking**: Shows remaining interactions and usage statistics
- **Error Handling**: Graceful failure recovery with user-friendly messages

**Usage Flow**:
```python
# Agent Initialization (happens once per session)
agent = HiringAgent(
    candidate_details=session_candidate_data,
    resume_details=parsed_resume_content,
    jd_details=selected_jd_content
)
await agent.init_func()  # Async question generation

# Chat Loop
user_input → agent.get_response(chat_history) → AI response → update_session
```

### **Application Logic & State Management**

#### **Session State Variables**
```python
st.session_state = {
    "session_id": "unique_uuid",           # Session tracking
    "form_submitted": False,               # Form completion status
    "active_tab": 0,                       # Current tab index
    "jd_content_dict": {},                 # Parsed JD contents
    "candidate_data": {},                  # Form submission data
    "resume_details": {},                  # Parsed resume content
    "agent": HiringAgent_instance,         # Initialized agent
    "chat_messages": [],                   # Conversation history
    "interaction_count": 0                 # Usage tracking
    "total_time": 10`                      # Total Session duration
    "elapsed_time": 0                      # Total elapsed time
}
```



#### **File Processing Pipeline**
1. **JD Processing**: Automatically scans `JDs/` folder and parses all job descriptions
2. **Resume Upload**: Saves to `submissions/resumes/` with session-based naming
3. **Text Extraction**: Uses unified parser for PDF/DOCX processing
4. **Data Storage**: Saves all submissions to `submissions/candidates.csv`

#### **Smart JD Matching**
```python
# Dynamic JD Loading
JDs = get_jd_options()  # Scans JDs folder
jd_position_options = list(JDs.keys())

# Content Parsing & Storage
for position, file_path in JDs.items():
    jd_content = parser.extract_text(doc_path=file_path)
    st.session_state.jd_content_dict[position] = jd_content
```

### **UI/UX Design Features**

#### **User Experience Enhancements**
- **Progress Indicators**: Shows form completion and chat usage status
- **Visual Feedback**: Success messages, warnings, and error states
- **File Preview**: Shows uploaded documents in sidebar
- **Session Information**: Displays current session ID and status

#### **Safety & Usage Controls**
- **Interaction Limits**: Prevents excessive usage (15 interactions max)
- **Form Lock**: Prevents duplicate submissions once form is completed
- **Auto-redirect**: Switches to chat tab after successful form submission
- **Session Reset**: Option to start fresh session when needed

### **Error Handling & Resilience**
```python
try:
    agent = HiringAgent(...)
    asyncio.run(agent.init_func())
except Exception as e:
    st.error(f"Agent Initialization Failed: {e}")
    st.stop()
```

#### **Graceful Degradation**
- **Missing JD Files**: Falls back to text input if no JD files found
- **Resume Processing Errors**: Shows user-friendly error messages
- **Agent Failures**: Provides clear feedback and prevents app crashes
- **File Upload Issues**: Validates file types and handles upload errors

### **Data Flow Architecture**
```
User Input → Form Validation → File Processing → Data Storage → Agent Initialization → Chat Interface → Response Generation → UI Update
```

This comprehensive UI layer makes the powerful HiringAgent accessible to non-technical users while maintaining all the sophisticated AI capabilities underneath.

## 🚀 Getting Started

1. **Environment Setup**: Configure API keys and endpoints
2. **Data Preparation**: Gather resume, candidate details, and JD
3. **Agent Initialization**: Create HiringAgent instance
4. **Async Setup**: Call `init_func()` for question generation
5. **Interview Execution**: Use `get_response()` for conversation flow
6. **Analysis**: Generate final recommendations post-interview

## 📈 Performance Metrics

- **Question Generation**: ~30-60 seconds (async)
- **Response Time**: <5 seconds per interaction
- **Evaluation Accuracy**: Structured scoring with detailed feedback
- **Session Completion**: 15-25 minutes average interview time

---
