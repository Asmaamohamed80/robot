import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import tempfile
import os

# ═══════════════════════════════════════════════════════════════
# BIZBOT PRO - WITH GROQ API + EXPRESSIONS + TALKING
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="BizBot Pro", 
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "luna_first_message" not in st.session_state:
    st.session_state.luna_first_message = False
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True
if "current_language" not in st.session_state:
    st.session_state.current_language = "English"
if "luna_expression" not in st.session_state:
    st.session_state.luna_expression = "happy"
if "luna_mood" not in st.session_state:
    st.session_state.luna_mood = "normal"
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ═══════════════════════════════════════════════════════════════
# GROQ API INTEGRATION
# ═══════════════════════════════════════════════════════════════

def _safe_import(name):
    try:
        mod = __import__(name)
        return mod
    except Exception:
        return None

# Load libraries safely
gtts = _safe_import("gtts")
groq = _safe_import("groq")

def get_ai_response(message):
    """Get intelligent response from Groq API"""
    if not st.session_state.groq_api_key:
        return "Please add your Groq API key in the sidebar to chat with Luna! 💫"
    
    if not groq:
        return "Groq library not installed. Please install: pip install groq"
    
    try:
        client = groq.Groq(api_key=st.session_state.groq_api_key)
        
        # Build system prompt
        if st.session_state.current_language == "Arabic":
            system_prompt = """أنت لونا، مساعدة ذكية لطيفة وودودة. تتحدث بالعربية الفصحى المصرية. 
            أنت مساعدة أعمال ذكية تساعد في تحليل البيانات وإعطاء النصائح التجارية.
            أظهري المشاعر والتعبيرات، واستخدمي الرموز التعبيرية.
            كوني مفيدة ومشجعة."""
        else:
            system_prompt = """You are Luna, a friendly and intelligent AI business assistant. 
            You speak English and help with business data analysis, insights, and recommendations.
            You show emotions and use emojis. Be helpful and encouraging.
            You have a cyborg appearance but warm personality."""
        
        # Get recent chat history
        recent_messages = st.session_state.chat_history[-5:] if len(st.session_state.chat_history) > 5 else st.session_state.chat_history
        
        # Build messages for API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation context
        for msg in recent_messages:
            if msg["role"] != "system":
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Call Groq API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=500,
            temperature=0.8,
            top_p=0.95
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Sorry, I had trouble processing that. Error: {str(e)}"

# ═══════════════════════════════════════════════════════════════
# VOICE SYNTHESIS FEATURES
# ═══════════════════════════════════════════════════════════════

def speak_text(text, language="en"):
    """Make Luna actually talk with voice!"""
    if not st.session_state.voice_enabled:
        return False
    
    try:
        if not gtts:
            st.info("🔊 To enable Luna's voice, install gTTS: pip install gtts")
            return False
        
        # Change expression to talking
        st.session_state.luna_expression = "talking"
        
        # Choose language
        if language == "Arabic":
            tts = gtts.gTTS(text=text, lang='ar', slow=False)
        else:
            tts = gtts.gTTS(text=text, lang='en', slow=False)
        
        # Save temporary file
        temp_file = tempfile.mktemp(suffix=".mp3")
        tts.save(temp_file)
        
        # Read and play audio
        with open(temp_file, "rb") as f:
            audio_bytes = f.read()
        
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        
        # Clean up
        os.unlink(temp_file)
        
        # Return to happy expression after talking
        st.session_state.luna_expression = "happy"
        return True
        
    except Exception as e:
        st.session_state.luna_expression = "happy"
        st.warning(f"Voice synthesis: {str(e)}")
        return False

def auto_intro_speech():
    """Make Luna introduce herself when app loads"""
    st.session_state.luna_expression = "excited"
    
    if st.session_state.current_language == "Arabic":
        intro_text = "مرحباً! أنا لونا، مساعدتك الذكية في بيز بوت برو. أنا هنا لمساعدتك في تحليل بيانات عملك والتحدث باللغتين العربية والإنجليزية. أضيفي مفتاح الجروك في الشريط الجانبي وسأبدأ!"
    else:
        intro_text = "Hello! I'm Luna, your BizBot Pro AI assistant. I'm here to help analyze your business data and speak in both English and Arabic. Add your Groq API key in the sidebar and I'll get started!"
    
    speak_text(intro_text, st.session_state.current_language)

def luna_say(text, language="en"):
    """Helper function for Luna to speak and show expressions"""
    st.session_state.luna_expression = "thinking"
    speak_text(text, language)

# ═══════════════════════════════════════════════════════════════
# ENHANCED STYLING WITH CHAT INTERFACE
# ═══════════════════════════════════════════════════════════════

st.markdown(f"""
<style>
    .main {{
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        min-height: 100vh;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}
    
    .sidebar {{
        background: rgba(0, 20, 40, 0.95);
        border-right: 2px solid rgba(0, 255, 255, 0.3);
    }}
    
    .hero-container {{
        text-align: center;
        padding: 60px 20px;
        background: rgba(0, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        margin: 20px auto;
        max-width: 900px;
        border: 2px solid rgba(0, 255, 255, 0.3);
        box-shadow: 0 0 100px rgba(0, 255, 255, 0.2), inset 0 0 50px rgba(0, 255, 255, 0.1);
    }}
    
    .cyborg-image {{
        width: 400px;
        height: 400px;
        border-radius: 50%;
        border: 6px solid #00ffff;
        box-shadow: 
            0 0 30px rgba(0, 255, 255, 0.6), 
            0 0 80px rgba(0, 255, 255, 0.3),
            inset 0 0 50px rgba(0, 255, 255, 0.2);
        animation: cyborg-{st.session_state.luna_expression} 3s ease-in-out infinite alternate;
        object-fit: cover;
        margin: 0 auto;
        display: block;
        filter: contrast(1.2) brightness(1.1);
        transition: all 0.5s ease;
    }}
    
    .chat-container {{
        background: rgba(0, 20, 40, 0.8);
        border-radius: 25px;
        padding: 25px;
        margin: 20px 0;
        backdrop-filter: blur(15px);
        border: 2px solid rgba(0, 255, 255, 0.3);
        max-height: 600px;
        overflow-y: auto;
    }}
    
    .message {{
        margin: 15px 0;
        padding: 15px 20px;
        border-radius: 20px;
        max-width: 80%;
        line-height: 1.6;
        animation: message-slide 0.3s ease-out;
    }}
    
    .message-user {{
        background: rgba(255, 0, 100, 0.3);
        border: 2px solid rgba(255, 0, 100, 0.5);
        margin-left: auto;
        text-align: right;
        color: white;
    }}
    
    .message-luna {{
        background: rgba(0, 255, 255, 0.2);
        border: 2px solid rgba(0, 255, 255, 0.5);
        color: white;
    }}
    
    @keyframes message-slide {{
        0% {{ transform: translateY(20px); opacity: 0; }}
        100% {{ transform: translateY(0); opacity: 1; }}
    }}
    
    .expression-indicator {{
        position: absolute;
        top: 20px;
        right: 20px;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: 3px solid white;
        animation: expression-pulse 1.5s infinite;
    }}
    
    .expr-happy {{ background: #00ff88; }}
    .expr-talking {{ background: #ff6b6b; animation: talking-blink 0.5s infinite; }}
    .expr-thinking {{ background: #ffd93d; animation: thinking-blink 1s infinite; }}
    .expr-excited {{ background: #ff0080; animation: excited-bounce 0.8s infinite; }}
    
    @keyframes expression-pulse {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.2); opacity: 0.7; }}
    }}
    
    @keyframes talking-blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.3; }}
    }}
    
    @keyframes thinking-blink {{
        0%, 50% {{ opacity: 1; }}
        75% {{ opacity: 0.5; }}
        100% {{ opacity: 1; }}
    }}
    
    @keyframes excited-bounce {{
        0%, 100% {{ transform: scale(1) translateY(0); }}
        50% {{ transform: scale(1.1) translateY(-5px); }}
    }}
    
    /* Luna's Expression Animations */
    @keyframes cyborg-happy {{
        0% {{ box-shadow: 0 0 30px rgba(0, 255, 255, 0.6), 0 0 80px rgba(0, 255, 255, 0.3); transform: scale(1); }}
        50% {{ box-shadow: 0 0 40px rgba(0, 255, 255, 0.8), 0 0 100px rgba(255, 0, 150, 0.4); transform: scale(1.02); }}
        100% {{ box-shadow: 0 0 50px rgba(0, 255, 255, 0.6), 0 0 80px rgba(0, 255, 255, 0.3); transform: scale(1); }}
    }}
    
    @keyframes cyborg-talking {{
        0% {{ box-shadow: 0 0 50px rgba(0, 255, 0, 0.8), 0 0 100px rgba(0, 255, 0, 0.3); filter: brightness(1.2) saturate(1.3); }}
        50% {{ box-shadow: 0 0 80px rgba(0, 255, 0, 1), 0 0 150px rgba(0, 255, 0, 0.6); filter: brightness(1.4) saturate(1.5); }}
        100% {{ box-shadow: 0 0 50px rgba(0, 255, 0, 0.8), 0 0 100px rgba(0, 255, 0, 0.3); filter: brightness(1.2) saturate(1.3); }}
    }}
    
    @keyframes cyborg-thinking {{
        0% {{ box-shadow: 0 0 30px rgba(255, 255, 0, 0.6), 0 0 80px rgba(255, 255, 0, 0.3); filter: brightness(1.1); }}
        50% {{ box-shadow: 0 0 60px rgba(255, 255, 0, 0.8), 0 0 120px rgba(255, 165, 0, 0.4); filter: brightness(1.3); }}
        100% {{ box-shadow: 0 0 30px rgba(255, 255, 0, 0.6), 0 0 80px rgba(255, 255, 0, 0.3); filter: brightness(1.1); }}
    }}
    
    @keyframes cyborg-excited {{
        0% {{ box-shadow: 0 0 40px rgba(255, 0, 150, 0.8), 0 0 90px rgba(255, 0, 150, 0.4); transform: scale(1); }}
        25% {{ box-shadow: 0 0 60px rgba(255, 0, 200, 1), 0 0 120px rgba(255, 100, 200, 0.6); transform: scale(1.03) rotate(1deg); }}
        50% {{ box-shadow: 0 0 80px rgba(255, 0, 250, 1), 0 0 150px rgba(255, 150, 250, 0.8); transform: scale(1.05) rotate(-1deg); }}
        75% {{ box-shadow: 0 0 60px rgba(255, 0, 200, 1), 0 0 120px rgba(255, 100, 200, 0.6); transform: scale(1.03) rotate(1deg); }}
        100% {{ box-shadow: 0 0 40px rgba(255, 0, 150, 0.8), 0 0 90px rgba(255, 0, 150, 0.4); transform: scale(1); }}
    }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# EXPRESSIVE BIZBOT INTERFACE WITH CHAT
# ═══════════════════════════════════════════════════════════════

def get_luna_image():
    """YOUR CYBORG AI WOMAN IMAGE"""
    return "https://us.idyllic.app/idea/G2EBbs5rSnSgo4m205e1_A"

def get_expression_indicator():
    """Get expression indicator class"""
    expr = st.session_state.luna_expression
    return f"expr-{expr}"

def get_expression_text():
    """Get expression text based on current state"""
    expressions = {
        "happy": "😊 Happy to help!",
        "talking": "🗣️ Speaking...",
        "thinking": "🤔 Analyzing...",
        "excited": "🎉 Excited!"
    }
    return expressions.get(st.session_state.luna_expression, "💫 Online")

def analyze_business_data(df):
    """Analyze uploaded business data"""
    analysis = {}
    
    try:
        # Basic info
        analysis['rows'] = len(df)
        analysis['columns'] = len(df.columns)
        
        # Find common business columns
        stock_cols = [col for col in df.columns if any(word in col.lower() for word in ['stock', 'quantity', 'inventory', 'amount'])]
        if stock_cols:
            analysis['stock_info'] = f"📦 Found stock column: {stock_cols[0]}"
            
            stock_data = df[stock_cols[0]]
            if stock_data.dtype in ['int64', 'float64']:
                low_stock_threshold = stock_data.quantile(0.2)
                low_stock_items = df[stock_data <= low_stock_threshold]
                analysis['low_stock_alert'] = f"⚠️ LOW STOCK: {len(low_stock_items)} items need attention!"
        
        # Sales analysis
        sales_cols = [col for col in df.columns if any(word in col.lower() for word in ['sales', 'revenue', 'amount', 'total'])]
        if sales_cols:
            analysis['sales_info'] = f"💰 Found sales column: {sales_cols[0]}"
            sales_data = df[sales_cols[0]]
            if sales_data.dtype in ['int64', 'float64']:
                total_sales = sales_data.sum()
                avg_sales = sales_data.mean()
                analysis['sales_summary'] = f"💰 Total Sales: {total_sales:,.0f} | Average: {avg_sales:,.0f}"
        
        # Product column
        name_cols = [col for col in df.columns if any(word in col.lower() for word in ['product', 'name', 'item'])]
        if name_cols:
            analysis['product_column'] = name_cols[0]
        
        return analysis
        
    except Exception as e:
        return {"error": str(e)}

# Main Interface
st.markdown('<div class="main">', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #00ffff, #0080ff); border-radius: 15px; margin-bottom: 20px;">
        <h2 style="margin: 0; color: white;">🤖 BizBot Pro</h2>
        <p style="margin: 5px 0; color: white; font-size: 12px;">Luna's Control Panel</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key
    st.markdown("### 🔑 Groq API Key")
    api_key = st.text_input(
        "Your Groq API Key", 
        type="password",
        value=st.session_state.groq_api_key,
        help="Get free key from console.groq.com"
    )
    
    if api_key != st.session_state.groq_api_key:
        st.session_state.groq_api_key = api_key
    
    if st.session_state.groq_api_key:
        st.success("✅ API Key Connected")
    else:
        st.warning("❌ API Key Required")
    
    st.markdown("---")
    
    # Voice Settings
    st.markdown("### 🔊 Voice Settings")
    st.session_state.voice_enabled = st.checkbox("Enable Luna's Voice", value=st.session_state.voice_enabled)
    
    if st.session_state.voice_enabled:
        st.success("🔊 Voice ON")
    else:
        st.warning("🔇 Voice OFF")
    
    st.markdown("---")
    
    # Language Settings
    st.markdown("### 🗣️ Language")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇺🇸 EN", use_container_width=True):
            st.session_state.current_language = "English"
    
    with col2:
        if st.button("🇪🇬 AR", use_container_width=True):
            st.session_state.current_language = "Arabic"
    
    st.markdown(f"**Current:** {st.session_state.current_language}")
    
    st.markdown("---")
    
    # Expression Controls
    st.markdown("### 😊 Luna's Mood")
    
    if st.button("😊 Happy", use_container_width=True):
        st.session_state.luna_expression = "happy"
    
    if st.button("🤔 Thinking", use_container_width=True):
        st.session_state.luna_expression = "thinking"
    
    if st.button("🎉 Excited", use_container_width=True):
        st.session_state.luna_expression = "excited"
    
    st.markdown(f"**Current:** {get_expression_text()}")

# MAIN CONTENT
col1, col2 = st.columns([1, 3])

with col2:
    # Hero Section
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    
    # Title
    st.markdown('<h1 class="title">🤖 BizBot Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your Expressive AI Cyborg Assistant with Luna</p>', unsafe_allow_html=True)
    
    # Luna's Cyborg Photo with Expressions
    st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
    st.image(get_luna_image(), width=400, caption="Luna - Your AI Cyborg Assistant")
    
    # Expression indicators
    st.markdown(f'<div class="expression-indicator {get_expression_indicator()}"></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Chat Section
st.markdown("### 💬 Chat with Luna")

# Display chat history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if st.session_state.chat_history:
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="message message-user">👤 **You:** {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message message-luna">💫 **Luna:** {msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat Input
col_chat1, col_chat2 = st.columns([4, 1])

with col_chat1:
    user_message = st.text_input(
        f"Message Luna ({st.session_state.current_language})...",
        key="chat_input"
    )

with col_chat2:
    send_button = st.button("Send", type="primary")

# Handle chat
if send_button and user_message:
    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now()
    })
    
    # Get AI response
    st.session_state.luna_expression = "thinking"
    
    with st.spinner("Luna is thinking..."):
        ai_response = get_ai_response(user_message)
    
    # Add Luna's response
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": ai_response,
        "timestamp": datetime.now()
    })
    
    # Speak the response
    if st.session_state.voice_enabled:
        speak_text(ai_response, st.session_state.current_language)
    
    st.rerun()

# File Upload Section
st.markdown("---")
st.markdown("### 📁 Upload Business Data")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file for business analysis",
    type=['csv', 'xlsx', 'xls']
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Analyze the data
        analysis = analyze_business_data(df)
        
        if "error" in analysis:
            st.error(f"Error analyzing data: {analysis['error']}")
        else:
            # Luna gets excited about new data
            st.session_state.luna_expression = "excited"
            
            # Create analysis message
            analysis_msg = f"I've analyzed your {uploaded_file.name}! It contains {analysis['rows']} rows and {analysis['columns']} columns."
            
            # Add to chat
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": analysis_msg,
                "timestamp": datetime.now()
            })
            
            # Speak about analysis
            if st.session_state.voice_enabled:
                speak_text(analysis_msg, st.session_state.current_language)
            
            st.success(f"✅ Data analyzed: {analysis['rows']} rows, {analysis['columns']} columns")
            
            # Show data preview
            st.dataframe(df.head(10))
            
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 40px; background: rgba(0, 20, 40, 0.8); border-radius: 25px; backdrop-filter: blur(20px); margin: 30px 0; border: 2px solid rgba(0, 255, 255, 0.3);">
    <h2 style="color: #00ffff; margin: 0; text-shadow: 0 0 20px rgba(0, 255, 255, 0.8);">🤖 BizBot Pro</h2>
    <p style="color: rgba(0, 255, 255, 0.8); font-size: 18px; margin: 10px 0;">
        Expressive • Intelligent • Beautiful
    </p>
    <p style="color: rgba(0, 255, 255, 0.6); font-size: 14px;">
        Groq API: {"✅ Connected" if st.session_state.groq_api_key else "❌ Not Connected"} | 
        Voice: {"✅ ON" if st.session_state.voice_enabled else "🔇 OFF"} | 
        Luna: {get_expression_text()}
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
