from ask_sdk_local_debug.local_debugger_invoker import LocalDebuggerInvoker
from dotenv import dotenv_values

if __name__ == "__main__":
  env = dotenv_values(".env")

  # The process just exits here, it suddenly stopped working.
  # Docs: https://github.com/alexa/alexa-skills-kit-sdk-for-python/tree/master/ask-sdk-local-debug
  # Wondering why they suggest this file path, propably totaly wayne.
  LocalDebuggerInvoker(
    [
      "--accessToken",
      env.get("ALEXA__LWA_TOKEN"),
      "--skillId",
      env.get("ALEXA__SKILL_ID"),
      "--skillHandler",
      "lambda_handler",
      "--skillFilePath",
      "lambda/lambda_function.py",
      "--region",
      "EU",
    ]
  ).invoke()
