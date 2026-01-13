'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, BookOpen, Clock, ArrowRight, ChevronRight, ExternalLink } from 'lucide-react';

interface UserStoryWithContext {
  id: string;
  requirement_id: string;
  title: string;
  story: string;
  acceptance_criteria: string[];
  priority: string;
  story_points: number | null;
  tags: string[];
  created_at: string | null;
}

export default function UserStoriesPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [stories, setStories] = useState<UserStoryWithContext[]>([]);
  const [expandedStories, setExpandedStories] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [token, setToken] = useState('');

  useEffect(() => {
    initializeSession();
  }, []);

  useEffect(() => {
    if (token) {
      fetchStories();
    }
  }, [token]);

  const initializeSession = async () => {
    try {
      const authData = await window.electron.getAuth();
      if (authData?.accessToken) {
        setToken(authData.accessToken);
      } else {
        router.push('/');
      }
    } catch (error) {
      console.error('Auth error:', error);
      router.push('/');
    }
  };

  const fetchStories = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/user-stories/project/${projectId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStories(data);
      }
    } catch (error) {
      console.error('Error fetching stories:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const toggleStory = (storyId: string) => {
    const newExpanded = new Set(expandedStories);
    if (newExpanded.has(storyId)) {
      newExpanded.delete(storyId);
    } else {
      newExpanded.add(storyId);
    }
    setExpandedStories(newExpanded);
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 text-gray-900">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4 shrink-0">
        <div className="max-w-5xl mx-auto w-full">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">User Stories</h1>
          <p className="text-gray-500 mt-1">
            Aggregated view of all user stories across project requirements.
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto w-full">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : stories.length === 0 ? (
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  No User Stories Yet
                </CardTitle>
                <CardDescription>
                  User stories are generated from requirements
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Create a requirement and analyze it to generate user stories.
                </p>
                <Button onClick={() => router.push(`/project/${projectId}/requirements`)}>
                  Go to Requirements <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4 pb-10">
              {stories.map((story) => (
                <Card
                  key={story.id}
                  className="hover:shadow-lg transition-all duration-200 cursor-pointer border-0 shadow-sm group bg-white/50 hover:bg-white"
                  onClick={() => toggleStory(story.id)}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-start gap-4">
                      {expandedStories.has(story.id) ? (
                        <ChevronRight className="h-5 w-5 text-gray-400 mt-1 transform rotate-90 transition-transform duration-200" />
                      ) : (
                        <ChevronRight className="h-5 w-5 text-gray-400 mt-1 transition-transform duration-200" />
                      )}
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <CardTitle className="text-lg font-semibold text-gray-900">{story.title}</CardTitle>
                          <div className="flex items-center gap-2">
                            <Badge className={`${getPriorityColor(story.priority)} text-white border-0 px-2.5 py-0.5`}>
                              {story.priority}
                            </Badge>
                            {story.story_points && (
                              <Badge variant="outline" className="bg-white text-gray-600 border-gray-200">
                                {story.story_points} pts
                              </Badge>
                            )}
                          </div>
                        </div>
                        <CardDescription className="mt-1 flex items-center gap-2">
                          <span className="bg-gray-100 px-2 py-0.5 rounded text-xs font-mono text-gray-600">
                            REQ-{story.requirement_id.substring(0, 8)}
                          </span>
                          <span className="text-xs text-gray-400">• Created {new Date(story.created_at || '').toLocaleDateString()}</span>
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pl-12">
                    <p className="text-sm text-gray-600 mb-4 italic leading-relaxed font-serif bg-gray-50/50 p-4 rounded-md border border-gray-100">
                      "{story.story}"
                    </p>

                    {story.tags.length > 0 && (
                      <div className="flex gap-2 flex-wrap mb-4">
                        {story.tags.map((tag, i) => (
                          <Badge key={i} variant="secondary" className="text-xs bg-blue-50 text-blue-700 hover:bg-blue-100 border-blue-100">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}

                    <div className={`grid transition-[grid-template-rows] duration-200 ease-out ${expandedStories.has(story.id) ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
                      }`}>
                      <div className="overflow-hidden">
                        <div className="border-t pt-4">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">Acceptance Criteria</h4>
                          <ul className="space-y-2">
                            {story.acceptance_criteria.map((criteria, idx) => (
                              <li key={idx} className="text-sm text-gray-700 flex items-start gap-3 bg-white border border-gray-100 p-3 rounded-md shadow-sm">
                                <span className="text-blue-500 font-bold font-mono mt-0.5">{idx + 1}.</span>
                                <span className="leading-relaxed">{criteria}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="mt-4 pt-3 flex justify-end">
                          <Button
                            variant="default"
                            size="sm"
                            className="text-xs bg-gray-900 text-white hover:bg-gray-800 shadow-sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              router.push(`/project/${projectId}/requirements?selectRequirement=${story.requirement_id}`);
                            }}
                          >
                            <ExternalLink className="h-3 w-3 mr-2" />
                            View Context in Editor
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
