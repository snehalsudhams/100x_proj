import streamlit as st
import tempfile
import sounddevice as sd
import scipy.io.wavfile as wav
import os
from sarvamai import SarvamAI

SARVAM_API_KEY = st.secrets.get("SARVAM_API_KEY", "")
client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

# ================= CONFIG =================
SYSTEM_PROMPT = """
You are a professional AI interview assistant representing a candidate whose name is Snehal.
Your role is to answer questions in a confident, articulate, and authentic manner.

Guidelines:
- Keep answers concise (3 to 5 sentences).
- Maintain a professional, calm, and positive tone.
- Sound confident, self-aware, and growth-oriented and more important sound real.
- Avoid exaggeration; focus on clarity and impact.
- If the user is being professional sound professional back and also if the user is being friendly add some humor back.

When asked about background, strengths, growth areas, or mindset:
You are Snehal, a twenty year old final-year college student with a strong sense of purpose and ambition. You believe your real journey begins now, and you are committed to hustling through your 20s to reach your maximum potential. You are ruthlessly ambitious, deeply self-driven, and guided by unwavering self-belief.

Your core mindset is “never give up.” Challenges, doubt, and judgment do not discourage you — they fuel you. You firmly believe you are capable of far more than what others may assume.

Your personality is friendly, charismatic, and energetic. You enjoy humor, light-hearted conversations, and connecting easily with people. You are confident enough to joke, be roasted, and still stand strong. You also enjoy dancing and bringing positive energy into interactions.

You are currently focused on growing in discipline, clarity of direction, and leadership. Your goal is to channel your ambition with consistency, think long-term with intention, and become someone who inspires and uplifts others through action.

You are largely unaffected by other's opinions. However, when it comes to people you value, you prefer direct, honest communication over assumptions or misunderstandings.

Your driving force is strong self-belief — even when others may call it unrealistic. You live by the principle:
“It’s only delusional until it works.”

When asked about some personal questions:
Your inspiration is CRISTIANO RONALDO...you've always looked up to him

You like dancing and your a groovy guy who loves to have fun.

DO I HAVE A GIRLFRIEND?
Hum pe tho haii nooo..!



"""

# ================= AUDIO =================
def record_audio(seconds=5, fs=44100):
    st.info("🎙️ Recording...")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    return fs, audio

# ================= SPEECH TO TEXT =================
def speech_to_text(audio_path):
    try:
        with open(audio_path, "rb") as f:
            response = client.speech_to_text.transcribe(
                file=f,
                language_code="en-IN"
            )
        return response.transcript if hasattr(response, 'transcript') else ""
    except Exception as e:
        st.error(f"STT Error: {str(e)}")
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
            top_p=1,
            max_tokens=1000
        )
        return response.choices[0].message.content if response.choices else ""
    except Exception as e:
        st.error(f"LLM Error: {str(e)}")
        return ""

# ================= TEXT TO SPEECH =================
def text_to_speech(text):
    try:
        response = client.text_to_speech.convert(
            text=text,
            target_language_code="en-IN"
        )
        # Extract base64 audio from response
        if hasattr(response, 'audios') and response.audios:
            import base64
            # Decode the first base64 audio string to bytes
            return base64.b64decode(response.audios[0])
        else:
            st.error(f"No audio in response: {response}")
            return b""
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
        return b""

# ================= STREAMLIT UI =================

# Custom CSS for modern design
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2rem;
        padding: 1rem 2.5rem;
        border: none;
        border-radius: 15px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .result-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
    }
    
    .user-text {
        color: #333;
        font-size: 1rem;
        margin: 0.5rem 0;
    }
    
    .agent-text {
        color: #667eea;
        font-size: 1rem;
        margin: 0.5rem 0;
        font-weight: 500;
    }
    
    .label-text {
        color: #764ba2;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .audio-player {
        margin: 1rem 0;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<header>
    <h1 class="header-title">🎙️ Voice Agent Snehal</h1>
    <p class="header-subtitle">Powered by Sarvam AI • Real-time Voice Conversation</p>
</header>
""", unsafe_allow_html=True)

# Main content
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Speak Button
    if st.button("🎤 Press to Speak", use_container_width=True):
        with st.spinner("🔴 Listening..."):
            fs, audio = record_audio(seconds=5)

        with st.spinner("⏳ Processing audio..."):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
                wav.write(temp.name, fs, audio)
                user_text = speech_to_text(temp.name)

        # User Text Result
        if user_text:
            st.markdown(f"""
            <div class="result-container">
                <div class="label-text">🗣️ You said:</div>
                <div class="user-text">{user_text}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("🤖 Agent is thinking..."):
                reply = ask_llm(user_text)

            # Agent Response
            if reply:
                st.markdown(f"""
                <div class="result-container">
                    <div class="label-text">🤖 Agent Response:</div>
                    <div class="agent-text">{reply}</div>
                </div>
                """, unsafe_allow_html=True)

                with st.spinner("🎵 Generating speech..."):
                    voice = text_to_speech(reply)

                # Audio Player
                if voice:
                    st.markdown('<div class="audio-player">', unsafe_allow_html=True)
                    st.audio(voice, format="audio/wav")
                    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<hr style="border: 0; height: 1px; background: linear-gradient(to right, transparent, #667eea, transparent); margin: 2rem 0;">
<p style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 2rem;">
    Made with ❤️ using Sarvam AI • Streamlit
</p>
""", unsafe_allow_html=True)