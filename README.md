# 🎵 VOIA – Voice Operated Intelligent Assistant  

VOIA is a **Streamlit-based voice assistant** that transcribes multilingual audio (Hindi, Gujarati, English, Hinglish, Gujlish) and converts it into **structured tasks** (e.g., booking a meeting or sending an email).  
It uses **OpenAI Whisper** for transcription and **GPT (Chat Completions API)** for language correction, intent classification, and entity extraction.  

---

## 🚀 Features  
- 🎙️ **Audio Input**: Record from microphone or upload audio files (`.wav`, `.mp3`).  
- 🌍 **Multilingual Support**: Handles Hindi, Gujarati, English, Hinglish, and Gujlish.  
- ✨ **Smart Processing Pipeline**:  
  1. Transcribes audio with Whisper (`whisper-1`).  
  2. Repairs and refines transcription (grammar + coherence).  
  3. Detects correct language & converts to English.  
  4. Classifies user intent (**Meeting booking** / **Email sending**).  
  5. Extracts important entities (names, locations, times, etc.).  
  6. Produces a structured JSON-like response.  
- 📊 **Interactive UI**: Built with Streamlit for simple and intuitive interaction.  
- 💾 **Option to Save Recordings** for later use.

---

## 🛠️ Tech Stack  
- **Frontend/UI**: Streamlit  
- **Transcription**: OpenAI Whisper (`whisper-1`)  
- **NLP & Reasoning**: OpenAI GPT (Chat Completions API)  
- **Language Handling**: Mixed-language (code-switched Hindi, Gujarati, Hinglish) detection & repair  

---

## 📂 Project Structure  
```plaintext
.
├── app.py              # Main Streamlit app
└── README.md           # Documentation
```

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/voia.git
cd voia
```
### 2. Install dependencies
pip install -r requirements.txt

### 3. Add Streamlit Secrets
Create .streamlit/secrets.toml and add your OpenAI key:
```bash
openai_voia_key = "your_openai_api_key"
```
### 4. Run the app
```bash
streamlit run app.py
```
### 🎯 Example Workflow

- Upload or record an audio file.
- VOIA transcribes and repairs the transcription.
- The system identifies whether it’s about sending an email or booking a meeting.
- Extracted details (recipient name, time, place, etc.) and a detailed description are displayed in a structured format
