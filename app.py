import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from astrology_agent import AstrologyRAGAgent
import os

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY, 
                  dob TEXT, 
                  zodiac TEXT,
                  profession TEXT,
                  relationship_status TEXT)''')
    conn.commit()
    conn.close()

def get_user_profile(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'user_id': row[0],
            'dob': row[1],
            'zodiac': row[2],
            'profession': row[3],
            'relationship_status': row[4]
        }
    return None

def update_profile(user_id, **kwargs):
    profile = get_user_profile(user_id) or {'user_id': user_id, 'dob': None, 'zodiac': None, 'profession': None, 'relationship_status': None}
    profile.update(kwargs)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO users 
                 VALUES (?,?,?,?,?)''', 
             (profile['user_id'], profile['dob'], profile['zodiac'],
              profile['profession'], profile['relationship_status']))
    conn.commit()
    conn.close()

def get_zodiac(dob):
    try:
        date = datetime.strptime(dob, "%Y-%m-%d")
        month_day = (date.month, date.day)
        zodiac = [
            ((1, 20), (2, 18), "Aquarius"),
            ((2, 19), (3, 20), "Pisces"),
            ((3, 21), (4, 19), "Aries"),
            ((4, 20), (5, 20), "Taurus"),
            ((5, 21), (6, 20), "Gemini"),
            ((6, 21), (7, 22), "Cancer"),
            ((7, 23), (8, 22), "Leo"),
            ((8, 23), (9, 22), "Virgo"),
            ((9, 23), (10, 22), "Libra"),
            ((10, 23), (11, 21), "Scorpio"),
            ((11, 22), (12, 21), "Sagittarius"),
            ((12, 22), (1, 19), "Capricorn")
        ]
        for start, end, sign in zodiac:
            if start <= month_day <= end:
                return sign
        return "Capricorn"
    except:
        return None

def detect_intent(question):
    q = question.lower()
    if "career" in q or "job" in q or "profession" in q:
        return "career"
    elif "love" in q or "relationship" in q or "marriage" in q:
        return "love"
    elif "health" in q or "disease" in q or "sick" in q:
        return "health"
    else:
        return "general"

def required_fields_for_intent(intent):
    if intent == "career":
        return ["dob", "profession"]
    elif intent == "love":
        return ["dob", "relationship_status"]
    elif intent == "health":
        return ["dob"]
    else:
        return ["dob"]

def prompt_for_field(field):
    if field == "dob":
        return "📅 Please enter your date of birth (YYYY-MM-DD):"
    elif field == "profession":
        return "💼 What is your profession?"
    elif field == "relationship_status":
        return "💖 What is your relationship status? (Single, In a relationship, Married, Divorced)"
    else:
        return f"🔎 Please provide your {field}:"

def decorate_response(text, intent):
    if intent == "career":
        return "🚀 " + text
    elif intent == "love":
        return "💖 " + text
    elif intent == "health":
        return "🩺 " + text
    else:
        return "🔮 " + text
    
    
    
# --------- THEME & HEADLINE CSS ---------
st.set_page_config(page_title="AstroAI: Your Personalized Astrology Guide by DHIAN", page_icon="🔮", layout="wide")
st.markdown("""
    <style>
    body {
        background: linear-gradient(120deg, #7b2ff2 0%, #f357a8 100%);
        color: #fff;
    }
    .main {
        background: linear-gradient(120deg, #7b2ff2 0%, #f357a8 100%);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .headline {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #7b2ff2 40%, #f357a8 60%, #ff9800 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: 0.04em;
    }
    .subheadline {
        font-size: 1.2rem;
        color: #fff;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .stButton>button {
        background: linear-gradient(90deg, #f357a8 0%, #ff9800 100%);
        color: white;
        font-weight: bold;
        border-radius: 25px;
        padding: 10px 24px;
        border: none;
        transition: 0.2s;
        margin-top: 8px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #ff9800 0%, #f357a8 100%);
        color: #fff;
        box-shadow: 0 0 8px #ff9800;
    }
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        border-radius: 20px;
        padding: 12px;
        border: 2px solid #7b2ff2;
    }
    .stFileUploader>div>div {
        background: #fff8e1;
        border-radius: 20px;
        border: 2px dashed #ff9800;
    }
    .stChatMessage {
        background: rgba(123,47,242,0.08);
        border-radius: 16px;
        margin-bottom: 10px;
        padding: 12px;
    }
    /* Responsive tweaks for mobile */
    @media (max-width: 600px) {
        .headline { font-size: 2rem !important; }
        .subheadline { font-size: 1rem !important; }
        .block-container { padding: 0.5rem !important; }
        .stButton>button { padding: 8px 12px !important; font-size: 1rem !important; }
        .stTextInput>div>div>input, .stTextArea>div>textarea {
            font-size: 1rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="headline">🔮 AstroAI: Your Personalized Astrology Guide by DHIAN</div>', unsafe_allow_html=True)
st.markdown('<div class="subheadline">Harness the wisdom of the stars. Get insights, predictions, and guidance tailored to <b>you</b>—with a vibrant, modern touch.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🌟 About AstroAI")
    st.info("AstroAI delivers personalized, AI-powered astrology predictions. Upload your birth details and let the stars guide you!", icon="✨")

init_db()

if 'user_id' not in st.session_state:
    st.session_state.user_id = ""
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'knowledge' not in st.session_state:
    st.session_state.knowledge = ""
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'pending_field' not in st.session_state:
    st.session_state.pending_field = None
if 'pending_intent' not in st.session_state:
    st.session_state.pending_intent = None

# Centered input
col1, col2, col3 = st.columns([1,2,1])
with col2:
    user_id = st.text_input("👤 Enter your email/phone:", 
                          placeholder="user@example.com ",
                          value=st.session_state.user_id)
    
    if user_id and not st.session_state.user_id:
        st.session_state.user_id = user_id
        existing = get_user_profile(user_id)
        if existing:
            st.session_state.profile = existing
        st.rerun()

with st.expander("📁 Upload Knowledge Base", expanded=True):
    uploaded_files = st.file_uploader("📂 Upload Excel/CSV/PDF/TXT", 
                                    type=["xlsx", "csv", "pdf", "txt"],
                                    accept_multiple_files=True)
    
    if uploaded_files:
        knowledge_text = ""
        for file in uploaded_files:
            if file.name.endswith(('.xlsx', '.csv')):
                df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
                knowledge_text += df.to_markdown(index=False) + "\n\n"
            elif file.name.endswith('.pdf'):
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(file)
                knowledge_text += "\n".join([page.extract_text() for page in pdf_reader.pages])
            else:
                knowledge_text += file.getvalue().decode()
        st.session_state.knowledge = knowledge_text

if st.session_state.user_id:
      GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

    

    agent = AstrologyRAGAgent(GROQ_API_KEY, st.session_state.knowledge)
    profile = st.session_state.profile or get_user_profile(st.session_state.user_id) or {'user_id': st.session_state.user_id}

    # Display chat history with emojis
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown("🗣️ " + msg["content"])
            else:
                # Use the last intent for emoji, fallback to general
                intent = st.session_state.pending_intent or "general"
                st.markdown(decorate_response(msg["content"], intent))

    prompt = st.chat_input("💬 Ask your astrology question...")

    # Handle pending field answer
    if st.session_state.pending_field and prompt:
        field = st.session_state.pending_field
        value = prompt.strip()
        if field == "dob":
            try:
                dob = datetime.strptime(value, "%Y-%m-%d")
                zodiac = get_zodiac(value)
                update_profile(st.session_state.user_id, dob=value, zodiac=zodiac)
            except Exception:
                st.session_state.messages.append({"role": "assistant", "content": "⚠️ Please enter DOB in YYYY-MM-DD format."})
                st.rerun()
        elif field == "profession":
            update_profile(st.session_state.user_id, profession=value)
        elif field == "relationship_status":
            update_profile(st.session_state.user_id, relationship_status=value)
        # Update profile in session
        st.session_state.profile = get_user_profile(st.session_state.user_id)
        st.session_state.pending_field = None
        # After updating, check if more fields are missing for the original intent
        intent = st.session_state.pending_intent
        required_fields = required_fields_for_intent(intent)
        missing = [f for f in required_fields if not st.session_state.profile.get(f)]
        if missing:
            next_field = missing[0]
            st.session_state.pending_field = next_field
            st.session_state.messages.append({"role": "assistant", "content": prompt_for_field(next_field)})
        else:
            # All info present, provide prediction
            question = st.session_state.last_user_question
            with st.spinner("🔮 Consulting the stars..."):
                response = agent.ask(f"""
                    User Profile:
                    - DOB: {st.session_state.profile.get('dob')}
                    - Zodiac: {st.session_state.profile.get('zodiac')}
                    - Profession: {st.session_state.profile.get('profession')}
                    - Relationship Status: {st.session_state.profile.get('relationship_status')}
                    Question: {question}
                """)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.pending_intent = None
        st.rerun()

    # Handle new user question
    elif prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.last_user_question = prompt  # Save for after info collection
        intent = detect_intent(prompt)
        st.session_state.pending_intent = intent
        required_fields = required_fields_for_intent(intent)
        missing = [f for f in required_fields if not profile.get(f)]
        if missing:
            next_field = missing[0]
            st.session_state.pending_field = next_field
            st.session_state.messages.append({"role": "assistant", "content": prompt_for_field(next_field)})
            st.rerun()
        else:
            # All info present, answer directly
            with st.spinner("🔮 Consulting the stars..."):
                response = agent.ask(f"""
                    User Profile:
                    - DOB: {profile.get('dob')}
                    - Zodiac: {profile.get('zodiac')}
                    - Profession: {profile.get('profession')}
                    - Relationship Status: {profile.get('relationship_status')}
                    Question: {prompt}
                """)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
