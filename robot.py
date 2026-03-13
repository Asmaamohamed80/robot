import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
from gtts import gTTS
import io
import smtplib
from email.message import EmailMessage

# ═══════════════════════════════════════════════════════════════
# 1. إعدادات الصفحة والتصميم الفاخر (Premium UI)
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="BilinguaBot Pro 🤖", page_icon="🤖", layout="wide")

# رابط صورة الروبوت الخاصة بك
ROBOT_IMG = "https://share.google/images/JPMFf0FV1vpUGdQSG"

st.markdown(f"""
<style>
    .stApp {{ background: #0d1117; color: #e6edf3; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
    
    /* تنسيق فقاعات الدردشة */
    .user-bubble {{ 
        background: linear-gradient(135deg, #007bff, #0056b3); 
        color: white; padding: 15px; border-radius: 20px 20px 5px 20px; 
        margin: 10px 0 10px 20%; text-align: right; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    
    .bot-container {{ display: flex; align-items: flex-start; margin: 15px 20% 15px 0; }}
    .bot-avatar {{ 
        width: 50px; height: 50px; border-radius: 50%; 
        background-image: url('{ROBOT_IMG}'); background-size: cover; 
        border: 2px solid #00d4ff; margin-right: 15px; flex-shrink: 0;
        box-shadow: 0 0 10px #00d4ff;
    }}
    
    .bot-bubble {{ 
        background: #161b22; border: 1px solid #30363d; 
        padding: 15px; border-radius: 5px 20px 20px 20px; 
        border-left: 5px solid #00d4ff; color: #e6edf3; line-height: 1.6;
    }}

    /* كروت الإحصائيات */
    .metric-card {{
        background: rgba(22, 27, 34, 0.8); border: 1px solid #00d4ff33;
        border-radius: 15px; padding: 25px; text-align: center;
        transition: 0.3s;
    }}
    .metric-card:hover {{ transform: translateY(-5px); border-color: #00d4ff; }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 2. الدوال الذكية (AI, TTS, Email)
# ═══════════════════════════════════════════════════════════════

def detect_language(text):
    return "ar" if any('\u0600' <= c <= '\u06FF' for c in text) else "en"

def speak_text(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3', autoplay=True)
    except: pass

def get_ai_response(message, lang, df=None):
    if not st.session_state.get("api_key"): return "⚠️ Please add your Groq API Key in the Sidebar."
    client = Groq(api_key=st.session_state.api_key)
    
    context = ""
    if df is not None and not df.empty:
        context = f"\n[Data Context]:\n{df.head(15).to_string()}\nColumns: {list(df.columns)}"

    system_msg = (
        f"You are BilinguaBot, a professional AI Analyst. {context}\n"
        "Respond in friendly Egyptian Arabic for 'ar', or professional English for 'en'."
    )

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": message}],
            temperature=0.7
        )
        return res.choices[0].message.content
    except Exception as e: return f"Error: {str(e)}"

# ═══════════════════════════════════════════════════════════════
# 3. واجهة المستخدم والتحكم
# ═══════════════════════════════════════════════════════════════
if "messages" not in st.session_state: st.session_state.messages = []
if "inventory_df" not in st.session_state: st.session_state.inventory_df = pd.DataFrame()

with st.sidebar:
    st.image(ROBOT_IMG, width=100)
    st.title("Admin Panel")
    st.session_state.api_key = st.text_input("🔑 Groq API Key", type="password")
    st.divider()
    st.subheader("📧 Notifications")
    sender = st.text_input("Sender Email")
    password = st.text_input("App Password", type="password")
    admin_mail = st.text_input("Admin Email")
    st.divider()
    uploaded = st.file_uploader("📂 Upload CSV/Excel", type=["csv", "xlsx"])
    if uploaded:
        df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
        df.columns = [str(c).strip() for c in df.columns]
        st.session_state.inventory_df = df

tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📊 Smart Dashboard", "🔔 Alert System"])

with tab1:
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f'<div class="user-bubble">{m["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-container"><div class="bot-avatar"></div><div class="bot-bubble">{m["content"]}</div></div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ask BilinguaBot..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)
        
        with st.spinner("Processing..."):
            lang = detect_language(prompt)
            reply = get_ai_response(prompt, lang, st.session_state.inventory_df)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.markdown(f'<div class="bot-container"><div class="bot-avatar"></div><div class="bot-bubble">{reply}</div></div>', unsafe_allow_html=True)
            speak_text(reply, lang)

with tab2:
    df = st.session_state.inventory_df
    if not df.empty:
        # حل مشكلة الرسم البياني
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        txt_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric-card"><h4>Records</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><h4>Analysis</h4><h2 style="color:#00ff00;">AI Active</h2></div>', unsafe_allow_html=True)
        with c3: 
            val = df[num_cols[0]].sum() if num_cols else 0
            st.markdown(f'<div class="metric-card"><h4>Sum Metric</h4><h2>{val:,.0f}</h2></div>', unsafe_allow_html=True)
        
        st.divider()
        if num_cols and txt_cols:
            fig = px.bar(df, x=txt_cols[0], y=num_cols[0], color=num_cols[0], template="plotly_dark", title="Smart Visualization")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

with tab3:
    st.header("Admin Alerts")
    alert_msg = st.text_area("Alert Details")
    if st.button("🚀 Send Email Now"):
        # منطق الإرسال المذكور سابقاً
        st.info("Email Feature Ready for Setup.")