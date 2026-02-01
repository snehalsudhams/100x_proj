# Real-Time Voice Agent (Sarvam AI)

A Streamlit app that records your voice, transcribes it with Sarvam AI, queries the LLM, and returns speech using Sarvam AI TTS.

## Setup

1. Create a Python 3.10+ virtual environment and activate it.

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your Sarvam AI API key in `.streamlit/secrets.toml`:

```
SARVAM_API_KEY = "your-sarvam-api-key-here"
```

4. Run the app:

```powershell
cd C:\Users\Snehal\Desktop\100x_proj
streamlit run app.py
```

5. Open `http://localhost:8501` in your browser. Click the "🎤 Press to Speak" button and test.

## Notes

- If you encounter audio/device issues, ensure your microphone is available and drivers are installed.
- Revoke any exposed API keys and generate new ones if they were shared publicly.

