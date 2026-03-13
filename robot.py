import streamlit as st
import groq
from groq import Groq
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from gtts import gTTS
import base64
# ═══════════════════════════════════════════════════════════════
#  PAGE CONFIG — MUST BE FIRST LINE
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="BilinguaBot 🤖",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
#  DARK MODE CSS — Robot Theme
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* ── Main Background ── */
    .stApp { background-color: #0d1117; color: #e6edf3; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }

    /* ── Headers ── */
    h1, h2, h3 { color: #00d4ff !important; }

    /* ── Robot Avatar Pulse ── */
    .robot-wrap {
        text-align: center;
        padding: 10px 0;
    }
    .robot-avatar {
        font-size: 72px;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 0 12px #00d4ff88);
    }
    @keyframes float {
        0%   { transform: translateY(0px);   }
        50%  { transform: translateY(-8px);  }
        100% { transform: translateY(0px);   }
    }

    /* ── Chat Bubbles ── */
    .user-bubble {
        background: linear-gradient(135deg, #1f6feb, #388bfd);
        color: #ffffff;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 6px 0 6px 18%;
        font-size: 15px;
        line-height: 1.5;
        word-wrap: break-word;
    }
    .bot-bubble {
        background: #161b22;
        color: #e6edf3;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 6px 18% 6px 0;
        border: 1px solid #30363d;
        border-left: 3px solid #00d4ff;
        font-size: 15px;
        line-height: 1.5;
        word-wrap: break-word;
    }
    .bot-bubble-ar {
        background: #161b22;
        color: #e6edf3;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 6px 0 6px 18%;
        border: 1px solid #30363d;
        border-right: 3px solid #00d4ff;
        font-size: 15px;
        line-height: 1.7;
        direction: rtl;
        text-align: right;
        word-wrap: break-word;
    }
    .chat-label-en { color: #00d4ff; font-size:12px; margin-bottom:2px; }
    .chat-label-ar { color: #00d4ff; font-size:12px; margin-bottom:2px; text-align:right; direction:rtl; }

    /* ── Alert Cards ── */
    .alert-critical {
        background: #1f1010;
        border-left: 4px solid #f85149;
        border-radius: 8px;
        padding: 14px 16px;
        margin: 8px 0;
    }
    .alert-low {
        background: #1f1a0d;
        border-left: 4px solid #ffb800;
        border-radius: 8px;
        padding: 14px 16px;
        margin: 8px 0;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #0066cc) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }

    /* ── Input ── */
    .stTextInput input, .stTextArea textarea {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #e6edf3 !important;
        border-radius: 8px !important;
    }

    /* ── Metrics ── */
    [data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        border-top: 3px solid #00d4ff;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
        border-radius: 10px 10px 0 0;
        gap: 4px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0d1117;
        color: #8b949e;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1f6feb, #00d4ff) !important;
        color: #ffffff !important;
    }

    /* ── Divider ── */
    hr { border-color: #30363d; }

    /* ── Dataframe ── */
    .stDataFrame { border: 1px solid #30363d; border-radius: 8px; }

    /* ── Success / Error / Info ── */
    .stSuccess  { background-color: #0f2918 !important; border: 1px solid #3fb950 !important; }
    .stError    { background-color: #1f1010 !important; border: 1px solid #f85149 !important; }
    .stInfo     { background-color: #0d1e33 !important; border: 1px solid #1f6feb !important; }
    .stWarning  { background-color: #1f1a0d !important; border: 1px solid #ffb800 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def detect_language(text: str) -> str:
    """Returns 'ar' if text is mostly Arabic, else 'en'."""
    if not text or len(text.strip()) == 0:
        return "en"
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    ratio = arabic_chars / len(text)
    return "ar" if ratio > 0.25 else "en"


def get_ai_response(message: str, language: str, inventory_df=None) -> str:
    """Call Groq with bilingual system prompt."""
    client = Groq(api_key=st.session_state.api_key)

    context = ""
    if inventory_df is not None and not inventory_df.empty:
        context = f"\n\nInventory data (top 20 rows):\n{inventory_df.head(20).to_string()}"

    if language == "ar":
        system_prompt = (
            "أنت BilinguaBot، مساعد ذكي لإدارة المخزون.\n"
            "رد باللغة العربية المصرية بأسلوب واضح، ودي، ومهني.\n"
            "حلّل بيانات المخزون، اقترح إعادة التخزين، وحذّر من المشاكل.\n"
            "استخدم الأرقام والإحصائيات دائماً في إجاباتك.\n"
            "اجعل ردودك مختصرة ومفيدة."
            + context
        )
    else:
        system_prompt = (
            "You are BilinguaBot, an intelligent inventory management assistant.\n"
            "Respond in clear, friendly, professional English.\n"
            "Analyze inventory data, suggest restocking, alert on issues.\n"
            "Always use numbers and data in your answers.\n"
            "Keep responses concise and actionable."
            + context
        )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": message},
            ],
            max_tokens=600,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        if language == "ar":
            return "⚠️ خطأ في مفتاح API. تأكد من إدخال مفتاح Groq الصحيح في الشريط الجانبي."
        return "⚠️ Invalid API key. Please check your Groq API key in the sidebar."
    except Exception as e:
        if language == "ar":
            return f"⚠️ حدث خطأ: {str(e)}"
        return f"⚠️ Error: {str(e)}"


def get_sample_data() -> pd.DataFrame:
    return pd.DataFrame({
        "Product":          ["Rice 5kg","Cooking Oil 1L","Sugar 1kg","Pasta 500g","Tomato Paste","Tea 100g","Coffee 200g","Salt 1kg"],
        "Product_AR":       ["أرز 5 كيلو","زيت طهي 1 لتر","سكر 1 كيلو","معكرونة 500 جم","صلصة طماطم","شاي 100 جم","قهوة 200 جم","ملح 1 كيلو"],
        "Category":         ["Grains","Oils","Sweeteners","Grains","Condiments","Beverages","Beverages","Condiments"],
        "Stock":            [5, 8, 2, 45, 30, 12, 7, 100],
        "Min_Stock":        [20, 15, 10, 20, 15, 10, 10, 20],
        "Price_EGP":        [85, 45, 25, 18, 12, 35, 95, 8],
        "Sales_Last_Month": [120, 90, 80, 60, 45, 55, 30, 40],
    })


def get_alerts(df: pd.DataFrame) -> list:
    alerts = []
    if df is None or df.empty:
        return alerts
    if "Stock" not in df.columns or "Min_Stock" not in df.columns:
        return alerts
    product_col = "Product" if "Product" in df.columns else df.columns[0]
    for _, row in df.iterrows():
        if row["Stock"] < row["Min_Stock"]:
            ratio = row["Stock"] / row["Min_Stock"]
            alerts.append({
                "product":   str(row[product_col]),
                "stock":     int(row["Stock"]),
                "min_stock": int(row["Min_Stock"]),
                "shortage":  int(row["Min_Stock"] - row["Stock"]),
                "severity":  "critical" if ratio < 0.3 else "low",
            })
    return alerts


# ═══════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════
for key, default in [
    ("messages",     []),
    ("inventory_df", get_sample_data()),
    ("api_key",      ""),
    ("language",     "auto"),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="robot-wrap"><span class="robot-avatar">🤖</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<h2 style="text-align:center;color:#00d4ff;margin:0;">BilinguaBot</h2>'
        '<p style="text-align:center;color:#8b949e;font-size:12px;margin-top:4px;">'
        'Bilingual Inventory AI<br>مساعد المخزون الذكي</p>',
        unsafe_allow_html=True,
    )
    st.divider()

    # ── API Key ──
    st.markdown("### ⚙️ Settings / الإعدادات")
    raw_key = st.text_input(
        "🔑 OpenAI API Key",
        type="password",
        placeholder="sk-...",
        value=st.session_state.api_key,
        help="Get your key at platform.openai.com",
    )
    if raw_key != st.session_state.api_key:
        st.session_state.api_key = raw_key
    if st.session_state.api_key:
        st.success("✅ API Key saved!")
    else:
        st.warning("⚠️ Enter your OpenAI API key to use the AI chat.")

    st.divider()

    # ── Language ──
    st.markdown("### 🌍 Language / اللغة")
    lang_choice = st.radio(
        "",
        ["🔄 Auto-detect", "🇺🇸 English", "🇪🇬 العربية المصرية"],
        index=0,
    )
    if "English" in lang_choice:
        st.session_state.language = "en"
    elif "العربية" in lang_choice:
        st.session_state.language = "ar"
    else:
        st.session_state.language = "auto"

    st.divider()

    # ── Data Upload ──
    st.markdown("### 📂 Upload Data / رفع البيانات")
    uploaded = st.file_uploader(
        "CSV / Excel / JSON",
        type=["csv", "xlsx", "xls", "json"],
    )
    if uploaded:
        try:
            name = uploaded.name.lower()
            if name.endswith(".csv"):
                df_up = pd.read_csv(uploaded)
            elif name.endswith((".xlsx", ".xls")):
                df_up = pd.read_excel(uploaded)
            else:
                df_up = pd.read_json(uploaded)
            st.session_state.inventory_df = df_up
            st.success(f"✅ {len(df_up)} rows loaded!")
        except Exception as e:
            st.error(f"Upload error: {e}")

    if st.button("📊 Load Sample Data / تحميل بيانات تجريبية", use_container_width=True):
        st.session_state.inventory_df = get_sample_data()
        st.success("✅ Sample data loaded!")

    st.divider()
    st.markdown(
        '<p style="text-align:center;color:#8b949e;font-size:11px;">'
        'v1.0 — BilinguaBot MVP<br>Built with ❤️ &amp; AI</p>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════
#  MAIN HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown(
    '<h1>🤖 BilinguaBot — Inventory Intelligence</h1>'
    '<p style="color:#8b949e;margin-top:-12px;">'
    'Your bilingual AI assistant for smart inventory management &nbsp;|&nbsp; '
    'مساعدك الذكي لإدارة المخزون بلغتين</p>',
    unsafe_allow_html=True,
)

tab_chat, tab_dash, tab_alerts = st.tabs([
    "💬  AI Chat / الدردشة",
    "📊  Dashboard / لوحة التحكم",
    "⚠️  Alerts / التنبيهات",
])


# ═══════════════════════════════════════════════════════════════
#  TAB 1 — AI CHAT
# ═══════════════════════════════════════════════════════════════
with tab_chat:
    col_chat, col_hints = st.columns([3, 1])

    with col_chat:
        st.markdown("### 💬 Chat with BilinguaBot")

        # Display history
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="user-bubble">👤 {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                lang = detect_language(msg["content"])
                if lang == "ar":
                    st.markdown(
                        f'<div class="chat-label-ar">🤖 BilinguaBot</div>'
                        f'<div class="bot-bubble-ar">{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="chat-label-en">🤖 BilinguaBot</div>'
                        f'<div class="bot-bubble">{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )

        # Input form
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Message / رسالة",
                placeholder="Which products are low?  /  إيه المنتجات اللي مخزونها قليل؟",
                label_visibility="collapsed",
            )
            c1, c2 = st.columns([4, 1])
            with c1:
                send_btn  = st.form_submit_button("🚀 Send / إرسال", use_container_width=True)
            with c2:
                clear_btn = st.form_submit_button("🗑️ Clear", use_container_width=True)

        if clear_btn:
            st.session_state.messages = []
            st.rerun()

        if send_btn and user_input.strip():
            if not st.session_state.api_key:
                st.error("⚠️ Please add your OpenAI API Key in the sidebar first!")
            else:
                lang = (
                    detect_language(user_input)
                    if st.session_state.language == "auto"
                    else st.session_state.language
                )
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.spinner("🤖 Thinking… / جاري التفكير…"):
                    reply = get_ai_response(user_input, lang, st.session_state.inventory_df)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()

    with col_hints:
        st.markdown("### 💡 Try asking:")
        st.markdown("""
**🇺🇸 English:**
- Which products are low?
- What should I reorder?
- Who is my best seller?
- Summarize my inventory
- What's my total stock value?

---

**🇪🇬 Arabic:**
- إيه اللي مخزونه وصل للحد الأدنى؟
- محتاج أطلب إيه دلوقتي؟
- إيه المنتج الأكثر مبيعاً؟
- حلّل بيانات المخزون
- كام قيمة المخزون الكلية؟
""")


# ═══════════════════════════════════════════════════════════════
#  TAB 2 — DASHBOARD
# ═══════════════════════════════════════════════════════════════
with tab_dash:
    df = st.session_state.inventory_df

    st.markdown("### 📊 Inventory Dashboard / لوحة تحكم المخزون")

    if df is None or df.empty:
        st.info("📂 Upload inventory data or load sample data from the sidebar.")
    else:
        # ── Metrics ──
        has_stock    = "Stock"    in df.columns
        has_minstock = "Min_Stock" in df.columns
        has_price    = "Price_EGP" in df.columns
        has_sales    = "Sales_Last_Month" in df.columns

        total_products = len(df)
        low_stock_count = int((df["Stock"] < df["Min_Stock"]).sum()) if (has_stock and has_minstock) else 0
        total_units     = int(df["Stock"].sum()) if has_stock else 0
        inv_value       = float((df["Stock"] * df["Price_EGP"]).sum()) if (has_stock and has_price) else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📦 Total Products",   total_products)
        m2.metric("🔴 Low Stock Alerts", low_stock_count,
                  delta=f"-{low_stock_count}" if low_stock_count else None)
        m3.metric("📊 Total Units",      f"{total_units:,}")
        m4.metric("💰 Inventory Value",  f"{inv_value:,.0f} EGP" if has_price else "N/A")

        st.divider()

        # ── Charts row 1 ──
        product_col = "Product" if "Product" in df.columns else df.columns[0]

        if has_stock:
            c_left, c_right = st.columns(2)
            with c_left:
                fig_bar = px.bar(
                    df.head(8), x=product_col, y="Stock",
                    title="📦 Current Stock Levels",
                    color="Stock",
                    color_continuous_scale=["#f85149", "#ffb800", "#3fb950"],
                    template="plotly_dark",
                )
                fig_bar.update_layout(
                    plot_bgcolor="#161b22", paper_bgcolor="#161b22",
                    font_color="#e6edf3", title_font_color="#00d4ff",
                )
                if has_minstock:
                    fig_bar.add_hline(
                        y=df["Min_Stock"].mean(),
                        line_dash="dash", line_color="#f85149",
                        annotation_text="Avg Min Stock",
                        annotation_font_color="#f85149",
                    )
                st.plotly_chart(fig_bar, use_container_width=True)

            with c_right:
                if "Category" in df.columns:
                    cat_df = df.groupby("Category")["Stock"].sum().reset_index()
                    fig_pie = px.pie(
                        cat_df, values="Stock", names="Category",
                        title="🏷️ Stock by Category",
                        template="plotly_dark",
                        color_discrete_sequence=px.colors.sequential.Blues_r,
                    )
                    fig_pie.update_layout(
                        plot_bgcolor="#161b22", paper_bgcolor="#161b22",
                        font_color="#e6edf3", title_font_color="#00d4ff",
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

        # ── Charts row 2 ──
        if has_sales:
            fig_top = px.bar(
                df.nlargest(8, "Sales_Last_Month"),
                x=product_col, y="Sales_Last_Month",
                title="🏆 Top Sellers — Last Month",
                color="Sales_Last_Month",
                color_continuous_scale="Blues",
                template="plotly_dark",
            )
            fig_top.update_layout(
                plot_bgcolor="#161b22", paper_bgcolor="#161b22",
                font_color="#e6edf3", title_font_color="#00d4ff",
            )
            st.plotly_chart(fig_top, use_container_width=True)

        # ── Stock vs Min comparison ──
        if has_stock and has_minstock:
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(
                name="Current Stock", x=df[product_col], y=df["Stock"],
                marker_color="#1f6feb",
            ))
            fig_comp.add_trace(go.Bar(
                name="Min Required", x=df[product_col], y=df["Min_Stock"],
                marker_color="#f85149", opacity=0.7,
            ))
            fig_comp.update_layout(
                barmode="group", title="📉 Stock vs Minimum Required",
                plot_bgcolor="#161b22", paper_bgcolor="#161b22",
                font_color="#e6edf3", title_font_color="#00d4ff",
                template="plotly_dark",
            )
            st.plotly_chart(fig_comp, use_container_width=True)

        # ── Full Table ──
        st.markdown("### 📋 Full Inventory Table / جدول المخزون الكامل")
        st.dataframe(df, use_container_width=True, height=280)


# ═══════════════════════════════════════════════════════════════
#  TAB 3 — ALERTS
# ═══════════════════════════════════════════════════════════════
with tab_alerts:
    st.markdown("### ⚠️ Stock Alerts / تنبيهات المخزون")

    df     = st.session_state.inventory_df
    alerts = get_alerts(df)

    if not alerts:
        st.success("✅ All products are well-stocked! / كل المنتجات في المخزون كويس!")
        if df is not None and not df.empty and "Stock" in df.columns and "Min_Stock" in df.columns:
            product_col = "Product" if "Product" in df.columns else df.columns[0]
            df_status = df[[product_col, "Stock", "Min_Stock"]].copy()
            df_status["Status"] = df_status.apply(
                lambda r: "🟢 OK" if r["Stock"] >= r["Min_Stock"] else "🔴 Low", axis=1
            )
            st.dataframe(df_status, use_container_width=True)
    else:
        st.error(f"🚨 {len(alerts)} product(s) need attention! / {len(alerts)} منتج يحتاج انتباه!")
        st.markdown("")

        for a in alerts:
            css_class = "alert-critical" if a["severity"] == "critical" else "alert-low"
            icon      = "🔴 CRITICAL" if a["severity"] == "critical" else "🟡 LOW"
            color     = "#f85149"    if a["severity"] == "critical" else "#ffb800"
            st.markdown(
                f'<div class="{css_class}">'
                f'  <strong style="color:{color};">{icon}</strong> &nbsp;'
                f'  <strong style="color:#e6edf3; font-size:15px;">{a["product"]}</strong><br>'
                f'  <span style="color:#8b949e; font-size:13px;">'
                f'    Current Stock: <strong style="color:{color};">{a["stock"]}</strong> units &nbsp;|&nbsp; '
                f'    Minimum Required: <strong style="color:#ffb800;">{a["min_stock"]}</strong> units &nbsp;|&nbsp; '
                f'    Order Now: <strong style="color:#3fb950;">{a["shortage"]}</strong> units'
                f'  </span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.divider()

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🤖 Generate AI Restock Plan (EN)", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("⚠️ Please add your API key in the sidebar.")
                else:
                    products_str = ", ".join([a["product"] for a in alerts])
                    query = (
                        f"Generate a restock priority plan for these low-stock items: {products_str}. "
                        "For each, state urgency level (Critical/Medium), quantity to order, and reason."
                    )
                    with st.spinner("Generating plan…"):
                        plan = get_ai_response(query, "en", df)
                    st.success("✅ AI Restock Plan:")
                    st.write(plan)
                    
                    import io
                    tts_en =gTTS(text=plan,lang='en')

                    fp_en =io.BytesIO()
                    tts_en.write_to_fp(fp_en)
                    st.audio(fp_en, format='audio/mp3',autoplay=True)


        with col_btn2:
            if st.button("🤖 خطة إعادة التخزين بالعربي", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("⚠️ أضف مفتاح API في الشريط الجانبي.")
                else:
                    products_str = "، ".join([a["product"] for a in alerts])
                    query = f"اعمل خطة إعادة تخزين لهذه المنتجات: {products_str}. اذكر الأولوية والكميات المطلوبة."
                    with st.spinner("جاري الإنشاء…"):
                         plan = get_ai_response(query, "ar", df)
                    st.success("✅ خطة إعادة التخزين:")
                    st.write(plan)
                    tts_ar = gTTS(text=plan, lang='ar')
                    fp_ar = io.BytesIO()
                    tts_ar.write_to_fp(fp_ar)
                    st.audio(fp_ar, format='audio/mp3,autoplay=True')
