import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
from gtts import gTTS
import io
import smtplib
from email.message import EmailMessage

# ═══════════════════════════════════════════════════════════════
# 1. إعدادات الهوية البصرية (Premium UI for Gumroad)
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="BilinguaBot Pro", page_icon="🤖", layout="wide")

ROBOT_IMG = "https://share.google/images/JPMFf0FV1vpUGdQSG"

st.markdown(f"""
<style>
    .stApp {{ background: #0e1117; color: #e6edf3; }}
    .user-bubble {{ background: #1f6feb; color: white; padding: 12px; border-radius: 15px 15px 0 15px; margin: 10px 0 10px 20%; text-align: right; }}
    .bot-container {{ display: flex; align-items: flex-start; margin: 10px 20% 10px 0; }}
    .bot-avatar {{ width: 45px; height: 45px; border-radius: 50%; background-image: url('{ROBOT_IMG}'); background-size: cover; border: 2px solid #00d4ff; margin-right: 12px; flex-shrink: 0; }}
    .bot-bubble {{ background: #161b22; border: 1px solid #30363d; padding: 12px; border-radius: 0 15px 15px 15px; border-left: 4px solid #00d4ff; }}
    .metric-card {{ background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; text-align: center; border-top: 3px solid #00d4ff; }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 2. الدوال الأساسية (AI & Email)
# ═══════════════════════════════════════════════════════════════

def send_email_alert(recipient, subject, body, sender_email, sender_pass):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_pass)
            smtp.send_message(msg)
        return True
    except: return False

def get_ai_response(message, df=None):
    if not st.session_state.api_key: return "Please enter API Key."
    client = Groq(api_key=st.session_state.api_key)
    context = f"Data:\n{df.head(10).to_string()}" if df is not None and not df.empty else ""
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"You are a Pro Data Assistant. {context}"}, {"role": "user", "content": message}]
        )
        return res.choices[0].message.content
    except Exception as e: return str(e)

# ═══════════════════════════════════════════════════════════════
# 3. إدارة الحالة (State)
# ═══════════════════════════════════════════════════════════════
if "messages" not in st.session_state: st.session_state.messages = []
if "inventory_df" not in st.session_state: st.session_state.inventory_df = pd.DataFrame()

# ═══════════════════════════════════════════════════════════════
# 4. واجهة المستخدم (Tabs)
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("⚙️ Setup Panel")
    st.session_state.api_key = st.text_input("Groq API Key", type="password")
    st.divider()
    st.subheader("📧 Email Settings")
    sender = st.text_input("Your Email (Gmail)")
    password = st.text_input("App Password", type="password")
    admin_mail = st.text_input("Admin Recipient")
    st.divider()
    uploaded = st.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"])
    if uploaded:
        st.session_state.inventory_df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)

tab1, tab2, tab3 = st.tabs(["💬 AI Chat", "📊 Analytics", "🔔 Alerts"])

with tab1:
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f'<div class="user-bubble">{m["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-container"><div class="bot-avatar"></div><div class="bot-bubble">{m["content"]}</div></div>', unsafe_allow_html=True)

    if p := st.chat_input("Ask BilinguaBot..."):
        st.session_state.messages.append({"role": "user", "content": p})
        st.markdown(f'<div class="user-bubble">{p}</div>', unsafe_allow_html=True)
        r = get_ai_response(p, st.session_state.inventory_df)
        st.session_state.messages.append({"role": "assistant", "content": r})
        st.markdown(f'<div class="bot-container"><div class="bot-avatar"></div><div class="bot-bubble">{r}</div></div>', unsafe_allow_html=True)

with tab2:
    df = st.session_state.inventory_df
    if not df.empty:
        nums = df.select_dtypes(include=['number']).columns
        txts = df.select_dtypes(include=['object']).columns
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="metric-card"><h3>Rows</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><h3>Columns</h3><h2>{len(df.columns)}</h2></div>', unsafe_allow_html=True)
        if len(nums) > 0 and len(txts) > 0:
            fig = px.bar(df, x=txts[0], y=nums[0], template="plotly_dark", color_discrete_sequence=['#00d4ff'])
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

with tab3:
    st.header("Admin Notification Center")
    msg_text = st.text_area("Alert Message")
    if st.button("🚀 Send Alert to Admin"):
        if sender and password and admin_mail:
            if send_email_alert(admin_mail, "BilinguaBot System Alert", msg_text, sender, password):
                st.success("Email sent!")
            else: st.error("Failed to send.")
        else: st.warning("Please fill all email settings in sidebar.")