import React, { useState } from 'react';
import Header from './components/Header';
import AnalyzerForm from './components/AnalyzerForm';
import AnalysisResult from './components/AnalysisResult';
import { AnalysisRequest, AnalysisResult as AnalysisResultType } from './types';
import { analyzeIssue, ApiError } from './services/api';

function App() {
  const [result, setResult] = useState<AnalysisResultType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (data: AnalysisRequest) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const analysisResult = await analyzeIssue(data);
      setResult(analysisResult);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please check your connection and try again.');
      }
      console.error('Analysis error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="space-y-6">
          <AnalyzerForm 
            onSubmit={handleAnalyze}
            isLoading={isLoading}
            error={error}
          />
          
          {result && <AnalysisResult result={result} />}
        </div>
      </main>
    </div>
  );
}

export default App;