# app/models.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============== ENUMS ==============

class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"


class RemoteType(str, Enum):
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class JobSource(str, Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    JOBSBW = "jobsbw"
    FACEBOOK = "facebook"
    GLASSDOOR = "glassdoor"


# ============== JOB MODELS ==============

class Salary(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    currency: str = "BWP"
    period: str = "monthly"
    display: Optional[str] = None


class Company(BaseModel):
    name: str
    logo: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None


class Location(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "Botswana"
    address: Optional[str] = None
    remote: RemoteType = RemoteType.ONSITE


class JobListing(BaseModel):
    id: str
    source: JobSource
    source_url: Optional[str] = None

    title: str
    company: Company
    location: Location
    description: Optional[str] = None

    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None

    salary: Optional[Salary] = None
    benefits: Optional[List[str]] = None

    skills: Optional[List[str]] = None
    requirements: Optional[List[str]] = None

    posted_date: Optional[str] = None
    deadline: Optional[str] = None

    apply_url: Optional[str] = None
    easy_apply: bool = False

    # CV Matching
    match_score: Optional[float] = None
    match_reasons: Optional[List[str]] = None

    tags: Optional[List[str]] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============== SEARCH MODELS ==============

class SearchRequest(BaseModel):
    keywords: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    country: str = "Botswana"

    job_types: Optional[List[JobType]] = None
    experience_levels: Optional[List[ExperienceLevel]] = None
    remote: Optional[RemoteType] = None

    salary_min: Optional[float] = None
    salary_max: Optional[float] = None

    posted_days: Optional[int] = None
    skills: Optional[List[str]] = None

    sources: Optional[List[JobSource]] = None

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: str = "relevance"


class SearchResponse(BaseModel):
    success: bool = True
    total: int
    page: int
    per_page: int
    pages: int
    sources: List[str]
    jobs: List[JobListing]
    search_time_ms: float
    cached: bool = False


# ============== CV MODELS ==============

class Experience(BaseModel):
    title: str
    company: Optional[str] = None
    years: Optional[float] = None
    description: Optional[str] = None


class Education(BaseModel):
    degree: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[int] = None


class ParsedCV(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

    summary: Optional[str] = None
    current_title: Optional[str] = None
    experience_years: Optional[float] = None

    experiences: Optional[List[Experience]] = None
    education: Optional[List[Education]] = None

    skills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    certifications: Optional[List[str]] = None

    raw_text: Optional[str] = None


# ============== API RESPONSE MODELS ==============

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    uptime: float


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None