from openai import OpenAI
from dotenv import load_dotenv
import json
from tools import add_book, get_books, update_book, delete_book, get_reading_summary
from my_tools import my_tools

load_dotenv()

client = OpenAI()

SYSTEM_INSTRUCTIONS = """
You are a reading tracker assistant with access to tools for adding, viewing,
updating, and deleting books.

If you need information from one tool before you can complete the user's actual
request, call that tool first, then use its result to call the next tool needed
to finish the task. Do not stop and report back partial information if a tool
call would let you complete what the user asked for. For example, if a user asks
to delete or update a book using a description (like a title) and you are unsure
of the exact record, first call get_books to find it, then call delete_book or
update_book with the details you found. Only ask the user for clarification if
get_books returns more than one matching record, or none at all.
"""

tool_mapping = {
    'add_book': add_book,
    'get_books': get_books,
    'update_book': update_book,
    'delete_book': delete_book,
    'get_reading_summary': get_reading_summary
}

previous_response_id = None

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    if previous_response_id is None:
        response = client.responses.create(model='gpt-5.6-sol',
                                input = user_input,
                                instructions = SYSTEM_INSTRUCTIONS,
                                tools = my_tools
                                )
    else:
        response = client.responses.create(model='gpt-5.6-sol',
                                input = user_input,
                                previous_response_id = previous_response_id,
                                instructions = SYSTEM_INSTRUCTIONS,
                                tools = my_tools
                                )

    response_id = response.id

    while True:
        tool_outputs = []
        llm_output = response.output
        for item in llm_output:
            if item.type == 'function_call':
                args = json.loads(item.arguments)
                function_name = item.name
                print(function_name, args)
                call_function = tool_mapping[function_name]
                tool_result = call_function(**args)
                call_id = item.call_id
                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": str(tool_result)
                    }
                )

        if not tool_outputs:
            break

        response = client.responses.create(model='gpt-5.6-sol',
                            input = tool_outputs,
                            previous_response_id = response_id,
                            instructions = SYSTEM_INSTRUCTIONS,
                            tools = my_tools
                            )

        response_id = response.id

    previous_response_id = response_id
    print(response.output_text)