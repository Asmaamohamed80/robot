# 🤖 BilinguaBot — Bilingual AI Inventory Assistant

A smart inventory management app that speaks **English AND Egyptian Arabic**.

---

## 🚀 HOW TO RUN (Step by Step)

### ✅ STEP 1 — Make sure Python is installed
- Open your terminal or VS Code terminal
- Type: `python --version`
- If you see Python 3.8 or higher → you're good!
- If not → download from: https://www.python.org/downloads/

---

### ✅ STEP 2 — Install the required libraries
Open terminal in this folder and run:

```
pip install -r requirements.txt
```

Wait for it to finish (takes 1–2 minutes).

---

### ✅ STEP 3 — Run the app

```
streamlit run app.py
```

Your browser will open automatically at:
👉 http://localhost:8501

---

### ✅ STEP 4 — Get your OpenAI API Key
1. Go to: https://platform.openai.com
2. Create a free account
3. Click "API Keys" → "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. Paste it in the **sidebar** of the app

---

## 📱 What the App Does

| Feature | Description |
|---------|-------------|
| 💬 AI Chat | Talk to the robot in English OR Arabic |
| 📊 Dashboard | See charts of your stock levels |
| ⚠️ Alerts | Get warnings when products are low |
| 📂 Upload | Import CSV, Excel, or JSON files |
| 🔄 Language | Auto-detects English or Egyptian Arabic |

---

## 🗂️ File Structure

```
bilinguabot/
├── app.py              ← Main app (run this!)
├── requirements.txt    ← Libraries to install
└── README.md           ← This file
```

---

## 💬 Sample Questions to Ask the Robot

**English:**
- "Which products are low on stock?"
- "What should I reorder today?"
- "Who is my best selling product?"
- "Summarize my inventory status"

**العربية:**
- "إيه المنتجات اللي مخزونها قليل؟"
- "محتاج أطلب إيه دلوقتي؟"
- "إيه المنتج الأكثر مبيعاً؟"
- "حلّل بيانات المخزون"

---

## ⚙️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `streamlit: command not found` | Run `pip install streamlit` again |
| App won't start | Make sure you're in the `bilinguabot` folder |
| API key error | Double-check your key starts with `sk-` |
| Arabic text looks weird | Make sure your browser is set to UTF-8 encoding |

---

Built with ❤️ using Python, Streamlit & OpenAI
