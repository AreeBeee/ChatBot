import base64
import io
import os
import random
from pathlib import Path

import groq
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="The literary Quill", page_icon="🪶", layout="wide")

HERE = Path(__file__).parent
MAX_DOC_CHARS = 12000  # keeps requests inside Groq's free-tier limits


def svg_uri(name):
    return "data:image/svg+xml;base64," + base64.b64encode((HERE / name).read_bytes()).decode()


FEATHER_URI = svg_uri("feather.svg")
QUILL_URI = svg_uri("quill.svg")
INK_URI = "data:image/svg+xml;base64," + base64.b64encode(
    b"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 20' preserveAspectRatio='none'>"
    b"<path d='M0 12 C15 2 25 18 40 9 S65 4 80 12 S105 18 120 8 S145 3 160 12 S185 17 200 9 "
    b"S225 4 240 12 S265 17 280 9 L300 10' fill='none' stroke='#6B2F48' stroke-width='2.2' "
    b"stroke-linecap='round'/></svg>"
).decode()

# ---------- Styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=Lora:wght@400;500&family=Caveat:wght@500;700&family=Great+Vibes&display=swap');

    html, body, .stMarkdown, p { font-family: 'Lora', serif; }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 78% 12%, rgba(255,255,255,.75), rgba(255,255,255,0) 40%),
            radial-gradient(circle at 20% 85%, rgba(255,255,255,.25), rgba(255,255,255,0) 35%),
            linear-gradient(160deg, #F7C6CF 0%, #EFA7B4 55%, #E893A3 100%);
        background-attachment: fixed;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMain"], [data-testid="stHeader"] { position: relative; z-index: 1; }
    [data-testid="stMainBlockContainer"] { padding: 1rem 2rem 0.5rem; max-width: 1300px; margin-top: -2.4rem; }
    [data-testid="stMain"] { padding-bottom: 0 !important; }
    [data-testid="stHeaderActionElements"] { display: none !important; }   /* hide link icons on headings */

    /* Fit everything on one screen: the chat box and note grow/shrink with the window */
    .st-key-chatbox,
    [data-testid="stLayoutWrapper"]:has(> .st-key-chatbox) {
        height: calc(100vh - 254px) !important; min-height: 300px; max-height: none !important;
        flex: 0 0 auto !important;
    }
    .st-key-notepad textarea { height: calc(100vh - 320px) !important; min-height: 180px; }

    .hero-title {
        font-family: 'Great Vibes', 'Playfair Display', serif; font-size: 3.4rem; font-weight: 400;
        color: #FFFFFF !important; text-align: center; margin: 0; padding: 0 !important; line-height: 1.15;
        text-shadow: 0 2px 12px rgba(160, 40, 80, 0.35);
    }
    .hero-sub {
        font-family: 'Playfair Display', serif; font-style: italic;
        text-align: center; color: #7A3550; margin: 0 0 0.6rem;
    }

    /* Chat area */
    .st-key-chatbox {
        background: rgba(255, 255, 255, 0.28);
        border: 1px solid rgba(255, 255, 255, 0.7) !important;
        border-radius: 22px;
    }
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 18px; padding: 0.8rem 1rem;
        box-shadow: 0 6px 20px rgba(160, 40, 80, 0.12);
    }
    [data-testid="stChatInput"] {
        border-radius: 24px; border: 1.5px solid #FFFFFF;
        background: rgba(255, 255, 255, 0.92);
    }
    .doc-chip {
        display: inline-block; padding: 0.3rem 0.9rem; margin-bottom: 0.6rem;
        border-radius: 999px; background: rgba(255,255,255,0.85);
        color: #7A3550; font-size: 0.9rem; box-shadow: 0 2px 8px rgba(160,40,80,.12);
    }

    /* ---------- Fairy-tale note ---------- */
    .st-key-notepad {
        position: relative;
        background:
            radial-gradient(circle at 85% 8%, rgba(255,255,255,.95), rgba(255,255,255,0) 45%),
            repeating-linear-gradient(transparent 0 33px, rgba(232, 160, 185, 0.35) 33px 34px) 0 70px / 100% 100% no-repeat,
            linear-gradient(170deg, #FFFAFC 0%, #FDEFF4 60%, #FAE1EA 100%);
        padding: 1.6rem 1.4rem 1.2rem !important;
        border-radius: 26px;
        border: 1px solid rgba(255, 255, 255, 0.95) !important;
        box-shadow:
            inset 0 0 0 7px rgba(255, 255, 255, 0.9),
            inset 0 0 0 8px #EBB8C8,
            0 18px 40px rgba(150, 40, 80, 0.22),
            0 0 30px rgba(255, 255, 255, 0.55);
        margin-top: 1.4rem;
    }
    .st-key-notepad::before {   /* ribbon bow */
        content: "🎀"; position: absolute; top: -30px; left: 50%;
        transform: translateX(-50%); font-size: 2.6rem;
        filter: drop-shadow(0 3px 4px rgba(150, 40, 80, .25));
    }
    .st-key-notepad::after {    /* corner sparkles */
        content: "✧  ✦"; position: absolute; bottom: 14px; left: 20px;
        color: #E7A3BA; font-size: 1.1rem; letter-spacing: 2px;
    }
    .note-title {
        font-family: 'Great Vibes', 'Caveat', cursive !important; font-size: 2.3rem;
        color: #C2185B; margin: 0; line-height: 1.1; text-align: center;
        text-shadow: 0 1px 0 #fff;
    }
    .st-key-notepad textarea {
        font-family: 'Caveat', cursive !important; font-size: 1.45rem !important;
        line-height: 34px !important; color: #6B2F48 !important;
        padding: 0 4px !important; resize: none;
    }
    .st-key-notepad textarea::placeholder { color: #C98BA2 !important; }
    .st-key-notepad [data-testid="stTextArea"] div {
        background: transparent !important; border: none !important; box-shadow: none !important;
    }
    .st-key-notepad [data-testid="InputInstructions"] { display: none; }
    .st-key-notepad .stDownloadButton button {
        background: linear-gradient(90deg, #F8BBD0, #FCE4EC);
        border: 1px solid #fff; border-radius: 999px;
        font-family: 'Caveat', cursive; font-size: 1.25rem; color: #9C2F57;
        box-shadow: 0 4px 12px rgba(194, 24, 91, .18);
    }

    /* The quill: big, bright and glowing. Rests on the corner, writes when you type */
    .quill-zone { position: absolute; inset: 0; pointer-events: none; z-index: 5; }
    .quill {
        position: absolute; right: -62px; top: -150px;
        width: 120px; height: 285px;
        background: url(QUILL) center/contain no-repeat;
        filter: brightness(1.15)
                drop-shadow(0 0 6px rgba(255, 255, 255, 1))
                drop-shadow(0 0 18px rgba(255, 190, 215, 0.95))
                drop-shadow(0 8px 10px rgba(150, 40, 80, 0.35));
        transform: rotate(16deg);
        animation: float 4s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(16deg); }
        50%      { transform: translateY(-10px) rotate(12deg); }
    }

    /* ---------- The writing quill (moved by the script at the bottom) ---------- */
    .st-key-notepad.js-quill .quill { display: none; }
    #fq-quill {
        position: fixed; left: 0; top: 0; width: 120px; height: 285px;
        z-index: 10001; pointer-events: none;
        will-change: transform;               /* moved by the GPU, no repainting */
        transition: transform .7s cubic-bezier(.3, .7, .3, 1);
    }
    #fq-quill.writing { transition: transform .07s linear; }
    #fq-quill .fq-inner {
        width: 100%; height: 100%;
        background: url(QUILL) center/contain no-repeat;
        transform-origin: 29% 99.6%;          /* rotate around the nib */
        transform: rotate(16deg);
        will-change: transform;
        filter: drop-shadow(0 0 5px #fff) drop-shadow(0 0 14px rgba(255,190,215,.95));
        animation: fq-float 4s ease-in-out infinite;
    }
    #fq-quill.writing .fq-inner { transform: rotate(24deg); animation: none; }
    @keyframes fq-float {
        0%, 100% { transform: translateY(0) rotate(16deg); }
        50%      { transform: translateY(-10px) rotate(12deg); }
    }
    .fq-spark {
        position: fixed; z-index: 10002; pointer-events: none; color: #fff; font-size: 12px;
        text-shadow: 0 0 6px #FF9EC4, 0 0 12px #fff;
        animation: fq-spark .9s ease-out forwards;
    }
    @keyframes fq-spark {
        from { transform: translate(0, 0) scale(1); opacity: 1; }
        to   { transform: translate(var(--dx), -28px) scale(.3); opacity: 0; }
    }

    /* ---------- Storybook replies ---------- */
    [data-testid="stChatMessageAvatarCustom"], [class*="st-key-"] [data-testid^="stChatMessageAvatar"] {
        background: #fff !important; border-radius: 50% !important;
        box-shadow: 0 3px 10px rgba(160, 40, 80, .18);
    }
    [class*="st-key-assistant-msg"] [data-testid="stChatMessage"] {
        position: relative;
        background: linear-gradient(170deg, #FFFDFE 0%, #FFF4F8 100%);
        border: 1px solid #F6D3DE;
        border-radius: 6px 24px 24px 24px;
        padding: 1.2rem 1.5rem 1.6rem;
        box-shadow: inset 0 0 0 5px rgba(255,255,255,.9), inset 0 0 0 6px #F7D6E1,
                    0 10px 28px rgba(160, 40, 80, .14);
    }
    [class*="st-key-assistant-msg"] [data-testid="stChatMessage"]::after {
        content: "❦"; position: absolute; right: 18px; bottom: 6px;
        color: #E7A3BA; font-size: 1.2rem;
    }
    [class*="st-key-assistant-msg"] [data-testid="stMarkdownContainer"] p,
    [class*="st-key-assistant-msg"] [data-testid="stMarkdownContainer"] li {
        font-size: 1.04rem; line-height: 1.8; color: #4A2C3A; font-family: 'Lora', serif;
    }
    [class*="st-key-assistant-msg"] [data-testid="stMarkdownContainer"] > p:first-child::first-letter {
        font-family: 'Great Vibes', 'Playfair Display', serif;
        float: left; font-size: 3.4em; line-height: .85; color: #C2185B;
        padding: 4px 8px 0 0; text-shadow: 0 2px 6px rgba(194, 24, 91, .2);
    }
    [class*="st-key-assistant-msg"] h1, [class*="st-key-assistant-msg"] h2,
    [class*="st-key-assistant-msg"] h3, [class*="st-key-assistant-msg"] h4 {
        font-family: 'Playfair Display', serif !important; color: #B0285A !important;
        font-weight: 600 !important; padding: .6rem 0 .2rem !important;
    }
    [class*="st-key-assistant-msg"] h2, [class*="st-key-assistant-msg"] h3 {
        border-bottom: 1px dashed #F4B6C9; font-size: 1.3rem !important;
    }
    [class*="st-key-assistant-msg"] strong { color: #9C2F57; }
    [class*="st-key-assistant-msg"] em { color: #8E4A64; }
    [class*="st-key-assistant-msg"] ul { list-style: none; padding-left: 1.2rem; }
    [class*="st-key-assistant-msg"] ul li::before {
        content: "✦"; color: #E07A9E; margin-left: -1.2rem; margin-right: .5rem; font-size: .8em;
    }
    [class*="st-key-assistant-msg"] ol li::marker { color: #C2185B; font-family: 'Playfair Display', serif; }
    [class*="st-key-assistant-msg"] blockquote {
        border-left: 3px solid #F4A6C0; background: rgba(252, 228, 236, .55);
        border-radius: 0 14px 14px 0; padding: .4rem 1rem; margin: .6rem 0;
        font-style: italic; color: #7A3550;
    }
    [class*="st-key-assistant-msg"] code {
        background: #FCE4EC !important; color: #9C2F57 !important; border-radius: 6px;
    }
    [class*="st-key-assistant-msg"] pre { background: #FFF0F5 !important; border: 1px solid #F8D1DE; border-radius: 12px; }
    [class*="st-key-assistant-msg"] hr { border: none; border-top: 1px dashed #F4A6C0; margin: 1rem 0; }
    [class*="st-key-assistant-msg"] table { border-collapse: collapse; border-radius: 12px; overflow: hidden; }
    [class*="st-key-assistant-msg"] th { background: #FCE4EC; color: #9C2F57; font-family: 'Playfair Display', serif; }
    [class*="st-key-assistant-msg"] th, [class*="st-key-assistant-msg"] td { border: 1px solid #F8D1DE !important; padding: .4rem .8rem; }

    /* Your messages: a soft pink bubble on the right */
    [class*="st-key-user-msg"] [data-testid="stChatMessage"] {
        flex-direction: row-reverse; margin-left: auto; max-width: 78%;
        background: linear-gradient(135deg, #E2739C 0%, #C94677 100%);
        border: 1px solid rgba(255,255,255,.7);
        border-radius: 24px 6px 24px 24px;
        box-shadow: 0 8px 20px rgba(194, 24, 91, .2);
    }
    [class*="st-key-user-msg"] [data-testid="stChatMessage"] p {
        color: #fff !important; text-align: right; text-shadow: 0 1px 2px rgba(150, 30, 70, .2);
    }

    /* Twinkling stars in the background */
    .twinkle {
        position: fixed; z-index: -1; pointer-events: none; color: #fff;
        text-shadow: 0 0 8px #fff, 0 0 14px #FFB6D5;
        animation: twinkle ease-in-out infinite;
    }
    @keyframes twinkle { 0%, 100% { opacity: .15; transform: scale(.7); } 50% { opacity: 1; transform: scale(1.1); } }

    /* ---------- Falling feathers ---------- */
    .fall { position: fixed; top: -40vh; z-index: -1; pointer-events: none; animation: fall linear infinite; }
    .sway {
        background: url(FEATHER) center/contain no-repeat;
        animation: sway ease-in-out infinite alternate;
    }
    @keyframes fall { from { transform: translateY(0); } to { transform: translateY(150vh); } }
    @keyframes sway {
        from { transform: translateX(-40px) rotate(calc(var(--r) - 18deg)); }
        to   { transform: translateX(40px)  rotate(calc(var(--r) + 18deg)); }
    }
    </style>
    """.replace("QUILL", QUILL_URI).replace("INK", INK_URI).replace("FEATHER", FEATHER_URI),
    unsafe_allow_html=True,
)

# ---------- Falling feathers ----------
rng = random.Random(42)
feathers = ""
for _ in range(12):
    depth = rng.random()                          # 0 = far away, 1 = close up
    height = int(120 + depth**2 * 420)
    blur = 1.5 if depth < 0.3 else 0              # only the farthest are soft
    opacity = 0.55 + depth * 0.3
    feathers += (
        f'<div class="fall" style="left:{rng.randint(-5, 92)}vw; '
        f'animation-duration:{rng.uniform(18, 34):.1f}s; animation-delay:-{rng.uniform(0, 34):.1f}s;">'
        f'<div class="sway" style="height:{height}px; width:{int(height * 0.42)}px; opacity:{opacity:.2f}; '
        f'filter:blur({blur}px) drop-shadow(0 6px 10px rgba(160,40,80,.25)); '
        f'animation-duration:{rng.uniform(4, 7):.1f}s; --r:{rng.randint(-60, 60)}deg;"></div></div>'
    )
for _ in range(18):
    feathers += (
        f'<span class="twinkle" style="left:{rng.randint(1, 98)}vw; top:{rng.randint(2, 95)}vh; '
        f'font-size:{rng.uniform(0.5, 1.2):.2f}rem; animation-duration:{rng.uniform(2.5, 5):.1f}s; '
        f'animation-delay:-{rng.uniform(0, 5):.1f}s;">✦</span>'
    )
st.markdown(feathers, unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<h1 class="hero-title">Literary Quill</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">a quiet place to chat with your books and documents</p>',
    unsafe_allow_html=True,
)


# ---------- Document helpers ----------
def read_document(file):
    """Return the text of an uploaded PDF / TXT / MD file."""
    data = file.getvalue()
    if file.name.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return data.decode("utf-8", errors="ignore")


def system_prompt():
    base = (
        "You are a warm, thoughtful reading companion who loves books. "
        "Format every reply in Markdown so it reads like a beautiful page: open with one warm sentence, "
        "use ### headings for sections when the answer has parts, keep paragraphs short, use bullet points "
        "for lists, **bold** key ideas, and > blockquotes when quoting the reader's document. "
        "Keep it elegant and uncluttered, and avoid emojis except an occasional 🪶 or ✨."
    )
    if st.session_state.get("doc_text"):
        return (
            f"{base} The reader has shared a document called '{st.session_state.doc_name}'. "
            "Answer using this document, and say so if the answer isn't in it.\n\n"
            f"--- DOCUMENT ---\n{st.session_state.doc_text}\n--- END ---"
        )
    return base + " Invite the reader to upload a book or document with the + button in the chat box."


AVATARS = {"user": "🌸", "assistant": "📖"}
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Layout: chat on the left, sticky note on the right ----------
chat_col, note_col = st.columns([2.3, 1], gap="large")

with chat_col:
    if st.session_state.get("doc_name"):
        st.markdown(f'<span class="doc-chip">📄 Reading: {st.session_state.doc_name}</span>',
                    unsafe_allow_html=True)

    chatbox = st.container(height=480, border=True, key="chatbox")
    with chatbox:
        if not st.session_state.messages:
            with st.container(key="assistant-msg-welcome"):
                with st.chat_message("assistant", avatar=AVATARS["assistant"]):
                    st.markdown("Welcome, dear reader. Attach a book or document with the **+** button "
                                "below, then ask me anything about it.")
        for i, msg in enumerate(st.session_state.messages):
            with st.container(key=f"{msg['role']}-msg-{i}"):
                with st.chat_message(msg["role"], avatar=AVATARS[msg["role"]]):
                    st.markdown(msg["content"])

    prompt = st.chat_input(
        "Ask about your book, or attach one with +",
        accept_file=True,
        file_type=["pdf", "txt", "md"],
    )

    if prompt:
        # A file was attached: read it and remember it
        if prompt.files:
            file = prompt.files[0]
            with st.spinner(f"Reading {file.name}..."):
                text = read_document(file).strip()
            if not text:
                st.warning("I couldn't find any text in that file (scanned PDFs aren't supported yet).")
            else:
                st.session_state.doc_name = file.name
                st.session_state.doc_text = text[:MAX_DOC_CHARS]
                if len(text) > MAX_DOC_CHARS:
                    st.toast("It's a long one! I've read the first part for now.", icon="🪶")

        question = prompt.text or (
            f"Please give me a short, friendly summary of '{st.session_state.doc_name}'."
            if st.session_state.get("doc_name") else ""
        )

        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            n = len(st.session_state.messages)
            with chatbox:
                with st.container(key=f"user-msg-{n - 1}"):
                    with st.chat_message("user", avatar=AVATARS["user"]):
                        st.markdown(question)
                with st.container(key=f"assistant-msg-{n}"), \
                        st.chat_message("assistant", avatar=AVATARS["assistant"]):
                    try:
                        stream = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[{"role": "system", "content": system_prompt()}]
                            + st.session_state.messages,
                            stream=True,
                        )
                        reply = st.write_stream(
                            chunk.choices[0].delta.content
                            for chunk in stream
                            if chunk.choices[0].delta.content
                        )
                    except groq.RateLimitError:
                        reply = "I'm a little out of breath. Too many requests! Please try again in a minute. 🪶"
                        st.markdown(reply)
                    except groq.APIError:
                        reply = "Something went wrong talking to the model. Please try again."
                        st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

with note_col:
    with st.container(key="notepad"):
        st.markdown(
            '<div class="quill-zone"><div class="quill"></div></div>'
            '<p class="note-title">My notes</p>',
            unsafe_allow_html=True,
        )
        notes = st.text_area(
            "Notes", key="notes", height=410, label_visibility="collapsed",
            placeholder="Jot down thoughts, quotes, page numbers...",
        )
        st.download_button("Save my notes", notes or "", file_name="my-notes.txt",
                           use_container_width=True)

# ---------- The quill follows your writing ----------
# A tiny script that runs in the page: it finds the text cursor in the note
# and moves the quill's nib there with every letter you type.
components.html(
    """
<script>
(function () {
  const P = window.parent, doc = P.document;
  if (P.__fqQuill2) return;             // install only once
  P.__fqQuill2 = true;
  const old = doc.getElementById("fq-quill"); if (old) old.remove();

  const quill = doc.createElement("div");
  quill.id = "fq-quill";
  quill.innerHTML = '<div class="fq-inner"></div>';
  doc.body.appendChild(quill);
  const inner = quill.firstChild;
  const NIB_X = 0.29 * 120, NIB_Y = 0.996 * 285;

  // one hidden "mirror" box, reused to measure where the cursor is
  const mirror = doc.createElement("div");
  Object.assign(mirror.style, {position: "absolute", visibility: "hidden", whiteSpace: "pre-wrap",
                               wordWrap: "break-word", top: "0", left: "-9999px", overflow: "hidden"});
  const mark = doc.createElement("span");
  mark.textContent = "\u200b";
  doc.body.appendChild(mirror);
  let mirrorFor = null;

  const note = () => doc.querySelector(".st-key-notepad");
  let writing = false, idleTimer = null, pending = null, lastX = -1, lastY = -1;

  function place(x, y) {                 // put the nib at (x, y)
    if (Math.abs(x - lastX) < 0.5 && Math.abs(y - lastY) < 0.5) return;
    lastX = x; lastY = y;
    quill.style.transform = `translate3d(${x - NIB_X}px, ${y - NIB_Y}px, 0)`;
  }
  function rest() {                      // perch beside the note's corner
    const n = note();
    if (!n) return;
    n.classList.add("js-quill");
    const r = n.getBoundingClientRect();
    place(r.right - 46, r.top + 170);
  }
  function caretXY(ta) {
    if (mirrorFor !== ta) {              // copy the note's text style once
      const s = P.getComputedStyle(ta);
      ["boxSizing","width","borderTopWidth","borderLeftWidth","paddingTop","paddingRight",
       "paddingBottom","paddingLeft","fontFamily","fontSize","fontWeight","fontStyle","lineHeight",
       "letterSpacing","wordSpacing","textIndent","tabSize"].forEach(p => mirror.style[p] = s[p]);
      mirror.dataset.lh = parseFloat(s.lineHeight) || 30;
      mirrorFor = ta;
    }
    mirror.textContent = ta.value.substring(0, ta.selectionEnd);
    mirror.appendChild(mark);
    const r = ta.getBoundingClientRect();
    return {x: r.left + mark.offsetLeft - ta.scrollLeft + 2,
            y: r.top + mark.offsetTop - ta.scrollTop + mirror.dataset.lh * 0.78};
  }
  function sparkle(x, y) {
    const sp = doc.createElement("span");
    sp.className = "fq-spark";
    sp.textContent = Math.random() < 0.5 ? "\u2726" : "\u2727";
    sp.style.left = (x - 4) + "px";
    sp.style.top = (y - 10) + "px";
    sp.style.setProperty("--dx", (Math.random() * 30 - 10) + "px");
    doc.body.appendChild(sp);
    setTimeout(() => sp.remove(), 950);
  }
  function wiggle() {                    // tiny pen stroke, no page reflow
    inner.animate([
      {transform: "rotate(24deg) translate(0,0)"},
      {transform: "rotate(20deg) translate(2px,-4px)"},
      {transform: "rotate(27deg) translate(-1px,1px)"},
      {transform: "rotate(24deg) translate(0,0)"}
    ], {duration: 180, easing: "ease-in-out"});
  }
  function write(ta, typed) {
    if (!writing) { writing = true; quill.classList.add("writing"); }
    if (pending) return;                 // at most one update per frame
    pending = P.requestAnimationFrame(() => {
      pending = null;
      const {x, y} = caretXY(ta);
      place(x, y);
      if (typed) { wiggle(); if (Math.random() < 0.45) sparkle(x, y); }
    });
    clearTimeout(idleTimer);
    idleTimer = setTimeout(stop, 1500);
  }
  function stop() {
    writing = false;
    quill.classList.remove("writing");
    rest();
  }
  const isNote = t => t && t.tagName === "TEXTAREA" && t.closest(".st-key-notepad");

  doc.addEventListener("input", e => { if (isNote(e.target)) write(e.target, true); }, true);
  doc.addEventListener("keyup", e => { if (isNote(e.target) && e.key.startsWith("Arrow")) write(e.target, false); }, true);
  doc.addEventListener("click", e => { if (isNote(e.target)) write(e.target, false); }, true);
  doc.addEventListener("focusout", e => { if (isNote(e.target)) stop(); }, true);
  doc.addEventListener("scroll", e => {
    const ta = doc.querySelector(".st-key-notepad textarea");
    if (writing && ta) write(ta, false); else rest();
  }, true);
  P.addEventListener("resize", () => { mirrorFor = null; if (!writing) rest(); });
  setInterval(() => { if (!writing) rest(); }, 500);   // keep it in place after page updates
  rest();
})();
</script>
""",
    height=0,
)