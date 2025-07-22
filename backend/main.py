# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import IssueRequest, IssueAnalysis
import requests
import os
import json
import logging
import re
from typing import Optional, Tuple
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate required environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Optional but recommended for rate limits

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(
    title="GitHub Issue Analyzer",
    description="AI-powered GitHub issue analysis and prioritization",
    version="1.0.0"
)

# CORS middleware configuration
app = FastAPI()

# ✅ CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],                      
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "GitHub Issue Analyzer API"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test Gemini API connectivity
        model = genai.GenerativeModel("gemini-1.5-flash")
        test_response = model.generate_content("Hello")
        gemini_status = "healthy" if test_response else "unhealthy"
    except Exception as e:
        logger.error(f"Gemini API health check failed: {e}")
        gemini_status = "unhealthy"
    
    return {
        "status": "healthy",
        "services": {
            "gemini_api": gemini_status,
            "github_api": "healthy"
        }
    }

@app.post("/analyze", response_model=IssueAnalysis)
async def analyze_issue(data: IssueRequest):
    """
    Analyze a GitHub issue using AI to provide structured insights
    """
    logger.info(f"Analyzing issue {data.issue_number} from {data.repo_url}")
    
    try:
        # Parse and validate GitHub URL
        owner, repo = parse_github_url(data.repo_url)
        logger.info(f"Parsed repository: {owner}/{repo}")
        
        # Fetch issue data from GitHub API
        issue_data = get_issue_data(owner, repo, data.issue_number)
        logger.info(f"Successfully fetched issue data: {issue_data['title']}")
        
        # Fetch comments if they exist
        comments = ""
        if issue_data.get("comments", 0) > 0:
            comments = get_issue_comments(issue_data.get("comments_url", ""))
            logger.info(f"Fetched {len(comments.split('---COMMENT---')) if comments else 0} comments")
        
        # Analyze with AI
        analysis_result = analyze_with_llm(
            title=issue_data.get("title", ""),
            body=issue_data.get("body", "") or "",
            comments=comments,
            labels=issue_data.get("labels", []),
            state=issue_data.get("state", "")
        )
        
        logger.info("Successfully completed AI analysis")
        return analysis_result
        
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except requests.exceptions.RequestException as re:
        logger.error(f"GitHub API error: {re}")
        raise HTTPException(status_code=502, detail="Failed to fetch data from GitHub API")
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")

def parse_github_url(repo_url: str) -> Tuple[str, str]:
    """
    Parse GitHub repository URL to extract owner and repo name
    Supports various GitHub URL formats
    """
    if not repo_url:
        raise ValueError("Repository URL cannot be empty")
    
    # Remove trailing slash and whitespace
    repo_url = repo_url.strip().rstrip('/')
    
    # Support various GitHub URL formats
    patterns = [
        r'https://github\.com/([^/]+)/([^/]+)/?$',
        r'http://github\.com/([^/]+)/([^/]+)/?$', 
        r'github\.com/([^/]+)/([^/]+)/?$',
        r'^([^/]+)/([^/]+)/?$'  # Just owner/repo format
    ]
    
    for pattern in patterns:
        match = re.match(pattern, repo_url)
        if match:
            owner, repo = match.groups()
            # Remove .git suffix if present
            if repo.endswith('.git'):
                repo = repo[:-4]
            return owner, repo
    
    raise ValueError("Invalid GitHub repository URL format. Expected: https://github.com/owner/repo")

def get_github_headers() -> dict:
    """Get headers for GitHub API requests"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Issue-Analyzer/1.0"
    }
    
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        logger.info("Using GitHub token for authenticated requests")
    else:
        logger.warning("No GitHub token provided - rate limits may apply")
    
    return headers

def get_issue_data(owner: str, repo: str, issue_number: int) -> dict:
    """
    Fetch issue data from GitHub API with proper error handling
    """
    if issue_number <= 0:
        raise ValueError("Issue number must be positive")
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    headers = get_github_headers()
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            raise ValueError(f"Issue #{issue_number} not found in repository {owner}/{repo}")
        elif response.status_code == 403:
            raise ValueError("GitHub API rate limit exceeded or repository is private")
        elif response.status_code != 200:
            raise requests.RequestException(f"GitHub API returned status {response.status_code}")
        
        issue_data = response.json()
        
        # Validate that this is actually an issue, not a pull request
        if issue_data.get("pull_request"):
            logger.warning(f"Issue #{issue_number} is actually a pull request")
        
        return issue_data
        
    except requests.exceptions.Timeout:
        raise requests.RequestException("GitHub API request timed out")
    except requests.exceptions.ConnectionError:
        raise requests.RequestException("Failed to connect to GitHub API")

def get_issue_comments(comments_url: str) -> str:
    """
    Fetch and format issue comments
    """
    if not comments_url:
        return ""
    
    try:
        headers = get_github_headers()
        response = requests.get(comments_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Failed to fetch comments: status {response.status_code}")
            return ""
        
        comments_data = response.json()
        
        if not comments_data:
            return ""
        
        # Format comments for AI processing
        formatted_comments = []
        for comment in comments_data:
            author = comment.get("user", {}).get("login", "unknown")
            body = comment.get("body", "").strip()
            if body:
                formatted_comments.append(f"Comment by {author}:\n{body}")
        
        return "\n---COMMENT---\n".join(formatted_comments)
        
    except Exception as e:
        logger.error(f"Error fetching comments: {e}")
        return ""

def analyze_with_llm(title: str, body: str, comments: str, labels: list, state: str) -> IssueAnalysis:
    """
    Analyze issue content using Gemini AI with robust error handling
    """
    # Prepare existing labels for context
    existing_labels = [label.get("name", "") for label in labels] if labels else []
    
    prompt = f"""You are an expert GitHub issue analyst. Analyze the following issue and provide a structured JSON response.

ISSUE DETAILS:
Title: {title}
Body: {body or "No description provided"}
Current State: {state}
Existing Labels: {existing_labels}
Comments: {comments or "No comments"}

Please analyze this issue and respond with ONLY a valid JSON object in this exact format:
{{
  "summary": "A clear one-sentence summary of the issue",
  "type": "bug|feature_request|documentation|question|other",
  "priority_score": "1-5 score with brief justification (e.g., '3 - Moderate impact on user experience')",
  "suggested_labels": ["2-3 relevant labels"],
  "potential_impact": "Brief description of impact on users (especially for bugs)"
}}

Guidelines:
- Summary should be concise but informative
- Type must be exactly one of: bug, feature_request, documentation, question, other
- Priority: 1=low, 2=minor, 3=moderate, 4=high, 5=critical
- Suggested labels should be practical and commonly used in GitHub projects
- For non-bugs, potential_impact can describe general user benefit

Respond with ONLY the JSON object, no additional text."""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise ValueError("Empty response from AI model")
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Extract JSON from response if it contains extra text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group()
        
        # Parse JSON response
        try:
            analysis_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Raw response: {response_text}")
            # Return a fallback response
            analysis_data = create_fallback_analysis(title, body, existing_labels)
        
        # Validate and create response model
        return IssueAnalysis(**analysis_data)
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        # Return fallback analysis
        return IssueAnalysis(**create_fallback_analysis(title, body, existing_labels))

def create_fallback_analysis(title: str, body: str, existing_labels: list) -> dict:
    """
    Create a basic fallback analysis when AI processing fails
    """
    # Simple heuristics for classification
    title_lower = title.lower()
    body_lower = (body or "").lower()
    
    # Determine type based on keywords
    if any(word in title_lower for word in ["bug", "error", "issue", "broken", "not working"]):
        issue_type = "bug"
    elif any(word in title_lower for word in ["feature", "add", "support", "enhancement"]):
        issue_type = "feature_request"
    elif any(word in title_lower for word in ["doc", "documentation", "readme"]):
        issue_type = "documentation"
    elif title_lower.startswith(("how", "why", "what", "?")):
        issue_type = "question"
    else:
        issue_type = "other"
    
    return {
        "summary": f"Issue regarding: {title[:100]}{'...' if len(title) > 100 else ''}",
        "type": issue_type,
        "priority_score": "3 - Unable to determine exact priority, defaulting to moderate",
        "suggested_labels": existing_labels[:3] if existing_labels else ["needs-triage"],
        "potential_impact": "Impact assessment requires manual review due to processing error"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")