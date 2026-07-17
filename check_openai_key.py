from openai import OpenAI

from explorer.secrets import get_openai_api_key


api_key = get_openai_api_key()
client = OpenAI(api_key=api_key)

try:
    response = client.responses.create(
        model="gpt-5-mini",
        input="Reply only with: API connection successful",
    )
    print(response.output_text)
except Exception as error:
    print(type(error).__name__)
    print(error)
