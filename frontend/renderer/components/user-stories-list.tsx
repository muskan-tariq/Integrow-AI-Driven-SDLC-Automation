import React from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { Checkbox } from './ui/checkbox';
import {
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  TrendingUp,
  Copy,
  Sparkles,
  CheckCircle,
  X,
  Network,
  Trash2,
  Plus,
  MoreHorizontal
} from 'lucide-react';
import { UserStory } from '@/hooks/use-user-stories';
import { StoryApprovalModal } from './story-approval-modal';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface UserStoriesListProps {
  stories: UserStory[];
  expandedStories: Set<number>;
  modifiedStories: Set<number>;
  selectedStories: Set<number>;
  onToggleStory: (index: number) => void;
  onToggleSelection: (index: number) => void;
  onSelectAll: () => void;
  onAddStory: (story: UserStory) => void;
  onDeleteStory: (index: number) => void;
  onClose: () => void;
  requirementId: string;
  token: string;
}

export function UserStoriesList({
  stories,
  expandedStories,
  modifiedStories,
  selectedStories,
  onToggleStory,
  onToggleSelection,
  onSelectAll,
  onAddStory,
  onDeleteStory,
  onClose,
  requirementId,
  token
}: UserStoriesListProps) {
  const router = useRouter();
  const params = useParams();
  const [showApprovalModal, setShowApprovalModal] = React.useState(false);
  const [isApproved, setIsApproved] = React.useState(false);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const handleApprovalSuccess = () => {
    setIsApproved(true);
    setShowApprovalModal(false);
  };

  const handleViewUML = () => {
    const projectId = params.id as string;
    router.push(`/project/${projectId}/requirements/${requirementId}/uml`);
  };

  const handleManualAdd = () => {
    onAddStory({
        title: "New User Story",
        story: "As a user, I want to [feature], so that [benefit].",
        acceptance_criteria: ["Given [context], When [action], Then [outcome]"],
        priority: "medium",
        story_points: null,
        tags: ["manual"]
    });
  };

  const handleDeleteSelected = () => {
    // Delete in reverse order to preserve indices of earlier items
    const indicesToDelete = Array.from(selectedStories).sort((a, b) => b - a);
    indicesToDelete.forEach(index => onDeleteStory(index));
  };

  return (
    <div className="h-full flex flex-col bg-white rounded-lg border shadow-sm">
      {/* Header */}
      <div className="p-4 border-b flex items-center justify-between bg-gray-50/50">
        <div className="flex items-center gap-3">
          <Checkbox 
            checked={stories.length > 0 && selectedStories.size === stories.length}
            onCheckedChange={onSelectAll}
            aria-label="Select all"
          />
          <div>
            <h3 className="font-semibold text-lg flex items-center gap-2">
              Generated User Stories
              {selectedStories.size > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {selectedStories.size} Selected
                </Badge>
              )}
            </h3>
            <p className="text-sm text-gray-500">
              {stories.length} stories • Select to refine
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {selectedStories.size > 0 && (
             <Button 
               size="sm" 
               variant="destructive" 
               className="h-8"
               onClick={handleDeleteSelected}
             >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Selected
             </Button>
          )}
          
          <Button
            size="sm"
            variant="outline"
            className="h-8"
            onClick={handleManualAdd}
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Story
          </Button>

          <Button
            size="sm"
            onClick={() => setShowApprovalModal(true)}
            disabled={isApproved || stories.length === 0}
            className={`h-8 ${isApproved ? "bg-green-600 hover:bg-green-700 text-white" : ""}`}
          >
            {isApproved ? (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Approved
              </>
            ) : (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Approve {selectedStories.size > 0 ? 'Selected' : 'All'}
              </>
            )}
          </Button>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreHorizontal className="h-4 w-4" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleViewUML}>
                    <Network className="h-4 w-4 mr-2" />
                    View UML Diagram
                </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="ml-2 hover:bg-red-50 hover:text-red-600 h-8 w-8"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>
      </div>

      {/* Stories List */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4 max-w-4xl mx-auto">
          {stories.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
                <p>No user stories yet.</p>
                <Button variant="link" onClick={handleManualAdd}>Add one manually</Button>
            </div>
          ) : (
            stories.map((story, index) => {
                const isModified = modifiedStories.has(index);
                const isSelected = selectedStories.has(index);
                
                return (
                <div key={index} className="group relative flex items-start gap-3">
                    <div className="pt-4">
                        <Checkbox 
                            checked={isSelected}
                            onCheckedChange={() => onToggleSelection(index)}
                        />
                    </div>
                
                    <Card
                        className={`flex-1 transition-all duration-200 border-0 shadow-sm hover:shadow-md ${
                        isSelected ? 'bg-purple-50 ring-1 ring-purple-200' : 
                        isModified ? 'bg-green-50 ring-1 ring-green-200' : 'bg-white'
                        }`}
                    >
                        <div
                        className="p-5 cursor-pointer"
                        onClick={() => onToggleStory(index)}
                        >
                        <div className="flex items-start gap-3">
                            {expandedStories.has(index) ? (
                            <ChevronDown className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0 transition-transform duration-200" />
                            ) : (
                            <ChevronRight className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0 transition-transform duration-200" />
                            )}
                            <div className="flex-1 min-w-0">
                            <div className="flex items-start gap-2 mb-3 flex-wrap">
                                <h4 className="font-semibold text-base text-gray-900 leading-none mt-0.5">{story.title}</h4>
                                {isModified && (
                                <Badge className="bg-green-600 hover:bg-green-700 text-white text-xs border-0 px-2 py-0.5 animate-in fade-in zoom-in duration-300">
                                    <Sparkles className="h-3 w-3 mr-1" />
                                    Updated
                                </Badge>
                                )}
                                <Badge className={`${getPriorityColor(story.priority)} text-xs border-0 px-2 py-0.5`}>
                                {story.priority}
                                </Badge>
                                {story.story_points && (
                                <Badge variant="outline" className="text-xs bg-white text-gray-600 border-gray-200 px-2 py-0.5">
                                    <TrendingUp className="h-3 w-3 mr-1" />
                                    {story.story_points}sp
                                </Badge>
                                )}
                            </div>
                            <p className="text-sm text-gray-600 italic leading-relaxed font-serif bg-gray-50/50 p-3 rounded-md border border-gray-100">
                                "{story.story}"
                            </p>
                            </div>
                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all duration-200">
                                <Button
                                    size="icon"
                                    variant="ghost" 
                                    className="h-8 w-8 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onDeleteStory(index);
                                    }}
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                                <Button
                                size="icon"
                                variant="ghost"
                                className="h-8 w-8 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    copyToClipboard(`${story.title}\n\n${story.story}`);
                                }}
                                >
                                <Copy className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                        </div>

                        {expandedStories.has(index) && (
                        <div className="px-4 pb-4 border-t pt-4">
                            <div className="mb-3">
                            <h5 className="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-1">
                                <CheckCircle2 className="h-4 w-4" />
                                Acceptance Criteria
                            </h5>
                            <ul className="space-y-2">
                                {story.acceptance_criteria.map((criteria, idx) => (
                                <li key={idx} className="text-xs text-gray-600 flex items-start gap-2 bg-gray-50 p-2 rounded">
                                    <span className="text-blue-600 font-mono mt-0.5">{idx + 1}.</span>
                                    <span className="flex-1">{criteria}</span>
                                </li>
                                ))}
                            </ul>
                            </div>
                            {story.tags?.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                                {story.tags.map((tag, idx) => (
                                <Badge key={idx} variant="outline" className="text-xs">{tag}</Badge>
                                ))}
                            </div>
                            )}
                        </div>
                        )}
                    </Card>
                </div>
                );
            })
          )}
        </div>
      </ScrollArea>

      <StoryApprovalModal
        stories={selectedStories.size > 0 ? stories.filter((_, i) => selectedStories.has(i)) : stories}
        requirementId={requirementId}
        isOpen={showApprovalModal}
        onClose={() => setShowApprovalModal(false)}
        onSuccess={handleApprovalSuccess}
        token={token}
      />
    </div>
  );
}
