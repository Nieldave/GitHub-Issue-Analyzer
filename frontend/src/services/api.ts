import { AnalysisRequest, AnalysisResult } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export class ApiError extends Error {
  status?: number;
  
  constructor(message: string, status?: number) {
    super(message);
    this.status = status;
  }
}

export const analyzeIssue = async (data: AnalysisRequest): Promise<AnalysisResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      let errorMessage = 'Failed to analyze issue. Please try again.';
      
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // Status-based error messages
        if (response.status === 404) {
          errorMessage = 'Repository or issue not found. Please check the URL and issue number.';
        } else if (response.status === 400) {
          errorMessage = 'Invalid request. Please check the repository URL format.';
        } else if (response.status === 502) {
          errorMessage = 'Failed to fetch data from GitHub API. Please try again.';
        } else if (response.status === 500) {
          errorMessage = 'Internal server error during analysis. Please try again later.';
        } else if (response.status === 403) {
          errorMessage = 'GitHub API rate limit exceeded or repository is private.';
        }
      }
      
      throw new ApiError(errorMessage, response.status);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiError('Unable to connect to the analysis service. Please ensure the backend is running on http://localhost:8000');
    }
    
    throw new ApiError('An unexpected error occurred. Please try again.');
  }
};