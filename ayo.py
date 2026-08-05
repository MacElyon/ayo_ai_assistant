from datetime import datetime
from zoneinfo import ZoneInfo
import ollama
import sqlite3
from Tools.calendar import CalendarTool

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
    def __init__(self, calendar):
        self.model = "qwen2.5:7b"
        self.calendar = calendar
        self.available_functions = {
            "get_events": self.calendar.get_events,
            "schedule_event": self.calendar.schedule_event,
            "delete_event": self.calendar.delete_event
            }

    def build_system_prompt(self):
        now = datetime.now(ZoneInfo("America/New_York")).strftime("%A, %B %d, %Y, %I:%M %p")
        return f"""
        You are Ayo, a personal AI assistant.

        Today's date and time is {now} (America/New_York)
        Interpret words such as "today", "tomorrow", and "next Monday" relative to this date.
        

        Your highest priority is to respond naturally and helpfully.

        Greeting behavior:
        - Always reply to greetings.
        - A simple "Hello, sir." is sufficient.

        Calendar deletion behavior:
        - Users do not know calendar event IDs.
        - Never ask the user for an event ID.
        - If the user wants to delete an event but does not provide an ID, use get_events to locate the event.
        - Only ask for clarification if multiple matching events exist.

        Tool usage:
        - Tools are internal.
        - Never mention internal reasoning.
        - Use tools only when they are required to answer the user's request.
        - Never use tools for greetings or casual conversation.

        Conversation:
        - If a request is unclear, ask a brief clarifying question.
        - Do not assume information that the user has not provided.

        Personality:
        - Calm, precise, efficient.
        - Slightly formal.
        - Concise.
        - Address the user as "sir" naturally, not constantly.

        Safety:
        - Confirm before destructive actions."""

    def think(self, conversation):
        messages = [{"role": "system", "content": self.build_system_prompt()}] + conversation

        while True:
            #initialize the ollama chat model with the conversation history
            response = ollama.chat(model=self.model, messages= messages, tools = list(self.available_functions.values()))
            #add assistant response to the conversation
            messages.append(response.message.model_dump())

            if response.message.tool_calls:
                for tool in response.message.tool_calls:
                    function_name = tool.function.name
                    args = tool.function.arguments
                    print(f"Calling tool: {function_name} with args: {args}")
                    # Avoid calling delete_event without a valid event_id
                    if function_name == "delete_event":
                        if not args.get("event_id"):
                            result = "Missing event ID. Retrieve events first."
                            messages.append({
                            "role": "tool",
                            "tool_name": function_name,
                            "content": str(result)
                            })
                            continue

                    function = self.available_functions[function_name]
                    try:
                        result = function(**args)

                    except Exception as e:
                        print(f"Error occurred while calling tool: {e}")
                        result = {"success": False, "error": str(e)}

                    messages.append({'role': 'tool', "tool_name": function_name, "content": str(result)})

            else:
                #No tool call
                return response.message.content

            

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
        self.calendar = CalendarTool()
        #self.calendar.debug_calendar_identity() for debugging
        self.brain = Brain(self.calendar)
        
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
