import json
import ollama
import sqlite3
git config --global user.name "MacElyon"
$ git config --global user.email macelyon@gmail.com

class Memory:
    def __init__(self):
        self.conn = sqlite3.connect('memory.db')
        self.cursor = self.conn.cursor()
        self.file = "memory.json"

    def load_memory(self):
        try:
            with open(self.file, "r") as file:
                return json.load(file)

        except FileNotFoundError:
            return []#handle the case where the file doesn't exist yet by saving the conversation to an empty list
    
    def save_memory(self,conversation):
        with open(self.file, "w") as file:
            json.dump(conversation, file,indent=4)#save the updated conversation history to memory.json with indentation for readability

class Brain:
    def __init__(self):
        self.model = "llama3.2:3b"
        self.system_prompt = """You are an AI assistant named Ayo. 

        Your core behaviours are being:
        calm, precise, and efficient.
        Minimal words, with maximum clarity and helpfulness
        Slightly formal, never verbose
        Rare and subtle dry humor

        Addressing the user:
        Always address as "sir"
        Using "sir" only when appropriate and not excessively

        Response Style:
        Speak in 1-4 sentences
        Only go beyond that range if explicitly asked
        No filler or repitition
        No emojis

        Interaction:
        If the user is inefficient or incorrect:
            respond with “That approach is suboptimal, sir. I recommend…”

        Language:
        Clean, neutral

        Constraints:
        Do not reply theatrically
        Do not overexplain
        Do not be verbose
        """

    def think(self, conversation):
        system_message = [{"role": "system", "content": self.system_prompt}]
        messages = system_message + conversation
        response = ollama.chat(model=self.model, messages= messages) #initialize the ollama chat model with the conversation history
        return response["message"]["content"]

class Conversation:
    def __init__(self, saved_messages=None):
        if saved_messages is None:
            self.messages = []
        else:
            self.messages = saved_messages

    def add_user_message(self,user_input):
        self.messages.append({"role": "user", "content": user_input})#save user input to conversation


    def add_assistant_message(self,answer):
        self.messages.append({"role": "assistant", "content": answer})#save assistant response to conversation1

    def get_messages(self):
        return self.messages.copy()
        

class Ayo:
    def __init__(self):
        self.memory = Memory()
        self.brain = Brain()
        saved_messages = self.memory.load_memory()
        self.conversation = Conversation(saved_messages)


    def run(self):
        while True: #talk to ayo until user types "quit"
            user_input = input("You: ")

            if user_input.lower() == "quit":#end loop
                break

            self.conversation.add_user_message(user_input)#save user input to conversation

            answer = self.brain.think(self.conversation.get_messages())
            print(f"Ayo: {answer}")
    
            self.conversation.add_assistant_message(answer)#save assistant response to conversation1
            self.memory.save_memory(self.conversation.get_messages())

def main():
    ayo = Ayo()
    ayo.run()

if __name__ == "__main__":
    main()