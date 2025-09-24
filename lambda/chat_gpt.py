from logger import logger
from enum import Enum
import openai

openai.api_key = "<CHAT_GPT__API_TOKEN>"


class Roles(Enum):
  SYSTEM = "system"
  ASSISTANT = "assistant"
  USER = "user"


INIT_MESSAGE = [
  {
    "role": Roles.SYSTEM.value,
    "content": "Du bist ein Assistent der mir hilft Antworten auf verschiedene Themen zu finden. Bitte keine sehr langen antworten, halte dich kurz wenn möglich.",
  },
]


def command(messages, max_tokens=200):
  # messages.append({"role": "user", "content": message})

  messages = INIT_MESSAGE + messages

  logger.info(f"///// GPT MESSAGES: {messages}")

  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    max_tokens=max_tokens,
    n=1,
  )

  answer = response["choices"][0]["message"]["content"]

  return answer


def __create_message_object(role, message):
  # type: (Roles, str) -> object

  return {"role": role.value, "content": message}


def to_message_object(message):
  # type: (str) -> object

  return __create_message_object(Roles.USER, message)


def to_answer_object(message):
  # type: (str) -> object

  return __create_message_object(Roles.ASSISTANT, message)


# For manual testing purposes. `logger` does not print for on local debugging tho...
if __name__ == "__main__":
  message = "Wie heist die Hauptstadt von Deutschland?"
  print(command([to_message_object(message)]))
