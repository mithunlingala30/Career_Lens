"""Pydantic request schemas."""
import re
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


def check_password(pw: str) -> str:
    problems = []
    if len(pw) < 8: problems.append("at least 8 characters")
    if not re.search(r"[A-Z]", pw): problems.append("an uppercase letter")
    if not re.search(r"[a-z]", pw): problems.append("a lowercase letter")
    if not re.search(r"\d", pw): problems.append("a digit")
    if problems:
        raise ValueError("Password needs " + ", ".join(problems))
    return pw


class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def _pw(cls, v): return check_password(v)


class LoginIn(BaseModel):
    email: EmailStr
    password: str
    role: Optional[Literal["candidate", "admin"]] = None


class ForgotIn(BaseModel):
    email: EmailStr


class ResetIn(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _pw(cls, v): return check_password(v)


class SkillIn(BaseModel):
    skill_name: str = Field(min_length=1, max_length=80)
    skill_type: Literal["technical", "non-technical"] = "technical"


class EducationIn(BaseModel):
    degree: str = Field(min_length=1, max_length=150)
    field_of_study: str = ""
    institution: str = ""
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: str = ""
    level: int = Field(0, ge=0, le=4)


class ExperienceIn(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    duration_months: int = Field(0, ge=0)
    description: str = ""


class CertificationIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    issuer: str = ""
    year: str = ""


class ProjectIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    technologies: str = ""


class ProfileUpdate(BaseModel):
    full_name: str = Field("", max_length=120)
    email: str = Field("", max_length=255)
    phone: str = Field("", max_length=40)
    location: str = Field("", max_length=150)
    summary: str = ""
    skills: list[SkillIn] = []
    education: list[EducationIn] = []
    experience: list[ExperienceIn] = []
    certifications: list[CertificationIn] = []
    projects: list[ProjectIn] = []


class JobRequirementIn(BaseModel):
    skill_name: str = Field(min_length=1, max_length=80)
    importance: int = Field(3, ge=1, le=5)
    is_mandatory: bool = False


class JobIn(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    company: str = Field("", max_length=150)
    category: str = Field(min_length=2, max_length=100)
    location: str = ""
    employment_type: str = "Full-time"
    salary_range: str = ""
    description: str = Field(min_length=10)
    min_education_level: int = Field(2, ge=0, le=4)
    min_experience_years: float = Field(0, ge=0, le=40)
    is_active: bool = True
    requirements: list[JobRequirementIn] = []


class ExtractSkillsIn(BaseModel):
    description: str


class RenameCategoryIn(BaseModel):
    old: str
    new: str = Field(min_length=2, max_length=100)
