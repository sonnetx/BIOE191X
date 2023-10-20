import streamlit as st
import streamlit as st
import gspread
import json

st.set_page_config(page_title='Label Medical Misinformation', page_icon=':face_with_thermometer:', layout='wide')

# Initialize Google Sheets with service account credentials
gc = gspread.service_account(filename='llms-for-misinformation-196fdd9cebe7.json')

# Public Google Sheet URL (replace with your URL)
sheet_url = 'https://docs.google.com/spreadsheets/d/1Srh7lQffIXZQEJA0eBImE9LiTf0lJWZ-cvKuaDmqI7Y/edit'

# Define CSS for styling your app
css = """
<style>
.container {
    margin: 20px;
}

.comment {
    padding: 2px;
    margin-top: 5px;
}

.comment p {
    margin-left: 20px;
    margin-bottom: 5px;
}

h1 {
    color: #3498db;
    font-size: 24px;
}

h2 {
    color: #e74c3c;
    font-size: 18px;
}
</style>
"""

# Apply CSS to the whole app
st.markdown(css, unsafe_allow_html=True)

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

# Define a function to display comments recursively in a threaded format
def display_comments(comment, level, parent_comment_author):
    st.write('<div class="comment">', unsafe_allow_html=True)
    st.write(f"**{comment.get('author')}** (Reply to {parent_comment_author}):", unsafe_allow_html=True)
    st.write(f"<p style='margin-left: {10 * level}px; margin-bottom: 1px;'>{comment.get('body')}</p>", unsafe_allow_html=True)
    for reply in comment.get('replies'):
        display_comments(reply, level + 1, comment.get('author'))
    st.write('</div>', unsafe_allow_html=True)

# Function to find and update a row based on userID and postID
def update_or_append_data(gc, sheet_url, user_input):
    # Open the Google Sheet by URL
    sh = gc.open_by_url(sheet_url)

    # Select a specific worksheet (you can replace 'Sheet1' with your actual sheet name)
    worksheet = sh.worksheet('Sheet1')

    # Get all the data from the worksheet
    values = worksheet.get_all_values()

    # Find the index (row) of the matching userID and postID
    found_index = -1
    for i, row in enumerate(values):
        if len(row) >= 2 and row[0] == user_input["Username"] and row[1] == user_input["Reddit Post ID"]:
            found_index = i
            break

    if found_index != -1:
        # Update the existing row with the new data
        worksheet.update(f"A{found_index + 1}:G{found_index + 1}", [list(user_input.values())])
        st.success("Data updated in Google Sheets.")
    else:
        # If not found, append a new row
        worksheet.append_row(list(user_input.values()))
        st.success("Data appended to Google Sheets.")


# Header
with st.container():
    st.subheader('Detecting Misinformation with LLMs')
    st.title('Labeling Misinformation from Reddit Responses')
    st.write('Thanks for taking the time to label whether responses to medical questions on Reddit are misinformation or not.')
    st.write('[Learn More About the Lab and Team >](https://www.daneshjoulab.com/)')

with st.container():
    st.write('---')
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

with st.container():
    st.title('Evaluate')

    # Streamlit app title and introduction
    st.title("Reddit Data Scraper")
    st.write("Enter a subreddit name and the range of posts you want to scrape (up to the top 100).")

    # Sidebar input fields
    st.write(
        """
        On the left, type in a subreddit name from those listed below.
        - DermatologyQuestions
        - Skin
        - AskDocs
        - Dermatology
        - SkincareAddictions
        - Popping
        - Hair
        - SkincareAddicts
        """
    )

    # Load your JSON data
    with open('reddit_data1.json', 'r') as json_file:
        data = json.load(json_file)

    # Extract the list of available subreddits from your JSON data
    subreddits = list(data.keys())

    # Create a Streamlit dropdown menu for subreddit selection
    selected_subreddit = st.sidebar.selectbox("Select a Subreddit", subreddits)

    # If your JSON data contains posts under the key "posts," extract them
    if selected_subreddit in data:
        all_posts = data[selected_subreddit]

        # Get the total number of posts
        total_posts = len(all_posts)

        # Sidebar input fields for selecting the range
        st.write("Select the range of posts to display:")
        start_post = st.sidebar.slider("Start Post", 1, total_posts, 1)
        end_post = st.sidebar.slider("End Post", start_post, total_posts, total_posts)
    else:
            st.write("No 'posts' found in your JSON data.")

    # Button to load data
    if st.sidebar.button("Load"):
            
        st.write(f"Loading posts {start_post} to {end_post} from r/{selected_subreddit}...")

        # Extract and display the selected range of posts
        selected_posts = all_posts[start_post - 1:end_post]

        # Inject CSS
        st.markdown(css, unsafe_allow_html=True)

        # Use a horizontal scrollable container for posts
        post_container = st.container()
        with post_container:
            for post in selected_posts:
                with st.expander(f"Title: {post.get('title')}"):
                    st.write("Post ID:", post.get('id'))
                    st.write("Author:", post.get('author'))
                    st.write("Score:", post.get('score'))
                    permalink = post.get('permalink')
                    base_url = "https://www.reddit.com"
                    full_url = base_url + permalink
                    st.write("URL:", full_url)

                    st.write("Comments:")
                    for comment in post.get('comments'):
                        display_comments(comment, level=0, parent_comment_author=post.get('author'))

    userID = st.text_input('Your UserID', value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible")
    postID = st.text_input('Reddit Post ID', value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible")
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
    choose1 = st.radio("To the best of your knowledge is this truthful?",("NA","Strongly Disagree","Disagree", "Neutral", "Agree", "Strongly Agree"))
    choose2 = st.radio("If false how harmful would this information be?",("NA","Strongly Disagree","Disagree", "Neutral", "Agree", "Strongly Agree"))
    choose3 = st.radio("Does this information come from supported information (opt)?",("NA","Strongly Disagree","Disagree", "Neutral", "Agree", "Strongly Agree"))
    choose4 = st.radio("Does this response answer the initial question?",("NA","Strongly Disagree","Disagree", "Neutral", "Agree", "Strongly Agree"))
    choose5 = st.radio("Does response show evidence of reasoning?",("NA","Strongly Disagree","Disagree", "Neutral", "Agree", "Strongly Agree"))

    user_input = {"Username": userID, "Reddit Post ID": postID, "Q1": choose1, "Q2": choose2, "Q3": choose3, "Q4": choose4, "Q5": choose5} 

    key = (userID, postID)  # Use a tuple as the key

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

    # When you want to export user input to Google Sheets
    if st.button("Export Evaluations To Google Sheets"):
        # Load your Google Sheets credentials (replace with your own JSON file)
        gc = gspread.service_account(filename="llms-for-misinformation-196fdd9cebe7.json")

        # Iterate through all the user inputs in the session and update/append them to Google Sheets
        for key, user_input in session_state._state.items():
            update_or_append_data(gc, sheet_url, user_input)

        st.success("Data successfully added to Google Sheets.")
