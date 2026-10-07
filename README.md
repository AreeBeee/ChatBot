<div align="center">

# 🪶 Feather & Folio

*a quiet place to chat with your books and documents*

**[✨ Step inside ✨](https://feather-and-folio.streamlit.app)**

</div>

---

Pull up a chair. Pour something warm.

Feather & Folio is a gentle little reading companion. Bring it a book, a chapter, an essay or a stack of notes, and it will read alongside you, answer your questions, and help you find your way through the pages.

Soft pink skies, drifting white feathers, and a quill that writes beside you as you jot down your thoughts. No rush. No noise. Just you and your story.

## What you can do here

**📖 Share a document**
Tap the **+** in the chat box and choose a PDF, a `.txt` or a `.md` file. Feather & Folio will read it and give you a short summary to begin.

**💬 Ask anything**
*"Who is the narrator?"*
*"What does chapter two say about friendship?"*
*"Explain this paragraph like I'm new to the subject."*
Your companion answers from the page you shared, and tells you honestly when something isn't in it.

**🪶 Keep your own notes**
On the right sits a little notebook tied with a ribbon. Start writing, and the quill will follow your words across the page. When you're done, press **Save my notes** to take them home with you.

**🌸 Or simply talk about books**
No document needed. Ask for a recommendation, talk about a favourite character, or wonder aloud about an ending.

## A few gentle notes

- **Sleepy mornings.** If no one has visited for a while, Feather & Folio may be resting. Click the button to wake it and give it about half a minute to stretch.
- **Your notes are yours.** Nothing you write in the notebook is stored. Save your notes before you close the page if you'd like to keep them.
- **Your documents stay private.** Files you share are only read during your visit and aren't kept afterwards.
- **Shorter is sweeter, for now.** Feather & Folio reads the first several pages of longer documents. Whole-book reading is on its way.
- **Scanned pages.** Photos of pages can't be read yet; documents with selectable text work best.
- **A busy moment.** If many readers arrive at once, you may be asked to wait a minute. Try again shortly and it will be ready.

## Woven together with

Python · Streamlit · the Groq API · an open-source language model · a little bit of SVG and a lot of care.

<details>
<summary>For the curious: running it on your own computer</summary>

<br>

You'll need [uv](https://docs.astral.sh/uv/) and a free [Groq API key](https://console.groq.com).

```bash
git clone https://github.com/AreeBeee/ChatBot.git
cd ChatBot
echo "GROQ_API_KEY=your_key_here" > .env
uv sync
uv run streamlit run app.py
```

Then open the address shown in your terminal.

</details>

---

<div align="center">

*Made with love by Rosh* 🌸
*If Feather & Folio kept you company, feel free to leave a ⭐*

</div>
