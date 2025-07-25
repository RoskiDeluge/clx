## Cbot-cli Basics

The application is a Python script that prompts the Llama/Ollama text completion endpoint with a system message and can identify the OS of the current system. This helps ensure that Linux, Mac, and Windows specific commands tend to be more accurate.

## Installation

## For Development: 
- Clone this repo to your computer using your terminal.
- `cd ~/<your-directory>/cbot/`
- Run `pip install -e .` inside your cbot directory

- A "cbot-cli" command should be available to use cbot from your CLI, e.g. `cbot-cli -g "Who was the 45th president of the United States?`

- cbot will automatically store questions and responses in a local SQLite database located at `~/.cbot_cache`

- NOTE: For the script to work, you will need to have Ollama running in the background. To install a desired Ollama model go to https://ollama.com/search


## Model Selection
  
You can choose which Ollama model Cbot uses by passing one of these flags before your question:
  
- `-l32` : use `llama3.2` (default)  
- `-ds`  : use `deepseek-r1`
- `-oa`: use `openai o4-mini`
  
Example:
  
```
cbot-cli -l32 -g "List files in my home directory"
cbot-cli -ds -g "Explain how a for loop works in Python"
cbot-cli -oa -g "Who is the president of the United States?"
```

You can also call cbot with a **-s** option. This will save any command as a shortcut with whatever name you choose. The first parameter is the name of the command and the second is the command itself in quotes.

```
$> cbot-cli -s nap "pmset sleepnow"
   Saving shortcut nap, will return: pmset sleepnow
$> cbot-cli -x nap
   Sleeping now...
```

To copy a command directly into the clipboard use the **-c** option. Can be useful if you want to execute the command but you don't trust cbot to do so automatically.

Cbot has a -g option to ask general questions. The results when you ask a general question will not be formated as a command line. This is useful for asking general questions, historical facts or other information not likely to be formated as a command.

```
$> cbot-cli -g "Who was the 23rd president?"
  Herbert Hoover
$> cbot-cli -g "What is the meaning of life?"
   42
```

## Agent Mode

Cbot includes an agent mode with persistent conversation memory using the **-a** flag. In agent mode, the AI maintains context across multiple interactions, remembering your conversation history even between sessions.

```
$> cbot-cli -a
   Entering agent mode. Type 'exit' to end the agent chat.
   Type 'clear' to clear conversation history.
You: What's my name?
Agent: I don't have any information about your name from our conversation.

You: My name is John
Agent: Nice to meet you, John! I'll remember that.

You: exit
   Exiting chat mode.
```

When you restart agent mode later, it will remember previous conversations. Use `clear` to reset the conversation history if needed.

#### Credits

---

Forked by Roberto Delgado. \
Thanks to Gregory Raiz for the original version. \
This code is free to use under the MIT liscense.
