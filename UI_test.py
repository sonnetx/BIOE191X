import requests
import streamlit as st
from streamlit_lottie import st_lottie
import pandas as pd
import os

st.set_page_config(page_title='Label Medical Misinformation', page_icon=':face_with_thermometer:', layout='wide')

class SessionState:
    def __init__(self, session):
        if 'data' not in session:
            session.data = {}
        self._state = session.data

    def get(self, key, default):
        return self._state.get(key, default)

    def set(self, key, value):
        self._state[key] = value

    def delete(self, key):
        if key in self._state:
            del self._state[key]

# Create a session state
session_state = SessionState(st.session_state)

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load Assets
lottie_coding = load_lottieurl('https://lottie.host/736990b8-90e6-4c1a-b273-cc21759292a9/PFVfPSGow1.json')

# Header
with st.container():
    st.subheader('Detecting Misinformation with LLMs')
    st.title('Labeling Misinformation from Reddit Responses')
    st.write('Thanks for taking the time to label whether responses to medical questions on Reddit are misinformation or not.')
    st.write('[Learn More About the Lab and Team >](https://www.daneshjoulab.com/)')

with st.container():
    st.write('---')
    left_column, right_column = st.columns(2)
    with left_column:
        st.header('What we plan on doing:')
        st.write('##')
        st.write(
            """
            Phase 1: 
            - Analyzing Base GPT and LLAMA2
            - Extracting and parsing layers of Reddit Q&As regarding biomedicine.

            Phase 2:
            - Train LLAMA2 with human preference standards with reinforcement learning.
            - Build code to evaluate Reddit
            - Use Likert Scale to evaluate Reddit responses
            """
        )
    with right_column:
        st_lottie(lottie_coding, height=300, key='coding')

with st.container():
    st.title('Evaluate')

    # Create a list of image paths (replace with actual image file paths)
    # "image1.jpg", "image2.jpg", "image3.jpg", "image4.jpg"
    image_paths = []

    # Display images with incremental labels
    for i, image_path in enumerate(image_paths):
        st.image(image_path, caption=f"Image {i + 1}")
        st.text("")  # Add some space between images

    userID = st.text_input('Your UserID', value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible")
    threadID = st.text_input('Reddit Thread ID', value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible")
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
    choose1 = st.radio("To the best of your knowledge is this truthful?",("NA","Strongly Disagree","Disagree", "Neutral", "Agree", "Strongly Agree"))
    choose2 = st.radio("If false how harmful would this information be?",("NA","Strongly Disagree","Disagree", "Neutral", "Agree", "Strongly Agree"))
    choose3 = st.radio("Does this information come from supported information (opt)?",("NA","Strongly Disagree","Disagree", "Neutral", "Agree", "Strongly Agree"))
    choose4 = st.radio("Does this response answer the initial question?",("NA","Strongly Disagree","Disagree", "Neutral", "Agree", "Strongly Agree"))
    choose5 = st.radio("Does response show evidence of reasoning?",("NA","Strongly Disagree","Disagree", "Neutral", "Agree", "Strongly Agree"))

    user_input = {"Username": userID, "Reddit Thread ID": threadID, "Q1": choose1, "Q2": choose2, "Q3": choose3, "Q4": choose4, "Q5": choose5} 

    key = (userID, threadID)  # Use a tuple as the key

    if st.button("Submit"):
        if user_input:
            session_state.set(key, user_input)
            st.success(f"Data '{user_input}' added to the session with key {key}.")

    delete_options = list(session_state._state.keys())  # Get the keys for delete options
    delete_options.insert(0, 'None')  # Add 'None' as the default option
    delete_key = st.selectbox("Select data to delete:", delete_options)
    if delete_key != 'None':
        session_state.delete(delete_key)
        st.success(f"Data with key {delete_key} deleted from the session.")

    # Display the session data
    st.write("Session Data:")
    if session_state._state:
        for key, data in session_state._state.items():
            st.write(f"Key: {key}, Data: {data}")

    # User input for file destination (directory path)
    st.write('For Windows: "C:\\Users\\YourUsername\\Documents\\"')
    st.write('For macOS or Linux: "/Users/YourUsername/Documents/"')
    file_destination = st.text_input("Enter the Directory Path to Save CSV File", "/path/to/directory")

    # Export session data to a local CSV file in the specified directory
    if st.button("Export CSV Locally"):
        if session_state._state:
            data_list = [data for data in session_state._state.values()]
            df = pd.DataFrame(data_list, columns=["Username", "Reddit Thread ID", "Q1", "Q2", "Q3", "Q4", "Q5"])
            
            if file_destination:
                destination_path = os.path.join(file_destination, "user_data.csv")
                df.to_csv(destination_path, index=False)
                st.success(f"Data exported to {destination_path}")
            else:
                st.warning("Please specify a directory path to save the CSV file.")
        else:
            st.warning("No data to export.")

    st.write('Please email the exported csv to: minhle19@stanford.edu')
    st.write('Thank you for your time!')
