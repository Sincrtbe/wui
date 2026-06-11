"""Pydantic schemas for Channel entity"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ChannelBase(BaseModel):
    youtube_id: str
    title: str
    description: Optional[str] = ""
    custom_url: Optional[str] = ""
    thumbnail_url: Optional[str] = ""
    color: Optional[str] = "#000000"

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    custom_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    color: Optional[str] = None
    email: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None

class Channel(ChannelBase):
    id: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    email: Optional[str] = ""
    social_links: Optional[Dict[str, str]] = {}
    last_scraped_at: Optional[datetime] = None
    last_scrape_status: Optional[str] = None
    scrape_data: Optional[Dict[str, int]] = {}

    model_config = {"from_attributes": True}
