# Ayo - Personal AI Assistant

## Description
Ayo is a local AI assistant built in Python using Ollama and Google Calendar API, that has the ability to chat and remember conversations thanks to sqlite being used as memory, as well having the ability to manage your Google Calendar events for you.

## Getting Started

### Pre-requisites
- Install your preferred IDE e.g. Visual Studio Code
- Clone the repository
- Python
- Ollama installed and running locally
- A Google Cloud project with the Calendar API enabled

### Installing dependencies

pip install -r requirements.txt

### Pull the Ollama model

Ayo uses qwen2.5:7b by default:

- ollama pull qwen2.5:7b
- Confirm it downloaded: ollama list

*I recommend using a larger model for faster response times and more accurate responses*

### Configuration
The model used for reasoning can be found and changed in Brain.__init__ inside ayo.py: self.model = "qwen2.5:7b"

### Set up Google Calendar API access

Follow Google's guide to creating OAuth Credentials for a desktop app:

https://developers.google.com/workspace/calendar/api/quickstart/python

Once you have "credentials.json", place it in the project root
"credentials.json" and "token.json" should be kept in ".gitignore" as they are private

### Run Ayo
- Run in python main.py
- On first run, you will be asked to authorize calendar access, and then your "token.json" file will be automatically created.
- Type "quit" at anytime to exit the chat

## Features

- Local LLM inference using Ollama
- Persistent conversation memory with SQLite
- Google Calendar integration
- Calendar event creation, retrieval, and deletion
- Tool calling architecture

## Technologies

- Python
- Ollama
- SQLite
- Google Calendar API

## Future Plans

Ayo is actively being developed. Future improvements include:
- Voice integration
- Email integration
- More tools
- Improved planning/reasoning
- Better memory systems
- Web search capability

## Known Limitations

- Ayo can misinterpret relative dates e.g. "today", "tomorrow". Has to be fixed using datetime in the system prompt to tell it what the current date is
- Ayo may hallucinate using prompts. Fixed by gving it tool usage rules in the system prompt

## Author

MacElyon Akinbanjo

## License

This project is licensed under the MIT License - see the LICENSE file for details
