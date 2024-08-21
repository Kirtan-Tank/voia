import streamlit as st
import openai
import numpy as np
from io import BytesIO
import subprocess
import os

# Load API key from Streamlit secrets
openai_voia_key = st.secrets["openai_voia_key"]
openai.api_key = openai_voia_key

# Create a virtual folder in memory
virtual_folder = {}

# Function to record audio from the microphone
def load_audio_from_mic(threshold=500, silence_limit=7, duration=10, rate=44100, channels=1):
    recorded_audio = "SORRY, RECORDING AUDIO IS NOT SUPPORTED ON THIS DEPLOYMENT PLATFORM"
    return recorded_audio

# Function to convert files in a virtual directory to WAV format
def convert_files_in_virtual_dir_to_wav(virtual_folder, save=False):
    converted_files = []

    for filename, filedata in virtual_folder.items():
        input_file = BytesIO(filedata)
        if save:
            filename_without_ext = os.path.splitext(filename)[0]
            output_file = f"{filename_without_ext}.wav"
            try:
                subprocess.run(['ffmpeg', '-i', input_file, output_file], check=True)
                converted_files.append(output_file)
            except subprocess.CalledProcessError as e:
                st.write(f"Error converting {filename} to WAV: {e}")
                converted_files.append(None)
        else:
            try:
                result = subprocess.run(
                    ['ffmpeg', '-i', '-', '-f', 'wav', 'pipe:1'],
                    input=filedata,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                converted_files.append(result.stdout)
            except subprocess.CalledProcessError as e:
                st.write(f"Error converting {filename} to WAV: {e.stderr.decode()}")
                converted_files.append(None)

    return converted_files

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
st.title("Voice Assistant Task Processor")

# Move options to the sidebar
st.sidebar.header("Options")

# Option to record from mic
mic_input = st.sidebar.checkbox("Record from microphone")
save_recording_status = st.sidebar.checkbox("Save recording")

# Option to upload files to the virtual folder
if not mic_input:
    uploaded_files = st.sidebar.file_uploader("Upload Files", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            virtual_folder[uploaded_file.name] = uploaded_file.read()

# Option to clear the virtual folder
if st.sidebar.button("Clear Virtual Folder"):
    virtual_folder.clear()
    st.sidebar.write("Virtual folder cleared.")

# Button to start recording or convert files
if mic_input:
    if st.sidebar.button("Press and hold to record"):
        audio = load_audio_from_mic(save_recording=save_recording_status)
else:
    if st.sidebar.button("Convert Files"):
        audio = convert_files_in_virtual_dir_to_wav(virtual_folder, save=save_recording_status)

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
