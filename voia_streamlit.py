import streamlit as st
from openai import OpenAI
import openai
import json

# Load API key from Streamlit secrets
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
- Ensure all identified text is in ENGLISH only except for `transcribed_text`.
- The audio may contain a mix of Hindi, Gujarati, English, Hinglish, or Gujlish.
- Follow the ORDER strictly for processing.
- Handle misclassification of language carefully; detect and repair it.
- Focus on identifying the intent correctly for task classification.
- DO NOT PRINT ORDER OR FORMAT, just print the response in the dictionary form as instructed in RESPONSE

ORDER:
1. Analyze and repair the transcribed text, fixing grammatical errors and making it more coherent.
2. Identify the correct language: If the language is incorrectly identified, detect the true language by analyzing sentence structure and keywords. Convert the transcription to the correct language and store it as `transcribed_text`.
3. Translate to English: Ensure the transcription is translated into English for further steps.
4. Task classification: Based on the provided text, accurately classify the task from TASKS."
5. Extract key entities: Extract important details such as names, locations, times, and other relevant entities from the text.
6. Generate detailed description: Summarize the user's intent, describing what the user aims to do with all relevant details included.
7. Populate RESPONSE FORMAT: Ensure the final output is correctly formatted as per the RESPONSE FORMAT.
8. Ensure correctness: Verify that the entire response, except transcribed_text, is in English and properly formatted 
9. RETURN RESPONSE as dictionary

TASKS:
- Booking a meeting: There is no clear mention of sending an email.
- Sending an email: A clear mention of sending an email is the biggest indicator.

RESPONSE (DICTIONARY- ENGLISH LANGUAGE ONLY):
- 'type_of_task': Identified task from TASKS.
- 'important_details': Key entities extracted from the text (e.g., recipient name, location, time).
- 'detailed_description': A detailed summary of what the user wants to do.
- 'transcribed_text': The corrected and repaired transcription in the originally detected language (if different from English).

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
                                st.text(response) 
                                return
                        elif isinstance(response, dict):
                            response_dict = response
                        else:
                            st.warning("Unexpected response format.")
                            return

                        # Display the response in a more organized way
                        st.markdown(f"**Type of Task:** {response_dict.get('type_of_task', 'N/A')}")
                        st.markdown(f"**Important Details:**")
                        important_details = response_dict.get('important_details', [])
                        if important_details:
                            for detail in important_details:
                                st.markdown(f"- {detail}")
                        else:
                            st.markdown("- No important details found.")

                        st.markdown(f"**Detailed Description:** {response_dict.get('detailed_description', 'N/A')}")
                        st.markdown(f"**Transcribed Text:** {response_dict.get('transcribed_text', 'N/A')}")

                    # Display formatted markdown response
                    display_markdown(response)

                st.success("Processing complete!")
            except Exception as e:
                st.write(f"Error processing file: {e}")
                st.warning("An error occurred while processing this file.")
        progress_bar.empty()
    else:
        st.write("No audio available for transcription.")
