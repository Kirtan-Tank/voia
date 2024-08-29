import streamlit as st
from openai import OpenAI
import openai
import json

# Load API key from .env file
openai_voia_key = st.secrets["openai_voia_key"]
openai.api_key = openai_voia_key

# Function to get GPT response
def get_gpt_response(text, prompt_template, model="gpt-3.5-turbo-0125"):
    prompt = prompt_template.format(text=text)

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant who is master in understanding tasks and detecting languages."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the response
        answer = response.choices[0].message.content.strip()
        return answer

    except Exception as e:
        st.write(f"Error: {e}")
        return None

# Define prompt template
prompt_template = """
    Execute task from TASKS by following INSTRUCTIONS
    
    

INSTRUCTIONS:
1. Not all tasks are mandatory to perform.
2. Both tasks are distinct.
3. Follow the given ORDER strictly.
4. Do not assume stuff, just follow the process
4. ALL TEXT must be in ENGLISH only.

TASKS:
1. Booking a meeting.
2. Sending an email.

TASK FEATURES:
1. Booking a meeting: No clear mention of sending an email.
2. Sending an email: Clear mention of sending an email (biggest hint).

ORDER:
1. Analyze and repair the text to make it more sensible.
2. Determine the correct lanaguage from grammar, keywords and converted it to correct one and save it as `transcribed_new`.
3. Translate the given text into English (mandatory) and use it for further operations.
4. Understand the meaning of the text, and decide the type of task by matching it with TASK FEATURES.
5. Provide a summary of what the user wants to do and extract key entities.
6. Populate the information in the RESPONSE FORMAT.
7. Ensure the entire response is in ENGLISH only.
8. Verify that all text is in ENGLISH and properly formatted.

RESPONSE FORMAT - DICTIONARY:
Include ONLY the following information:
- 'type of task': Identified task from TASKS.
- 'extracted entities': Important entities.
- 'details': Detailed description of what the user wants to do.
- 'transcribed_new': Paste the text as saved earlier as in STEP 2 of ORDER.

NOTE: Ensure RESPONSE has all the mentioned variables. 
    Here is the text {text}
    """

# Streamlit UI
st.title("🎵 VOIA")
st.sidebar.title("⚙️ SIDE PANEL")

# Option to record from mic
mic_input = st.sidebar.checkbox("Record from microphone")
save_recording_status = st.sidebar.checkbox("Save recording")

# Option to upload files
if not mic_input:
    uploaded_files = st.sidebar.file_uploader("Upload files", accept_multiple_files=True, type=['wav', 'mp3'])

# Automatically convert files if uploaded
audio_files = None
if uploaded_files:
    audio_files = uploaded_files

client = OpenAI(api_key=openai_voia_key)

# Option to transcribe and process audio
if st.sidebar.button("Transcribe and Process"):
    if audio_files:
        progress_bar = st.progress(0)
        total_files = len(audio_files)

        for idx, audio in enumerate(audio_files):
            # Update progress bar
            progress = (idx + 1) / total_files
            progress_bar.progress(progress)

            # Perform transcription directly using the file object
            try:
                with st.spinner("Transcribing audio..."):
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1", 
                        temperature=0.2,
                        file=audio,  # Directly pass the file object
                    )
                text = transcription.text

                # Display the transcribed text
                st.write("### Transcribed Text")
                st.markdown(f"**Transcription:** {text}")

                # Extract and display the GPT response
                with st.spinner("Extracting details..."):
                    response = get_gpt_response(text, prompt_template)
                    st.write("### Processed Response")

                    # Function to display formatted markdown response
                    def display_markdown(response):
                        if isinstance(response, str):
                            try:
                                # Attempt to convert the string response to a dictionary
                                response_dict = json.loads(response)
                            except json.JSONDecodeError:
                                st.markdown(response)
                                return
                        elif isinstance(response, dict):
                            response_dict = response
                        else:
                            st.warning("Unexpected response format.")
                            return

                        # Display formatted markdown response
                        for key, value in response_dict.items():
                            if isinstance(value, dict):
                                st.markdown(f"- **{key}:**")
                                display_markdown(value)
                            elif isinstance(value, list):
                                st.markdown(f"- **{key}:**")
                                for item in value:
                                    if isinstance(item, dict):
                                        st.markdown(f"  - **{item.get('key', 'Item')}:** {item.get('value', '')}")
                                    else:
                                        st.markdown(f"  - {item}")
                            else:
                                st.markdown(f"- **{key}:** {value}")

                    # Display formatted markdown response
                    display_markdown(response)

                    # Display the raw JSON string as text
                    # st.markdown("## JSON")
                    # st.text(response)

                st.success("Processing complete!")
            except Exception as e:
                st.write(f"Error processing file: {e}")
                st.warning("An error occurred while processing this file.")
        progress_bar.empty()
    else:
        st.write("No audio available for transcription.")
