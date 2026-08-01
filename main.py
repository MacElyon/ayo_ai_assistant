import ollama
import sqlite3

class Memory:
    def __init__(self):
        self.conn = sqlite3.connect('memory.db')
        self.cursor = self.conn.cursor()
        self.create_table()
        
    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )""")

        self.conn.commit()

    def load_memory(self):
        self.cursor.execute("SELECT role, content FROM messages")

        rows = self.cursor.fetchall()

        messages = []

        for role, content in rows:
            messages.append({"role" : role, "content": content})
        return messages
        
    
    def save_memory(self, message):
        self.cursor.execute("INSERT INTO messages (role, content) VALUES(?, ?)", (message["role"], message["content"]))
        self.conn.commit()
        
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
        messages = [{"role": "system", "content": self.system_prompt}] + conversation
        response = ollama.chat(model=self.model, messages= messages) #initialize the ollama chat model with the conversation history
        return response["message"]["content"]

class Conversation:
    def __init__(self, saved_messages=None):
        if saved_messages is None:
            self.messages = []
        else:
            self.messages = saved_messages

    def add_user_message(self,user_input):
        messages = {"role": "user", "content": user_input}
        self.messages.append(messages)#save user input to conversation
        return messages


    def add_assistant_message(self,answer):
        messages = {"role": "assistant", "content": answer}
        self.messages.append(messages)#save assistant response to conversation1
        return messages

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

            user_message = self.conversation.add_user_message(user_input)
            self.memory.save_memory(user_message)#save user input to conversation

            answer = self.brain.think(self.conversation.get_messages())
            print(f"Ayo: {answer}")
    
            assistant_message = self.conversation.add_assistant_message(answer)#save assistant response to conversation1
            self.memory.save_memory(assistant_message)

def main():
    ayo = Ayo()
    ayo.run()

if __name__ == "__main__":
    main()