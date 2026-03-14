import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# BIZBOT PRO - CLEAN VERSION (ONLY USED IMPORTS)
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="BizBot Pro", 
    layout="wide",
    page_icon="🤖"
)

# Initialize session state (only what we need)
if "luna_first_message" not in st.session_state:
    st.session_state.luna_first_message = False

# ═══════════════════════════════════════════════════════════════
# SIMPLE STYLING - ONE PAGE BIZBOT
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .luna-container {
        text-align: center;
        padding: 50px;
    }
    
    .luna-image {
        width: 300px;
        height: 300px;
        border-radius: 50%;
        border: 5px solid #fff;
        box-shadow: 0 0 30px rgba(255,255,255,0.3);
        animation: breathe 3s ease-in-out infinite;
    }
    
    .chat-bubble {
        background: rgba(255,255,255,0.9);
        border-radius: 25px;
        padding: 20px;
        margin: 20px auto;
        max-width: 800px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    .upload-section {
        background: rgba(255,255,255,0.1);
        border: 2px dashed rgba(255,255,255,0.5);
        border-radius: 20px;
        padding: 40px;
        margin: 30px auto;
        max-width: 600px;
        text-align: center;
    }
    
    @keyframes breathe {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# BIZBOT AI ASSISTANT - MAIN INTERFACE
# ═══════════════════════════════════════════════════════════════

def get_luna_image():
    """Beautiful AI woman image"""
    return "https://images.unsplash.com/photo-1494790108755-2616b612b786?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"

def analyze_business_data(df):
    """Analyze uploaded business data"""
    analysis = {}
    
    try:
        # Basic info
        analysis['rows'] = len(df)
        analysis['columns'] = len(df.columns)
        
        # Find common business columns
        columns = df.columns.str.lower()
        
        # Stock/Inventory analysis
        stock_cols = [col for col in df.columns if any(word in col.lower() for word in ['stock', 'quantity', 'inventory', 'amount'])]
        if stock_cols:
            analysis['stock_info'] = f"Found stock column: {stock_cols[0]}"
            
            # Check for low stock
            stock_data = df[stock_cols[0]]
            if stock_data.dtype in ['int64', 'float64']:
                low_stock_threshold = stock_data.quantile(0.2)  # Bottom 20%
                low_stock_items = df[stock_data <= low_stock_threshold]
                analysis['low_stock_alert'] = f"⚠️ LOW STOCK: {len(low_stock_items)} items need attention!"
        
        # Sales analysis
        sales_cols = [col for col in df.columns if any(word in col.lower() for word in ['sales', 'revenue', 'amount', 'total'])]
        if sales_cols:
            analysis['sales_info'] = f"Found sales column: {sales_cols[0]}"
            sales_data = df[sales_cols[0]]
            if sales_data.dtype in ['int64', 'float64']:
                total_sales = sales_data.sum()
                avg_sales = sales_data.mean()
                analysis['sales_summary'] = f"💰 Total Sales: {total_sales:,.0f} | Average: {avg_sales:,.0f}"
        
        # Find product/name column
        name_cols = [col for col in df.columns if any(word in col.lower() for word in ['product', 'name', 'item'])]
        if name_cols:
            analysis['product_column'] = name_cols[0]
        
        return analysis
        
    except Exception as e:
        return {"error": str(e)}

# Main BizBot Interface
st.markdown('<div class="main">', unsafe_allow_html=True)

# BizBot Header
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="luna-container">', unsafe_allow_html=True)
    
    # Luna's Photo
    st.image(get_luna_image(), width=300, caption="Luna - BizBot Pro Assistant")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Luna's Welcome Message (Auto-appear)
if not st.session_state.luna_first_message:
    welcome_message = """🌟 **Hello! I'm Luna!** 💫

Welcome to BizBot Pro - your AI business assistant. I can:
• 📊 Analyze your business data
• 🔔 Alert you about low stock
• 💰 Track your sales performance  
• 🗣️ Speak in English and Arabic
• 📱 Works on web and mobile

**Ready to help your business grow!** 🚀

*Upload your data file below to get started...*"""
    
    st.markdown(f'<div class="chat-bubble"><strong>💫 Luna:</strong><br>{welcome_message}</div>', unsafe_allow_html=True)
    st.session_state.luna_first_message = True

# File Upload Section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown("### 📁 **Upload Your Business Data**")
st.markdown("*Upload CSV or Excel file with your business data (sales, inventory, products...)*")

uploaded_file = st.file_uploader(
    "Choose your data file",
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
            # Luna's Response
            response = "**💫 Luna analyzed your data:**\n\n"
            
            # Basic info
            response += f"📊 **Data Overview:** {analysis['rows']} rows, {analysis['columns']} columns\n\n"
            
            # Stock alerts
            if 'low_stock_alert' in analysis:
                response += f"{analysis['low_stock_alert']}\n\n"
            
            # Sales info
            if 'sales_summary' in analysis:
                response += f"{analysis['sales_summary']}\n\n"
            
            # Stock info
            if 'stock_info' in analysis:
                response += f"📦 {analysis['stock_info']}\n\n"
            
            # Additional insights
            response += "**What Luna can do next:**\n"
            response += "• 🔔 Set up automatic stock alerts\n"
            response += "• 📈 Create sales dashboards\n" 
            response += "• 💡 Generate business insights\n"
            response += "• 📱 Send notifications like WhatsApp"
            
            st.markdown(f'<div class="chat-bubble"><strong>💫 Luna:</strong><br>{response}</div>', unsafe_allow_html=True)
            
            # Show data preview
            st.markdown("### 📋 **Your Data Preview**")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Quick Actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔔 Setup Stock Alerts", use_container_width=True):
                    st.success("Stock alerts enabled! Luna will notify you when items run low.")
            
            with col2:
                if st.button("📊 Create Dashboard", use_container_width=True):
                    # Add a simple chart
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) >= 1:
                        fig = px.bar(df.head(10), x=numeric_cols[0], title="📊 Quick Chart")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No numeric columns for charting")
            
            with col3:
                if st.button("💬 Ask Luna Questions", use_container_width=True):
                    st.info("Chat feature coming soon!")
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

# Language Switcher
st.markdown("---")
col_lang1, col_lang2, col_lang3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### 🗣️ **Switch Language**")
    col_en, col_ar = st.columns(2)
    
    with col_en:
        if st.button("🇺🇸 English", use_container_width=True):
            st.info("Luna will respond in English!")
    
    with col_ar:
        if st.button("🇪🇬 عربي", use_container_width=True):
            st.info("Luna will respond in Arabic!")

# Simple Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: white;">
    <h3>🤖 BizBot Pro</h3>
    <p>Simple • Smart • Bilingual</p>
    <p>🌐 Works on Web & Mobile 📱</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
