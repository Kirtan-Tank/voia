import streamlit as st
import openai
import numpy as np
from io import BytesIO
import subprocess
import os

# Load API key from Streamlit secrets
openai_voia_key = st.secrets["openai_voia_key"]
openai.api_key = openai_voia_key

# Function to record audio from the microphone using sounddevice
def load_audio_from_mic(threshold=500, silence_limit=7, duration=10, rate=44100, channels=1):
    # st.write("Recording... Press 'Stop Recording' to finish.")
    
    # # Record audio for the specified duration
    # audio = sd.rec(int(duration * rate), samplerate=rate, channels=channels, dtype='int16')
    # sd.wait()

    # # Convert the recorded audio to bytes
    # recorded_audio = audio.tobytes()

    # # Check for silence
    # np_audio = np.frombuffer(recorded_audio, dtype=np.int16)
    # volume = np.abs(np_audio).mean()

    # if volume < threshold:
    #     st.write("Silence detected, stopping recording.")
    # else:
    #     st.write("Recording stopped.")
    recorded_audio = "SORRY, RECORDNIG AUDIO IS NOT SUPPORTED ON THIS DEPLOYMENT PLATFORM"
    return recorded_audio

# Function to convert files to WAV format
def convert_files_to_wav(uploaded_files):
    converted_files = []
    for uploaded_file in uploaded_files:
        with BytesIO(uploaded_file.read()) as input_file:
            try:
                result = subprocess.run(
                    ['ffmpeg', '-i', 'pipe:0', '-f', 'wav', 'pipe:1'],
                    input=input_file.read(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                converted_files.append(result.stdout)
            except subprocess.CalledProcessError as e:
                st.write(f"Error converting {uploaded_file.name} to WAV: {e.stderr.decode()}")
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
#TEMPORARY FUNCTION
def is_wav_file(file):
    """Check if a given file is a WAV file based on its magic number."""
    try:
        # Read the first 12 bytes (RIFF header)
        header = file.read(12)
        file.seek(0)  # Reset file pointer after reading

        # Check if the file starts with 'RIFF' and has 'WAVE' as the format identifier
        return header.startswith(b'RIFF') and header[8:12] == b'WAVE'
    except Exception as e:
        print(f"Error checking WAV file: {e}")
        return False

# Streamlit UI
st.sidebar.title("Voice Assistant Task Processor")

# Option to record from mic
mic_input = st.sidebar.checkbox("Record from microphone")
save_recording_status = st.sidebar.checkbox("Save recording")

# Option to upload files
if not mic_input:
    uploaded_files = st.sidebar.file_uploader("Upload files", accept_multiple_files=True, type=None)

# Button to start recording or convert files
if mic_input:
    if st.sidebar.button("Press and hold to record"):
        audio = load_audio_from_mic(save_recording=save_recording_status)
else:
    if uploaded_files and st.sidebar.button("Convert Files"):
        # audio = convert_files_to_wav(uploaded_files) #COMMENTED 
        is_audio= is_wave_file(uploaded_files)
        if is_audio=False:
            st.warning(st.markdown("# PLEASE ONLY UPLOAD WAV FILES"))
            

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
