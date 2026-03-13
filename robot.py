import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
from gtts import gTTS
import io

# ═══════════════════════════════════════════════════════════════
# 1. إعدادات الصفحة (يجب أن تكون أول سطر)
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="BilinguaBot 🤖",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# 2. تنسيق الواجهة (CSS) - ثيم الروبوت المظلم
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #00d4ff !important; }
    .user-bubble { background: linear-gradient(135deg, #1f6feb, #388bfd); color: #ffffff; padding: 12px 18px; border-radius: 18px 18px 4px 18px; margin: 6px 0 6px 18%; font-size: 15px; line-height: 1.5; word-wrap: break-word; }
    .bot-bubble { background: #161b22; color: #e6edf3; padding: 12px 18px; border-radius: 18px 18px 18px 4px; margin: 6px 18% 6px 0; border: 1px solid #30363d; border-left: 3px solid #00d4ff; font-size: 15px; line-height: 1.5; word-wrap: break-word; }
    .bot-bubble-ar { background: #161b22; color: #e6edf3; padding: 12px 18px; border-radius: 18px 18px 4px 18px; margin: 6px 0 6px 18%; border: 1px solid #30363d; border-right: 3px solid #00d4ff; font-size: 15px; line-height: 1.7; direction: rtl; text-align: right; word-wrap: break-word; }
    .chat-label-en { color: #00d4ff; font-size:12px; margin-bottom:2px; }
    .chat-label-ar { color: #00d4ff; font-size:12px; margin-bottom:2px; text-align:right; direction:rtl; }
    .stButton > button { background: linear-gradient(135deg, #00d4ff, #0066cc) !important; color: white !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 3. الدوال المساعدة (الصوت، الذكاء الاصطناعي، البيانات)
# ═══════════════════════════════════════════════════════════════

def detect_language(text: str) -> str:
    if not text or len(text.strip()) == 0: return "en"
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    return "ar" if (arabic_chars / len(text)) > 0.25 else "en"

def speak_text(text: str, lang: str):
    """تحويل النص لصوت وتشغيله تلقائياً (Autoplay)"""
    try:
        clean_text = text.replace("🤖", "").replace("✅", "").replace("⚠️", "").replace("🚨", "")
        tts = gTTS(text=clean_text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3', autoplay=True)
    except Exception as e:
        st.error(f"TTS Error: {e}")

def get_ai_response(message: str, language: str, inventory_df=None) -> str:
    """استدعاء Groq API للرد بذكاء على أي سؤال عام أو خاص بالمخزون"""
    if not st.session_state.api_key:
        return "⚠️ Please add your Groq API Key in the sidebar."
    
    client = Groq(api_key=st.session_state.api_key)
    context = f"\n\nInventory data:\n{inventory_df.to_string()}" if inventory_df is not None and not inventory_df.empty else ""

    system_prompt = (
        "أنت BilinguaBot، مساعد ذكي شامل. يمكنك الإجابة على أي سؤال عام أو تقني.\n"
        "إذا سألك المستخدم عن المخزون، استخدم البيانات المرفقة. رد باللغة العربية المصرية بأسلوب ودي." if language == "ar" else
        "You are BilinguaBot, a smart general assistant. Answer any general or technical questions.\n"
        "If asked about inventory, use the provided data. Respond in professional English."
    ) + context

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": message}],
            max_tokens=800, temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def get_sample_data():
    return pd.DataFrame({
        "Product": ["Rice 5kg","Oil 1L","Sugar 1kg","Pasta 500g"],
        "Stock": [5, 8, 2, 45],
        "Min_Stock": [20, 15, 10, 20],
        "Price_EGP": [85, 45, 25, 18]
    })

# ═══════════════════════════════════════════════════════════════
# 4. إدارة الحالة (Session State)
# ═══════════════════════════════════════════════════════════════
if "messages" not in st.session_state: st.session_state.messages = []
if "inventory_df" not in st.session_state: st.session_state.inventory_df = get_sample_data()
if "api_key" not in st.session_state: st.session_state.api_key = ""

# ═══════════════════════════════════════════════════════════════
# 5. الشريط الجانبي (Sidebar)
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("🤖 BilinguaBot")
    st.session_state.api_key = st.text_input("🔑 Groq API Key", type="password", value=st.session_state.api_key)
    st.divider()
    uploaded = st.file_uploader("📂 Upload Inventory (CSV/Excel)", type=["csv", "xlsx"])
    if uploaded:
        st.session_state.inventory_df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
        st.success("Data Loaded!")

# ═══════════════════════════════════════════════════════════════
# 6. الواجهة الرئيسية (Tabs)
# ═══════════════════════════════════════════════════════════════
tab_chat, tab_dash = st.tabs(["💬 AI Chat", "📊 Dashboard"])

with tab_chat:
    # عرض تاريخ الدردشة
    for msg in st.session_state.messages:
        role_class = "user-bubble" if msg["role"] == "user" else ("bot-bubble-ar" if detect_language(msg["content"]) == "ar" else "bot-bubble")
        st.markdown(f'<div class="{role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

    # إدخال المستخدم
    user_input = st.chat_input("Ask me anything... / اسألني أي حاجة...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(f'<div class="user-bubble">{user_input}</div>', unsafe_allow_html=True)
        
        with st.spinner("Thinking..."):
            lang = detect_language(user_input)
            reply = get_ai_response(user_input, lang, st.session_state.inventory_df)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
            role_class = "bot-bubble-ar" if lang == "ar" else "bot-bubble"
            st.markdown(f'<div class="{role_class}">{reply}</div>', unsafe_allow_html=True)
            speak_text(reply, lang) # تشغيل الصوت تلقائياً

with tab_dash:
    st.write("### Inventory Overview")
    st.dataframe(st.session_state.inventory_df, use_container_width=True)
    if not st.session_state.inventory_df.empty:
        fig = px.bar(st.session_state.inventory_df, x=st.session_state.inventory_df.columns[0], y="Stock", color="Stock", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)