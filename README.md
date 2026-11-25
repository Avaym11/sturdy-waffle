# Lecture to Study Materials Converter

## Phase 1: Audio Processing & Transcription ✅
## Phase 2: AI Orchestrator (Summary & Quiz Generation) ✅

### Features
- ✅ Video/Audio file upload
- ✅ Audio extraction from video (MoviePy)
- ✅ Speech-to-text transcription (Whisper)
- ✅ Speaker diarization (Pyannote.audio)

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Get API Keys:**
   - **Google Gemini API Key**: https://aistudio.google.com/app/apikey
   - **Hugging Face Token**: https://huggingface.co/settings/tokens
   - Accept terms for `pyannote/speaker-diarization-3.1` model

3. **Run the app:**
```bash
streamlit run app.py
```

### Usage

1. Enter OpenAI API Key in the sidebar
2. Enter Hugging Face Token in the sidebar
3. Upload a lecture video/audio file
4. Click "Process Lecture"
5. View transcription with speaker labels

### Cloud AI Mode ☁️
- Uses OpenAI Whisper API (cloud transcription)
- Uses Pyannote.audio via Hugging Face (speaker diarization)
- No offline model downloads required

### Next Phases
- Phase 2: AI Orchestrator (Summary & Quiz Generation)
- Phase 3: Concept Map Visualization
- Phase 4: PDF Export

### Tech Stack
- Streamlit (UI)
- OpenAI Whisper API (Cloud Transcription)
- Pyannote.audio (Speaker Diarization via Hugging Face)
- MoviePy (Audio Extraction)
