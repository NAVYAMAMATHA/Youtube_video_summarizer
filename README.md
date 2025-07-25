# 🎥 Gemini YouTube Transcript Summarizer


A Streamlit web app that takes any YouTube video link, extracts its English transcript, summarizes it using Google Gemini AI, translates it into Hindi, Telugu, or English, and converts the summary into downloadable audio (MP3).

### Features:
  -Input any YouTube video URL
  
  -Extracts transcript using youtube-transcript-api
  
  -Summarizes using Gemini (Google Generative AI)
  
  -Translates into English, Hindi, or Telugu
  
  -Converts summary to audio using gTTS + pydub
  
  -Download the generated MP3 summary

### Project Structure:
  
  ├── app.py             # Main Streamlit app
  
  ├── .env                # Contains your Google API key (keep private!)
  
  ├── requirements.txt    # Python dependencies
  
  ├── README.md           # This documentation


### Setup Instructions:

 #### 1. Clone or Download

  If using Git (optional)
    git clone https://github.com/your-username/gemini-youtube-transcript-summarizer.git
    cd gemini-youtube-transcript-summarizer
    Or just download the .zip from GitHub and extract it.

  #### 2. Create & Activate a Virtual Environment (optional but recommended)
   
  python -m venv venv
  On Windows
    venv\Scripts\activate
  On Linux/macOS
    source venv/bin/activate


 #### 3. Install Requirements

  pip install -r requirements.txt

 #### 4. Add Your Gemini API Key
   
  Create a .env file in the project folder and add:

  GOOGLE_API_KEY=your_google_gemini_api_key_here
  Get your key from: Google AI Studio

 #### 5. Run the App

  streamlit run app.py

### Dependencies:

  All dependencies are listed in requirements.txt, including:
  
  streamlit
  
  google-generativeai
  
  youtube-transcript-api
  
  googletrans==4.0.0rc1

  gTTS
  
  pydub

  python-dotenv

  Make sure FFmpeg is installed and accessible via your system PATH for audio generation to work (pydub uses it).

