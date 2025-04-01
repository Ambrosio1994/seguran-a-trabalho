import google.generativeai as genai
import time
from prompts import prompt_video
from dotenv import load_dotenv
import os

load_dotenv()

apiKey = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=apiKey)

fileList = genai.list_files(page_size=100)

# Check uploaded file.
def analyze_video(video_file_name:str, 
                  display_name:str="video.mp4",
                  model_name:str="gemini-2.0-flash"):
    
    video_file = next((f for f in fileList if f.display_name == display_name), None)
    if video_file is None:
        print(f"Uploading file...")
        video_file = genai.upload_file(path=video_file_name, display_name=display_name, resumable=True)
        print(f"Completed upload: {video_file.uri}")
    else:
        print(f"File URI: {video_file.uri}")

    # Check the state of the uploaded file.
    print("Processing file...")
    while video_file.state.name == "PROCESSING":
        time.sleep(5)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)

    # Generate content using the uploaded file.
    model = genai.GenerativeModel(model_name=f'models/{model_name}')
    print("Making LLM inference request...")
    response = model.generate_content([video_file, prompt_video], request_options={"timeout": 600})
    return response.text