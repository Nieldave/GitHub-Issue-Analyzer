import React, { useState } from 'react';
import { Search, AlertCircle } from 'lucide-react';
import { AnalysisRequest } from '../types';
import LoadingSpinner from './LoadingSpinner';

interface AnalyzerFormProps {
  onSubmit: (data: AnalysisRequest) => void;
  isLoading: boolean;
  error: string | null;
}

const AnalyzerForm: React.FC<AnalyzerFormProps> = ({ onSubmit, isLoading, error }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [issueNumber, setIssueNumber] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const validateGitHubUrl = (url: string): boolean => {
    const githubPattern = /^(https?:\/\/)?(www\.)?github\.com\/[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+\/?$/;
    return githubPattern.test(url);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!repoUrl.trim()) {
      setFormError('Please enter a GitHub repository URL');
      return;
    }

    if (!validateGitHubUrl(repoUrl.trim())) {
      setFormError('Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)');
      return;
    }

    if (!issueNumber.trim()) {
      setFormError('Please enter an issue number');
      return;
    }

    const issueNum = parseInt(issueNumber.trim(), 10);
    if (isNaN(issueNum) || issueNum <= 0) {
      setFormError('Please enter a valid issue number');
      return;
    }

    onSubmit({
      repo_url: repoUrl.trim(),
      issue_number: issueNum,
    });
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="repo-url" className="block text-sm font-medium text-gray-700 mb-1">
            GitHub Repository URL
          </label>
          <input
            id="repo-url"
            type="url"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/facebook/react"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-colors"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="issue-number" className="block text-sm font-medium text-gray-700 mb-1">
            Issue Number
          </label>
          <input
            id="issue-number"
            type="number"
            value={issueNumber}
            onChange={(e) => setIssueNumber(e.target.value)}
            placeholder="12345"
            min="1"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-colors"
            disabled={isLoading}
          />
        </div>

        {(formError || error) && (
          <div className="flex items-start space-x-2 p-3 bg-red-50 border border-red-200 rounded-md">
            <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-red-700">{formError || error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium py-2.5 px-4 rounded-md transition-colors duration-200 flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <LoadingSpinner />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              <span>Analyze Issue</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default AnalyzerForm;