export interface AnalysisRequest {
  repo_url: string;
  issue_number: number;
}

export interface AnalysisResult {
  summary: string;
  type: 'bug' | 'feature_request' | 'documentation' | 'question' | 'other';
  priority_score: string;
  suggested_labels: string[];
  potential_impact: string;
}

export interface ApiError {
  message: string;
  status?: number;
}