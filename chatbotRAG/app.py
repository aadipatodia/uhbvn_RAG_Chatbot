import streamlit as st
import os
import datetime
from dotenv import load_dotenv

import google.generativeai as genai
from rag_core import setup_rag_system, search_document_scope
from app_db_manager import save_user_feedback, save_chat_session, load_chat_sessions, load_session_messages
from api_services import (
    get_accounts_by_mobile, get_account_details, get_bill_and_payment_details,
    get_last_5_complaints, get_complaint_detail_by_number, get_complaints_for_feedback,
    submit_complaint_feedback, register_technical_complaint_no_account,
    register_technical_complaint_with_account, send_bill_sms_unregistered_mobile,
    generate_callback_request, register_commercial_complaint,
    check_registration_status, check_outage_details, get_district_details,
    get_subdivision_details, get_area_details
)

# Load environment variables and configure Gemini
load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY')

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    st.error("GOOGLE_API_KEY not found. Please create a .env file and add your key.")
    st.stop()

# --- 1. CONFIGURATION AND INITIALIZATION ---

AVAILABLE_TOOLS = {
    "search_document_scope": search_document_scope,
    "get_accounts_by_mobile": get_accounts_by_mobile,
    "get_account_details": get_account_details,
    "get_bill_and_payment_details": get_bill_and_payment_details,
    "get_last_5_complaints": get_last_5_complaints,
    "get_complaint_detail_by_number": get_complaint_detail_by_number,
    "get_complaints_for_feedback": get_complaints_for_feedback,
    "submit_complaint_feedback": submit_complaint_feedback,
    "register_technical_complaint_no_account": register_technical_complaint_no_account,
    "register_technical_complaint_with_account": register_technical_complaint_with_account,
    "send_bill_sms_unregistered_mobile": send_bill_sms_unregistered_mobile,
    "generate_callback_request": generate_callback_request,
    "register_commercial_complaint": register_commercial_complaint,
    "check_registration_status": check_registration_status,
    "check_outage_details": check_outage_details,
    "get_district_details": get_district_details,
    "get_subdivision_details": get_subdivision_details,
    "get_area_details": get_area_details,
}

# Initialize Gemini Model with tools
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    tools=list(AVAILABLE_TOOLS.values()),
)

# Initialize RAG System (runs only once per Streamlit session)
if "rag_initialized" not in st.session_state:
    st.session_state["rag_initialized"] = setup_rag_system(["Chatbotv1.docx"])
    
if not st.session_state["rag_initialized"]:
    st.error("RAG system failed to initialize. Check RAG core logs.")
    st.stop()
    
# --- 2. SESSION MANAGEMENT FUNCTIONS ---

def get_session_title(messages):
    """Generates a title from the first user question."""
    if len(messages) > 1:
        first_user_prompt = messages[1].get("parts")[0].get("text", "New Chat")
        return first_user_prompt[:30].strip() + "..."
    return "New Chat Session"

def new_chat_session(save_current=True):
    """Saves the current session and starts a new one."""
    if save_current and len(st.session_state.messages) > 1:
        title = get_session_title(st.session_state.messages)
        save_chat_session(title, st.session_state.messages)

    system_prompt = "You are a helpful and friendly RAG Chatbot with access to special tools. Always use the search_document_scope tool for general knowledge questions."
    st.session_state["messages"] = [{
        "role": "user",
        "parts": [{"text": system_prompt}]
    }]
    if "feedback_submitted" in st.session_state:
        del st.session_state["feedback_submitted"]
    if "current_session_id" in st.session_state:
        del st.session_state["current_session_id"]
    if "awaiting_feedback" in st.session_state:
        del st.session_state["awaiting_feedback"]
    
    st.rerun()

def load_old_session(session_id, title):
    """Loads a chat history from the database."""
    if st.session_state.get("current_session_id") != session_id:
        st.session_state.messages = load_session_messages(session_id)
        st.session_state.current_session_id = session_id
        st.session_state.session_title = title
        if "feedback_submitted" in st.session_state:
             del st.session_state["feedback_submitted"]
        if "awaiting_feedback" in st.session_state:
             del st.session_state["awaiting_feedback"]
        st.rerun()

# --- 3. FEEDBACK LOGIC ---

def handle_feedback_submission(rating, comment):
    """Saves feedback to SQLite and triggers session save/reset."""
    log_history = st.session_state.messages[1:]
    if save_user_feedback(rating, comment, log_history):
        st.session_state.feedback_submitted = True
        new_chat_session(save_current=True) 

# Initialize Chat History
if "messages" not in st.session_state:
    new_chat_session(save_current=False)
    
# --- 4. STREAMLIT FRONTEND LAYOUT ---

st.set_page_config(page_title="RAG Chatbot Assistant", layout="wide")

# Sidebar
with st.sidebar:
    st.title("💬 Chats")
    if st.button("➕ Start New Chat", use_container_width=True, key="new_chat_btn"):
        new_chat_session(save_current=True)

    st.markdown("---")
    sessions = load_chat_sessions()
    if sessions:
        for session_id, title, timestamp in sessions:
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
                display_time = dt.strftime("%b %d, %I:%M %p")
            except ValueError:
                display_time = "Unknown time"
            
            button_label = f"{title} ({display_time})"
            if st.button(button_label, key=f"session_btn_{session_id}", use_container_width=True):
                load_old_session(session_id, title)
    else:
        st.markdown("No saved chat sessions yet.")

# Main Chat Area
st.title("💡UHBVN Chatbot Assistant")
st.markdown("Type 'exit' to end the conversation and provide feedback.")

for message in st.session_state.messages[1:]:
    role = message["role"]
    content = message.get("content") or message.get("parts")[0].get("text")
    with st.chat_message(role):
        st.markdown(content)

# --- 6. HANDLE USER INPUT ---

if not st.session_state.get("awaiting_feedback", False):
    if prompt := st.chat_input("Ask a question about bills or lodge a complaint..."):
        if prompt.lower().strip() == 'exit':
            st.session_state.awaiting_feedback = True
            st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
            st.rerun() 
        else:
            if st.session_state.get("feedback_submitted", False):
                del st.session_state["feedback_submitted"]
                
            user_message = {"role": "user", "parts": [{"text": prompt}]}
            st.session_state.messages.append(user_message)
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    chat = model.start_chat(history=st.session_state.messages)
                    response_stream = chat.send_message(prompt, stream=True)
                    full_response = ""
                    response_placeholder = st.empty()
                    for chunk in response_stream:
                        full_response += chunk.text
                        response_placeholder.markdown(full_response + " ")
                    response_placeholder.markdown(full_response)
                    
                assistant_message = {"role": "model", "parts": [{"text": full_response}]}
                st.session_state.messages.append(assistant_message)

# --- 7. FEEDBACK FORM ---

if st.session_state.get("awaiting_feedback", False) and not st.session_state.get("feedback_submitted", False):
    st.subheader("Action: End Chat and Provide Feedback")
    st.markdown("---")
    with st.form(key='feedback_form'):
        st.write("Conversation ended by 'exit'. Please rate this session:")
        rating = st.slider('Rating (1-5)', 1, 5, 5)
        comment = st.text_area('Comments / Suggestions')
        submit_button = st.form_submit_button(label='Submit Feedback & End Chat')

        if submit_button:
            if rating < 3 and not comment:
                st.warning("For ratings below 3, please comment.")
            else:
                handle_feedback_submission(rating, comment)