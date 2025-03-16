import streamlit as st
import google.generativeai as genai
import os
import time 
import joblib

f = open("key/api.txt")
key = f.read()
genai.configure(api_key=key)


new_chat_id = f"{time.time()}"
MODEL_ROLE = 'ai'
AI_AVATAR_ICON = "ai-technology.png"

# Create a data/ folder if it doesn't already exist
try:
    os.mkdir('data1/')
except:
    # if the the data/ folder already exist
    pass

# Load past chats (if available)
try:
    past_chats: dict = joblib.load('data1/past_chats_list')
except:
    past_chats = {}

if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"

with st.sidebar:
    st.write("# Past Chats")
    if st.session_state.get("chat_id") is None:
        st.session_state.chat_id = st.selectbox(
            label = 'Pick a Past Chat',
            options = [new_chat_id] + list(past_chats.keys()),
            format_func=lambda x : past_chats.get(x, "New Chat"),
            placeholder="_"
        )
    else:
        st.session_state.chat_id = st.selectbox(
            label = 'Pick a Past Chat',
            options = [new_chat_id, st.session_state.chat_id] + list(past_chats.keys()), 
            index =1,
            format_func=lambda x: past_chats.get(x, 'New Chat' if x!= st.session_state.chat_id else st.session_state.chat_title),
            placeholder='_'
        )
        st.session_state.chat_title = f'ChatSession-{st.session_state.chat_id}'
st.write('# Chat with Google AI - Gemini')

# Chat history allows to ask multiple questions
try:
    st.session_state.messages = joblib.load(
        f'data1/{st.session_state.chat_id}-st_messages'
    )
    st.session_state.gemini_history = joblib.load(
        f'data1/{st.session_state.chat_id}-gemini_messages'
    )
    print('old cache')
except:
    st.session_state.messages=[]
    st.session_state.gemini_history=[]
    print('New_cache made')

st.session_state.model = genai.GenerativeModel('gemini-1.5-pro-latest')
st.session_state.chat = st.session_state.model.start_chat(
    history = st.session_state.gemini_history,
)

# Display chat message from history on app rerun

for message in st.session_state.messages:
    with st.chat_message(
        name = message['role'],
        avatar = message.get('avatar'),
    ):
        st.markdown(message['content'])

if prompt := st.chat_input("Your message here.............."):
    if st.session_state.chat_id not in past_chats.keys():
        past_chats[st.session_state.chat_id] = st.session_state.chat_title
        joblib.dump(past_chats, 'data1/past_chat_list')
    with st.chat_message('user'):
        st.markdown(prompt)
    st.session_state.messages.append(
        dict(
            role = 'user',
            content = prompt
        )
    )
    response = st.session_state.chat.send_message(
        prompt, stream = True
    )
    with st.chat_message(
        name = MODEL_ROLE,
        avatar = AI_AVATAR_ICON,
    ):
        message_placeholder = st.empty()
        fully_response = ''
        assistant_response = response
        for chunk in response:
            for ch in chunk.text.split(" "):
                fully_response +=ch + ' '
                time.sleep(0.05)
                message_placeholder.write(fully_response + ' ')
        message_placeholder.write(fully_response)
    st.session_state.messages.append(
        dict(
            role = MODEL_ROLE,  
            content = st.session_state.chat.history[-1].parts[0].text,
            avatar = AI_AVATAR_ICON,
        )
    )
    st.session_state.gemini_history = st.session_state.chat.history
    joblib.dump(
        st.session_state.messages,
        f'data1/{st.session_state.chat_id}-st_messages',
    )
    joblib.dump(
        st.session_state.gemini_history,
        f'data1/{st.session_state.chat_id}-gemini_messages',
    )