import { useState, useEffect } from 'react';

export interface UserStory {
  title: string;
  story: string;
  acceptance_criteria: string[];
  priority: 'high' | 'medium' | 'low';
  story_points: number | null;
  tags: string[];
}

interface UseUserStoriesProps {
  initialStories?: UserStory[];
  getAuthToken?: () => string | null;
}

export function useUserStories({ initialStories = [], getAuthToken }: UseUserStoriesProps) {
  const [currentStories, setCurrentStories] = useState<UserStory[]>(initialStories);
  const [expandedStories, setExpandedStories] = useState<Set<number>>(new Set());
  const [modifiedStories, setModifiedStories] = useState<Set<number>>(new Set());
  const [selectedStories, setSelectedStories] = useState<Set<number>>(new Set());
  const [chatHistory, setChatHistory] = useState<Array<{role: 'user' | 'ai', message: string}>>([]);
  const [isRefining, setIsRefining] = useState(false);
  const [refinementPrompt, setRefinementPrompt] = useState('');

  // Update stories when initialStories change
  useEffect(() => {
    if (initialStories.length > 0) {
      setCurrentStories(initialStories);
      setExpandedStories(new Set(initialStories.map((_, idx) => idx)));
      setModifiedStories(new Set());
      setSelectedStories(new Set());
    }
  }, [initialStories]);

  const toggleStory = (index: number) => {
    const newExpanded = new Set(expandedStories);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedStories(newExpanded);
  };

  const toggleSelection = (index: number) => {
    const newSelected = new Set(selectedStories);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedStories(newSelected);
  };

  const selectAll = () => {
    if (selectedStories.size === currentStories.length) {
      setSelectedStories(new Set());
    } else {
      setSelectedStories(new Set(currentStories.map((_, idx) => idx)));
    }
  };

  const addStory = (story: UserStory) => {
    setCurrentStories(prev => [...prev, story]);
    // Optionally auto-select new story so user can refine it immediately
    setSelectedStories(prev => {
        const newSet = new Set(prev);
        newSet.add(currentStories.length); 
        return newSet;
    });
    // Mark as modified so UI shows it as new/changed if needed
    setModifiedStories(prev => {
        const newSet = new Set(prev);
        newSet.add(currentStories.length);
        return newSet;
    });
  };

  const updateStory = (index: number, updatedStory: UserStory) => {
    const newStories = [...currentStories];
    newStories[index] = updatedStory;
    setCurrentStories(newStories);
    setModifiedStories(prev => {
        const newSet = new Set(prev);
        newSet.add(index);
        return newSet;
    });
  };

  const deleteStory = (index: number) => {
    // Remove story at index
    const newStories = currentStories.filter((_, i) => i !== index);
    setCurrentStories(newStories);
    
    // We need to shift indices for sets greater than index
    const shiftSet = (originalSet: Set<number>) => {
        const newSet = new Set<number>();
        originalSet.forEach(i => {
            if (i < index) newSet.add(i);
            if (i > index) newSet.add(i - 1);
        });
        return newSet;
    };

    setSelectedStories(shiftSet(selectedStories));
    setExpandedStories(shiftSet(expandedStories));
    setModifiedStories(shiftSet(modifiedStories));
  };

  const handleRefineStories = async () => {
    if (!refinementPrompt.trim() || currentStories.length === 0) return;

    // Determine target stories (selected or all)
    const targetIndices = selectedStories.size > 0 
      ? Array.from(selectedStories).sort((a, b) => a - b)
      : currentStories.map((_, i) => i);
    
    const targetStories = targetIndices.map(i => currentStories[i]);

    setIsRefining(true);
    const scopeMsg = selectedStories.size > 0 
      ? `(Refining ${selectedStories.size} selected stories)` 
      : '(Refining all stories)';
    
    setChatHistory(prev => [...prev, { role: 'user', message: `${refinementPrompt} \n\n${scopeMsg}` }]);

    try {
      const token = getAuthToken?.();
      if (!token) throw new Error('Authentication required');

      const response = await fetch('/api/user-stories/refine', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          story_id: `batch_${Date.now()}`,
          stories: targetStories,
          refinement_request: refinementPrompt,
          conversation_history: chatHistory.map(h => ({ role: h.role, content: h.message }))
        })
      });

      if (!response.ok) throw new Error('Refinement failed');

      const result = await response.json();
      
      setChatHistory(prev => [...prev, { 
        role: 'ai', 
        message: result.explanation || `Updated ${result.refined_stories.length} stories successfully` 
      }]);

      // Merge refined stories back into currentStories
      const newStories = [...currentStories];
      const refinedList = result.refined_stories;
      const newModified = new Set(modifiedStories);

      // We assume strict order matching for now (agent does this)
      targetIndices.forEach((storyIndex, idx) => {
        if (refinedList[idx]) {
          newStories[storyIndex] = refinedList[idx];
          newModified.add(storyIndex);
        }
      });
      
      setCurrentStories(newStories);
      setModifiedStories(newModified);
      setRefinementPrompt('');

    } catch (error) {
      console.error('Error refining stories:', error);
      setChatHistory(prev => [...prev, { 
        role: 'ai', 
        message: 'Sorry, I encountered an error during refinement. Please try again.' 
      }]);
    } finally {
      setIsRefining(false);
    }
  };

  return {
    currentStories,
    setCurrentStories,
    expandedStories,
    toggleStory,
    modifiedStories,
    selectedStories,
    toggleSelection,
    selectAll,
    addStory,
    updateStory,
    deleteStory,
    chatHistory,
    isRefining,
    refinementPrompt,
    setRefinementPrompt,
    handleRefineStories
  };
}
