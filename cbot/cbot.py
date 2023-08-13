#!/usr/bin/env python3
from os.path import expanduser
import os
import openai
import json
import sys
import sqlite3
import pyperclip
from dotenv import load_dotenv

from langchain import OpenAI

from langchain.agents import Tool, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.agents import initialize_agent

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
google_cse_id = os.getenv("GOOGLE_CSE_ID")

# LangChain Initialization
llm = OpenAI(temperature=0)

# Initialize the Conversational Agent with Search tool
search = GoogleSearchAPIWrapper()
tools = [
    Tool(
        name="Current Search",
        func=search.run,
        description="useful for answering questions about current events or the current state of the world"
    ),
]

memory = ConversationBufferMemory(memory_key="chat_history")
agent_chain = initialize_agent(
    tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=False, memory=memory)

global question
question = ""


def run_cbot(argv):

    global sys
    sys.argv = argv

    if "-a" in argv:
        print("Entering agent mode. Type 'exit' to end the agent chat.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Exiting chat mode.")
                sys.exit()  # Terminate the program immediately
            response = agent_chain.run(input=user_input)
            print("agent:", response)

    def initDB():
        global cache
        cache = sqlite3.connect(home + "/.cbot_cache")
        cache.execute("""
                    CREATE TABLE IF NOT EXISTS questions
                    (id INTEGER PRIMARY KEY,
                    question TEXT,
                    answer TEXT,
                    count INTEGER DEFAULT 1,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")  # Add timestamp column

        # Create conversations table
        cache.execute("""
                    CREATE TABLE IF NOT EXISTS conversations
                    (id INTEGER PRIMARY KEY,
                    messages TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")

    def closeDB():
        global cache
        cache.commit()
        cache.close()

    def checkQ(question_text):
        global cache
        sql = "SELECT id,answer,count FROM questions WHERE question =" + question_text
        answer = cache.execute(
            "SELECT id,answer,count FROM questions WHERE question = ?", (question_text,))
        answer = answer.fetchone()
        if (answer):
            response = answer[1]
            newcount = int(answer[2]) + 1
            counter = cache.execute(
                " UPDATE questions SET count = ? WHERE id = ?", (newcount, answer[0]))
            return(response)
        else:
            return(False)

    def insertQ(question_text, answer_text):
        global cache
        answer = cache.execute(
            "DELETE FROM questions WHERE question = ?", (question_text,))
        answer = cache.execute(
            "INSERT INTO questions (question,answer) VALUES (?,?)", (question_text, answer_text))

        # Insert message history into conversations table
        messages = [{"role": "user", "content": question_text},
                    {"role": "assistant", "content": answer_text}]
        cache.execute(
            "INSERT INTO conversations (messages) VALUES (?)", (json.dumps(messages),))

    def fetchQ():
        question = ""
        # [cbot,-x,  What,is,the,date]  # execute the response
        # [cbot,What,is, the,date]      # no quotes will work
        # [cbot,What is the date]       # with quotes will work
        for a in range(1, len(argv)):
            question = question + " " + argv[a]
        question = question.strip()
        return question

    def parseOptions(question):
        global question_mode    # modes are normal, shortcut and general
        global general_q
        global execute
        global clip
        global shortcut
        shortcut = ""
        execute = False
        clip = False
        question_mode = "normal"
        if ("-h" in question) or (question == " "):  # Return basic help info
            print("Cbot is a simple utility powered by GPT3")
            print("""
            Example usage:
            cbot how do I copy files to my home directory
            cbot "How do I put my computer to sleep
            cbot -c "how do I install homebrew?"      (copies the result to clipboard)
            cbot -x what is the date                  (executes the result)
            cbot -g who was the 22nd president        (runs in general question mode)
            """)
            exit()

        if ("-x" in question):      # Execute the command
            execute = True
            question = question.replace("-x ", "")

        if ("-c" in question):      # Copy the command to clipboard
            clip = True
            question = question.replace("-c ", "")

        if ("-g" in question):      # General question, not command prompt specific
            question_mode = "general"
            question = question.replace("-g ", "")

        if ("-s" in question):         # Save the command as a shortcut
            question_mode = "shortcut"
            question = argv[2]
            shortcut = argv[3]

        return(question)

    def fetch_previous_prompts():
        global cache
        prompts = cache.execute(
            "SELECT messages FROM conversations ORDER BY timestamp DESC LIMIT 6"
        ).fetchall()
        previous_prompts = []

        for prompt in prompts:
            messages = json.loads(prompt[0])
            previous_prompts.extend(messages)

        return previous_prompts

    # Detect the platform. This helps with platform specific paths
    # and system specific options for certain commands
    platform = sys.platform
    if platform == "darwin":
        platform = "Mac"
    elif platform == "win32":
        platform = "Windows"
    else:
        platform = "Linux"

    question = fetchQ()
    question = parseOptions(question)

    # If we change our training/prompts, just delete the cache and it'll
    # be recreated on future runs.
    home = expanduser("~")
    initDB()

    # check if we're saving a shortcut
    # then check if there's an aswer in our cache
    # then execute a GPT request as needed

    if (question_mode == "shortcut"):
        insertQ(question, shortcut)
        print("Saving Shortcut")
        cache_answer = False
    else:
        cache_answer = checkQ(question)

    response = ""
    if not(cache_answer) and ((question_mode == "general") or (question_mode == "normal")):
        temp_question = question
        if not("?" in question):
            temp_question = question + "?"  # GPT produces better results
            # if there's a question mark.
            # using a temp variable so the ? doesn't get cached

        if (question_mode == "general"):
            system_message = "You are a helpful assistant. Answer the user's question in the best and most concise way possible."
        else:  # question_mode is "normal"
            system_message = f"You are a command line translation tool for {platform}. You will provide a concise answer to the user's question with the correct command. Do not provide examples."

        # Fetch previous prompts from the cache
        previous_prompts = fetch_previous_prompts()

        prompt = [{"role": "system", "content": system_message}] + \
            previous_prompts

        prompt += [{"role": "user", "content": temp_question}]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            temperature=0,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        result = response.choices[0].message["content"]
        insertQ(question, result)

    else:
        result = cache_answer
        if not(question_mode == "shortcut"):
            print("💾 Cache Hit")

    if clip:
        pyperclip.copy(result)
    if execute:
        print("cbot executing: " + result)
        if ("sudo" in result):
            print("Execution canceled, cbot will not execute sudo commands.")
        else:
            result = os.system(result)
    else:
        if not(question_mode == "shortcut"):
            print(result)

    closeDB()
