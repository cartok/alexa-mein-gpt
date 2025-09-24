from logger import logger
from dotenv import dotenv_values
import os
from ask_sdk_core.utils import (
  is_request_type,
  is_intent_name,
  get_slot_value,
  get_intent_name,
)
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
import chat_gpt

# ruff: noqa: F401 - imports used for type hints
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response


class LaunchRequestHandler(AbstractRequestHandler):
  def can_handle(self, handler_input):
    # type: (HandlerInput) -> bool

    return is_request_type("LaunchRequest")(handler_input)

  def handle(self, handler_input):
    # type: (HandlerInput) -> Response

    speak_output = 'Sage "Frage", "GPT" oder "Chat", gefolgt von einer Nachricht'

    return handler_input.response_builder.speak(speak_output).response


class ChatIntentHandler(AbstractRequestHandler):
  def can_handle(self, handler_input):
    # type: (HandlerInput) -> bool

    return is_intent_name("ChatIntent")(handler_input)

  def handle(self, handler_input):
    # type: (HandlerInput) -> Response
    input = get_slot_value(handler_input, "input")

    session_attributes = handler_input.attributes_manager.session_attributes

    if "messages" not in session_attributes:
      session_attributes["messages"] = []
    session_attributes["messages"].append(input)

    if "gpt_messages" not in session_attributes:
      session_attributes["gpt_messages"] = []
    session_attributes["gpt_messages"].append(chat_gpt.to_message_object(input))

    if os.environ.get("DEBUG"):  # WIP
      logger.info(f"intent: {get_intent_name(handler_input)}")
      logger.info(f"input: {input}")
      # Echo all messages
      answer = " ".join(session_attributes["messages"])
    else:
      # answer = command(input)
      answer = chat_gpt.command(session_attributes["gpt_messages"])
      session_attributes["gpt_messages"].append(chat_gpt.to_answer_object(answer))

    # Reprompts funktionieren leider nicht, warum auch immer, ich könnte einen "und {input}" intent
    return handler_input.response_builder.speak(answer).ask("").response


class HelpIntentHandler(AbstractRequestHandler):
  def can_handle(self, handler_input):
    # type: (HandlerInput) -> bool

    return is_intent_name("AMAZON.HelpIntent")(handler_input)

  def handle(self, handler_input):
    # type: (HandlerInput) -> Response

    return handler_input.response_builder.speak(
      'Sage "Frage", "GPT" oder "Chat", gefolgt von einer Nachricht um einen Chat zu starten. Für alles andere lies die Beschreibung des Skills "Mein GPT"'
    ).response


class CancelIntentHandler(AbstractRequestHandler):
  def can_handle(self, handler_input):
    # type: (HandlerInput) -> bool

    return is_intent_name("AMAZON.CancelIntent")(handler_input)

  def handle(self, handler_input):
    # type: (HandlerInput) -> Response

    """
    Is it possible to find out from which handler the intent was canceled?
    If it was canceled in the chat handler, the message should propably be removed like this:

      session_attributes = handler_input.attributes_manager.session_attributes
      if "messages" in session_attributes:
        session_attributes["messages"].pop()
    """

    return handler_input.response_builder.speak("Ok").response


class StopIntentHandler(AbstractRequestHandler):
  def can_handle(self, handler_input):
    # type: (HandlerInput) -> bool

    return is_intent_name("AMAZON.StopIntent")(handler_input)

  def handle(self, handler_input):
    # type: (HandlerInput) -> Response

    return handler_input.response_builder.speak("Beendet").set_should_end_session(True).response


class SessionEndedRequestHandler(AbstractRequestHandler):
  def can_handle(self, handler_input):
    # type: (HandlerInput) -> bool

    return is_request_type("SessionEndedRequest")(handler_input)

  def handle(self, handler_input):
    # type: (HandlerInput) -> Response

    # Hier koennte ich session daten in der dynamodb speichern

    return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
  def can_handle(self, handler_input, exception):
    # type: (HandlerInput, Exception) -> bool

    return True

  def handle(self, handler_input, exception):
    # type: (HandlerInput, Exception) -> Response

    logger.error(exception, exc_info=True)

    return handler_input.response_builder.speak("Programmfehler").response


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ChatIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelIntentHandler())
sb.add_request_handler(StopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
