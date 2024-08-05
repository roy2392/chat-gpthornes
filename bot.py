import streamlit as st
from utils import write_message
from agent import generate_response

# Page Config
st.set_page_config("Game of Thrones Lore Master", page_icon="🐉")

# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Greetings, my lord! I am your Game of Thrones Lore Master. What tales of Westeros and beyond shall I recount for you today?"},
    ]

# Submit handler
def handle_submit(message):
    with st.spinner('Consulting the ancient texts...'):
        response = generate_response(message)
        write_message('assistant', response)

# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle any user input
if question := st.text_input("What would you like to know about the world of Ice and Fire?"):
    write_message('user', question)
    handle_submit(question)

# Add some GoT themed elements to the UI
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/d/d8/Game_of_Thrones_title_card.jpg", use_column_width=True)
st.sidebar.title("Realms of Knowledge")
st.sidebar.write("Ask me about:")
st.sidebar.write("- The Great Houses of Westeros")
st.sidebar.write("- Dragons and Other Creatures")
st.sidebar.write("- Battles and Wars")
st.sidebar.write("- The Night's Watch and The Wall")
st.sidebar.write("- Legends and Prophecies")