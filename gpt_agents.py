import openai

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

#Chat agent
class Chat:
    def __init__(self, model):
        openai.api_key = open("openai_key.txt", "r").read().strip("\n")
        self.model = model
    def __str__(self):
        name = "Chat Agent [" + self.model + "]"
        return name
    def chat(self, messages):
        completion = openai.ChatCompletion.create(
            model = self.model,
            temperature = 0.7,
            messages = messages
        )
        reply_content = completion.choices[0].message.content
        return reply_content

#Checks a user input to see if we need to make a call, send an SMS or email, or create an event.
#Uses instruct-gpt model so GPT-4 is only called when necessary.
def instruct_agent(prompt):
    keywords = [
        "make a call", "call", "phone",
        "send an email", "email",
        "send a text", "send an sms", "text", "sms",
        "create an event", "add to calendar", "calendar event",
    ]
    response = openai.Completion.create(
        engine="davinci-instruct-beta",
        prompt=f"Given the following user input, identify if any of these tasks are requested: {', '.join(keywords)}.\n\nUser input: {prompt}\n\nIdentified tasks:",
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0,
    )
    identified_tasks = response.choices[0].text.strip().lower().split(',')
    # Check if any identified tasks are in the list of keywords
    for task in identified_tasks:
        if task.strip() in keywords:
            return True
    return False

class Executive:
    def __init__(self, model):
        openai.api_key = open("openai_key.txt", "r").read().strip("\n")
        self.model = model
    def __str__(self):
        name = "Executive Agent [" + self.model + "]"
        return name
    def identify_task(self, prompt):
        #dictionary used to call functions depending on output of executive
        agent_dict = { 
                "send_email": send_email,
                }
        completion = openai.ChatCompletion.create(
            model = self.model,
            temperature = 0,
            messages=[
                    {"role":"system", "content": "You analyze user input, and output the names of functions to fullfil a user's needs. You can only output: ['send_email', 'chat']"},
                    {"role":"user", "content": prompt}
                    ] 
        )
        reply_content = completion.choices[0].message.content
        if "send_email" in reply_content:
            agent_response = agent_dict[reply_content](prompt)
            return agent_response #response should be status of agent attempt to complete task
        else:
            return False #False means default to chat

def main():
    print("Welcome to the Pico Assistant interface!")
    print("Type 'quit' to exit the chat.\n")

    message_history = []
    system_message = [{"role": "system", "content": "You are Pico. Pico is an AI assistant. Your name is Pico."}]
    message_history.append(system_message[0])
    max_history = 5  # Adjust this value to limit the number of messages considered

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        else:
            message_history.append({"role": "user", "content": user_input})
            #Keeps inserting system message as first message when max history is exceeded.
            if len(message_history) > max_history:
                message_history.insert(-max_history + 1, system_message[0])
            message_history = message_history[-max_history:]
            gpt4_chat = Chat("gpt-4")
            response = gpt4_chat.chat(message_history)
            message_history.append({"role": "assistant", "content": response})
            print(f"Pico: {response}\n")
        
if __name__ == "__main__":
    main()