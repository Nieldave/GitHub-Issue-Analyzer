import React from 'react';
import { MessageSquare, Tag, Star, AlertTriangle, CheckCircle } from 'lucide-react';
import { AnalysisResult as AnalysisResultType } from '../types';

interface AnalysisResultProps {
  result: AnalysisResultType;
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'bug':
      return <AlertTriangle className="w-4 h-4" />;
    case 'feature_request':
      return <Star className="w-4 h-4" />;
    case 'documentation':
      return <MessageSquare className="w-4 h-4" />;
    default:
      return <CheckCircle className="w-4 h-4" />;
  }
};

const getTypeColor = (type: string) => {
  switch (type) {
    case 'bug':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'feature_request':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'documentation':
      return 'bg-purple-100 text-purple-800 border-purple-200';
    case 'question':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getPriorityColor = (priority: string) => {
  const priorityMatch = priority.match(/^(\d+)/);
  const priorityNum = priorityMatch ? parseInt(priorityMatch[1]) : 3;
  if (priorityNum >= 4) return 'bg-red-100 text-red-800 border-red-200';
  if (priorityNum >= 3) return 'bg-orange-100 text-orange-800 border-orange-200';
  if (priorityNum >= 2) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  return 'bg-green-100 text-green-800 border-green-200';
};

const AnalysisResult: React.FC<AnalysisResultProps> = ({ result }) => {
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
          <MessageSquare className="w-5 h-5 text-gray-600" />
          <span>Analysis Results</span>
        </h3>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Summary */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-1">
            <span>🔍</span>
            <span>Summary</span>
          </h4>
          <p className="text-base font-medium text-gray-900 leading-relaxed">
            {result.summary}
          </p>
        </div>

        {/* Type */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-1">
            <span>🏷</span>
            <span>Type</span>
          </h4>
          <div className="flex items-center">
            <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-sm font-medium border ${getTypeColor(result.type)}`}>
              {getTypeIcon(result.type)}
              <span>{result.type.replace(/_/g, ' ')}</span>
            </span>
          </div>
        </div>

        {/* Priority */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-1">
            <span>⭐</span>
            <span>Priority</span>
          </h4>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium border ${getPriorityColor(result.priority_score)}`}>
            {result.priority_score}
          </span>
        </div>

        {/* Suggested Labels */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-1">
            <span>🏁</span>
            <span>Suggested Labels</span>
          </h4>
          <div className="flex flex-wrap gap-2">
            {result.suggested_labels.map((label, index) => (
              <span
                key={index}
                className="inline-flex items-center space-x-1 px-2.5 py-0.5 bg-gray-100 text-gray-800 text-sm font-medium rounded-full border border-gray-200"
              >
                <Tag className="w-3 h-3" />
                <span>{label}</span>
              </span>
            ))}
          </div>
        </div>

        {/* Potential Impact */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-1">
            <span>⚠️</span>
            <span>Potential Impact</span>
          </h4>
          <p className="text-sm text-gray-600 italic leading-relaxed">
            {result.potential_impact}
          </p>
        </div>
      </div>
    </div>
  );
};

export default AnalysisResult;