import streamlit as st
import pandas as pd
from groq import Groq
from gtts import gTTS
import io

# ═══════════════════════════════════════════════════════════════
# 1. تصميم الـ "Full-Screen Bot" (ده اللي هيظبط الصورة يا محمد)
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="BilinguaBot Pro 🤖", layout="wide")

ROBOT_IMG = "https://share.google/images/JPMFf0FV1vpUGdQSG"

st.markdown(f"""
<style>
    /* جعل الخلفية ثابتة وبكامل الشاشة بدون تكرار */
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.7)), url('{ROBOT_IMG}');
        background-size: cover;
        background-position: top center;
        background-attachment: fixed;
    }}
    
    /* إخفاء الزيادات */
    [data-testid="stHeader"], [data-testid="stFooter"], [data-testid="stToolbar"] {{ visibility: hidden; }}

    /* صندوق الكلام: شفاف وأنيق أسفل الشاشة */
    .chat-container {{
        position: fixed;
        bottom: 110px;
        left: 10%;
        right: 10%;
        background: rgba(0, 0, 0, 0.85); /* شفافية غامقة عشان الكلام يبان */
        border: 1px solid #00d4ff;
        border-radius: 20px;
        padding: 25px;
        z-index: 1000;
        backdrop-filter: blur(5px); /* تأثير زجاجي */
        direction: rtl;
    }}

    .bot-name {{ color: #00d4ff; font-weight: bold; font-size: 18px; margin-bottom: 5px; }}
    .bot-text {{ font-size: 24px; color: #ffffff; line-height: 1.4; }}
    .user-text {{ font-size: 14px; color: #888; margin-bottom: 10px; }}

    /* خانة الكتابة تكون تحت الصندوق بالضبط */
    .stChatInput {{
        position: fixed !important;
        bottom: 30px !important;
        left: 10% !important;
        right: 10% !important;
        z-index: 1001;
    }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 2. الدوال الذكية (Egyptian Arabic)
# ═══════════════════════════════════════════════════════════════

def get_ai_response(message, df=None):
    if not st.session_state.get("api_key"): return "يا باشا حط الـ API Key في الجنب الأول!"
    client = Groq(api_key=st.session_state.api_key)
    
    context = f"\n[Data]:\n{df.head(5).to_string()}" if df is not None and not df.empty else ""
    
    system_instruction = (
        f"You are BilinguaBot. {context}\n"
        "Respond ONLY in Egyptian Arabic (لهجة مصرية عامية). "
        "Be friendly, use words like 'يا باشا', 'يا هندسة', 'من عنيا'."
    )

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": message}]
        )
        return res.choices[0].message.content
    except Exception as e: return f"حصلت مشكلة: {str(e)}"

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ar')
        fp = io.BytesIO(); tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3', autoplay=True)
    except: pass

# ═══════════════════════════════════════════════════════════════
# 3. التشغيل
# ═══════════════════════════════════════════════════════════════
if "chat_history" not in st.session_state: st.session_state.chat_history = []

with st.sidebar:
    st.title("Admin")
    st.session_state.api_key = st.text_input("Groq API Key", type="password")
    uploaded = st.file_uploader("ارفع الملف هنا")
    if uploaded:
        st.session_state.df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)

# عرض آخر رد بشكل سينمائي
if st.session_state.chat_history:
    last = st.session_state.chat_history[-1]
    st.markdown(f'''
        <div class="chat-container">
            <div class="user-text">إنت قلت: {last['u']}</div>
            <div class="bot-name">BilinguaBot 🤖</div>
            <div class="bot-text">{last['b']}</div>
        </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown('''
        <div class="chat-container">
            <div class="bot-text">أهلاً بيك يا محمد يا هندسة! أنا جاهز.. تحب نبدأ بإيه النهاردة؟</div>
        </div>
    ''', unsafe_allow_html=True)

if prompt := st.chat_input("اكتب سؤالك هنا يا محمد..."):
    with st.spinner("بيفكر..."):
        answer = get_ai_response(prompt, st.session_state.get('df'))
        st.session_state.chat_history.append({"u": prompt, "b": answer})
        play_audio(answer)
        st.rerun()