
from openai import OpenAI
client = OpenAI(api_key="", base_url="https://api.groq.com/openai/v1")
model="openai/gpt-oss-20b"
from database import add_user, register, save_message, get_user_history
import json
messages=[
        {
            "role":"system",
            "content":"Ты полезный ассистент который нужен чтобы смотреть в SQLite таблицу данные пользователя, отвечай кратко и по делу и проверяй информацию из таблицы",
        }
    ]
Tool=[
    {
    "type": "function",
    "function": {
        "name": "Subscription",
        "description": "Проверка информации о пользователе",
        "parameters": {
            "type": "object",
            "properties": {
                "mail": {
                    "type": "string",
                    "description": "Онлайн почта пользователя"
                        }
                    }
                },
            "required": ["mail"]
            },
        },
    {
    "type": "function",
        "function": {
            "name": "Registration",
                "description": "Регистрация нового пользователя",
                    "parameters": {
                        "type": "object",
                            "properties": {

                                "mail": {
                                    "type": "string",
                                    "description": "Онлайн почта пользователя"
                                },
                                "protocol": {
                                    "type": "string",
                                    "description": "Желаемый протокол пользователя"
                                },
                                "name":{
                                    "type": "string",
                                    "description":"Имя пользователя"
                                }

                            }
                        },
            "required": ["mail", "protocol", "name"]
        },
    }
    ]
def main(user_input, user_id):
    messages=get_user_history(user_id)
    messages.append({"role":"user","content":user_input})
    save_message(user_id=user_id, role="user", content=user_input)
    response=client.chat.completions.create(
        model=model,
        messages=messages,
        tools=Tool,
        tool_choice="auto"
    )
    response_message=response.choices[0].message
    print(response_message)
    tool_calls=response_message.tool_calls
    if tool_calls:
        print("Агент использовал инструмент")
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name=tool_call.function.name
            function_args=json.loads(tool_call.function.arguments)
            if function_name == "Subscription":
                function_response=add_user(function_args.get("mail"))
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role":"tool",
                        "name": function_name,
                        "content": function_response
                    }
                )

            elif function_name == "Registration":
                function_response = register(function_args.get("mail"),function_args.get("protocol"),function_args.get("name"))
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response
                    }
                )
            second_response = client.chat.completions.create(model=model, messages=messages)
            final_text = second_response.choices[0].message.content
            messages.append({"role": "assistant", "content": final_text})
            save_message(user_id=user_id, role="assistant", content=final_text)
            print(final_text)
            return final_text


    else:
        print("Тул не пригодился")
        final_response = response_message.content
        messages.append({"role": "assistant", "content": final_response})
        print(final_response)
        return final_response