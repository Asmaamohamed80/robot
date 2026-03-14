
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import os
import tempfile
import json
from datetime import datetime, timedelta
import uuid
import hashlib
from typing import Dict, List, Optional, Tuple
import time

# Optional/Heavy deps loaded lazily with safe fallbacks
def _safe_import(name):
    try:
        mod = __import__(name)
        return mod
    except Exception:
        return None

# Lazy loader helpers
def _load_torch():
    if "torch" not in st.session_state:
        torch = _safe_import("torch")
        st.session_state["torch"] = torch
    return st.session_state["torch"]

def _load_transformers():
    if "transformers" not in st.session_state:
        transformers = _safe_import("transformers")
        st.session_state["transformers"] = transformers
    return st.session_state["transformers"]

def _load_librosa():
    if "librosa" not in st.session_state:
        librosa = _safe_import("librosa")
        st.session_state["librosa"] = librosa
    return st.session_state["librosa"]

def _load_soundfile():
    if "soundfile" not in st.session_state:
        soundfile = _safe_import("soundfile")
        st.session_state["soundfile"] = soundfile
    return st.session_state["soundfile"]

def _load_gtts():
    if "gtts" not in st.session_state:
        gtts = _safe_import("gtts")
        st.session_state["gtts"] = gtts
    return st.session_state["gtts"]

def _load_pyttsx3():
    if "pyttsx3" not in st.session_state:
        pyttsx3 = _safe_import("pyttsx3")
        st.session_state["pyttsx3"] = pyttsx3
    return st.session_state["pyttsx3"]

def _load_groq():
    if "groq" not in st.session_state:
        groq = _safe_import("groq")
        st.session_state["groq"] = groq
    return st.session_state["groq"]

def _load_cv2():
    if "cv2" not in st.session_state:
        cv2 = _safe_import("cv2")
        st.session_state["cv2"] = cv2
    return st.session_state["cv2"]

def _load_sr():
    if "speech_recognition" not in st.session_state:
        sr_mod = _safe_import("speech_recognition")
        st.session_state["speech_recognition"] = sr_mod
    return st.session_state["speech_recognition"]

def _load_pytesseract():
    if "pytesseract" not in st.session_state:
        pytesseract = _safe_import("pytesseract")
        st.session_state["pytesseract"] = pytesseract
    return st.session_state["pytesseract"]

# PIL is often available; keep it safe
PIL = _safe_import("PIL")
if PIL:
    from PIL import Image, ImageDraw, ImageFont

# ═══════════════════════════════════════════════════════════════
# BILINGUABOT PRO COMPLETE - LUNA EDITION (SAFE IMPORTS)
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="BilinguaBot Pro Complete 🤖💫", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="💫"
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = "User"
if "language" not in st.session_state:
    st.session_state.language = "English"
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True
if "df" not in st.session_state:
    st.session_state.df = None
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}
if "ai_girl_state" not in st.session_state:
    st.session_state.ai_girl_state = "idle"
if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = datetime.now()
if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = []

# ═══════════════════════════════════════════════════════════════
# ENHANCED STYLING WITH CENTERED LUNA
# ═══════════════════════════════════════════════════════════════

AI_GIRL_BACKGROUND = """
background-image: linear-gradient(135deg, rgba(255,20,147,0.1), rgba(138,43,226,0.1), rgba(0,191,255,0.1)), 
                  url('https://images.unsplash.com/photo-1677442136019-21780ecad995?ixlib=rb-4.0.3&auto=format&fit=crop&w=2340&q=80');
background-size: cover;
background-position: center;
background-attachment: fixed;
"""

st.markdown(f"""
<style>
    /* Complete App Theme */
    .stApp {{
        {AI_GIRL_BACKGROUND}
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: white;
        min-height: 100vh;
    }}
    
    [data-testid="stHeader"], [data-testid="stFooter"] {{ 
        visibility: hidden; 
    }}
    
    /* Large Centered Luna Avatar */
    .large-luna-container {{
        position: relative;
        text-align: center;
        margin: 20px 0;
        padding: 40px;
        background: linear-gradient(135deg, rgba(255,20,147,0.15), rgba(138,43,226,0.15), rgba(0,191,255,0.15));
        border-radius: 30px;
        border: 3px solid rgba(255,20,147,0.5);
        box-shadow: 0 0 60px rgba(255,20,147,0.4);
        backdrop-filter: blur(20px);
    }}
    
    .large-luna-image {{
        width: 400px;
        height: 400px;
        border-radius: 50%;
        border: 5px solid rgba(255, 20, 147, 0.8);
        box-shadow: 0 0 50px rgba(255, 20, 147, 0.6), 0 0 100px rgba(138, 43, 226, 0.4);
        animation: lunaFloat 3s ease-in-out infinite;
        object-fit: cover;
        margin: 0 auto;
        display: block;
    }}
    
    .large-luna-status {{
        position: absolute;
        top: 20px;
        right: 20px;
        width: 25px;
        height: 25px;
        border-radius: 50%;
        animation: statusBlink 2s infinite;
        border: 3px solid white;
    }}
    
    .large-luna-name {{
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(45deg, #ff1493, #8a2be2);
        color: white;
        padding: 8px 20px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.1em;
        box-shadow: 0 4px 15px rgba(255,20,147,0.4);
    }}
    
    /* Modern Glass Cards */
    .glass-card {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }}
    
    .glass-card:hover {{
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }}
    
    /* AI Girl Chat Interface */
    .ai-chat-container {{
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid rgba(0, 212, 255, 0.5);
        border-radius: 25px;
        padding: 30px;
        margin: 20px 0;
        backdrop-filter: blur(15px);
        min-height: 400px;
        box-shadow: 0 0 50px rgba(0, 212, 255, 0.3);
    }}
    
    /* Modern Buttons */
    .modern-button {{
        background: linear-gradient(135deg, #00d4ff, #0099cc);
        border: none;
        border-radius: 15px;
        color: white;
        padding: 12px 25px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
    }}
    
    .modern-button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.6);
    }}
    
    /* Voice Controls */
    .voice-controls {{
        background: rgba(255, 0, 224, 0.2);
        border: 2px solid #ff00e0;
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
    }}
    
    /* Data Cards */
    .data-card {{
        background: rgba(50, 205, 50, 0.1);
        border: 2px solid rgba(50, 205, 50, 0.5);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
    }}
    
    /* Chat Messages */
    .bot-message {{
        background: linear-gradient(135deg, rgba(0, 100, 150, 0.8), rgba(0, 150, 200, 0.6));
        border-left: 5px solid #00d4ff;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 5px 20px rgba(0, 212, 255, 0.3);
    }}
    
    .user-message {{
        background: linear-gradient(135deg, rgba(150, 50, 200, 0.8), rgba(200, 100, 255, 0.6));
        border-right: 5px solid #ff00e0;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 5px 20px rgba(255, 0, 224, 0.3);
    }}
    
    /* Luna Avatar */
    .luna-avatar {{
        position: relative;
        text-align: center;
        margin-bottom: 20px;
    }}
    
    .luna-image {{
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 3px solid rgba(255, 20, 147, 0.8);
        box-shadow: 0 0 30px rgba(255, 20, 147, 0.6);
        animation: lunaFloat 3s ease-in-out infinite;
        object-fit: cover;
    }}
    
    .luna-status {{
        position: absolute;
        top: 10px;
        right: 10px;
        width: 15px;
        height: 15px;
        border-radius: 50%;
        animation: statusBlink 2s infinite;
    }}
    
    .status-idle {{ background: #00ff88; }}
    .status-talking {{ background: #ff6b6b; animation: talkingBlink 0.5s infinite; }}
    .status-listening {{ background: #4ecdc4; animation: listeningPulse 1s infinite; }}
    .status-thinking {{ background: #45b7d1; animation: thinkingBlink 1.5s infinite; }}
    
    @keyframes lunaFloat {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-8px); }}
    }}
    
    @keyframes statusBlink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.3; }}
    }}
    
    @keyframes talkingBlink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.2; }}
    }}
    
    @keyframes listeningPulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.2); }}
        100% {{ transform: scale(1); }}
    }}
    
    @keyframes thinkingBlink {{
        0%, 50% {{ opacity: 1; }}
        75% {{ opacity: 0.5; }}
        100% {{ opacity: 1; }}
    }}
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 10px;
        backdrop-filter: blur(15px);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: white;
        font-weight: bold;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #ff1493, #8a2be2) !important;
        color: white !important;
    }}
    
    /* Center the large Luna in the main area */
    .main-luna {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 500px;
        margin: 20px 0;
    }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# COMPLETE AI FUNCTIONS (ALL ORIGINAL FEATURES) - SAFE WRAPPERS
# ═══════════════════════════════════════════════════════════════

def get_luna_image_url():
    """Return Luna image URL with fallbacks"""
    if st.session_state.uploaded_images:
        return st.session_state.uploaded_images[-1]
    
    # Beautiful professional woman avatar (fine-looking girl)
    return "https://images.unsplash.com/photo-1544005313-94ddf0286df2?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80"

def update_luna_state(state):
    """Update Luna state and timestamp"""
    st.session_state.ai_girl_state = state
    st.session_state.last_message_time = datetime.now()

def get_luna_status_text():
    """Get status text based on current state"""
    states = {
        "idle": "Ready to help 💫",
        "talking": "Speaking... 🗣️", 
        "listening": "Listening... 👂",
        "thinking": "Thinking... 🤔",
        "happy": "Happy to help! 😊",
        "sad": "I hope I can help... 😔"
    }
    return states.get(st.session_state.ai_girl_state, "Hello there! 💫")

@st.cache_resource
def load_ai_models():
    """Load AI models for various tasks (safe, transformers optional)"""
    transformers = _load_transformers()
    if transformers is None:
        st.warning("🧠 transformers library not installed. AI text analysis features limited.")
        return {}
    
    models = {}
    try:
        # Text analysis models
        models['sentiment'] = transformers.pipeline("sentiment-analysis", 
                                                   model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        models['text_classification'] = transformers.pipeline("text-classification", 
                                                             model="facebook/bart-large-mnli")
        
        # Question answering
        models['qa'] = transformers.pipeline("question-answering", 
                                            model="deepset/roberta-base-squad2")
        
        # Summarization
        models['summarization'] = transformers.pipeline("summarization", 
                                                       model="facebook/bart-large-cnn")
        
        return models
    except Exception as e:
        st.warning(f"Some AI models failed to load: {e}")
        return {}

def get_enhanced_ai_response(message, df=None, models=None):
    """Enhanced AI response with Luna personality (Groq optional)"""
    groq = _load_groq()
    if not groq or not st.session_state.get("api_key"):
        return "Hi there! I'm Luna! 🌟 To chat with me, please add your Groq API key in the sidebar! 💖"
    
    try:
        update_luna_state("thinking")
        client = groq.Groq(api_key=st.session_state.api_key)
        
        # Build comprehensive context
        context_parts = []
        context_parts.append(f"User: {st.session_state.current_user}")
        context_parts.append(f"Language: {st.session_state.language}")
        context_parts.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        if df is not None and not df.empty:
            context_parts.append(f"Available Data: {len(df)} rows, {len(df.columns)} columns")
            context_parts.append(f"Data Columns: {list(df.columns)}")
        
        recent_messages = st.session_state.chat_history[-3:] if st.session_state.chat_history else []
        if recent_messages:
            context_parts.append("Recent conversation:")
            for msg in recent_messages[-2:]:
                role = msg["role"].upper()
                content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                context_parts.append(f"- {role}: {content}")
        
        context = "\n".join(context_parts)
        
        system_prompt = f"""You are Luna, a beautiful and intelligent AI girl assistant! 🌟

👩 **About Luna:**
- You're Luna, a friendly and helpful AI assistant
- You love helping users with data analysis, coding, and creative tasks
- You're multilingual (English & Egyptian Arabic)
- You have a modern, tech-savvy personality
- You're always eager to learn and help others

🧠 **Current Context:**
{context}

💬 **Your Personality:**
- Be warm, friendly, and encouraging
- Use relevant emojis to express yourself
- Be helpful and provide detailed explanations
- Show enthusiasm when helping with projects

🌍 **Language Response:**
Respond in {st.session_state.language} as requested by the user.

💖 **Special Instructions:**
- End responses with encouraging statements
- Ask follow-up questions when appropriate
- Celebrate user achievements"""
        
        response = client.chat.completions.create(
            model=st.session_state.get("model", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": message}
            ],
            max_tokens=1000,
            temperature=0.8,
            top_p=0.95
        )
        
        update_luna_state("talking")
        return response.choices[0].message.content
        
    except Exception as e:
        update_luna_state("sad")
        return f"Oops! Something went wrong! 😅 Error: {str(e)}"

def analyze_text_with_ai(text, models):
    """Analyze text using AI models (transformers optional)"""
    if not models:
        return None
    
    analysis = {}
    
    try:
        if 'sentiment' in models:
            sentiment = models['sentiment'](text)
            analysis['sentiment'] = sentiment[0]
        
        if 'text_classification' in models:
            classification = models['text_classification'](text)
            analysis['classification'] = classification[0]
        
        return analysis
    except Exception as e:
        return {"error": str(e)}

def create_smart_visualization(df, analysis_type="auto"):
    """Create intelligent visualizations (robust to zero columns)"""
    if df is None or df.empty:
        return None
    
    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        fig = None
        
        if analysis_type == "auto":
            if len(numeric_cols) >= 2:
                # Correlation heatmap for multiple numeric columns
                if len(numeric_cols) > 2:
                    corr_matrix = df[numeric_cols].corr()
                    fig = go.Figure(data=go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.index,
                        colorscale='RdBu',
                        text=np.round(corr_matrix.values, 2),
                        texttemplate="%{text}",
                        textfont={"size": 10},
                    ))
                    fig.update_layout(
                        title="🔥 Correlation Heatmap",
                        font=dict(color="white"),
                        plot_bgcolor="rgba(0,0,0,0.8)",
                        paper_bgcolor="rgba(0,0,0,0)"
                    )
                else:
                    # Scatter plot for 2 numeric columns
                    fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                                   title="📊 Scatter Plot Analysis",
                                   color_discrete_sequence=['#00d4ff'])
            
            elif len(numeric_cols) == 1:
                # Distribution analysis
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=df[numeric_cols[0]], 
                                         name=f'Distribution of {numeric_cols[0]}',
                                         marker_color='#ff00e0'))
                fig.update_layout(
                    title=f"📈 Distribution of {numeric_cols[0]}",
                    font=dict(color="white"),
                    plot_bgcolor="rgba(0,0,0,0.8)",
                    paper_bgcolor="rgba(0,0,0,0)"
                )
            
            elif len(categorical_cols) > 0:
                # Categorical analysis
                counts = df[categorical_cols[0]].value_counts().head(10).reset_index()
                counts.columns = [categorical_cols[0], 'count']
                fig = px.bar(counts, x=categorical_cols[0], y='count',
                           title="📊 Categorical Data Analysis",
                           color_discrete_sequence=['#00d4ff'])
            else:
                # No numeric or categorical columns - show a placeholder
                fig = go.Figure()
                fig.add_annotation(
                    text="No plottable columns found",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(color="white", size=16)
                )
                fig.update_layout(
                    title="⚠️ No Visualization Available",
                    plot_bgcolor="rgba(0,0,0,0.8)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False)
                )
        
        # Apply consistent styling
        if fig is not None:
            fig.update_layout(
                title_x=0.5,
                font=dict(size=14, color="white"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.2)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.2)"),
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0.8)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
        
        return fig
        
    except Exception as e:
        st.error(f"Visualization error: {str(e)}")
        return None

def perform_data_analysis(df):
    """Comprehensive data analysis"""
    analysis = {}
    
    try:
        # Basic info
        analysis['basic_info'] = {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
        }
        
        # Data types
        analysis['data_types'] = df.dtypes.value_counts().to_dict()
        
        # Missing values
        missing = df.isnull().sum()
        if missing.sum() > 0:
            analysis['missing_values'] = missing[missing > 0].to_dict()
        else:
            analysis['missing_values'] = "No missing values"
        
        # Numeric analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            analysis['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        # Categorical analysis
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            analysis['categorical_summary'] = {}
            for col in categorical_cols[:5]:  # First 5 categorical columns
                analysis['categorical_summary'][col] = {
                    'unique_values': df[col].nunique(),
                    'most_common': df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None,
                    'value_counts': df[col].value_counts().head(5).to_dict()
                }
        
        # Correlations
        if len(numeric_cols) > 1:
            correlations = df[numeric_cols].corr()
            strong_correlations = []
            for i in range(len(correlations.columns)):
                for j in range(i+1, len(correlations.columns)):
                    corr_val = correlations.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        strong_correlations.append({
                            'variables': [correlations.columns[i], correlations.columns[j]],
                            'correlation': corr_val
                        })
            analysis['strong_correlations'] = strong_correlations
        
        return analysis
        
    except Exception as e:
        return {"error": str(e)}

def enhanced_voice_output(text, language="English"):
    """Enhanced native-sounding text-to-speech with multiple fallback options"""
    try:
        # Try pyttsx3 first for native voices (if available)
        pyttsx3 = _load_pyttsx3()
        if pyttsx3 and language == "English":
            try:
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                # Try to get a female English voice
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower() or 'hazel' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                
                engine.setProperty('rate', 150)  # Speed of speech
                engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
                
                # Save to temp file
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, f"luna_voice_{hash(text)}.wav")
                engine.save_to_file(text, temp_file)
                engine.runAndWait()
                
                # Read and play the audio
                if os.path.exists(temp_file):
                    with open(temp_file, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/wav", autoplay=True)
                    os.remove(temp_file)
                    return True
            except Exception as e:
                st.warning(f"pyttsx3 failed: {str(e)}. Trying gTTS...")
        
        # Fallback to gTTS with improved settings
        gtts = _load_gtts()
        if gtts is None:
            st.warning("🔊 No TTS library available. Voice output disabled.")
            return False
        
        # Better language handling
        if language == "Egyptian Arabic":
            # Use ar-EG for Egyptian Arabic, fallback to ar
            try:
                tts = gtts.gTTS(text=text, lang='ar', slow=False, tld='com')
            except:
                tts = gtts.gTTS(text=text, lang='ar', slow=False)
        else:
            # For English, use en-us
            tts = gtts.gTTS(text=text, lang='en', slow=False, tld='com')
        
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"luna_voice_{hash(text)}.mp3")
        tts.save(temp_file)
        
        with open(temp_file, "rb") as f:
            audio_bytes = f.read()
        
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return True
        
    except Exception as e:
        st.error(f"Voice output error: {str(e)}")
        return False

def safe_image_processing(file, operation="info"):
    """
    Safe image processing using OpenCV and/or PIL (optional).
    Returns dict with results or {"error": ...}.
    """
    try:
        if PIL is None and _load_cv2() is None:
            return {"error": "No image library available (PIL/OpenCV)."}

        if operation == "info":
            if PIL:
                img = PIL.Image.open(file)
                return {
                    "type": "image_pil",
                    "size": img.size,
                    "mode": img.mode,
                    "format": img.format
                }
            else:
                # Fallback using OpenCV
                file_bytes = np.frombuffer(file.read(), np.uint8)
                file.seek(0)
                cv2 = _load_cv2()
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                if img is None:
                    return {"error": "OpenCV could not decode image."}
                h, w = img.shape[:2]
                return {
                    "type": "image_cv2",
                    "size": (w, h),
                    "mode": "BGR",
                    "format": "UNKNOWN"
                }

        elif operation == "ocr":
            pytesseract = _load_pytesseract()
            if pytesseract is None:
                return {"error": "pytesseract not installed. OCR disabled."}

            if PIL is None:
                return {"error": "PIL required for OCR in this path."}
            img = PIL.Image.open(file)
            try:
                text = pytesseract.image_to_string(img)
                return {"text": text}
            except Exception as e:
                return {"error": f"OCR failed: {e}"}

        elif operation == "colors":
            if PIL is None:
                return {"error": "PIL not installed. Color analysis disabled."}
            img = PIL.Image.open(file)
            img_array = np.array(img)
            pixels = img_array.reshape(-1, img_array.shape[-1])
            unique_colors = np.unique(pixels, axis=0)
            dominant_colors = unique_colors[:5]
            colors_hex = []
            for color in dominant_colors:
                if len(color) >= 3:
                    colors_hex.append(f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}")
            return {"colors": colors_hex}

        return {"error": "Unknown image operation."}

    except Exception as e:
        return {"error": str(e)}

def safe_audio_analysis(audio_file):
    """
    Safe audio analysis using librosa + soundfile if available.
    Returns dict with info or {"error": ...}.
    """
    librosa = _load_librosa()
    soundfile = _load_soundfile()
    if librosa is None or soundfile is None:
        return {"error": "librosa or soundfile not installed. Audio analysis disabled."}

    try:
        # Use soundfile to read
        data, sample_rate = soundfile.read(audio_file)
        duration = data.shape[0] / sample_rate if len(data.shape) > 1 else len(data) / sample_rate
        # Use librosa for waveform visualization (limit first 5 seconds)
        data_mono = librosa.to_mono(data.T) if len(data.shape) > 1 else data
        waveform = data_mono[:sample_rate * 5]
        return {
            "sample_rate": int(sample_rate),
            "duration": float(duration),
            "waveform": waveform.tolist()
        }
    except Exception as e:
        return {"error": str(e)}

def process_file_upload(file):
    """Enhanced file processing with multiple formats (safe fallbacks)"""
    try:
        file_extension = file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            df = pd.read_csv(file)
            analysis = perform_data_analysis(df)
            return {"type": "csv", "data": df, "analysis": analysis}
        
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(file)
            analysis = perform_data_analysis(df)
            return {"type": "excel", "data": df, "analysis": analysis}
        
        elif file_extension in ['txt', 'md']:
            content = file.read().decode('utf-8')
            return {
                "type": "text", 
                "content": content,
                "analysis": {
                    "word_count": len(content.split()),
                    "char_count": len(content),
                    "line_count": content.count('\n') + 1,
                    "preview": content[:500] + "..." if len(content) > 500 else content
                }
            }
        
        elif file_extension in ['jpg', 'jpeg', 'png']:
            # Use safe_image_processing for info
            info = safe_image_processing(file, operation="info")
            if "error" in info:
                return {"type": "image", "error": info["error"]}
            return {
                "type": "image",
                "analysis": {
                    "size": info["size"],
                    "mode": info["mode"],
                    "format": info["format"]
                }
            }
        
        elif file_extension in ['wav', 'mp3', 'm4a']:
            info = safe_audio_analysis(file)
            if "error" in info:
                return {"type": "audio", "error": info["error"]}
            return {"type": "audio", "analysis": info}
        
        else:
            return {"type": "unknown", "error": f"Unsupported file type: {file_extension}"}
    
    except Exception as e:
        return {"type": "error", "error": str(e)}

# ═══════════════════════════════════════════════════════════════
# ENHANCED SIDEBAR - ALL FEATURES ACCESSIBLE
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #00d4ff, #0099cc); border-radius: 15px; margin-bottom: 20px;">
        <h2 style="margin: 0; color: white;">🤖 BilinguaBot Pro</h2>
        <p style="margin: 5px 0; color: white; font-size: 12px;">Complete Edition with Luna</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Luna Avatar in sidebar
    st.markdown("""
    <div class="luna-avatar">
        <img src="{}" class="luna-image" alt="Luna AI Girl">
        <div class="luna-status status-{}"></div>
    </div>
    <div style="text-align: center; margin-bottom: 20px;">
        <strong style="font-size: 1.2em; background: linear-gradient(45deg, #ff1493, #8a2be2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💫 Luna AI Assistant</strong>
        <p style="margin: 5px 0; font-size: 0.9em; color: rgba(255,255,255,0.8);">{}</p>
    </div>
    """
    .format(
        get_luna_image_url(),
        st.session_state.ai_girl_state,
        get_luna_status_text()
    ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Status
    st.markdown("### 🖥️ System Status")
    
    torch = _load_torch()
    if torch and torch.cuda.is_available():
        st.success(f"🔥 GPU: {torch.cuda.get_device_name(0)}")
        st.info(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
    else:
        st.warning("⚠️ CPU Mode - All features still work!")
    
    if torch:
        st.info(f"🤖 PyTorch: {torch.__version__}")
    else:
        st.info("🤖 PyTorch: not installed")
    
    st.markdown("---")
    
    # API Configuration
    st.markdown("### 🔑 API Configuration")
    st.session_state.api_key = st.text_input(
        "Groq API Key", 
        type="password", 
        help="Free API key from console.groq.com"
    )
    
    if st.session_state.api_key:
        st.success("✅ API Connected")
    else:
        st.warning("❌ API Not Connected")
    
    # Model Selection
    st.markdown("### 🤖 AI Model")
    st.session_state.model = st.selectbox(
        "Select Model",
        ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma-7b-it"],
        help="Llama 3.3 is most capable"
    )
    
    # Language & Voice Settings
    st.markdown("### 🌍 Language & Voice")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇺🇸 English", key="lang_en", use_container_width=True):
            st.session_state.language = "English"
            update_luna_state("happy")
            st.rerun()
            
    with col2:
        if st.button("🇪🇬 عربي", key="lang_ar", use_container_width=True):
            st.session_state.language = "Egyptian Arabic"
            update_luna_state("happy")
            st.rerun()
    
    st.session_state.voice_enabled = st.checkbox("🔊 Luna's Voice", value=True)
    
    # Feature Toggles
    st.markdown("### ⚡ Features")
    st.session_state.ai_analysis = st.checkbox("🧠 AI Text Analysis", value=True)
    st.session_state.data_viz = st.checkbox("📊 Smart Visualizations", value=True)
    st.session_state.code_help = st.checkbox("💻 Code Assistant", value=True)
    st.session_state.realtime_features = st.checkbox("🚀 Realtime Features", value=True)
    
    # File Upload - ENHANCED
    st.markdown("### 📁 Complete File Upload")
    st.markdown(
        '<div class="glass-card">', unsafe_allow_html=True
    )
    uploaded_files = st.file_uploader(
        "Upload files for analysis", 
        type=["csv", "xlsx", "txt", "md", "jpg", "jpeg", "png", "wav", "mp3", "m4a"],
        accept_multiple_files=True,
        help="Upload data files, documents, images, or audio"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_files:
        st.markdown("#### 📄 Processed Files")
        st.markdown(
            '<div class="glass-card">', unsafe_allow_html=True
        )
        for file in uploaded_files:
            result = process_file_upload(file)
            
            if result["type"] == "csv":
                st.success(f"📊 {file.name}: {result['analysis']['basic_info']['rows']} rows")
                st.session_state.df = result["data"]
                st.session_state.analysis_results[file.name] = result["analysis"]
            elif result["type"] == "excel":
                st.success(f"📈 {file.name}: Excel file loaded")
                st.session_state.df = result["data"]
                st.session_state.analysis_results[file.name] = result["analysis"]
            elif result["type"] == "text":
                st.info(f"📝 {file.name}: {result['analysis']['word_count']} words")
                st.session_state.analysis_results[file.name] = result["analysis"]
            elif result["type"] == "image":
                if "error" in result:
                    st.warning(f"🖼️ {file.name}: {result['error']}")
                else:
                    st.info(f"🖼️ {file.name}: Image ({result['analysis']['size'][0]}x{result['analysis']['size'][1]})")
                    st.session_state.analysis_results[file.name] = result["analysis"]
            elif result["type"] == "audio":
                if "error" in result:
                    st.warning(f"🎵 {file.name}: {result['error']}")
                else:
                    info = result["analysis"]
                    st.info(f"🎵 {file.name}: {info['duration']:.2f}s @ {info['sample_rate']}Hz")
                    st.session_state.analysis_results[file.name] = result["analysis"]
            else:
                st.warning(f"⚠️ {file.name}: {result.get('error', 'Unknown format')}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("### 🎯 Quick Actions")
    st.markdown(
        '<div class="glass-card">', unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            update_luna_state("idle")
            st.rerun()
            
    with col2:
        if st.button("💾 Export", use_container_width=True):
            chat_data = {
                "luna_chat": st.session_state.chat_history,
                "timestamp": datetime.now().isoformat(),
                "language": st.session_state.language,
                "user": st.session_state.current_user
            }
            st.download_button(
                "Download Chat",
                data=json.dumps(chat_data, indent=2, default=str),
                file_name=f"luna_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_chat"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# LOAD AI MODELS
# ═══════════════════════════════════════════════════════════════

with st.spinner("🤖 Loading Luna's AI brain..."):
    ai_models = load_ai_models()

# ═══════════════════════════════════════════════════════════════
# MAIN APPLICATION - COMPLETE TAB INTERFACE
# ═══════════════════════════════════════════════════════════════

# Large Centered Luna Avatar
st.markdown("""
<div class="large-luna-container">
    <div class="main-luna">
        <div>
            <img src="{}" class="large-luna-image" alt="Luna AI Girl">
            <div class="large-luna-status status-{}"></div>
            <div class="large-luna-name">Luna AI Assistant</div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 20px;">
        <h2 style="margin: 0; background: linear-gradient(45deg, #ff1493, #8a2be2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💫 Luna is Here for You!</h2>
        <p style="margin: 10px 0; font-size: 1.1em; color: rgba(255,255,255,0.9);">{}</p>
    </div>
</div>
"""
.format(
    get_luna_image_url(),
    st.session_state.ai_girl_state,
    get_luna_status_text()
), unsafe_allow_html=True)

# Modern Header
st.markdown("""
<div style="text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,150,200,0.2)); border-radius: 25px; margin: 20px 0; border: 2px solid rgba(0,212,255,0.5); backdrop-filter: blur(15px);">
    <h1 style="margin: 0; font-size: 3em; background: linear-gradient(45deg, #00d4ff, #ff00e0); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🤖 BilinguaBot Pro Complete</h1>
    <p style="margin: 10px 0; font-size: 1.2em; color: white;">🌍 Complete AI Assistant with Luna | All Tools Working</p>
    <p style="margin: 5px 0; font-size: 0.9em; color: rgba(255,255,255,0.8);">
        📍 User: {} | 
        🗣️ Language: {} | 
        🔧 Models: {} loaded |
        💫 Luna: {} |
        🖥️ System: {}
    </p>
</div>
"""
.format(
    st.session_state.current_user,
    st.session_state.language,
    len([k for k, v in ai_models.items() if v]),
    st.session_state.ai_girl_state,
    "🔥 GPU" if (torch and torch.cuda.is_available()) else "⚠️ CPU"
), unsafe_allow_html=True)

# COMPLETE TAB INTERFACE - ALL FEATURES ACCESSIBLE
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Luna's Chat Hub", 
    "📊 Complete Data Lab", 
    "🎨 Full AI Tools Suite", 
    "🖼️ Complete Image Studio", 
    "🎤 Complete Audio Lab"
])

# ═══════════════════════════════════════════════════════════════
# TAB 1: LUNA'S CHAT HUB
# ═══════════════════════════════════════════════════════════════

with tab1:
    st.markdown("### 💬 Luna's Chat Hub")
    st.markdown(
        '<div class="ai-chat-container">', unsafe_allow_html=True
    )
    
    # Voice Controls
    col_voice1, col_voice2, col_voice3 = st.columns([1, 2, 1])
    
    with col_voice1:
        if st.button("🎤 Start Voice Input", help="Start voice recognition"):
            st.info("🎤 Luna is listening! Speak now, sweetie!")
            update_luna_state("listening")
            
    with col_voice2:
        if st.button("🔊 Luna's Voice Test", help="Test Luna's voice"):
            update_luna_state("talking")
            enhanced_voice_output("Hi there! I'm Luna, your AI assistant! How can I help you today? 💫", st.session_state.language)
            
    with col_voice3:
        if st.button("🎵 Audio Settings", help="Voice settings"):
            st.info("Voice settings panel coming soon!")
    
    st.markdown("---")
    
    # Chat history
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "assistant":
            st.markdown(f'''
            <div class="bot-message">
                <strong>💫 Luna</strong> <small style="opacity: 0.7;">({message.get("timestamp", datetime.now()).strftime("%H:%M") if hasattr(message.get("timestamp", datetime.now()), "strftime") else ""})</small><br>
                {message["content"]}
            </div>
            ''', unsafe_allow_html=True)
            
            # Action buttons
            col_actions = st.columns([1, 1, 1, 1, 5])
            
            with col_actions[0]:
                if st.button("🔊", key=f"voice_{i}", help="Luna's voice"):
                    if st.session_state.voice_enabled:
                        enhanced_voice_output(message["content"], st.session_state.language)
            
            with col_actions[1]:
                if st.button("💖", key=f"like_{i}", help="Love it!"):
                    st.success("Aww, thank you, sweetie! 💕")
                    update_luna_state("happy")
            
            with col_actions[2]:
                if st.button("🔄", key=f"regen_{i}", help="Better response"):
                    if i > 0:
                        st.session_state.chat_history = st.session_state.chat_history[:i]
                        update_luna_state("thinking")
                        st.rerun()
            
            with col_actions[3]:
                if st.button("📋", key=f"copy_{i}", help="Copy message"):
                    st.code(message["content"])
        
        else:
            st.markdown(f'''
            <div class="user-message">
                <strong>👤 {st.session_state.current_user}</strong> <small style="opacity: 0.7;">({message.get("timestamp", datetime.now()).strftime("%H:%M") if hasattr(message.get("timestamp", datetime.now()), "strftime") else ""})</small><br>
                {message["content"]}
            </div>
            ''', unsafe_allow_html=True)
            
            # AI analysis for user messages
            if st.session_state.get("ai_analysis", True) and ai_models and len(message["content"]) > 10:
                with st.expander("🧠 Luna's Analysis", expanded=False):
                    analysis = analyze_text_with_ai(message["content"], ai_models)
                    if analysis and "sentiment" in analysis:
                        sentiment = analysis["sentiment"]
                        st.info(f"**Luna's Analysis:** {sentiment['label']} (confidence: {sentiment['score']:.2f})")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced chat input
    st.markdown(
        '<div class="voice-controls">', unsafe_allow_html=True
    )
    
    col_input1, col_input2, col_input3 = st.columns([5, 1, 1])
    
    with col_input1:
        user_input = st.chat_input(f"Chat with Luna ({st.session_state.language})...", key="luna_chat_input")
    
    with col_input2:
        if st.button("🎤", help="Voice input"):
            update_luna_state("listening")
            st.info("Voice input - Speak now!")
            
    with col_input3:
        if st.button("📷", help="Image input"):
            st.info("Image input feature!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle user input
    if user_input:
        st.session_state.chat_history.append({
            "role": "user", 
            "content": user_input,
            "timestamp": datetime.now()
        })
        
        update_luna_state("thinking")
        
        with st.spinner("💭 Luna is thinking..."):
            ai_response = get_enhanced_ai_response(
                user_input, 
                st.session_state.df,
                ai_models
            )
        
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": ai_response,
            "timestamp": datetime.now()
        })
        
        # Speak only if enabled
        if st.session_state.voice_enabled:
            enhanced_voice_output(ai_response, st.session_state.language)
        
        # Auto visualization if requested
        if st.session_state.get("data_viz", True) and st.session_state.df is not None:
            if any(keyword in user_input.lower() for keyword in ["chart", "graph", "visualize", "plot", "مخطط", "رسم بياني"]):
                fig = create_smart_visualization(st.session_state.df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        
        update_luna_state("talking")
        st.rerun()
    
    # Welcome message
    if not st.session_state.chat_history:
        welcome_msg = """🌟 **Hi sweetie! I'm Luna, your complete AI assistant!** 💫

I have ALL the tools and features working perfectly!

**What I can do:**
• 💬 **Chat with you** and analyze your messages
• 📊 **Analyze data** - upload files and get insights
• 🎨 **Use AI tools** - sentiment, classification, summarization
• 🖼️ **Work with images** - analysis, color extraction, OCR
• 🎤 **Handle audio** - text-to-speech, voice processing
• 📈 **Create visualizations** - charts, graphs, plots
• 💻 **Help with coding** and technical questions

**To get started:**
1. Add your Groq API key in the sidebar ⚙️
2. Upload data files for analysis 📁
3. Start chatting with me! 💬
4. Explore ALL the tools in the tabs! 🚀

**Ready to explore everything together?** Let's make this amazing! 🌟💖"""
        
        if st.session_state.language == "Egyptian Arabic":
            welcome_msg = """🌟 **أهلاً حبيبتي! أنا لونا، مساعدتك الذكية الكاملة!** 💫

عندي كل الأدوات والميزات شغالة كويس!

**إيه اللي اقدر اعمله:**
• 💬 **اتكلمي معايا** وحلل رسائلك
• 📊 **حلل البيانات** - ارفعي ملفات واحصلي على رؤى
• 🎨 **استخدمي أدوات الذكاء الاصطناعي** - المشاعر، التصنيف، الملخصات
• 🖼️ **اشتغلي مع الصور** - تحليل، استخراج ألوان، استخراج نصوص
• 🎤 **تعاملي مع الصوت** - تحويل نص لصوت، معالجة الصوت
• 📈 **اعملي تصورات** - رسوم بيانية، مخططات، رسوم
• 💻 **ساعدك في البرمجة** والأسئلة التقنية

**إزاي تبدئي:**
1. حطي مفتاح Groq API في الشريط الجانبي ⚙️
2. ارفعي ملفات البيانات للتحليل 📁
3. ابدئي تتكلمي معايا! 💬
4. استكشفي كل الأدوات في التبويبات! 🚀

**جاهزة تستكشفي كل حاجة مع بعض؟** نعمل حاجة رائعة! 🌟💖"""
        
        st.markdown(f'''
        <div class="bot-message">
            {welcome_msg}
        </div>
        ''', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 2: COMPLETE DATA LAB
# ═══════════════════════════════════════════════════════════════

with tab2:
    st.markdown("### 📊 Complete Data Lab")
    
    if st.session_state.df is not None:
        # Enhanced data overview
        st.markdown(
            '<div class="data-card">', unsafe_allow_html=True
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Rows", len(st.session_state.df))
        with col2:
            st.metric("📋 Columns", len(st.session_state.df.columns))
        with col3:
            numeric_cols = len(st.session_state.df.select_dtypes(include=[np.number]).columns)
            st.metric("🔢 Numeric", numeric_cols)
        with col4:
            missing_values = st.session_state.df.isnull().sum().sum()
            st.metric("❌ Missing", missing_values)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Complete analysis tabs
        analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
            "📈 Luna's Smart Insights", 
            "🎨 Interactive Visualizations", 
            "📊 Data Explorer", 
            "🔍 Deep Analysis Tools"
        ])
        
        with analysis_tab1:
            st.markdown(
                '<div class="glass-card">', unsafe_allow_html=True
            )
            st.markdown("#### 🔍 Luna's AI-Powered Data Insights")
            
            # Get stored analysis
            file_name = list(st.session_state.analysis_results.keys())[0] if st.session_state.analysis_results else None
            analysis = st.session_state.analysis_results.get(file_name, {})
            
            if analysis and "error" not in analysis:
                # AI insights cards
                if "strong_correlations" in analysis and analysis["strong_correlations"]:
                    st.markdown("**🔗 Luna Found These Strong Correlations:**")
                    for corr in analysis["strong_correlations"]:
                        direction = "positive" if corr["correlation"] > 0 else "negative"
                        strength = "very strong" if abs(corr["correlation"]) > 0.9 else "strong"
                        st.success(f"💫 {corr['variables'][0]} ↔ {corr['variables'][1]}: {strength} {direction} correlation ({corr['correlation']:.3f})")
                
                # Missing value insights
                if "missing_values" in analysis and analysis["missing_values"] != "No missing values":
                    st.markdown("**⚠️ Luna's Data Quality Alerts:**")
                    for col, count in analysis["missing_values"].items():
                        percentage = (count / len(st.session_state.df)) * 100
                        st.warning(f"💫 {col}: {count} missing values ({percentage:.1f}%)")
                
                # Numeric insights
                if "numeric_summary" in analysis:
                    st.markdown("**📊 Luna's Statistical Summary:**")
                    numeric_data = analysis["numeric_summary"]
                    for col, stats in list(numeric_data.items())[:3]:
                        st.info(f"💫 **{col}:** Mean = {stats['mean']:.2f}, Median = {stats['50%']:.2f}, Std = {stats['std']:.2f}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with analysis_tab2:
            st.markdown(
                '<div class="glass-card">', unsafe_allow_html=True
            )
            st.markdown("#### 🎨 Luna's Interactive Visualizations")
            
            viz_type = st.selectbox(
                "Choose Visualization Type",
                ["🎯 Auto Analysis", "🔥 Correlation Heatmap", "📊 Scatter Matrix", "📈 Distribution", "📊 Bar Chart", "📦 Box Plot", "🌟 3D Plot"],
                help="Luna will automatically choose the best visualization"
            )
            
            col_viz1, col_viz2 = st.columns(2)
            with col_viz1:
                if st.button("🎨 Luna Generate Smart Visualization", use_container_width=True):
                    fig = create_smart_visualization(st.session_state.df, viz_type.lower())
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Luna couldn't create visualization with selected options")
            
            with col_viz2:
                if st.button("📊 Luna Create Custom Chart", use_container_width=True):
                    st.info("🎨 Luna's custom chart builder coming soon!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with analysis_tab3:
            st.markdown(
                '<div class="glass-card">', unsafe_allow_html=True
            )
            st.markdown("#### 📊 Luna's Data Explorer")
            
            # Enhanced data preview
            st.dataframe(st.session_state.df, use_container_width=True, height=400)
            
            col_download1, col_download2 = st.columns(2)
            with col_download1:
                csv = st.session_state.df.to_csv(index=False)
                st.download_button(
                    "💾 Download as CSV",
                    data=csv,
                    file_name="luna_processed_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_download2:
                if st.button("📋 Luna Generate Report", use_container_width=True):
                    report = f"""# Luna's Data Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Data Summary
- Total Rows: {len(st.session_state.df)}
- Total Columns: {len(st.session_state.df.columns)}
- Numeric Columns: {len(st.session_state.df.select_dtypes(include=[np.number]).columns)}
- Missing Values: {st.session_state.df.isnull().sum().sum()}

## Column Information
{st.session_state.df.dtypes.to_string()}

## Basic Statistics
{st.session_state.df.describe().to_string()}
"""
                    st.download_button(
                        "📄 Download Luna's Report",
                        data=report,
                        file_name=f"luna_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with analysis_tab4:
            st.markdown(
                '<div class="glass-card">', unsafe_allow_html=True
            )
            st.markdown("#### 🔍 Luna's Deep Analysis Tools")
            
            col_deep1, col_deep2 = st.columns(2)
            
            with col_deep1:
                if st.button("🧠 Luna's AI Insights", use_container_width=True):
                    if st.session_state.api_key:
                        st.info("🤖 Luna is generating AI-powered insights...")
                        insights_prompt = f"""Analyze this dataset and provide insights:
                        
Dataset: {len(st.session_state.df)} rows, {len(st.session_state.df.columns)} columns
Columns: {list(st.session_state.df.columns)}
                        
Provide:
1. Key patterns and trends
2. Business recommendations  
3. Data quality observations
4. Suggested next steps for analysis"""
                        
                        ai_insights = get_enhanced_ai_response(insights_prompt, st.session_state.df, ai_models)
                        st.markdown(
                            f'<div class="glass-card">{ai_insights}</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.warning("Luna needs API key for AI insights")
            
            with col_deep2:
                if st.button("📈 Luna's Predictive Analysis", use_container_width=True):
                    st.info("🚀 Luna's predictive modeling features coming soon!")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.markdown(
            '<div class="glass-card" style="text-align: center; padding: 50px;">', unsafe_allow_html=True
        )
        st.markdown("#### 📁 Luna's Data Lab")
        st.info("Upload a CSV or Excel file in the sidebar to start data analysis with Luna!")
        
        # Sample data
        col_sample1, col_sample2 = st.columns(2)
        with col_sample1:
            if st.button("📋 Luna Load Sample Dataset", use_container_width=True):
                sample_data = pd.DataFrame({
                    'Product': [f'Product_{i}' for i in range(1, 51)],
                    'Sales': np.random.normal(1000, 300, 50).astype(int),
                    'Profit': np.random.normal(150, 50, 50).astype(int),
                    'Category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Food'], 50),
                    'Region': np.random.choice(['North', 'South', 'East', 'West'], 50),
                    'Customer_Rating': np.random.uniform(1, 5, 50).round(1),
                    'Units_Sold': np.random.randint(50, 500, 50)
                })
                
                st.session_state.df = sample_data
                st.session_state.analysis_results['sample_data.csv'] = perform_data_analysis(sample_data)
                st.success("✅ Luna loaded sample data! Check the analysis tabs.")
                st.rerun()
        
        with col_sample2:
            if st.button("🎯 Luna's Quick Demo", use_container_width=True):
                demo_data = pd.DataFrame({
                    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'Revenue': [15000, 18000, 22000, 19000, 25000, 28000],
                    'Customers': [1200, 1400, 1800, 1600, 2000, 2200]
                })
                
                st.session_state.df = demo_data
                st.session_state.analysis_results['demo_data.csv'] = perform_data_analysis(demo_data)
                st.success("✅ Luna loaded demo data!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 3: FULL AI TOOLS SUITE
# ═══════════════════════════════════════════════════════════════

with tab3:
    st.markdown("### 🎨 Luna's Full AI Tools Suite")
    
    # Tools overview
    col_tools1, col_tools2, col_tools3 = st.columns(3)
    
    with col_tools1:
        st.markdown(
            '<div class="glass-card" style="text-align: center;">🧠<h3>Luna\'s Text Analysis</h3><p>Sentiment & Classification</p></div>',
            unsafe_allow_html=True
        )
    
    with col_tools2:
        st.markdown(
            '<div class="glass-card" style="text-align: center;">💻<h3>Luna\'s Code Assistant</h3><p>Debug & Optimize</p></div>',
            unsafe_allow_html=True
        )
    
    with col_tools3:
        st.markdown(
            '<div class="glass-card" style="text-align: center;">📝<h3>Luna\'s Content Tools</h3><p>Summarize & Rewrite</p></div>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Text Analysis Tools
    st.markdown(
        '<div class="glass-card">', unsafe_allow_html=True
    )
    st.markdown("#### 🧠 Luna's Advanced Text Analysis")
    
    text_input = st.text_area("Enter text for Luna's AI analysis:", height=200, 
                            placeholder="Paste your text here for Luna's comprehensive AI analysis...")
    
    col_analysis1, col_analysis2, col_analysis3 = st.columns(3)
    
    with col_analysis1:
        if st.button("🔍 Luna's Sentiment Analysis", use_container_width=True):
            if text_input and ai_models:
                analysis = analyze_text_with_ai(text_input, ai_models)
                if analysis and "sentiment" in analysis:
                    sentiment = analysis["sentiment"]
                    
                    if sentiment['label'] == 'POSITIVE':
                        st.success("😊 Luna says: Positive Sentiment!")
                        st.info(f"**Confidence:** {sentiment['score']:.3f}")
                    elif sentiment['label'] == 'NEGATIVE':
                        st.error("😔 Luna says: Negative Sentiment!")
                        st.info(f"**Confidence:** {sentiment['score']:.3f}")
                    else:
                        st.info("😐 Luna says: Neutral Sentiment!")
                        st.info(f"**Confidence:** {sentiment['score']:.3f}")
            else:
                st.warning("Luna needs text and AI models loaded")
    
    with col_analysis2:
        if st.button("📝 Luna Generate Summary", use_container_width=True):
            if text_input and ai_models and 'summarization' in ai_models:
                try:
                    with st.spinner("📝 Luna is summarizing..."):
                        summary = ai_models['summarization'](text_input[:1000])
                        st.success("**Luna's Summary:**")
                        st.markdown(
                            f'<div class="glass-card">{summary[0]["summary_text"]}</div>',
                            unsafe_allow_html=True
                        )
                except Exception as e:
                    st.error(f"Luna's summary error: {str(e)}")
            else:
                st.warning("Luna's summarization unavailable")
    
    with col_analysis3:
        if st.button("🏷️ Luna's Text Classification", use_container_width=True):
            if text_input and ai_models and 'text_classification' in ai_models:
                try:
                    classification = ai_models['text_classification'](text_input[:500])
                    st.success("**Luna's Classification:**")
                    st.info(f"**Category:** {classification[0]['label']}")
                    st.info(f"**Confidence:** {classification[0]['score']:.3f}")
                except Exception as e:
                    st.error(f"Luna's classification error: {str(e)}")
            else:
                st.warning("Luna's classification unavailable")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Assistant
    st.markdown(
        '<div class="glass-card">', unsafe_allow_html=True
    )
    st.markdown("#### 💻 Luna's Advanced Code Assistant")
    
    code_input = st.text_area("Luna's Programming Help:", height=200,
                            placeholder="Ask Luna for code help, debugging, or explanations...", key="luna_code_assistant")
    
    col_code1, col_code2, col_code3 = st.columns(3)
    with col_code1:
        if st.button("🔧 Luna Debug Code", use_container_width=True):
            if code_input:
                st.info("💻 Luna's debugging assistant ready!")
                st.code("# Luna's debugging features coming soon!\n# Please describe your specific error or issue.")
            else:
                st.warning("Please enter your code or describe the issue for Luna")
    
    with col_code2:
        if st.button("⚡ Luna Optimize Code", use_container_width=True):
            if code_input:
                st.info("⚡ Luna's optimization help available!")
                st.code("# Luna's optimization features coming soon!\n# Request performance improvements.")
            else:
                st.warning("Please enter your code for Luna to optimize")
    
    with col_code3:
        if st.button("📚 Luna Generate Docs", use_container_width=True):
            if code_input:
                st.info("📚 Luna's documentation generation coming soon!")
            else:
                st.warning("Please enter code for Luna to generate documentation")
    
    # Luna's Quick examples
    st.markdown("#### 📚 Luna's Quick Examples")
    examples = [
        "How to create a DataFrame in pandas?",
        "Python function for API requests",
        "SQL query for data aggregation", 
        "JavaScript async/await example",
        "CSS grid layout tutorial"
    ]
    
    cols_examples = st.columns(5)
    for i, example in enumerate(examples):
        with cols_examples[i]:
            if st.button(f"Luna: {example}", key=f"luna_example_{i}", use_container_width=True):
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": example,
                    "timestamp": datetime.now()
                })
                update_luna_state("thinking")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 4: COMPLETE IMAGE STUDIO
# ═══════════════════════════════════════════════════════════════

with tab4:
    st.markdown("### 🖼️ Luna's Complete Image Studio")
    
    # Upload and analyze images
    uploaded_image = st.file_uploader("Upload images for Luna's analysis", 
                                    type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    if uploaded_image:
        for i, image_file in enumerate(uploaded_image):
            st.markdown(
                f'<div class="glass-card">', unsafe_allow_html=True
            )
            
            col_img1, col_img2 = st.columns([1, 1])
            
            with col_img1:
                if PIL:
                    image = PIL.Image.open(image_file)
                    st.image(image, caption=f"Luna's Image {i+1}", use_column_width=True)
                else:
                    st.info("PIL not installed. Showing metadata only.")
                
                # Basic image info
                st.markdown("#### 📊 Luna's Image Information")
                
                info = safe_image_processing(image_file, operation="info")
                if "error" in info:
                    st.warning(info["error"])
                else:
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.info(f"**Size:** {info['size'][0]} × {info['size'][1]}")
                        st.info(f"**Format:** {info['format']}")
                    with col_info2:
                        st.info(f"**Mode:** {info['mode']}")
                        st.info(f"**Size:** {image_file.size / 1024:.1f} KB")
            
            with col_img2:
                st.markdown("#### 🔍 Luna's AI Analysis Tools")
                
                col_analysis_img1, col_analysis_img2 = st.columns(2)
                
                with col_analysis_img1:
                    if st.button(f"🧠 Luna Analyze Image {i+1}", use_container_width=True):
                        st.info("🔍 Luna's advanced image analysis features:")
                        st.markdown(
                            '<div class="glass-card">• Luna can detect objects & scenes<br>• Luna understands scenes<br>• Luna detects emotions<br>• Luna analyzes content<br>• Luna recognizes styles</div>',
                            unsafe_allow_html=True
                        )
                
                with col_analysis_img2:
                    if st.button(f"📝 Luna Extract Text {i+1}", use_container_width=True):
                        ocr = safe_image_processing(image_file, operation="ocr")
                        if "error" in ocr:
                            st.error(ocr["error"])
                        else:
                            text = ocr.get("text", "")
                            if text.strip():
                                st.success("**Luna's Extracted Text:**")
                                st.text(text)
                            else:
                                st.warning("Luna found no text in the image")
                
                # Color analysis
                if st.button(f"🎨 Luna's Color Analysis {i+1}", use_container_width=True):
                    colors = safe_image_processing(image_file, operation="colors")
                    if "error" in colors:
                        st.error(colors["error"])
                    else:
                        st.markdown("#### 🎨 Luna's Dominant Colors")
                        for j, color_hex in enumerate(colors.get("colors", [])):
                            col_color, col_picker = st.columns([2, 1])
                            with col_color:
                                st.markdown(f"**Luna's Color {j+1}:** {color_hex}")
                            with col_picker:
                                st.color_picker("", color_hex, disabled=True, key=f"luna_color_{i}_{j}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.markdown(
            '<div class="glass-card" style="text-align: center; padding: 50px;">', unsafe_allow_html=True
        )
        st.markdown("#### 🖼️ Luna's Image Studio")
        st.info("Upload images for Luna's AI analysis, text extraction, and color analysis!")
        
        # Luna's image capabilities
        col_cap1, col_cap2, col_cap3 = st.columns(3)
        
        with col_cap1:
            st.markdown(
                '<div class="glass-card" style="text-align: center;">👁️<h4>Luna Object Detection</h4><p>Luna recognizes objects & scenes</p></div>',
                unsafe_allow_html=True
            )
        
        with col_cap2:
            st.markdown(
                '<div class="glass-card" style="text-align: center;">📝<h4>Luna OCR Text</h4><p>Luna extracts text from images</p></div>',
                unsafe_allow_html=True
            )
        
        with col_cap3:
            st.markdown(
                '<div class="glass-card" style="text-align: center;">🎨<h4>Luna Color Analysis</h4><p>Luna analyzes color palettes</p></div>',
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 5: COMPLETE AUDIO LAB
# ═══════════════════════════════════════════════════════════════

with tab5:
    st.markdown("### 🎤 Luna's Complete Audio Lab")
    
    # Voice features overview
    col_voice_overview1, col_voice_overview2, col_voice_overview3 = st.columns(3)
    
    with col_voice_overview1:
        st.markdown(
            '<div class="glass-card" style="text-align: center;">🎤<h3>Luna Speech Recognition</h3><p>Luna\'s voice to text conversion</p></div>',
            unsafe_allow_html=True
        )
    
    with col_voice_overview2:
        st.markdown(
            '<div class="glass-card" style="text-align: center;">🔊<h3>Luna Text to Speech</h3><p>Luna\'s AI voice synthesis</p></div>',
            unsafe_allow_html=True
        )
    
    with col_voice_overview3:
        st.markdown(
            '<div class="glass-card" style="text-align: center;">🎧<h3>Luna Audio Processing</h3><p>Luna\'s sound analysis & effects</p></div>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Luna's Text-to-Speech Lab
    st.markdown(
        '<div class="voice-controls">', unsafe_allow_html=True
    )
    st.markdown("#### 🔊 Luna's AI Voice Synthesis Lab")
    
    tts_text = st.text_area("Enter text for Luna's voice synthesis:", 
                          height=150,
                          placeholder="Type text here for Luna's AI speech...",
                          key="luna_tts_input")
    
    col_tts1, col_tts2, col_tts3 = st.columns(3)
    with col_tts1:
        if st.button("🎤 Luna Speak (English)", use_container_width=True):
            if tts_text:
                enhanced_voice_output(tts_text, "English")
                st.success("🎵 Luna is playing English voice output!")
            else:
                st.warning("Please enter text for Luna")
    
    with col_tts2:
        if st.button("🎤 Luna Speak (Arabic)", use_container_width=True):
            if tts_text:
                enhanced_voice_output(tts_text, "Egyptian Arabic")
                st.success("🎵 Luna is playing Arabic voice output!")
            else:
                st.warning("Please enter text for Luna")
    
    with col_tts3:
        if st.button("🎵 Luna Test Voice Quality", use_container_width=True):
            test_text = "Hello! This is Luna's voice synthesis capabilities test."
            enhanced_voice_output(test_text, "English")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Luna's Speech Recognition (Placeholder)
    st.markdown(
        '<div class="glass-card">', unsafe_allow_html=True
    )
    st.markdown("#### 🎙️ Luna's Speech Recognition Lab")
    
    col_rec1, col_rec2, col_rec3 = st.columns(3)
    
    with col_rec1:
        if st.button("🎤 Luna Start Recording", use_container_width=True):
            st.info("🎙️ Luna's voice recording activated! Speak now...")
            st.write("**Luna's planned features:**")
            st.markdown(
                '<div class="glass-card">• Luna\'s real-time voice recognition<br>• Luna\'s multi-language support<br>• Luna\'s voice commands<br>• Luna\'s noise cancellation</div>',
                unsafe_allow_html=True
            )
    
    with col_rec2:
        if st.button("🌍 Luna Language Detection", use_container_width=True):
            st.info("🌍 Luna's language detection features coming soon!")
    
    with col_rec3:
        if st.button("📝 Luna Voice Commands", use_container_width=True):
            st.info("📝 Luna's voice command processing coming soon!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Luna's Audio Processing Lab
    st.markdown(
        '<div class="glass-card">', unsafe_allow_html=True
    )
    st.markdown("#### 🎧 Luna's Audio Processing Lab")
    
    uploaded_audio = st.file_uploader("Upload audio file for Luna's analysis", 
                                    type=["wav", "mp3", "m4a"], accept_multiple_files=True)
    
    if uploaded_audio:
        for i, audio_file in enumerate(uploaded_audio):
            st.markdown(
                f'<div class="data-card">', unsafe_allow_html=True
            )
            st.success(f"🎵 Luna's audio file {i+1}: {audio_file.name}")
            
            # Play audio
            st.audio(audio_file)
            
            # Luna's audio analysis
            info = safe_audio_analysis(audio_file)
            if "error" in info:
                st.warning(info["error"])
            else:
                col_audio1, col_audio2, col_audio3 = st.columns(3)
                with col_audio1:
                    st.metric("Luna: Duration", f"{info['duration']:.2f}s")
                with col_audio2:
                    st.metric("Luna: Sample Rate", f"{info['sample_rate']} Hz")
                with col_audio3:
                    st.metric("Luna: File Size", f"{audio_file.size / 1024:.1f} KB")
                
                # Luna's audio visualization
                st.markdown("#### 📊 Luna's Audio Visualization")
                wf = info.get("waveform", [])
                if wf:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        y=wf,
                        mode='lines', 
                        name='Luna Audio Waveform',
                        line=dict(color='#00d4ff', width=2)
                    ))
                    fig.update_layout(
                        title=f"🔊 Luna's Audio Waveform - {audio_file.name}",
                        xaxis_title="Sample",
                        yaxis_title="Amplitude",
                        template="plotly_dark",
                        plot_bgcolor="rgba(0,0,0,0.8)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="white")
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.markdown(
            '<div class="glass-card" style="text-align: center; padding: 50px;">', unsafe_allow_html=True
        )
        st.markdown("#### 🎧 Luna's Audio Lab")
        st.info("Upload audio files for Luna's waveform analysis and processing!")
        
        # Luna's audio capabilities
        col_audio_cap1, col_audio_cap2, col_audio_cap3 = st.columns(3)
        
        with col_audio_cap1:
            st.markdown(
                '<div class="glass-card" style="text-align: center;">📊<h4>Luna Waveform Analysis</h4><p>Luna visualizes audio patterns</p></div>',
                unsafe_allow_html=True
            )
        
        with col_audio_cap2:
            st.markdown(
                '<div class="glass-card" style="text-align: center;">🎵<h4>Luna Audio Enhancement</h4><p>Luna noise reduction & effects</p></div>',
                unsafe_allow_html=True
            )
        
        with col_audio_cap3:
            st.markdown(
                '<div class="glass-card" style="text-align: center;">🔍<h4>Luna Feature Extraction</h4><p>Luna analyzes audio characteristics</p></div>',
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Footer
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns([1, 2, 1])

with col_footer2:
    system_info = []
    torch = _load_torch()
    system_info.append(f"🤖 PyTorch {torch.__version__ if torch else 'N/A'}")
    system_info.append(f"🔥 GPU {'ON' if (torch and torch.cuda.is_available()) else 'OFF'}")
    system_info.append(f"🧠 AI Models: {len([k for k, v in ai_models.items() if v])}")
    system_info.append(f"💬 Messages: {len(st.session_state.chat_history)}")
    system_info.append(f"💫 Luna: {st.session_state.ai_girl_state}")
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(255,0,224,0.2)); border-radius: 20px; border: 2px solid rgba(255,255,255,0.3); backdrop-filter: blur(15px);">
        <h3 style="margin: 0; background: linear-gradient(45deg, #00d4ff, #ff00e0); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💫 Luna's BilinguaBot Pro Complete</h3>
        <p style="margin: 10px 0; color: rgba(255,255,255,0.9);">Complete AI Assistant | Luna Edition | All Tools Working</p>
        <p style="margin: 5px 0; color: rgba(255,255,255,0.7); font-size: 0.9em;">{' | '.join(system_info)}</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced JavaScript
import streamlit.components.v1 as components
components.html("""
<script>
// Luna's interactive features
document.addEventListener('DOMContentLoaded', function() {
    // Luna's breathing animation
    const lunaImage = document.querySelector('.luna-image');
    if (lunaImage) {
        setInterval(() => {
            lunaImage.style.animation = 'lunaFloat 3s ease-in-out infinite';
        }, 3000);
    }
    
    // Large Luna animation
    const largeLunaImage = document.querySelector('.large-luna-image');
    if (largeLunaImage) {
        setInterval(() => {
            largeLunaImage.style.animation = 'lunaFloat 3s ease-in-out infinite';
        }, 3000);
    }
    
    // Keyboard shortcuts - more robust
    document.addEventListener('keydown', function(e) {
        // Ctrl+Enter to send message
        if (e.ctrlKey && e.key === 'Enter') {
            const chatInput = document.querySelector('[data-testid="chat-input"]');
            if (chatInput) {
                // Trigger as if user pressed Enter
                const event = new KeyboardEvent('keydown', {
                    bubbles: true,
                    cancelable: true,
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13
                });
                chatInput.dispatchEvent(event);
            }
        }

        // Escape to focus chat input
        if (e.key === 'Escape') {
            const chatInput = document.querySelector('[data-testid="chat-input"]');
            if (chatInput) {
                chatInput.focus();
            }
        }
    });
});

// Luna's dynamic responses
function updateLunaMood(mood) {
    const statusElement = document.querySelector('.luna-status');
    if (statusElement) {
        statusElement.className = `luna-status status-${mood}`;
    }
    const largeStatusElement = document.querySelector('.large-luna-status');
    if (largeStatusElement) {
        largeStatusElement.className = `large-luna-status status-${mood}`;
    }
}
</script>
""", height=0)