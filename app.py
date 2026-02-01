import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import tempfile
import os
from sarvamai import SarvamAI
import base64

SARVAM_API_KEY = st.secrets.get("SARVAM_API_KEY", "")
client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

# ================= CONFIG =================
SYSTEM_PROMPT = """
You are a polite, professional real-time voice assistant.
Your name is Snehal.
Keep answers concise and friendly.
"""

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# ================= SPEECH TO TEXT =================
def speech_to_text(audio_bytes):
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        with open(temp_path, "rb") as f:
            response = client.speech_to_text.transcribe(
                file=f,
                language_code="en-IN"
            )
        
        os.remove(temp_path)
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
        if hasattr(response, 'audios') and response.audios:
            return base64.b64decode(response.audios[0])
        else:
            st.error(f"No audio in response")
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
    
    # WebRTC Audio Recorder
    st.subheader("🎤 Record Your Message")
    webrtc_ctx = webrtc_streamer(
        key="snehal-voice-agent",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"audio": True},
        async_processing=True,
    )
    
    if st.button("🎵 Process Audio", use_container_width=True):
        if webrtc_ctx.state.playing:
            st.warning("Please stop recording first")
        elif webrtc_ctx.audio_processor:
            try:
                with st.spinner("⏳ Processing audio..."):
                    # Get the recorded audio
                    audio_frames = webrtc_ctx.audio_processor.get_frames()
                    if audio_frames:
                        # Convert audio frames to bytes
                        audio_bytes = b"".join([frame.to_ndarray().tobytes() for frame in audio_frames])
                        
                        # Speech to text
                        user_text = speech_to_text(audio_bytes)
                        
                        if user_text:
                            st.markdown(f"""
                            <div class="result-container">
                                <div class="label-text">🗣️ You said:</div>
                                <div class="user-text">{user_text}</div>
                            </div>
                            """, unsafe_allow_html=True)

                            with st.spinner("🤖 Agent is thinking..."):
                                reply = ask_llm(user_text)

                            if reply:
                                st.markdown(f"""
                                <div class="result-container">
                                    <div class="label-text">🤖 Agent Response:</div>
                                    <div class="agent-text">{reply}</div>
                                </div>
                                """, unsafe_allow_html=True)

                                with st.spinner("🎵 Generating speech..."):
                                    voice = text_to_speech(reply)

                                if voice:
                                    st.markdown('<div class="audio-player">', unsafe_allow_html=True)
                                    st.audio(voice, format="audio/wav")
                                    st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.error("Could not transcribe audio. Please try again.")
                    else:
                        st.warning("No audio recorded. Please record something first.")
            except Exception as e:
                st.error(f"Error processing audio: {str(e)}")

# Footer
st.markdown("""
<hr style="border: 0; height: 1px; background: linear-gradient(to right, transparent, #667eea, transparent); margin: 2rem 0;">
<p style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 2rem;">
    Made with ❤️ using Sarvam AI • Streamlit
</p>
""", unsafe_allow_html=True)
