from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


print("ChatBot: Type 'quit', 'bye', 'by' or 'exit' to stop\n")

while True:
    user_input = input ("You: ")
    if user_input.lower() in ['quit', 'bye', 'by','exit']:
        print("ChatBot: Bye! see you next time!")
        break

    print("ChatBot: ", end = "", flush = True)

    stream = client.chat.completions.create(

        model = "openai/gpt-oss-20b",
        messages = [
            {"role":"system", "content": "you are a helpful chatbot"},
            {"role":"user", "content":user_input}
        ],
        stream = True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end= "", flush = True)

    print()            



      



