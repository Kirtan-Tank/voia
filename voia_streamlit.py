import streamlit as st
import openai
import numpy as np
from io import BytesIO
import subprocess

# Load API key from Streamlit secrets
openai_voia_key = st.secrets["openai_voia_key"]
openai.api_key = openai_voia_key

# Function to record audio from the microphone (placeholder for unsupported platforms)
def load_audio_from_mic(threshold=500, silence_limit=7, duration=10, rate=44100, channels=1):
    recorded_audio = "SORRY, RECORDING AUDIO IS NOT SUPPORTED ON THIS DEPLOYMENT PLATFORM"
    return recorded_audio

# Function to check if a file is a WAV file based on its magic number
def is_wav_file(file):
    """Check if a given file is a WAV file based on its magic number."""
    try:
        # Read the first 12 bytes (RIFF header)
        header = file.read(12)
        file.seek(0)  # Reset file pointer after reading

        # Check if the file starts with 'RIFF' and has 'WAVE' as the format identifier
        return header.startswith(b'RIFF') and header[8:12] == b'WAVE'
    except Exception as e:
        st.write(f"Error checking WAV file: {e}")
        return False

# Function to get GPT response
def get_gpt_response(text, prompt_template, model="gpt-3.5-turbo-0125"):
    prompt = prompt_template.format(text=text)

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant who is master in understanding tasks."},
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.choices[0].message['content'].strip()
        return answer

    except Exception as e:
        st.write(f"Error: {e}")
        return None

# Define prompt template
prompt_template = """
    Execute task from TASKS by following INSTRUCTIONS
    
    INSTRUCTIONS:
    1. All tasks are not mandatory to perform
    2. Both tasks are different
    3. Follow the given ORDER strictly
    4. End text must be in ENGLISH only
    
    TASKS:
    1. Booking a meeting
    2. Sending an email
    
    ORDER:
    1. Analyze and repair the text to make it more sensible 
    2. Translate the given text into English is mandatory
    3. Analyze the text and decide the type of task by using keywords
    4. Give a summary what user wants to do and extracting key entities
    5. Set extracted information in given RESPONSE FORMAT
    6. MAKE SURE THE RESPONSE IS IN ENGLISH ONLY

    RESPONSE FORMAT - DICTIONARY
    It should ONLY include below information:
    - 'type of task': Identified task from TASKS,
    - 'extracted entities': Important entities,
    - 'summary': summary of what user wants to do
    
    Here is the text {text}
    """

# Streamlit UI
st.sidebar.title("Voice Assistant Task Processor")

# Option to record from mic
mic_input = st.sidebar.checkbox("Record from microphone")
save_recording_status = st.sidebar.checkbox("Save recording")

# Option to upload files
if not mic_input:
    uploaded_files = st.sidebar.file_uploader("Upload files", accept_multiple_files=True, type=None)

# Initialize audio variable
audio = None

# Button to start recording or process uploaded files
if mic_input:
    if st.sidebar.button("Press and hold to record"):
        audio = load_audio_from_mic()
else:
    if uploaded_files and st.sidebar.button("Convert Files"):
        is_audio = is_wav_file(uploaded_files[0])  # Check if the first uploaded file is a WAV file
        if not is_audio:
            st.warning("# PLEASE ONLY UPLOAD WAV FILES")
        else:
            audio = uploaded_files[0].getvalue()  # Load the WAV file into memory

# Option to transcribe and process audio
if st.sidebar.button("Transcribe and Process"):
    if audio:
        transcription = openai.Audio.transcribe("whisper-1", audio)
        text = transcription['text']
        response = get_gpt_response(text, prompt_template)
        st.write("### Processed Response")
        st.json(response)
    else:
        st.write("No audio available for transcription.")
