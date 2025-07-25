import os
import streamlit as st
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    CouldNotRetrieveTranscript,
)
import google.generativeai as genai
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
from pydub.utils import which
from urllib.parse import urlparse, parse_qs
import os.path

# Set ffmpeg and ffprobe paths explicitly
AudioSegment.converter = r"C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\\Program Files\\ffmpeg\\bin\\ffprobe.exe"

# Set Streamlit page config
st.set_page_config(
    page_title="Gemini YouTube Transcript Summarizer",
    page_icon="favicon.ico",
)

# Load .env
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt
prompt = """Welcome, Video Summarizer! Your task is to distill the essence of a given YouTube video transcript into a concise summary. Your summary should capture the key points and essential information, presented in bullet points, within a 250-word limit. Let's dive into the provided transcript and extract the vital details for our audience."""

# Function to extract video ID
def extract_video_id(youtube_url):
    try:
        parsed_url = urlparse(youtube_url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            query_params = parse_qs(parsed_url.query)
            return query_params['v'][0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        else:
            return None
    except Exception as e:
        st.error(f"Error extracting video ID: {e}")
        return None

# Function to extract transcript
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            return None
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        transcript = " ".join([item["text"] for item in transcript_data])
        return transcript
    except TranscriptsDisabled:
        st.warning("Transcripts are disabled for this video. Please try another video.")
    except NoTranscriptFound:
        st.warning("No transcript found for the requested language. Try another video.")
    except CouldNotRetrieveTranscript:
        st.warning("Could not retrieve a transcript for this video.")
    except Exception as e:
        st.error(f"Unexpected error while getting transcript: {e}")
    return None

# Split long transcript
def split_transcript(transcript, chunk_size=1000):
    words = transcript.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# Generate Gemini summary
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        chunks = split_transcript(transcript_text)
        summaries = []
        for chunk in chunks:
            response = model.generate_content(prompt + "\n\n" + chunk)
            summaries.append(response.text)
        return "\n".join(summaries)
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# Text to audio
def generate_audio_file(text, output_file="summary_audio.mp3", chunk_size=500):
    try:
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        temp_files = []
        for i, chunk in enumerate(chunks):
            temp_file = f"temp_audio_{i}.mp3"
            try:
                tts = gTTS(text=chunk, lang="en")
                tts.save(temp_file)
                temp_files.append(temp_file)
            except Exception as e:
                st.warning(f"Skipping audio chunk {i} due to error: {e}")
        # Combine audio
        combined = AudioSegment.empty()
        for file in temp_files:
            audio = AudioSegment.from_file(file)
            combined += audio
            os.remove(file)
        combined.export(output_file, format="mp3")
        return output_file
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None

# Translation
def translate_text(text, target_language):
    try:
        if not text.strip():
            st.warning("Text is empty. Cannot translate.")
            return None
        translator = Translator()
        translated = translator.translate(text, dest=target_language)
        return translated.text if translated else None
    except Exception as e:
        st.error(f"Error translating text: {e}")
        return None

# Streamlit UI
st.title("🎥 Gemini YouTube Transcript Summarizer")

youtube_link = st.text_input("🔗 Enter YouTube Video Link:")
video_id = extract_video_id(youtube_link) if youtube_link else None

if video_id:
    thumbnail_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
    st.image(thumbnail_url)

languages = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
}
selected_language = st.selectbox("🌐 Select the language for detailed notes:", list(languages.keys()))

# Generate Notes Button
if st.button("🧠 Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        if summary:
            target_lang = languages[selected_language]
            final_summary = translate_text(summary, target_lang) if target_lang != "en" else summary
            st.markdown(f"## 📝 Detailed Notes ({selected_language})")
            st.write(final_summary)

            # Generate audio
            audio_path = generate_audio_file(final_summary, f"summary_audio_{target_lang}.mp3")
            if audio_path and os.path.exists(audio_path):
                st.audio(audio_path, format="audio/mp3", start_time=0)
                with open(audio_path, "rb") as audio_file:
                    st.download_button(
                        label="⬇️ Download Audio",
                        data=audio_file,
                        file_name=audio_path,
                        mime="audio/mp3"
                    )
            else:
                st.warning("Audio could not be generated.")
