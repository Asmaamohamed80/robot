import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# BIZBOT PRO - BEAUTIFUL VERSION WITH GREAT PHOTO
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="BizBot Pro", 
    layout="wide",
    page_icon="💫",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if "luna_first_message" not in st.session_state:
    st.session_state.luna_first_message = False

# ═══════════════════════════════════════════════════════════════
# BEAUTIFUL STYLING - MODERN DESIGN
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    .hero-container {
        text-align: center;
        padding: 60px 20px;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(15px);
        border-radius: 30px;
        margin: 20px auto;
        max-width: 900px;
        border: 2px solid rgba(255,255,255,0.2);
        box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    }
    
    .luna-image {
        width: 350px;
        height: 350px;
        border-radius: 50%;
        border: 8px solid rgba(255,255,255,0.9);
        box-shadow: 0 0 50px rgba(255,255,255,0.6), 0 30px 80px rgba(0,0,0,0.3);
        animation: breathe 4s ease-in-out infinite;
        object-fit: cover;
        margin: 0 auto;
        display: block;
    }
    
    .chat-bubble {
        background: rgba(255,255,255,0.95);
        border-radius: 30px;
        padding: 30px;
        margin: 30px auto;
        max-width: 850px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.15);
        border: 3px solid rgba(255,255,255,0.3);
        color: #333;
        font-size: 18px;
        line-height: 1.6;
    }
    
    .upload-section {
        background: rgba(255,255,255,0.15);
        border: 3px dashed rgba(255,255,255,0.8);
        border-radius: 25px;
        padding: 50px;
        margin: 40px auto;
        max-width: 700px;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        background: rgba(255,255,255,0.2);
        transform: translateY(-5px);
    }
    
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin: 30px 0;
        flex-wrap: wrap;
    }
    
    .stat-card {
        background: rgba(255,255,255,0.2);
        padding: 20px 30px;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255,255,255,0.3);
        text-align: center;
        min-width: 150px;
    }
    
    .action-button {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        border: none;
        border-radius: 25px;
        color: white;
        padding: 15px 30px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(255,107,107,0.3);
    }
    
    .action-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(255,107,107,0.5);
    }
    
    .language-button {
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        border: none;
        border-radius: 20px;
        color: white;
        padding: 12px 25px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .language-button:hover {
        transform: scale(1.05);
    }
    
    @keyframes breathe {
        0%, 100% { transform: scale(1) rotate(0deg); }
        50% { transform: scale(1.03) rotate(1deg); }
    }
    
    .title {
        font-size: 3.5em;
        background: linear-gradient(45deg, #fff, #f0f8ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        text-shadow: 0 2px 20px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        font-size: 1.4em;
        color: rgba(255,255,255,0.9);
        margin-bottom: 30px;
    }
    
    .luna-status {
        position: relative;
        bottom: -20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 8px 20px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 4px 15px rgba(255,107,107,0.4);
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# BEAUTIFUL BIZBOT INTERFACE
# ═══════════════════════════════════════════════════════════════

def get_luna_image():
    """Beautiful professional AI woman photo"""
    return "https://images.unsplash.com/photo-1544005313-94ddf0286df2?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"

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

# Hero Section
st.markdown('<div class="hero-container">', unsafe_allow_html=True)

# Title
st.markdown('<h1 class="title">🤖 BizBot Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI Business Assistant with Luna</p>', unsafe_allow_html=True)

# Luna's Photo
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image(get_luna_image(), width=350, caption="Luna - Your AI Assistant")
    st.markdown('<div class="luna-status">💫 Online & Ready to Help</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Welcome Message
if not st.session_state.luna_first_message:
    welcome_message = """🌟 **Hello! I'm Luna!** 💫

I'm your AI business assistant in BizBot Pro. I can:
• 📊 **Analyze** your business data instantly
• 🔔 **Alert** you about low stock situations
• 💰 **Track** your sales performance
• 🗣️ **Speak** in English and Arabic
• 📱 **Work** on web and mobile seamlessly

**Ready to help your business thrive!** 🚀

*Upload your business data file below to get started...*"""
    
    st.markdown(f'<div class="chat-bubble"><strong>💫 Luna says:</strong><br>{welcome_message}</div>', unsafe_allow_html=True)
    st.session_state.luna_first_message = True

# File Upload Section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown("### 📁 **Upload Your Business Data**")
st.markdown("*Upload CSV or Excel file with your business data*")

uploaded_file = st.file_uploader(
    "Drag & drop or click to browse",
    type=['csv', 'xlsx', 'xls'],
    label_visibility="collapsed"
)

st.markdown('</div>', unsafe_allow_html=True)

# Process uploaded file
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
            # Stats cards
            st.markdown('<div class="stats-container">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="stat-card">', unsafe_allow_html=True)
                st.metric("📊 Data Rows", f"{analysis['rows']:,}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="stat-card">', unsafe_allow_html=True)
                st.metric("📋 Columns", f"{analysis['columns']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="stat-card">', unsafe_allow_html=True)
                file_size = uploaded_file.size / 1024  # KB
                st.metric("📦 File Size", f"{file_size:.1f} KB")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Luna's Response
            response = "**💫 Luna analyzed your data!**\n\n"
            
            if 'low_stock_alert' in analysis:
                response += f"{analysis['low_stock_alert']}\n\n"
            
            if 'sales_summary' in analysis:
                response += f"{analysis['sales_summary']}\n\n"
            
            if 'stock_info' in analysis:
                response += f"{analysis['stock_info']}\n\n"
            
            response += "**Next steps I recommend:**\n"
            response += "• 🔔 Enable automatic stock alerts\n"
            response += "• 📈 Set up sales tracking dashboard\n"
            response += "• 📊 Generate detailed business insights\n"
            response += "• 📱 Configure WhatsApp-style notifications"
            
            st.markdown(f'<div class="chat-bubble"><strong>💫 Luna:</strong><br>{response}</div>', unsafe_allow_html=True)
            
            # Data Preview
            st.markdown("### 📋 **Data Preview**")
            st.dataframe(df.head(8), use_container_width=True)
            
            # Action Buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔔 Enable Alerts", use_container_width=True, type="primary"):
                    st.success("✅ Stock alerts activated! Luna will notify you of any shortages.")
            
            with col2:
                if st.button("📊 Create Charts", use_container_width=True):
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) >= 1:
                        fig = px.bar(df.head(10), x=numeric_cols[0], 
                                   title="📊 Business Data Chart",
                                   color_discrete_sequence=['#667eea'])
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("💡 Add numeric columns to create charts")
            
            with col3:
                if st.button("💬 Ask Luna", use_container_width=True):
                    st.info("Chat with Luna feature coming soon!")
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

# Language Section
st.markdown("---")
st.markdown("### 🗣️ **Language Settings**")

col1, col2 = st.columns(2)
with col1:
    if st.button("🇺🇸 English", use_container_width=True, type="primary"):
        st.success("Luna will speak in English!")
with col2:
    if st.button("🇪🇬 Arabic", use_container_width=True):
        st.success("Luna will speak in Arabic!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 40px; background: rgba(255,255,255,0.1); border-radius: 25px; backdrop-filter: blur(15px); margin: 30px 0;">
    <h2 style="color: white; margin: 0;">🤖 BizBot Pro</h2>
    <p style="color: rgba(255,255,255,0.8); font-size: 18px; margin: 10px 0;">
        Simple • Powerful • Beautiful
    </p>
    <p style="color: rgba(255,255,255,0.6); font-size: 14px;">
        🌐 Works on Web & Mobile • 📱 AI-Powered • 💫 Luna Assistant
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
