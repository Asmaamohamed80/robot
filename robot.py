
import streamlit as st
import pandas as pd
from groq import Groq
from gtts import gTTS
import io

# ═══════════════════════════════════════════════════════════════
# 1. التصميم السينمائي (Full Screen AI Visual)
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="BilinguaBot Pro 🤖", layout="wide")

# رابط صورتك اللي اخترتها للروبوت
ROBOT_IMG = "https://share.google/images/JPMFf0FV1vpUGdQSG"

st.markdown(f"""
<style>
    /* جعل صورة الروبوت هي الخلفية الأساسية للشاشة بالكامل */
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), url('{ROBOT_IMG}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* إخفاء العناصر غير الضرورية للتركيز على تجربة الروبوت */
    [data-testid="stHeader"], [data-testid="stFooter"] {{ visibility: hidden; }}

    /* صندوق الكلام (أسفل الشاشة) */
    .chat-box {{
        position: fixed;
        bottom: 100px;
        left: 5%;
        right: 5%;
        background: rgba(13, 17, 23, 0.9);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 20px;
        z-index: 1000;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
        direction: rtl;
    }}

    .bot-text {{
        font-size: 22px;
        color: #00d4ff;
        font-weight: bold;
        margin-bottom: 5px;
    }}

    .user-text {{
        font-size: 16px;
        color: #888;
        margin-bottom: 10px;
    }}

    /* تعديل مكان خانة الكتابة لتكون تحت الصندوق مباشرة */
    .stChatInput {{
        position: fixed !important;
        bottom: 30px !important;
        left: 5% !important;
        right: 5% !important;
        z-index: 1001;
    }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 2. عقل الروبوت (Egyptian Arabic & Data Logic)
# ═══════════════════════════════════════════════════════════════

def get_ai_response(message, df=None):
    if not st.session_state.get("api_key"): 
        return "يا باشا، أضف مفتاح الـ API في القائمة الجانبية عشان أقدر أرد عليك!"
    
    client = Groq(api_key=st.session_state.api_key)
    
    # دمج بيانات المستخدم (لو موجودة) في سياق الكلام
    context = ""
    if df is not None and not df.empty:
        context = f"\n[بيانات المستخدم]:\n{df.head(10).to_string()}\n"

    system_msg = (
        f"You are BilinguaBot. {context}\n"
        "Strict Rule: Always respond in Egyptian Arabic (Ammiya/لهجة مصرية عامية).\n"
        "Be very helpful, use words like 'يا باشا', 'يا هندسة', 'من عيوني'.\n"
        "You are an expert data analyst and a friendly companion."
    )

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": message}],
            temperature=0.8
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"حصلت مشكلة بسيطة يا بطل: {str(e)}"

def play_audio(text):
    try:
        # تحويل النص العربي لصوت (gTTS يتعرف على اللهجة من النص المكتوب)
        tts = gTTS(text=text, lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3', autoplay=True)
    except: pass

# ═══════════════════════════════════════════════════════════════
# 3. التشغيل وإدارة الجلسة
# ═══════════════════════════════════════════════════════════════

if "history" not in st.session_state: st.session_state.history = []

with st.sidebar:
    st.title("⚙️ الإعدادات (Setup)")
    st.session_state.api_key = st.text_input("Groq API Key", type="password")
    st.divider()
    uploaded = st.file_uploader("ارفع ملف داتا لو حابب أحلله (CSV/Excel)", type=["csv", "xlsx"])
    st.session_state.df = pd.DataFrame()
    if uploaded:
        try:
            st.session_state.df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
            st.success("الداتا جاهزة يا باشا! ✅")
        except: st.error("في مشكلة في الملف.")

# عرض آخر محادثة في الصندوق السفلي (الشكل السينمائي)
if st.session_state.history:
    last = st.session_state.history[-1]
    st.markdown(f'''
        <div class="chat-box">
            <div class="user-text">إنت: {last['u']}</div>
            <div class="bot-text">الروبوت: {last['b']}</div>
        </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown('''
        <div class="chat-box">
            <div class="bot-text">أهلاً بيك يا باشا! أنا BilinguaBot.. أؤمرني، حابب نحلل داتا ولا ندردش في أي حاجة؟</div>
        </div>
    ''', unsafe_allow_html=True)

# خانة الإدخال
if prompt := st.chat_input("اكتب كلامك هنا يا هندسة..."):
    # معالجة الرد
    reply = get_ai_response(prompt, st.session_state.get('df'))
    st.session_state.history.append({"u": prompt, "b": reply})
    
    # تشغيل الصوت التلقائي
    play_audio(reply)
    st.rerun()