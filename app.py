import streamlit as st
import time
from datetime import date,timedelta
import pandas as pd
import os
from PIL import Image
import uuid
from utils.parse_docsuments import parser
from utils.hiring_agent import HiringAgent
from utils.get_JDs import get_jd_options
import asyncio

JDs = get_jd_options()
jd_position_options = list(JDs.keys()) if JDs else ["No JD files found"]

parser=parser()
resume_details={}
add_data={}
candidate_data={}

st.set_page_config(
    page_title="Hiring Agent Portal",
    page_icon=":briefcase:",
    layout="wide"
)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0
if "jd_content_dict" not in st.session_state:
    st.session_state.jd_content_dict = {}
if "resume_details" not in st.session_state:
    st.session_state.resume_details={}

# Function to parse and store JD content
def parse_and_store_jd_content():
    """Parse JD files and store their content in session state"""
    if JDs and st.session_state.jd_content_dict == {}: 
        for jd_position, jd_file_path in JDs.items():
            if jd_file_path and os.path.exists(jd_file_path):
                try:
                    jd_content = parser.extract_text(doc_path=jd_file_path)
                    st.session_state.jd_content_dict[jd_position] = jd_content
                except Exception as e:
                    print(f"Error parsing JD file {jd_file_path}: {str(e)}")
                    st.session_state.jd_content_dict[jd_position] = f"Error parsing JD: {str(e)}"
            else:
                st.session_state.jd_content_dict[jd_position] = "JD file not found or path is empty"

parse_and_store_jd_content()

col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("assets/logo.png"):
        st.image(Image.open("assets/logo.png"), width=100)
    else:
        st.write("🏢")  # Placeholder if logo doesn't exist

with col2:
    st.markdown("""
    <div class="title-section">
        <h1 style="margin-bottom: 0;">Candidate Hiring Portal</h1>
        <p style="margin-top: 0; font-size: 16px; color: #666;">Complete the form below to submit a candidate for consideration</p>
    </div>
    """, unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["📝 Candidate Form", "🤖 AI Chat"])

# Functions
def is_duplicate(first_name, last_name, email, phone):
    if os.path.exists("submissions/candidates.csv"):
        existing_df = pd.read_csv("submissions/candidates.csv")
        if len(existing_df) > 0:
            match = existing_df[
                (existing_df["first_name"].str.lower() == first_name.lower()) &
                (existing_df["last_name"].str.lower() == last_name.lower()) &
                (existing_df["email"].str.lower() == email.lower()) &
                (existing_df["phone"] == phone)
            ]
            return not match.empty
    return False

def switch_to_chat_tab():
    """Switch to AI Chat tab and disable form"""
    st.session_state.form_submitted = True
    st.session_state.active_tab = 1

with tab1:
    # Disable form if already submitted
    form_disabled = st.session_state.form_submitted
    
    if form_disabled:
        st.info("✅ Form has been submitted successfully! Please use the AI Chat tab for further interactions.")
        st.markdown("---")
        
        
        # Show submitted data summary
        if os.path.exists("submissions/candidates.csv"):
            df = pd.read_csv("submissions/candidates.csv")
            latest_submission = df[df["session_id"] == st.session_state.session_id].tail(1)
            if not latest_submission.empty:
                st.subheader("Submitted Candidate Details:")
                submission = latest_submission.iloc[0]
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {submission['first_name']} {submission['last_name']}")
                    st.write(f"**Email:** {submission['email']}")
                    st.write(f"**Phone:** {submission['phone']}")
                    st.write(f"**Position:** {submission['position_applied']}")
                    st.write(f"**Current Location:** {submission.get('current_location', 'N/A')}")
                with col2:
                    st.write(f"**Current Company:** {submission.get('current_company', 'N/A')}")
                    st.write(f"**Experience:** {submission['years_experience']} years")
                    # st.write(f"**Hiring Stage:** {submission['hiring_stage']}")
                    st.write(f"**Ready to Relocate:** {'Yes' if submission.get('ready_to_relocate', False) else 'No'}")
                    st.write(f"**Submission Date:** {submission['submission_date']}")
        
        # Button to reset form (for new submission)
        # if st.button("🔄 Start New Submission", type="secondary"):
        #     st.session_state.form_submitted = False
        #     st.session_state.session_id = str(uuid.uuid4())
        #     st.rerun()
    
    else:
        # Main Form
        with st.form(key="hiring_form", clear_on_submit=False):
            st.header("Candidate Information")
            
            # Basic Info
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name*", placeholder="John", key="form_first_name")
            with col2:
                last_name = st.text_input("Last Name*", placeholder="Doe", key="form_last_name")
            
            email = st.text_input("Email*", placeholder="john.doe@example.com", key="form_email")
            phone = st.text_input("Phone*", placeholder="+91 0123456789", key="form_phone")
            
            # Location Information
            st.subheader("Location Details")
            col1, col2 = st.columns([2, 1])
            with col1:
                current_location = st.text_input("Current Location*", placeholder="Mumbai, Maharashtra, India", key="form_current_location")
                ready_to_relocate = st.checkbox("Ready to Relocate(If Required)", key="form_ready_to_relocate")
            # Hiring Details
            st.subheader("Hiring Information")
            col1, col2 = st.columns(2)
            with col1:
                # Use selectbox with JD options
                if jd_position_options and jd_position_options[0] != "No JD files found":
                    position_applied = st.selectbox(
                        "Position Applying For(Only available jobs right now!)*", 
                        options=jd_position_options,
                        key="form_position_applied",
                        help=f"Available positions from JD files: {len(jd_position_options)} options"
                    )
                else:
                    position_applied = st.text_input("Position Applying For*", placeholder="Software Engineer", key="form_position_applied")
                    st.warning("⚠️ No JD files found in JDs folder. Using text input instead.")
                    
            # with col2:
            #     hiring_stage = st.selectbox(
            #         "Current Hiring Stage*",
            #         ["Sourced", "Screen", "Interview", "Offer", "Hired"],
            #         key="form_hiring_stage"
            #     )
            with col2:
                expected_salary = st.slider("Expected Salary (₹ LPA)*", 0, 30, 1, key="form_expected_salary")
            # Professional Info
            st.subheader("Professional Details")
            institute = st.text_input("Institute/University", placeholder="ABC Institute/University", key="institute")
            major = st.text_input("Major", placeholder="CSE/ECE...", key="major")
            current_company = st.text_input("Current Company", placeholder="Acme Inc.", key="form_current_company")
            current_title = st.text_input("Current Title", placeholder="Senior Developer", key="form_current_title")
            years_experience = st.slider("Years of Experience", 0, 30, 1, key="form_years_experience")
            tech_stack = st.text_input("Tech Stack (comma-separated)*", placeholder="Python, Cpp, Scrum Master, etc", key="form_tech_stack")

            # Social Links
            st.subheader("Social Profiles")
            linkedin = st.text_input("LinkedIn URL*", placeholder="https://linkedin.com/in/username", key="form_linkedin")
            github = st.text_input("GitHub URL*", placeholder="https://github.com/username", key="form_github")
            portfolio = st.text_input("Portfolio Website", placeholder="https://yourportfolio.com", key="form_portfolio")
            
            # Resume Upload
            st.subheader("Resume/CV Upload*")
            uploaded_file = st.file_uploader(
                "Upload candidate's resume (PDF/Docx files only)", 
                type=["pdf","docx"],
                accept_multiple_files=False,
                key="form_uploaded_file"
            )
            
            # Additional Documents
            # st.subheader("Additional Documents")
            # additional_files = st.file_uploader(
            #     "Upload supporting documents (certificates, references, etc.)",
            #     type=["pdf", "docx", "png", "jpg"],
            #     accept_multiple_files=True,
            #     help="Can be Blank!",
            #     key="form_additional_files"
            # )
            

            # Terms and Submit
            agree = st.checkbox("I confirm this candidate has consented to share their information*", key="form_agree")
            
            submitted = st.form_submit_button("Submit Candidate", type="primary")
    
        if submitted:
           # Updated validation to include current_location
            if not all([first_name, last_name, email, phone, uploaded_file, linkedin, github, position_applied, expected_salary, current_location,tech_stack,agree]):
                st.error("Please fill all required fields (*)")
            elif is_duplicate(first_name, last_name, email, phone):
                st.error("This candidate has already been submitted!")
            else:
                # Process the form data
                candidate_data = {
                    "session_id": st.session_state.session_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone,
                    "current_location": current_location,
                    "ready_to_relocate": ready_to_relocate,
                    "institute": institute,
                    "major": major,
                    "current_company": current_company,
                    "current_title": current_title,
                    "years_experience": years_experience,
                    "linkedin": linkedin,
                    "github": github,
                    "portfolio": portfolio,
                    "position_applied": position_applied,
                    # "hiring_stage": hiring_stage,
                    "expected_salary": expected_salary,
                    "tech_stack": tech_stack,
                    "submission_date": date.today().strftime("%Y-%m-%d"),
                    "jd_file_path": JDs.get(position_applied, "") if position_applied in JDs else ""
                }


                print(f"\ncandidate_details: {candidate_data}\n")
                print(f"Available JD positions: {list(JDs.keys())}\n")
                print(f"Selected JD file: {JDs.get(position_applied, 'Not found')}\n")
                print(f"JD Content Dictionary: {st.session_state.jd_content_dict}\n")
                
                # Save resume with session ID
                if uploaded_file:
                    os.makedirs("submissions/resumes", exist_ok=True)
                    resume_path = f"submissions/resumes/{first_name}_{last_name}_{st.session_state.session_id}_resume.{uploaded_file.name.split('.')[-1]}"
                    with open(resume_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    resume_details_ = parser.extract_text(doc_path=resume_path)
                    print(f"\nparsed_resume_data: \n {resume_details_}")
                    candidate_data["resume_path"] = resume_path
                
                st.session_state.candidate_data = candidate_data
                st.session_state.resume_details= {"resume_details": str(resume_details_)}
                st.session_state.add_data = add_data


                # Save additional files with session ID
                # if additional_files:
                #     additional_paths = []
                #     os.makedirs("submissions/additional", exist_ok=True)
                #     for i, file in enumerate(additional_files):
                #         file_path = f"submissions/additional/{st.session_state.session_id}_additional_{i+1}.{file.name.split('.')[-1]}"
                #         with open(file_path, "wb") as f:
                #             f.write(file.getbuffer())
                #         additional_paths.append(file_path)
                #         add_data[f"data_{i+1}"] = parser.extract_add_doc_text(add_doc_path=file_path)

                #     candidate_data["additional_files"] = str(additional_paths)
                
                # Save to CSV
                df = pd.DataFrame([candidate_data])
                if not os.path.exists("submissions/candidates.csv"):
                    df.to_csv("submissions/candidates.csv", index=False)
                else:
                    existing_df = pd.read_csv("submissions/candidates.csv")
                    updated_df = pd.concat([existing_df, df], ignore_index=True)
                    updated_df.to_csv("submissions/candidates.csv", index=False)
                
                st.success("✅ Candidate submitted successfully!")
                st.balloons()
                time.sleep(2)

                # Set form submitted state
                st.session_state.form_submitted = True
                st.session_state.active_tab = 1  # Switch to Tab 2
                st.session_state.show_switch_button = True  # Enable manual switch button
                st.rerun()

with tab2:
    
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = time.time()
        st.session_state.elapsed_time = 0
        st.session_state.total_time=10
    # Calculate elapsed time properly
    st.session_state.elapsed_seconds = time.time() - st.session_state.session_start_time
    st.session_state.elapsed_time = int(st.session_state.elapsed_seconds)  # Store as integer for sidebar
    elapsed_time_str = str(timedelta(seconds=int(st.session_state.elapsed_seconds)))
    
    st.header("🤖 AI Chat Assistant")
    st.markdown(f"**Session ID:** `{st.session_state.session_id}`")
    st.markdown(f"⏱️ **Total Allowed time:** `{st.session_state.total_time}:00 min`")
    st.markdown(f"⏱️ **Session Duration:** `{elapsed_time_str}`")

    # Initialize interaction counter
    if "interaction_count" not in st.session_state:
        st.session_state.interaction_count = 0

    max_interactions = 15
    remaining_interactions = max_interactions - st.session_state.interaction_count

    # Check for timeout first (before any other processing)
    if st.session_state.elapsed_seconds > st.session_state.total_time*60:
        st.session_state["timeout_occurred"] = True
        st.error("⏰ Interview session has timed out (3 minutes).")
        st.markdown(f"""
            ### ⏰ Session Timeout
            
            Your session has exceeded the 3-minute time limit.
            
            - **Total Duration:** `{elapsed_time_str}`
            - **Interactions Used:** `{st.session_state.interaction_count}/{max_interactions}`
            
            Please start a new session to continue.
        """)
        
        if st.button("🔄 Start New Session", type="primary"):
            # Reset all session state
            st.session_state.form_submitted = False
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.interaction_count = 0
            st.session_state.timeout_occurred = False
            st.session_state.limit_reached = False
            # Clear other session data
            for key in ["chat_messages", "agent", "session_start_time", "elapsed_time", "elapsed_seconds"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.stop()

    # Display interaction limits
    if remaining_interactions > 0:
        if remaining_interactions <= 1:
            st.warning(f"⚠️ **Only {remaining_interactions} interaction remaining**. Chat will end soon.")
        else:
            st.info(f"💬 **{remaining_interactions} interactions remaining**.")
    else:
        st.error("🚫 **Chat limit reached** - No more interactions available.")

    st.markdown("---")

    # Ensure form is submitted before proceeding
    if not st.session_state.form_submitted:
        st.info("👋 Please submit the candidate form first to unlock the AI chat functionality.")
        st.stop()

    # Check if interaction limit is reached
    if st.session_state.interaction_count >= max_interactions:
        st.session_state["limit_reached"] = True
        st.error("🚫 **Chat Session Ended**")
        st.markdown(f"""
        ### 🚫 Session Limit Reached

        You have reached the maximum of {max_interactions} interactions for this session. This is to ensure fair usage.

        - **Session Duration:** `{elapsed_time_str}`
        - **Interactions Used:** `{max_interactions}/{max_interactions}`

        **Next Steps:**
        - Review your conversation above
        - Submit a new form to start a fresh session
        - Contact support if needed
        """)
        
        if st.button("🔄 Start New Session", type="primary"):
            st.session_state.form_submitted = False
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.interaction_count = 0
            st.session_state.limit_reached = False
            st.session_state.timeout_occurred = False
            if "chat_messages" in st.session_state:
                del st.session_state.chat_messages
            for key in ["agent", "session_start_time", "elapsed_time", "elapsed_seconds"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.stop()

    # Check for other session states (these should not trigger now due to above checks)
    if st.session_state.get("timeout_occurred"):
        st.error("⏰ Session timed out due to inactivity or duration limit.")
        st.stop()
    elif st.session_state.get("limit_reached"):
        st.error("🚫 Chat session disabled due to reaching the interaction limit.")
        st.stop()

    # Initialize agent
    if "agent" not in st.session_state:
        try:
            agent = HiringAgent(
                candidate_details=st.session_state.get("candidate_data", {}),
                resume_details=st.session_state.get("resume_details", {}),
                add_details=st.session_state.get("add_data", {}),
                jd_details=st.session_state.get("jd_content_dict", {})
            )
            
            asyncio.run(agent.init_func())
            st.session_state.agent = agent 

        except Exception as e:
            st.error(f"Agent Initialization Failed: {e}")
            st.stop()
    
    agent = st.session_state.agent

    # Initialize chat
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": agent.greet_candidate()}
        ]

    # Display chat messages
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(str(msg["content"]))

    st.markdown("---")

    # Chat input
    if remaining_interactions > 0:
        prompt = st.chat_input("Ask me anything about the candidate, interview, or hiring process...")
    else:
        st.chat_input("Chat limit reached - no more interactions available", disabled=True)

    # Process user input
    if prompt and remaining_interactions > 0:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        end_list = ["end_chat", "end_conversation"]
        try:
            chat_history = st.session_state.chat_messages
            intent = prompt.strip().lower()

            response = agent.get_response(chat_history=chat_history)
            
            # Check for early termination
            if remaining_interactions >= 16:  # This condition seems wrong, maybe should be <= 1?
                if intent in end_list or response in end_list:
                    st.rerun()
        except Exception as e:
            response = f"⚠️ Sorry, I encountered an error: for {intent} : {e}"

        if response:
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
            
            # Increment interaction count
            st.session_state.interaction_count += 1
            
            # Check if limit reached after increment
            if st.session_state.interaction_count >= max_interactions:
                st.rerun()


# ---------------------- Sidebar --------------------------
st.sidebar.header("Session Information")
st.sidebar.markdown(f"**Current Session:** `{st.session_state.session_id[:8]}...`")
st.sidebar.markdown(f"**Form Status:** {'✅ Submitted' if st.session_state.form_submitted else '📝 Pending'}")

# Fix elapsed time display in sidebar
if "elapsed_time" in st.session_state:
    elapsed_minutes = st.session_state.elapsed_time // 60
    elapsed_seconds_remainder = st.session_state.elapsed_time % 60
    st.sidebar.markdown(f"**Total Time Allowed:** ⏰ {st.session_state.total_time}m 0s")
    st.sidebar.markdown(f"**Elapsed Time:** ⏰ {elapsed_minutes}m {elapsed_seconds_remainder}s")
else:
    st.sidebar.markdown(f"**Elapsed Time:** ⏰ 0m 0s")

if st.session_state.form_submitted:
    used = st.session_state.get("interaction_count", 0)
    left = max_interactions - used
    st.sidebar.markdown("---")
    st.sidebar.header("Chat Usage")
    st.sidebar.markdown(f"**Interactions Used:** {used}/{max_interactions}")
    st.sidebar.markdown(f"**Remaining:** {left}")
    st.sidebar.progress(used / max_interactions)

    if left <= 5 and left > 0:
        st.sidebar.warning("⚠️ Chat limit almost reached!")
    elif left == 0:
        st.sidebar.error("🚫 Chat limit reached")
    
    # Time warnings
    remaining_time = (st.session_state.total_time)*60 - st.session_state.get("elapsed_time", 0)
    if remaining_time <= 120 and remaining_time > 0:
        st.sidebar.warning(f"⚠️ Less than {remaining_time} seconds left!")
    elif remaining_time <= 0:
        st.sidebar.error("🚫 Time Limit Exceeded!!")

# Show uploaded files (before submission)
if not st.session_state.form_submitted:
    uploaded_file = st.session_state.get("form_uploaded_file")
    additional_files = st.session_state.get("form_additional_files")

    if uploaded_file or additional_files:
        st.sidebar.header("Uploaded Files Preview")
        if uploaded_file:
            st.sidebar.markdown(f"""
            <div class="uploadedFile">
                <strong>Resume:</strong> {uploaded_file.name}<br>
                <small>Type: {uploaded_file.type}</small>
            </div>
            """, unsafe_allow_html=True)

        if additional_files:
            st.sidebar.markdown("<strong>Additional Files:</strong>", unsafe_allow_html=True)
            for file in additional_files:
                st.sidebar.markdown(f"""
                <div class="uploadedFile">
                    {file.name}<br>
                    <small>Type: {file.type}</small>
                </div>
                """, unsafe_allow_html=True)

# Sidebar Instructions
st.sidebar.header("How to Use")
st.sidebar.markdown(f"""
1. Complete the candidate form
2. Upload a resume (mandatory)
3. Submit additional relevant files
4. Submit the form to unlock AI Assistant
5. Chat with the assistant for:
   - Profile insights
   - Interview questions
   - Hiring recommendations

⚠️ *Interaction limit is {max_interactions} per session.*
⏰ *Total Time limit is {st.session_state.total_time} minutes per session.*
""")