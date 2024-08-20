import streamlit as st
import openai
import numpy as np
import sounddevice as sd
#from datetime import datetime
from io import BytesIO
import subprocess
import os

# Load API key from Streamlit secrets
openai_voia_key = st.secrets["openai_voia_key"]
openai.api_key = openai_voia_key

# Function to record audio from the microphone using sounddevice
def load_audio_from_mic(threshold=500, silence_limit=7, duration=10, rate=44100, channels=1):
    st.write("Recording... Press 'Stop Recording' to finish.")
    
    # Record audio for the specified duration
    audio = sd.rec(int(duration * rate), samplerate=rate, channels=channels, dtype='int16')
    sd.wait()

    # Convert the recorded audio to bytes
    recorded_audio = audio.tobytes()

    # Check for silence
    np_audio = np.frombuffer(recorded_audio, dtype=np.int16)
    volume = np.abs(np_audio).mean()

    if volume < threshold:
        st.write("Silence detected, stopping recording.")
    else:
        st.write("Recording stopped.")

    return recorded_audio

# Function to convert files in a directory to WAV format
def convert_files_in_dir_to_wav(directory, save=False, output_dir=None):
    if not os.path.isdir(directory):
        st.write(f"Directory not found: {directory}")
        return None

    converted_files = []
    for filename in os.listdir(directory):
        input_file = os.path.join(directory, filename)
        
        if os.path.isfile(input_file):
            if save:
                if output_dir is None:
                    output_dir = os.path.dirname(input_file)
    
                filename_without_ext = os.path.splitext(os.path.basename(input_file))[0]
                output_file = os.path.join(output_dir, f"{filename_without_ext}.wav")
    
                try:
                    subprocess.run(['ffmpeg', '-i', input_file, output_file], check=True)
                    converted_files.append(output_file)
                except subprocess.CalledProcessError as e:
                    st.write(f"Error converting {input_file} to WAV: {e}")
                    converted_files.append(None)
            else:
                try:
                    result = subprocess.run(
                        ['ffmpeg', '-i', input_file, '-f', 'wav', 'pipe:1'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True
                    )
                    converted_files.append(result.stdout)

                except subprocess.CalledProcessError as e:
                    st.write(f"Error converting {input_file} to WAV: {e.stderr.decode()}")
                    converted_files.append(None)
        else:
            st.write(f"Skipping non-file item in directory: {input_file}")

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

# Option to record from mic
mic_input = st.checkbox("Record from microphone")
save_recording_status = st.checkbox("Save recording")

# Option to convert files in directory
if not mic_input:
    source_path = st.text_input("Source Directory Path")
    save_wav_files = st.checkbox("Save WAV files to directory")

# Button to start recording or convert files
if mic_input:
    if st.button("Press and hold to record"):
        audio = load_audio_from_mic(save_recording=save_recording_status)
else:
    if st.button("Convert Files"):
        audio = convert_files_in_dir_to_wav(directory=source_path, save=save_wav_files, output_dir=output_wav_dir)

# Option to transcribe and process audio
if st.button("Transcribe and Process"):
    if audio:
        transcription = openai.Audio.transcribe("whisper-1", audio)
        text = transcription['text']
        response = get_gpt_response(text, prompt_template)
        st.write("### Processed Response")
        st.json(response)
    else:
        st.write("No audio available for transcription.")
