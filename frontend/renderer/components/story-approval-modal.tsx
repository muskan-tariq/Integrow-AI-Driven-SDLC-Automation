"use client"

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Loader2, CheckCircle, ExternalLink, FileText, GitCommit } from 'lucide-react'
import { UserStory } from '@/types'

interface ApprovalModalProps {
  stories: UserStory[]
  requirementId: string
  isOpen: boolean
  onClose: () => void
  onSuccess?: (commitUrl: string) => void
  token: string
}

interface ApprovalResult {
  commit_sha: string
  commit_url: string
  file_path: string
  stories_count: number
}

export function StoryApprovalModal({ stories, requirementId, isOpen, onClose, onSuccess, token }: ApprovalModalProps) {
  const [commitMessage, setCommitMessage] = useState(`Add ${stories.length} user stories for requirement`)
  const [branch, setBranch] = useState('main')
  const [isApproving, setIsApproving] = useState(false)
  const [approvalResult, setApprovalResult] = useState<ApprovalResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const totalStoryPoints = stories.reduce((sum, story) => sum + (story.story_points || 0), 0)
  const priorityCounts = {
    high: stories.filter(s => s.priority === 'high').length,
    medium: stories.filter(s => s.priority === 'medium').length,
    low: stories.filter(s => s.priority === 'low').length,
  }

  const handleApprove = async () => {
    setIsApproving(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/api/user-stories/approve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          requirement_id: requirementId,
          user_stories: stories,
          commit_message: commitMessage,
          branch
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Approval failed')
      }

      const result: ApprovalResult = await response.json()
      setApprovalResult(result)

      if (onSuccess) {
        onSuccess(result.commit_url)
      }

    } catch (err) {
      console.error('Error approving stories:', err)
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsApproving(false)
    }
  }

  const handleClose = () => {
    setApprovalResult(null)
    setError(null)
    onClose()
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'low': return 'text-green-600 bg-green-50 border-green-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  // Success View
  if (approvalResult) {
    return (
      <Dialog open={isOpen} onOpenChange={handleClose}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-blue-600">
              <CheckCircle className="h-5 w-5" />
              Stories Approved Successfully!
            </DialogTitle>
            <DialogDescription>
              {approvalResult.stories_count} user stories have been committed to GitHub
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-500">Commit SHA:</span>
                <code className="text-sm font-mono bg-white px-2 py-1 rounded border">
                  {approvalResult.commit_sha.substring(0, 7)}
                </code>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-500">File Path:</span>
                <code className="text-sm font-mono bg-white px-2 py-1 rounded border text-xs max-w-[300px] truncate" title={approvalResult.file_path}>
                  {approvalResult.file_path}
                </code>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-500">Branch:</span>
                <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                  {branch}
                </Badge>
              </div>
            </div>

            <div className="flex justify-center">
              <a
                href={approvalResult.commit_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 hover:underline"
              >
                <GitCommit className="h-4 w-4" />
                View Commit on GitHub
              </a>
            </div>
          </div>

          <DialogFooter>
            <Button onClick={handleClose} className="w-full sm:w-auto">
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
  }

  // Approval View
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Approve User Stories</DialogTitle>
          <p className="text-sm text-muted-foreground">
            Ready to commit {stories.length} user {stories.length === 1 ? 'story' : 'stories'} to GitHub
          </p>
        </DialogHeader>

        <div className="flex-1 overflow-hidden flex flex-col gap-4">
          {/* Summary Stats */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white p-3 rounded-lg text-center border">
              <div className="text-2xl font-bold text-gray-900">{stories.length}</div>
              <div className="text-xs text-gray-500">Stories</div>
            </div>
            <div className="bg-white p-3 rounded-lg text-center border">
              <div className="text-2xl font-bold text-gray-900">{totalStoryPoints}</div>
              <div className="text-xs text-gray-500">Story Points</div>
            </div>
            <div className="bg-red-50 p-3 rounded-lg text-center border border-red-100">
              <div className="text-2xl font-bold text-red-600">{priorityCounts.high}</div>
              <div className="text-xs text-red-600">High Priority</div>
            </div>
            <div className="bg-yellow-50 p-3 rounded-lg text-center border border-yellow-100">
              <div className="text-2xl font-bold text-yellow-600">{priorityCounts.medium}</div>
              <div className="text-xs text-yellow-600">Medium Priority</div>
            </div>
          </div>

          {/* Git Configuration */}
          <div className="space-y-3">
            <div>
              <Label htmlFor="commit-message">Commit Message</Label>
              <Input
                id="commit-message"
                value={commitMessage}
                onChange={(e) => setCommitMessage(e.target.value)}
                placeholder="Add user stories for..."
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="branch">Target Branch</Label>
              <select
                id="branch"
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                className="w-full mt-1 p-2 border rounded-md bg-white"
              >
                <option value="main">main</option>
                <option value="develop">develop</option>
                <option value="feature/user-stories">feature/user-stories</option>
              </select>
            </div>
          </div>

          {/* Stories List */}
          <div>
            <Label>Stories to be committed:</Label>
            <ScrollArea className="h-[200px] mt-2 border rounded-lg p-4 bg-gray-50/50">
              <div className="space-y-2">
                {stories.map((story, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3 bg-white rounded-lg border shadow-sm"
                  >
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium truncate text-gray-900">{story.title}</span>
                        <Badge
                          variant="outline"
                          className={`${getPriorityColor(story.priority)} text-xs`}
                        >
                          {story.priority}
                        </Badge>
                        {story.story_points && (
                          <Badge variant="secondary" className="text-xs bg-gray-100 text-gray-700">
                            {story.story_points} pts
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 line-clamp-2">
                        {story.story}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 p-3 rounded-lg border border-red-200">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isApproving}>
            Cancel
          </Button>
          <Button
            onClick={handleApprove}
            disabled={isApproving || !commitMessage.trim()}
          >
            {isApproving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Committing...
              </>
            ) : (
              <>
                <CheckCircle className="mr-2 h-4 w-4" />
                Approve & Push to GitHub
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
