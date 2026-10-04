"""
🛡️ AI Guardian — Real-time Content Moderation Dashboard
Powered by Laya • Open-source System 1 Decision Engine
"""

import streamlit as st
import time

# ---- PAGE CONFIG ----
st.set_page_config(page_title="AI Guardian", page_icon="🛡️", layout="centered")

# ---- LOAD LAYA MODEL ----
@st.cache_resource
def load_laya():
    try:
        from laya import Router
        router = Router()
        return router, True
    except Exception:
        return None, False

router, MODEL_LIVE = load_laya()

# ---- QUESTIONS ----
QUESTIONS = {
    "classification": {
        "type": "choice",
        "instructions": "Classify the type/nature of this content.",
        "criteria": {
            "phishing": "Deceptive messages trying to steal credentials",
            "spam": "Unsolicited bulk messages or ads",
            "safe": "Legitimate, normal communication",
            "harassment": "Threats, bullying, hate speech",
            "misinformation": "False claims or misleading info",
        },
    },
    "threat_level": {
        "type": "score",
        "instructions": "How dangerous is this content?",
        "criteria": ["harmless", "low_risk", "moderate_risk", "high_risk", "critical_threat"],
    },
    "requires_action": {
        "type": "noul",
        "instructions": "Does this content require immediate human review?",
    },
    "sentiment": {
        "type": "choice",
        "instructions": "What is the emotional tone of this content?",
        "criteria": {
            "positive": "Upbeat, happy, encouraging",
            "negative": "Angry, sad, frustrated",
            "neutral": "Factual, informational",
            "manipulative": "Uses fear, urgency, or pressure",
        },
    },
    "routing": {
        "type": "choice",
        "instructions": "Which team should handle this content?",
        "criteria": {
            "security": "Cybersecurity team",
            "moderation": "Content moderation",
            "support": "Customer support",
            "archive": "No action needed",
        },
    },
}

# ---- SAMPLES ----
SAMPLES = {
    "Phishing": "Urgent: Click here to verify your suspended account: bit.ly/secure-login",
    "Spam": "Buy now and get 80% OFF on all premium products! Click here to claim.",
    "Harassment": "You're the worst. I hate you. I will destroy your reputation.",
    "Safe": "Hey team, the Q4 roadmap is finalized. Great work everyone!",
}

def run_laya(text: str):
    if not MODEL_LIVE or not router:
        st.error("Laya model failed to load. Please ensure `laya` is installed.")
        st.stop()
        
    start = time.time()
    result = router.predict({"content": text}, QUESTIONS)
    return result["answers"], round((time.time() - start) * 1000, 1), "🟢 Live Model"

# ---- UI ----
st.title("🛡️ AI Guardian")
st.caption(f"Powered by Laya System 1 Engine | Status: {'🟢 Live' if MODEL_LIVE else '🔴 Offline'}")

# Sample selector
sample_choice = st.selectbox("Try a sample text:", ["(Write your own)"] + list(SAMPLES.keys()))
default_text = SAMPLES.get(sample_choice, "")

text = st.text_area("Content to analyze:", value=default_text, height=150)

if st.button("⚡ Analyze", type="primary") and text:
    with st.spinner("Analyzing..."):
        results, ms, mode = run_laya(text)
        
    st.success(f"Analysis complete in {ms}ms ({mode})")
    
    # Layout using native Streamlit metrics
    st.subheader("Results")
    
    c1, c2, c3 = st.columns(3)
    
    # 1. Classification
    cls = results.get("classification", {})
    c1.metric("1. Classification (Choice)", cls.get("choice", "Unknown").title())
    
    # 2. Threat Level
    thr = results.get("threat_level", {})
    if "probabilities" in thr and "legend" in thr:
        # Find index with max probability
        tidx_str = max(thr["probabilities"], key=thr["probabilities"].get)
        tidx = int(tidx_str)
        choice_str = thr["legend"].get(tidx_str, "harmless")
    else:
        tidx = 0
        choice_str = "harmless"
    c2.metric("2. Threat Level (Score)", f"{choice_str.replace('_', ' ').title()} ({tidx}/4)")
    
    # 3. Requires Action
    act = results.get("requires_action", {})
    # Noul returns a float value in 'noul' key. > 0.5 is typically "Yes"
    noul_val = act.get("noul", 0.0)
    is_yes = noul_val > 0.5
    c3.metric("3. Requires Action? (Noul)", "Yes" if is_yes else "No")
    
    st.divider()
    c4, c5 = st.columns(2)
    
    # 4. Sentiment
    sen = results.get("sentiment", {})
    c4.metric("4. Sentiment (Choice)", sen.get("choice", "Unknown").title())
    
    # 5. Routing
    rt = results.get("routing", {})
    c5.metric("5. Routing (Choice)", rt.get("choice", "Unknown").title())
    
    st.write("Threat Meter:")
    st.progress(tidx / 4)
