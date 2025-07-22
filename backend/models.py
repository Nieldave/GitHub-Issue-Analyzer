from pydantic import BaseModel, Field, validator
from typing import List
import re

class IssueRequest(BaseModel):
    repo_url: str = Field(
        ..., 
        description="GitHub repository URL",
        example="https://github.com/facebook/react"
    )
    issue_number: int = Field(
        ..., 
        ge=1, 
        description="GitHub issue number",
        example=123
    )
    
    @validator('repo_url')
    def validate_repo_url(cls, v):
        if not v or not v.strip():
            raise ValueError('Repository URL cannot be empty')
        
        # Basic GitHub URL validation
        github_patterns = [
            r'https://github\.com/[^/]+/[^/]+/?$',
            r'http://github\.com/[^/]+/[^/]+/?$',
            r'github\.com/[^/]+/[^/]+/?$',
            r'^[^/]+/[^/]+/?$'
        ]
        
        if not any(re.match(pattern, v.strip()) for pattern in github_patterns):
            raise ValueError('Invalid GitHub repository URL format')
        
        return v.strip()

class IssueAnalysis(BaseModel):
    summary: str = Field(
        ..., 
        description="One-sentence summary of the issue",
        max_length=200
    )
    type: str = Field(
        ..., 
        description="Issue classification",
        pattern=r'^(bug|feature_request|documentation|question|other)$'

    )
    priority_score: str = Field(
        ..., 
        description="Priority score (1-5) with justification",
        max_length=100
    )
    suggested_labels: List[str] = Field(
        ..., 
        description="2-3 relevant GitHub labels",
        min_items=1,
        max_items=5
    )
    potential_impact: str = Field(
        ..., 
        description="Brief description of potential impact on users",
        max_length=200
    )
    
    @validator('suggested_labels')
    def validate_labels(cls, v):
        if not v:
            raise ValueError('At least one suggested label is required')
        
        # Clean up labels
        cleaned_labels = []
        for label in v:
            if isinstance(label, str) and label.strip():
                cleaned_label = label.strip().lower()
                # Basic label format validation
                if re.match(r'^[a-zA-Z0-9\-_\s]+$', cleaned_label):
                    cleaned_labels.append(cleaned_label)
        
        if not cleaned_labels:
            raise ValueError('No valid labels found')
        
        return cleaned_labels[:5]  # Limit to 5 labels max
    
    @validator('summary')
    def validate_summary(cls, v):
        if not v or not v.strip():
            raise ValueError('Summary cannot be empty')
        return v.strip()
    
    @validator('potential_impact')
    def validate_potential_impact(cls, v):
        if not v or not v.strip():
            raise ValueError('Potential impact cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "summary": "User authentication fails when using OAuth with third-party providers",
                "type": "bug",
                "priority_score": "4 - High impact on user onboarding experience",
                "suggested_labels": ["bug", "authentication", "oauth"],
                "potential_impact": "New users cannot sign up using Google or GitHub OAuth, blocking user acquisition"
            }
        }