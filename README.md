# cbot
Cbot is a command line chat bot that uses the gpt-3.5-turbo model from OpenAI. Like the ChatGPT web app, cbot will answer both general questions and specific questions about anything computer related. An OpenAI API key is required for this to work. 

## Example usage:
```
$> cbot -g "could you define the original meaning of the word symposium?"
   sure! the word "symposium" comes from ancient greek and originally referred to a drinking party or banquet
   where guests would engage in intellectual discussions, philosophical debates, and cultural performances.
   in ancient greece, symposia were often held after a formal dinner and were considered an important part of
   social and intellectual life. today, the word "symposium" is still used to refer to a formal meeting or
   conference where experts gather to discuss a particular t opic or issue.

$> cbot -g "could you summarize plato's dialog by the same name?"       
   sure! plato's "symposium" is a philosophical dialogue that takes place at a dinner party in ancient
   athens. the guests at the party, including socrates, aristophanes, and others, take turns giving speeches
   about the nature of love. each speaker presents a different perspective on love, ranging from the physical
   desire for beauty to the spiritual ques t for knowledge and wisdom. socrates, in particular, argues that true
   love is not just about physical attraction, but is a form of spiritual love that seeks to understand the true
   nature of beauty and goodness. throughout the dialogue, the characters engage in lively debates and discussions,
   exploring the complexities of love and desire. the "symposium" is considered one of plato's most important
   works, and has had a significant influence on weste rn philosophy and literature.

$> cbot -g "In google sheets, how should I change this formula '=sum($B30:$B32)' so I can keep an absolute
   reference to the sheet it's in 'RD 2023'?" 
   To keep an absolute reference to the sheet named 'RD 2023' in Google Sheets, you can modify the formula by
   using the `!` operator to specify the sheet name:

   '''
   =sum('RD 2023'!A1:A10)
   '''

   Replace `A1:A10` with the range of cells you want to sum in the 'RD 2023' sheet. This formula will calculate
   the sum of the values in the specified range on the 'RD 2023' sheet, regardless of which sheet the formula is
   entered on.

```

## Cbot Basics
The application is a Python script that prompts the gpt-3.5-turbo chat completions endpoint with a system message and can identify the OS of the current system. This helps ensure that Linux, Mac, and Windows specific commands tend to be more accurate.  

## Installation

- Add your OpenAI API key into an environmental variable. The easiest way to do this is to add to to your command line shell by adding the line:  export OPENAI_API_KEY="then_enter_your_key"
This is most commonly a file called .zshrc or .bashrc in your home directory.  The API key is something that you can get from: https://platform.openai.com/account/api-keys

- Clone this repo to your computer using your terminal.
- `cd ~/<your-directory>/cbot/`
- Run `pip install -e .` inside your cbot directory
- Add a `.env` file in your root directory and enter your OpenAI key `OPENAI_API_KEY=<YOUR-KEY-HERE>`
- A "cbot" command should be available to use cbot from your CLI, e.g. `cbot -g "Who was the 45th president of the United States?`

## Context (Memory)

This version of cbot is using OpenAI's chat completion endpoint which allows cbot to reference its chat history. If you ask it a question and mention a topic you have previously asked about, it should remember its previous responses and answer accordingly. 


# Advanced tricks...

You can call cbot with a **-s** option. This will save any command as a shortcut with whatever name you choose. The first parameter is the name of the command and the second is the command itself in quotes. 
```
$> cbot -s nap "pmset sleepnow"
   Saving shortcut nap, will return: pmset sleepnow
$> cbot -x nap
   Sleeping now...
```

To copy a command directly into the clipboard use the **-c** option. Can be useful if you want to execute the command but you don't trust cbot to do so automatically. 

Cbot has a -g option to ask general questions. The results when you ask a general question will not be formated as a command line. This is useful for asking general questions, historical facts or other information not likely to be formated as a command. 
```
$> cbot -g "Who was the 23rd president?"
  Herbert Hoover  
$> cbot -g "What is the meaning of life?"p
   42
```


Cbot saves every question and response in a SQLite3 database located in the home directory .cbot_cache. You can inspect or delete this directory, you can also directly add or remove shortcuts if needed.



#### Credits
----
Current version by Roberto Delgado. 
Initial version by Gregory Raiz. 
This code is free to use under the MIT liscense.
