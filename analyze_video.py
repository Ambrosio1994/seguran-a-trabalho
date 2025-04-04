import google.generativeai as genai
import time
import os

from prompts import PROMPT_VIDEO
from dotenv import load_dotenv

load_dotenv()

apiKey = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=apiKey)

fileList = genai.list_files(page_size=100)

# Check uploaded file.
def analyze_video(video_file_name, 
                  display_name:str="video.mp4",
                  model_name:str="gemini-2.0-flash"):
    
    video_file = next((f for f in fileList if f.display_name == display_name), None)
    if video_file is None:
        video_file = genai.upload_file(path=video_file_name, 
                                       display_name=display_name, 
                                       resumable=True)
        
    # Check the state of the uploaded file.
    while video_file.state.name == "PROCESSING":
        time.sleep(5)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)

    # Generate content using the uploaded file.
    model = genai.GenerativeModel(model_name=model_name)
    response = model.generate_content([video_file, PROMPT_VIDEO], 
                                      request_options={"timeout": 600})
    return response.text