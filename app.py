import os
import random
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Feather & Folio", page_icon="🪶", layout="centered")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=Lora:wght@400;500&display=swap');

    html, body, [class*="css"], .stMarkdown, p, div {
        font-family: 'Lora', serif;
    }

    /* Soft pink gradient background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #FFF0F5 0%, #FFE4EC 55%, #FAD0DE 100%);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stBottom"] > div { background: transparent; }

    /* Title */
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        color: #C2185B;
        text-align: center;
        margin-bottom: 0;
    }
    .hero-sub {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        text-align: center;
        color: #8E4A64;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid #F8BBD0;
        border-radius: 18px;
        padding: 0.8rem 1rem;
        box-shadow: 0 4px 14px rgba(231, 84, 128, 0.08);
        backdrop-filter: blur(4px);
    }

    /* Chat input box */
    [data-testid="stChatInput"] {
        border-radius: 24px;
        border: 1.5px solid #F48FB1;
        background: #FFFFFF;
    }

    /* Falling feathers */
    .feather {
        position: fixed;
        top: -10vh;
        z-index: 9999;
        pointer-events: none;   /* never blocks clicks or typing */
        opacity: 0.75;
        filter: drop-shadow(0 2px 3px rgba(194, 24, 91, 0.25));
        animation-name: fall;
        animation-timing-function: ease-in-out;
        animation-iteration-count: infinite;
    }
    @keyframes fall {
        0%   { transform: translate(0, 0) rotate(-15deg); }
        25%  { transform: translate(40px, 30vh) rotate(20deg); }
        50%  { transform: translate(-30px, 60vh) rotate(-20deg); }
        75%  { transform: translate(35px, 90vh) rotate(15deg); }
        100% { transform: translate(0, 120vh) rotate(-10deg); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Feathers: fixed seed so they don't restart every time you send a message
rng = random.Random(42)
feathers = ""
for _ in range(8):
    left = rng.randint(2, 95)
    duration = rng.uniform(14, 24)   # seconds to fall: slow and gentle
    delay = rng.uniform(0, 20)
    size = rng.uniform(1.2, 2.2)
    feathers += (
        f'<div class="feather" style="left:{left}vw; font-size:{size:.1f}rem; '
        f'animation-duration:{duration:.1f}s; animation-delay:-{delay:.1f}s;">🪶</div>'
    )
st.markdown(feathers, unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<h1 class="hero-title">Feather &amp; Folio</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">a quiet place to chat with your books and documents</p>',
    unsafe_allow_html=True,
)

# ---------- Chat ----------
AVATARS = {"user": "🌸", "assistant": "📖"}

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "you are a helpful, warm assistant who loves books"}
    ]

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"], avatar=AVATARS[msg["role"]]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
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