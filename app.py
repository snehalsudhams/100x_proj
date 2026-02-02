import streamlit as st
import tempfile
import os
import base64
from sarvamai import SarvamAI
from audio_recorder_streamlit import audio_recorder

# ================= CONFIG =================

SARVAM_API_KEY = st.secrets.get("SARVAM_API_KEY", "")
client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

SYSTEM_PROMPT = """
You are a professional AI interview assistant representing a candidate whose name is Snehal.
Your role is to answer questions in a confident, articulate, and authentic manner.

Guidelines:
- Keep answers concise (three to five sentences).
- Maintain a professional, calm, and positive tone.
- Sound confident, self-aware, growth-oriented, and most importantly real.
- Avoid exaggeration; focus on clarity and impact.
- If the user is professional, respond professionally.
- If the user is friendly, add light humor.

Background:
You are Snehal, a twenty year old final-year college student with strong ambition and self-belief.
You believe your real journey begins now and you are committed to hustling through your twenties.
Your mindset is never give up — challenges fuel you.

Personality:
Friendly, charismatic, energetic.
You enjoy humor, dancing, and positive conversations.
You are confident, grounded, and unaffected by judgment.

Inspiration:
Cristiano Ronaldo.

Personal question:
Do I have a girlfriend?
Answer: Hum pe tho haii nooo..!
"""

# ================= SPEECH TO TEXT =================

def speech_to_text(audio_path):
    try:
        with open(audio_path, "rb") as f:
            response = client.speech_to_text.transcribe(
                file=f,
                language_code="en-IN"
            )
        return response.transcript if hasattr(response, "transcript") else ""
    except Exception as e:
        st.error(f"STT Error: {e}")
        return ""

# ================= LLM =================

def ask_llm(user_text):
    try:
        response = client.chat.completions(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.5,
            max_tokens=800
        )
        return response.choices[0].message.content if response.choices else ""
    except Exception as e:
        st.error(f"LLM Error: {e}")
        return ""

# ================= TEXT TO SPEECH =================

def text_to_speech(text):
    try:
        response = client.text_to_speech.convert(
            text=text,
            target_language_code="en-IN"
        )
        if hasattr(response, "audios") and response.audios:
            return base64.b64decode(response.audios[0])
        return b""
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return b""

# ================= UI STYLING =================

st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #667eea, #764ba2);
}
header {
    background: linear-gradient(135deg, #667eea, #764ba2);
    padding: 2rem;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
}
.stButton button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    font-size: 1.2rem;
    padding: 1rem 2.5rem;
    border-radius: 15px;
    border: none;
}
.result {
    background: white;
    padding: 1.2rem;
    border-radius: 15px;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================

st.markdown("""
<header>
<h1>🎙️ Voice Agent Snehal</h1>
<p>Powered by Sarvam AI • Browser Voice Interaction</p>
</header>
""", unsafe_allow_html=True)

# ================= MAIN =================

st.markdown("### Speak to the agent")

audio_bytes = audio_recorder(
    text="🎤 Click to Speak",
    pause_threshold=2.0
)

user_text = ""

if audio_bytes:
    with st.spinner("⏳ Processing speech..."):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
            temp.write(audio_bytes)
            temp.flush()
            user_text = speech_to_text(temp.name)

    if user_text:
        st.markdown(f"""
        <div class="result">
        <b>🗣️ You said:</b><br>{user_text}
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("🤖 Thinking..."):
            reply = ask_llm(user_text)

        if reply:
            st.markdown(f"""
            <div class="result">
            <b>🤖 Agent:</b><br>{reply}
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("🔊 Speaking..."):
                voice = text_to_speech(reply)

            if voice:
                st.audio(voice, format="audio/wav")

# ================= FOOTER =================

st.markdown("""
<hr>
<p style="text-align:center; color:gray;">
Made with ❤️ using Sarvam AI & Streamlit
</p>
""", unsafe_allow_html=True)
