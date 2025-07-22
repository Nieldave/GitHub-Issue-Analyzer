import React from 'react';
import { Github } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex items-center space-x-3">
          <Github className="w-8 h-8 text-gray-800" />
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              GitHub Issue Analyzer
            </h1>
            <p className="text-gray-600 text-sm mt-1">
              Understand, prioritize, and label GitHub issues using AI
            </p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;