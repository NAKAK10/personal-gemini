import os
from vertexai.preview import generative_models


# google custom search engine id
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
# google custom search engine api key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# google cloud platform project id
PROJECT_ID = os.getenv("PROJECT_ID", "")
# google cloud platform region
REGION = os.getenv("REGION", "")

# notino api key
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")

# geminiAI safety config
# see https://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/configure-safety-attributes
SAFETY_CONFIG = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
}
