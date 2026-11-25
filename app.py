import streamlit as st
import google.generativeai as genai
from streamlit_mermaid import st_mermaid
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy import VideoFileClip
import os

st.set_page_config(page_title="Lecture to Study Materials", layout="wide")

if 'transcription' not in st.session_state:
    st.session_state.transcription = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'quiz' not in st.session_state:
    st.session_state.quiz = None
if 'concept_map' not in st.session_state:
    st.session_state.concept_map = None

def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    audio_path_mp3 = audio_path.replace('.wav', '.mp3')
    video.audio.write_audiofile(audio_path_mp3, codec='libmp3lame', bitrate='128k', logger=None)
    video.close()
    
    file_size_mb = os.path.getsize(audio_path_mp3) / (1024 * 1024)
    
    if file_size_mb > 20:
        video = VideoFileClip(video_path)
        bitrate = '64k' if file_size_mb > 30 else '96k'
        video.audio.write_audiofile(audio_path_mp3, codec='libmp3lame', bitrate=bitrate, logger=None)
        video.close()
        file_size_mb = os.path.getsize(audio_path_mp3) / (1024 * 1024)
    
    return audio_path_mp3, file_size_mb

def transcribe_audio(audio_path, gemini_key):
    import time
    genai.configure(api_key=gemini_key)
    
    file_size = os.path.getsize(audio_path) / (1024 * 1024)
    if file_size > 20:
        raise Exception(f"Audio file too large ({file_size:.1f}MB)")
    
    audio_file = genai.upload_file(path=audio_path)
    
    while audio_file.state.name == "PROCESSING":
        time.sleep(2)
        audio_file = genai.get_file(audio_file.name)
    
    if audio_file.state.name == "FAILED":
        raise Exception("Audio processing failed")
    
    model = genai.GenerativeModel('gemini-3-flash-preview')
    response = model.generate_content([audio_file, "Transcribe this audio word-for-word."])
    
    return {'text': response.text, 'segments': []}

def generate_summary(text, gemini_key):
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-3-flash-preview')
    response = model.generate_content(f"Create a structured summary of this lecture:\n\n{text}")
    return response.text

def generate_quiz(text, gemini_key):
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-3-flash-preview')
    response = model.generate_content(f"Create 5 multiple-choice questions with answers from this lecture:\n\n{text}")
    return response.text

def generate_concept_map(text, gemini_key):
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-3-flash-preview')
    prompt = f"""Create a simple Mermaid.js flowchart of key concepts from this lecture.

IMPORTANT RULES:
1. Start with: graph TD
2. Use simple IDs: A, B, C, D, E, F, G, H, I, J
3. Use square brackets: A[Text Here]
4. Use arrows: A --> B
5. NO HTML entities, NO special characters
6. Maximum 10 nodes
7. Return ONLY the mermaid code
8. Do NOT use &gt; or &lt; or &amp; - use plain text only

Example format:
graph TD
    A[Main Topic] --> B[Subtopic One]
    A --> C[Subtopic Two]
    B --> D[Detail]

Lecture:
{text[:2000]}"""
    response = model.generate_content(prompt)
    return response.text

st.title("🎓 Lecture to Study Materials Converter")
st.subheader("Phase 1 & 2: Transcription + AI Study Materials ☁️")

with st.sidebar:
    st.header("🔑 API Configuration")
    gemini_key = st.text_input("Google Gemini API Key", type="password")
    st.caption("Get from: https://aistudio.google.com/app/apikey")

uploaded_file = st.file_uploader("Upload Lecture Video/Audio", type=['mp4', 'avi', 'mov', 'mp3', 'wav', 'mkv'])

if uploaded_file:
    upload_path = os.path.join("uploads", uploaded_file.name)
    with open(upload_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    if st.button("🚀 Process Lecture", type="primary"):
        if not gemini_key:
            st.error("❌ Gemini API Key is required!")
        else:
            with st.spinner("Processing..."):
                try:
                    st.info("☁️ Step 1/3: Extracting audio...")
                    audio_path = os.path.join("outputs", "extracted_audio.mp3")
                    
                    if uploaded_file.name.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                        audio_path, file_size_mb = extract_audio(upload_path, audio_path)
                        st.info(f"📊 Audio: {file_size_mb:.1f}MB")
                    else:
                        audio_path = upload_path
                    
                    st.success("✅ Audio extracted")
                    
                    st.info("☁️ Step 2/2: Transcribing...")
                    transcription = transcribe_audio(audio_path, gemini_key)
                    st.session_state.transcription = transcription
                    st.success("✅ Transcription complete")
                    
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

if st.session_state.transcription:
    st.divider()
    st.header("🤖 Phase 2: AI Study Materials Generator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Generate Summary", use_container_width=True):
            with st.spinner("Generating..."):
                try:
                    st.session_state.summary = generate_summary(st.session_state.transcription['text'], gemini_key)
                    st.success("✅ Done!")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
    
    with col2:
        if st.button("❓ Generate Quiz", use_container_width=True):
            with st.spinner("Generating..."):
                try:
                    st.session_state.quiz = generate_quiz(st.session_state.transcription['text'], gemini_key)
                    st.success("✅ Done!")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
    
    with col3:
        if st.button("🗺️ Generate Concept Map", use_container_width=True):
            with st.spinner("Generating..."):
                try:
                    st.session_state.concept_map = generate_concept_map(st.session_state.transcription['text'], gemini_key)
                    st.success("✅ Done!")
                except Exception as e:
                    st.error(f"❌ {str(e)}")

if st.session_state.transcription:
    st.divider()
    st.header("📝 Results")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Transcription", "Summary", "Quiz", "Concept Map"])
    
    with tab1:
        st.text_area("Full Transcription", st.session_state.transcription['text'], height=400)
    
    with tab2:
        if st.session_state.summary:
            st.markdown(st.session_state.summary)
        else:
            st.info("Click 'Generate Summary' button")
    
    with tab3:
        if st.session_state.quiz:
            st.markdown(st.session_state.quiz)
        else:
            st.info("Click 'Generate Quiz' button")
    
    with tab4:
        if st.session_state.concept_map:
            st.subheader("Key Concept Map")
            
            mermaid_code = st.session_state.concept_map
            
            # Extract mermaid code from markdown blocks
            if "```mermaid" in mermaid_code:
                mermaid_code = mermaid_code.split("```mermaid")[1].split("```")[0].strip()
            elif "```" in mermaid_code:
                parts = mermaid_code.split("```")
                if len(parts) >= 2:
                    mermaid_code = parts[1].strip()
            
            # Remove 'mermaid' or 'graph' prefix if it appears as text
            if mermaid_code.startswith('mermaid'):
                mermaid_code = mermaid_code[7:].strip()
            
            # Fix HTML entities
            import html
            mermaid_code = html.unescape(mermaid_code)
            
            # Ensure it starts with graph TD
            if not mermaid_code.strip().startswith('graph'):
                mermaid_code = 'graph TD\n' + mermaid_code
            
            # Clean up lines
            lines = []
            for line in mermaid_code.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    lines.append(line)
            mermaid_code = '\n'.join(lines)
            
            # Display the diagram
            try:
                st_mermaid(mermaid_code, height=500)
                st.success("✅ Concept map rendered successfully!")
            except Exception as e:
                st.error(f"Rendering error: {str(e)}")
                st.info("Showing code instead:")
                st.code(mermaid_code, language="mermaid")
            
            # Show code in expander
            with st.expander("📋 View/Edit Mermaid Code"):
                st.code(mermaid_code, language="mermaid")
                st.caption("Copy this code to https://mermaid.live for editing")
        else:
            st.info("Click 'Generate Concept Map' button")

st.caption("Phase 1 & 2 Complete | Cloud AI ☁️")
