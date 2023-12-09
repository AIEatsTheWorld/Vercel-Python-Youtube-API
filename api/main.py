from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

# Define the Pydantic model for the request


class YouTubeURL(BaseModel):
    url: HttpUrl


app = FastAPI()


def get_video_id_from_url(url: str):
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None


@app.post("/transcript/")
async def get_transcript(youtube_url: YouTubeURL):
    video_id = get_video_id_from_url(youtube_url.url)
    if video_id:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=['en'])
            formatter = TextFormatter()
            formatted_transcript = formatter.format_transcript(transcript)
            return {"transcript": formatted_transcript}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

# Optionally, you can also add a root endpoint


@app.get("/")
async def read_root():
    return {"message": "YouTube Transcript API"}
