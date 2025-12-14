import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
response = ""
pre_response = ""
# Function to get Gemini AI response
def get_gemini_response(input_text, speech_text, image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    combined_input = f"{input_text}\n{speech_text}" if speech_text else input_text
    if combined_input.strip():
        response = model.generate_content([combined_input, image] if image else [combined_input])
        return response.text
    return "Please provide some input."

# Function to recognize speech input
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio."
        except sr.RequestError:
            return "Error with the speech recognition service."

# Function to convert text to speech using gTTS
def text_to_speech(text):
    tts = gTTS(text=text, lang="en")
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file

# Streamlit App UI
st.set_page_config(page_title="Multi-Input AI App", layout="wide")

st.title("AI Image Recognition & Speech App")

# Initialize session state for speech text and audio file
if 'speech_text' not in st.session_state:
    st.session_state['speech_text'] = ""
if 'audio_file' not in st.session_state:
    st.session_state['audio_file'] = None

col1, col2 = st.columns(2)

with col1:
    st.subheader(" Manual Text Input")
    input_text = st.text_area("Enter your prompt:", placeholder="Type your prompt here...")

    st.subheader(" Speech-to-Text")
    if st.button("Start Speaking"):
        spoken_text = recognize_speech()
        if spoken_text and "Could not understand" not in spoken_text:
            st.write(f"Recognized: {spoken_text}")
            st.session_state['speech_text'] += " " + spoken_text  # Store recognized text
            st.rerun()  # Refresh UI to update the text area

    # Display recognized speech text
    st.text_area("Recognized Speech:", st.session_state['speech_text'], disabled=True)

    st.subheader("Select Language")
    language = st.selectbox("Choose a language:", ["English", "Spanish", "French","Hindi", "German", "Japanese"])

with col2:
    st.subheader(" Upload an Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    image = Image.open(uploaded_file) if uploaded_file else None
    if image:
        st.image(image, caption="Uploaded Image", use_container_width=True)

# Combine both inputs
input_text = input_text + ".generate response in " + language
final_text = f"{input_text.strip()}\n{st.session_state['speech_text'].strip()}".strip()


if st.button("➤ Generate Response"):
    if not final_text.strip():
        st.warning("Please enter text or speak before generating a response.")
    else:
        with st.spinner("Generating response..."):
            pre_response = response
            response = get_gemini_response(input_text, st.session_state['speech_text'], image)
        st.success("Response generated!")
        st.write(pre_response+response)


        # Convert response to speech
        st.session_state['audio_file'] = text_to_speech(response)

# Play TTS Audio
if st.session_state['audio_file']:
    st.audio(st.session_state['audio_file'], format="audio/mp3")
