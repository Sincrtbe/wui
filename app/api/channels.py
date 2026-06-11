"""API Routes for Channels"""
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from app.schemas.channel import Channel, ChannelCreate, ChannelUpdate
from app.core.json_data_manager import (
    read_json_file,
    write_json_file,
    list_json_files,
    delete_json_file
)

router = APIRouter(prefix="/api/channels", tags=["channels"])

@router.get("/", response_model=List[Channel])
async def get_channels():
    channels = list_json_files("channels")
    return channels

@router.get("/{channel_id}", response_model=Channel)
async def get_channel(channel_id: str):
    channel = read_json_file("channels", channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel

@router.post("/", response_model=Channel)
async def create_channel(channel_in: ChannelCreate):
    channel_id = str(uuid.uuid4())
    now = datetime.now()
    channel_data = {
        "id": channel_id,
        "youtube_id": channel_in.youtube_id,
        "title": channel_in.title,
        "description": channel_in.description,
        "custom_url": channel_in.custom_url,
        "thumbnail_url": channel_in.thumbnail_url,
        "color": channel_in.color,
        "published_at": None,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "email": "",
        "social_links": {},
        "last_scraped_at": None,
        "last_scrape_status": None,
        "scrape_data": {}
    }
    write_json_file("channels", channel_id, channel_data)
    return channel_data

@router.put("/{channel_id}", response_model=Channel)
async def update_channel(channel_id: str, channel_in: ChannelUpdate):
    channel = read_json_file("channels", channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Update fields
    for key, value in channel_in.model_dump(exclude_unset=True).items():
        channel[key] = value
    channel["updated_at"] = datetime.now().isoformat()
    
    write_json_file("channels", channel_id, channel)
    return channel

@router.delete("/{channel_id}")
async def delete_channel(channel_id: str):
    if not delete_json_file("channels", channel_id):
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"status": "deleted"}
