# -*- coding: utf-8 -*-
import os
import unicodedata
import streamlit as st
from mistralai import Mistral

st.set_page_config(page_title="Health & Wellness Bot", page_icon="🩺")

# ---- Helpers ----
def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        return s
    # Replace smart quotes and normalize to NFC
    s = (s.replace("\u2019", "'")
           .replace("\u2018", "'")
           .replace("\u201C", '"')
           .replace("\u201D", '"'))
    return unicodedata.normalize("NFC", s)

# ---- API key ----
api_key = os.getenv("MISTRAL_API_KEY") or st.sidebar.text_input(
    "MISTRAL_API_KEY", type="password",
    help="Best practice: add this in Streamlit → Settings → Secrets."
)
if not api_key:
    st.info("Add your MISTRAL_API_KEY in Secrets or paste it on the left.")
    st.stop()

client = Mistral(api_key=api_key)
MODEL = "mistral-large-latest"

# ---- System Prompt ----
SYSTEM_PROMPT = (
    "You are a friendly health & wellness assistant. "
    "Give practical, evidence-informed tips on sleep, diet, hydration, "
    "exercise, and stress management. "
    "Keep answers short, simple, and helpful. "
    "⚠️ Do not give medical diagnoses or prescriptions. "
    "If asked, say you are not a doctor and advise seeing a professional."
)

# ---- State ----
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

st.title("🩺 Health & Wellness Chat Bot")

# ---- Show history ----
for m in st.session_state.messages:
    if m["role"] == "system":  # hide system
        continue
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(normalize_text(m["content"]))

# ---- Input ----
user_msg = st.chat_input("Ask me about health, wellness, or lifestyle tips...")
if user_msg:
    user_msg = normalize_text(user_msg)
    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    # ---- Call Mistral ----
    try:
        resp = client.chat.complete(
            model=MODEL,
            messages=[
                {"role": m["role"], "content": normalize_text(m["content"])}
                for m in st.session_state.messages
            ],
            temperature=0.6,
            max_tokens=400,
        )
        bot_reply = normalize_text(resp.choices[0].message.content)
    except Exception as e:
        bot_reply = f"Error: {normalize_text(str(e))}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

# ---- Sidebar actions ----
if st.sidebar.button("Cle
