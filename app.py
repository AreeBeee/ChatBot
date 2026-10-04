import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("ChatBot")

# Keep the conversation across messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "you are a helpful chatbot"}
    ]

# Show earlier messages (skip the system prompt)
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input box at the bottom
if user_input := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=st.session_state.messages,
            stream=True,
        )

        def stream_text():
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        reply = st.write_stream(stream_text())

    st.session_state.messages.append({"role": "assistant", "content": reply})