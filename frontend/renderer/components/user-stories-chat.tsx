import React from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { Sparkles, Send, Loader2 } from 'lucide-react';
import { TypewriterEffect } from './typewriter-effect';

interface UserStoriesChatProps {
  chatHistory: Array<{role: 'user' | 'ai', message: string}>;
  isRefining: boolean;
  prompt: string;
  setPrompt: (value: string) => void;
  onRefine: () => void;
  storiesCount: number;
  totalPoints: number;
  modifiedCount: number;
  selectedCount: number;
}

export function UserStoriesChat({
  chatHistory,
  isRefining,
  prompt,
  setPrompt,
  onRefine,
  storiesCount,
  totalPoints,
  modifiedCount,
  selectedCount
}: UserStoriesChatProps) {
  return (
    <div className="flex flex-col h-full bg-white border-l">
      <div className="p-4 border-b bg-white/50 backdrop-blur-sm sticky top-0 z-10">
        <h3 className="font-semibold flex items-center gap-2 text-gray-900">
          <Sparkles className="h-4 w-4 text-purple-600" />
          AI Assistant
        </h3>
        <p className="text-xs text-gray-500 mt-1">
            {selectedCount > 0 
                ? `Refining ${selectedCount} selected stor${selectedCount === 1 ? 'y' : 'ies'}` 
                : "Refining all stories"}
        </p>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {chatHistory.length === 0 && (
            <div className="text-center text-gray-500 mt-8">
              <Sparkles className="h-8 w-8 mx-auto mb-2 text-gray-300" />
              <p className="text-sm">Ask AI to refine your stories</p>
              <div className="text-xs mt-2 bg-gray-100 p-2 rounded">
                <p>Try:</p>
                <p>"Make acceptance criteria more specific"</p>
                <p>"Change priority of selected to High"</p>
              </div>
            </div>
          )}
          {chatHistory.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}
            >
              <div
                className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm shadow-sm ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-none'
                    : 'bg-white text-gray-800 border border-gray-100 rounded-bl-none shadow-sm'
                }`}
              >
                <div className="flex items-start gap-2">
                  {msg.role === 'ai' && (
                    <div className="bg-purple-100 p-1 rounded-full flex-shrink-0 mt-0.5">
                      <Sparkles className="h-3 w-3 text-purple-600" />
                    </div>
                  )}
                  {msg.role === 'ai' ? (
                    <TypewriterEffect text={msg.message} />
                  ) : (
                    <span className="break-words whitespace-pre-wrap leading-relaxed">{msg.message}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      <div className="p-4 border-t bg-white">
        <div className="flex items-center justify-between mb-3">
          {modifiedCount > 0 && (
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 shadow-sm">
              <Sparkles className="h-3 w-3 mr-1" />
              {modifiedCount} updated
            </Badge>
          )}
          <span className="text-xs text-gray-400 ml-auto font-medium">
            {storiesCount} stories • {totalPoints} pts
          </span>
        </div>
        
        <div className="flex gap-2 relative">
          <Input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && onRefine()}
            placeholder={selectedCount > 0 ? `Refine ${selectedCount} selected...` : "Ask AI to refine stories..."}
            disabled={isRefining}
            className="flex-1 pr-10 shadow-sm border-gray-200 focus:border-blue-500 transition-all font-light"
          />
          <Button
            onClick={onRefine}
            disabled={isRefining || !prompt.trim()}
            size="icon"
            className="absolute right-1 top-1 h-8 w-8 rounded-full shadow-sm"
          >
            {isRefining ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </div>
      </div>
    </div>
  );
}
