'use client';

import React, { useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import {
  AlertCircle,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Filter,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';

interface Issue {
  id: string;
  type: 'ambiguity' | 'completeness' | 'ethics';
  severity: 'high' | 'medium' | 'low';
  message: string;
  location: string;
  suggestions: string[];
  line?: number;
}

interface AnalysisResult {
  quality_score: number;
  total_issues: number;
  ambiguity_issues: Issue[];
  completeness_issues: Issue[];
  ethics_issues: Issue[];
  parsed_entities: {
    actors: string[];
    actions: string[];
    entities: string[];
  };
}

interface AnalysisPanelProps {
  analysisResult?: AnalysisResult;
  isAnalyzing?: boolean;
  onIssueClick?: (issue: Issue) => void;
}

export function AnalysisPanel({
  analysisResult,
  isAnalyzing = false,
  onIssueClick,
}: AnalysisPanelProps) {
  const [activeFilters, setActiveFilters] = useState<Set<string>>(new Set());
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['ambiguity', 'completeness', 'ethics'])
  );

  if (!analysisResult && !isAnalyzing) {
    return (
      <Card className="p-6 h-full flex items-center justify-center">
        <div className="text-center text-gray-500">
          <AlertCircle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p className="text-sm">No analysis results yet</p>
          <p className="text-xs mt-2">Click "Analyze Requirements" to get started</p>
        </div>
      </Card>
    );
  }

  if (isAnalyzing) {
    return (
      <Card className="p-6 h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-sm font-medium">Analyzing requirements...</p>
          <p className="text-xs text-gray-500 mt-2">This may take a few seconds</p>
        </div>
      </Card>
    );
  }

  const allIssues = [
    ...(analysisResult?.ambiguity_issues || []),
    ...(analysisResult?.completeness_issues || []),
    ...(analysisResult?.ethics_issues || []),
  ];

  const filteredIssues = activeFilters.size === 0
    ? allIssues
    : allIssues.filter(issue => activeFilters.has(issue.type));

  const toggleFilter = (type: string) => {
    const newFilters = new Set(activeFilters);
    if (newFilters.has(type)) {
      newFilters.delete(type);
    } else {
      newFilters.add(type);
    }
    setActiveFilters(newFilters);
  };

  const toggleSection = (section: string) => {
    const newSections = new Set(expandedSections);
    if (newSections.has(section)) {
      newSections.delete(section);
    } else {
      newSections.add(section);
    }
    setExpandedSections(newSections);
  };

  const getQualityColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'medium':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'low':
        return <AlertCircle className="h-4 w-4 text-blue-600" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'ambiguity':
        return 'bg-yellow-100 text-yellow-800';
      case 'completeness':
        return 'bg-orange-100 text-orange-800';
      case 'ethics':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <h3 className="font-semibold mb-4">Analysis Results</h3>
        
        {/* Quality Score */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Quality Score</span>
            <span className={`text-2xl font-bold ${getQualityColor(analysisResult?.quality_score || 0)}`}>
              {analysisResult?.quality_score || 0}%
            </span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden shadow-inner">
            <div
              className={`h-full rounded-full transition-all duration-1000 ease-out flex items-center justify-end pr-1 ${
                (analysisResult?.quality_score || 0) >= 80
                  ? 'bg-gradient-to-r from-green-400 to-green-600'
                  : (analysisResult?.quality_score || 0) >= 60
                  ? 'bg-gradient-to-r from-yellow-400 to-yellow-600'
                  : 'bg-gradient-to-r from-red-400 to-red-600'
              }`}
              style={{ width: `${analysisResult?.quality_score || 0}%` }}
            >
              <div className="h-1.5 w-1.5 bg-white/50 rounded-full" />
            </div>
          </div>
        </div>

        {/* Issue Summary */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="text-center p-3 bg-yellow-50 rounded-xl border border-yellow-100/50 shadow-sm transition-transform hover:scale-105">
            <div className="text-2xl font-bold text-yellow-700">
              {analysisResult?.ambiguity_issues?.length || 0}
            </div>
            <div className="text-xs font-medium text-yellow-600 uppercase tracking-wide opacity-80">Ambiguous</div>
          </div>
          <div className="text-center p-3 bg-orange-50 rounded-xl border border-orange-100/50 shadow-sm transition-transform hover:scale-105">
            <div className="text-2xl font-bold text-orange-700">
              {analysisResult?.completeness_issues?.length || 0}
            </div>
            <div className="text-xs font-medium text-orange-600 uppercase tracking-wide opacity-80">Incomplete</div>
          </div>
          <div className="text-center p-3 bg-red-50 rounded-xl border border-red-100/50 shadow-sm transition-transform hover:scale-105">
            <div className="text-2xl font-bold text-red-700">
              {analysisResult?.ethics_issues?.length || 0}
            </div>
            <div className="text-xs font-medium text-red-600 uppercase tracking-wide opacity-80">Ethics</div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2 flex-wrap">
          <Button
            size="sm"
            variant={activeFilters.has('ambiguity') ? 'default' : 'outline'}
            onClick={() => toggleFilter('ambiguity')}
            className="text-xs"
          >
            <Filter className="h-3 w-3 mr-1" />
            Ambiguity
          </Button>
          <Button
            size="sm"
            variant={activeFilters.has('completeness') ? 'default' : 'outline'}
            onClick={() => toggleFilter('completeness')}
            className="text-xs"
          >
            <Filter className="h-3 w-3 mr-1" />
            Completeness
          </Button>
          <Button
            size="sm"
            variant={activeFilters.has('ethics') ? 'default' : 'outline'}
            onClick={() => toggleFilter('ethics')}
            className="text-xs"
          >
            <Filter className="h-3 w-3 mr-1" />
            Ethics
          </Button>
        </div>
      </div>

      {/* Issues List */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {filteredIssues.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle2 className="h-12 w-12 mx-auto mb-2 text-green-500" />
              <p className="text-sm">No issues found!</p>
              <p className="text-xs mt-1">Your requirements look great.</p>
            </div>
          ) : (
            filteredIssues.map((issue) => (
              <div
                key={issue.id}
                className="border-0 shadow-sm rounded-xl p-4 bg-white hover:shadow-md transition-all cursor-pointer group relative overflow-hidden ring-1 ring-gray-100"
                onClick={() => onIssueClick?.(issue)}
              >
                <div className={`absolute top-0 left-0 w-1 h-full ${
                    issue.severity === 'high' ? 'bg-red-500' : 
                    issue.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                }`} />
                <div className="flex items-start gap-3 pl-2">
                  {getSeverityIcon(issue.severity)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge className={getTypeColor(issue.type)}>
                        {issue.type}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {issue.severity}
                      </Badge>
                      {issue.line && (
                        <span className="text-xs text-gray-500">
                          Line {issue.line}
                        </span>
                      )}
                    </div>
                    <p className="text-sm font-medium mb-2">{issue.message}</p>
                    {issue.location && (
                      <p className="text-xs text-gray-600 mb-2 font-mono bg-gray-100 p-1 rounded">
                        {issue.location}
                      </p>
                    )}
                    {issue.suggestions.length > 0 && (
                      <div className="mt-2">
                        <button
                          className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleSection(issue.id);
                          }}
                        >
                          {expandedSections.has(issue.id) ? (
                            <ChevronDown className="h-3 w-3" />
                          ) : (
                            <ChevronRight className="h-3 w-3" />
                          )}
                          {issue.suggestions.length} Suggestion{issue.suggestions.length > 1 ? 's' : ''}
                        </button>
                        {expandedSections.has(issue.id) && (
                          <ul className="mt-2 space-y-1 text-xs text-gray-700">
                            {issue.suggestions.map((suggestion, idx) => (
                              <li key={idx} className="flex items-start gap-2">
                                <span className="text-blue-600 mt-0.5">•</span>
                                <span>{suggestion}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      {analysisResult && (
        <div className="p-4 border-t bg-gray-50">
          <div className="text-xs text-gray-600">
            <p className="mb-1">
              <strong>Detected Entities:</strong>{' '}
              {analysisResult.parsed_entities?.actors?.length || 0} actors,{' '}
              {analysisResult.parsed_entities?.actions?.length || 0} actions,{' '}
              {analysisResult.parsed_entities?.entities?.length || 0} entities
            </p>
            <p className="text-xs text-gray-500">
              Powered by Groq (Ambiguity) • Gemini (Completeness) • AIF360 (Ethics)
            </p>
          </div>
        </div>
      )}
    </Card>
  );
}
