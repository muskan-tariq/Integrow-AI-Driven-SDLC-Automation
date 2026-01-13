'use client';

import React, { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, FolderGit2, CheckCircle2, XCircle } from 'lucide-react';
import { api, type CreateProjectInput } from '@/lib/api';

interface ProjectCreateModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onProjectCreated?: () => void;
}

type CreationStep = 'idle' | 'creating_repo' | 'initializing_git' | 'success' | 'error';

export function ProjectCreateModal({ open, onOpenChange, onProjectCreated }: ProjectCreateModalProps) {
  const [formData, setFormData] = useState<CreateProjectInput>({
    name: '',
    description: '',
    visibility: 'private',
    template: 'blank',
  });
  
  const [errors, setErrors] = useState<Partial<Record<keyof CreateProjectInput, string>>>({});
  const [creationStep, setCreationStep] = useState<CreationStep>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  // Validation
  const validateField = (field: keyof CreateProjectInput, value: string): string | null => {
    switch (field) {
      case 'name':
        if (!value.trim()) return 'Project name is required';
        if (!/^[a-zA-Z0-9-_]+$/.test(value)) {
          return 'Only alphanumeric characters, hyphens, and underscores allowed';
        }
        if (value.length < 3) return 'Name must be at least 3 characters';
        if (value.length > 50) return 'Name must be less than 50 characters';
        return null;
      
      case 'description':
        if (value && value.length > 500) return 'Description must be less than 500 characters';
        return null;
      
      default:
        return null;
    }
  };

  const handleFieldChange = (field: keyof CreateProjectInput, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    setErrors(prev => ({ ...prev, [field]: undefined }));
  };

  const handleFieldBlur = (field: keyof CreateProjectInput) => {
    const value = formData[field] as string;
    const error = validateField(field, value || '');
    if (error) {
      setErrors(prev => ({ ...prev, [field]: error }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof CreateProjectInput, string>> = {};
    
    // Validate name
    const nameError = validateField('name', formData.name);
    if (nameError) newErrors.name = nameError;
    
    // Validate description
    const descError = validateField('description', formData.description || '');
    if (descError) newErrors.description = descError;
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      setCreationStep('creating_repo');
      setErrorMessage('');
      
      // Create project via API
      const project = await api.createProject({
        name: formData.name,
        description: formData.description || undefined,
        visibility: formData.visibility,
        template: formData.template,
      });
      

      
      setCreationStep('initializing_git');
      
      // Simulate Git initialization (backend already did this)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setCreationStep('success');
      
      // Wait a moment to show success state
      setTimeout(() => {
        handleClose();
        onProjectCreated?.();
      }, 1500);
      
    } catch (error) {
      console.error('❌ Project creation failed:', error);
      setCreationStep('error');
      setErrorMessage(
        error instanceof Error 
          ? error.message 
          : 'Failed to create project. Please try again.'
      );
    }
  };

  const handleClose = () => {
    if (creationStep === 'creating_repo' || creationStep === 'initializing_git') {
      // Don't allow closing during creation
      return;
    }
    
    // Reset form
    setFormData({
      name: '',
      description: '',
      visibility: 'private',
      template: 'blank',
    });
    setErrors({});
    setCreationStep('idle');
    setErrorMessage('');
    onOpenChange(false);
  };

  const isFormValid = () => {
    // Check if name is valid (length and no validation errors)
    const nameError = validateField('name', formData.name);
    const descError = validateField('description', formData.description || '');
    
    return !nameError && !descError && formData.name.trim().length >= 3;
  };

  const isCreating = creationStep === 'creating_repo' || creationStep === 'initializing_git';

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FolderGit2 className="h-5 w-5" />
            Create New Project
          </DialogTitle>
          <DialogDescription>
            Create a new AI-powered development project with GitHub integration
          </DialogDescription>
        </DialogHeader>

        {creationStep === 'success' ? (
          <div className="flex flex-col items-center justify-center py-8">
            <CheckCircle2 className="h-16 w-16 text-green-500 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Project Created!</h3>
            <p className="text-muted-foreground text-center">
              Your project has been successfully created and initialized
            </p>
          </div>
        ) : creationStep === 'error' ? (
          <div className="flex flex-col items-center justify-center py-8">
            <XCircle className="h-16 w-16 text-red-500 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Creation Failed</h3>
            <p className="text-muted-foreground text-center mb-4">
              {errorMessage}
            </p>
            <Button onClick={() => setCreationStep('idle')} variant="outline">
              Try Again
            </Button>
          </div>
        ) : isCreating ? (
          <div className="flex flex-col items-center justify-center py-8">
            <Loader2 className="h-16 w-16 animate-spin text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              {creationStep === 'creating_repo' ? 'Creating GitHub Repository...' : 'Initializing Git...'}
            </h3>
            <p className="text-muted-foreground text-center">
              This may take a few moments
            </p>
            <div className="mt-4 space-y-2 w-full max-w-xs">
              <div className="flex items-center gap-2">
                <div className={`h-2 w-2 rounded-full ${
                  creationStep === 'creating_repo' || creationStep === 'initializing_git' 
                    ? 'bg-green-500' 
                    : 'bg-gray-300'
                }`} />
                <span className="text-sm">Creating repository</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`h-2 w-2 rounded-full ${
                  creationStep === 'initializing_git' 
                    ? 'bg-green-500' 
                    : 'bg-gray-300'
                }`} />
                <span className="text-sm">Initializing Git</span>
              </div>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="space-y-4 py-4">
              {/* Project Name */}
              <div className="space-y-2">
                <Label htmlFor="name">
                  Project Name <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="name"
                  placeholder="my-awesome-project"
                  value={formData.name}
                  onChange={(e) => handleFieldChange('name', e.target.value)}
                  onBlur={() => handleFieldBlur('name')}
                  className={errors.name ? 'border-red-500' : ''}
                  disabled={isCreating}
                />
                {errors.name && (
                  <p className="text-sm text-red-500">{errors.name}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Use lowercase letters, numbers, hyphens, and underscores
                </p>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="A brief description of your project..."
                  value={formData.description}
                  onChange={(e) => handleFieldChange('description', e.target.value)}
                  onBlur={() => handleFieldBlur('description')}
                  className={errors.description ? 'border-red-500' : ''}
                  disabled={isCreating}
                  rows={3}
                />
                {errors.description && (
                  <p className="text-sm text-red-500">{errors.description}</p>
                )}
              </div>

              {/* Visibility */}
              <div className="space-y-2">
                <Label htmlFor="visibility">
                  Visibility <span className="text-red-500">*</span>
                </Label>
                <Select
                  value={formData.visibility}
                  onValueChange={(value: 'public' | 'private') => 
                    handleFieldChange('visibility', value)
                  }
                  disabled={isCreating}
                >
                  <SelectTrigger id="visibility">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="private">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Private</span>
                        <span className="text-xs text-muted-foreground">
                          Only you can see this repository
                        </span>
                      </div>
                    </SelectItem>
                    <SelectItem value="public">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Public</span>
                        <span className="text-xs text-muted-foreground">
                          Anyone can see this repository
                        </span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Template */}
              <div className="space-y-2">
                <Label htmlFor="template">
                  Project Template <span className="text-red-500">*</span>
                </Label>
                <Select
                  value={formData.template}
                  onValueChange={(value) => handleFieldChange('template', value)}
                  disabled={isCreating}
                >
                  <SelectTrigger id="template">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="blank">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Blank</span>
                        <span className="text-xs text-muted-foreground">
                          Empty project with README
                        </span>
                      </div>
                    </SelectItem>
                    <SelectItem value="web-app">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Web Application</span>
                        <span className="text-xs text-muted-foreground">
                          React + TypeScript starter
                        </span>
                      </div>
                    </SelectItem>
                    <SelectItem value="mobile-app">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Mobile App</span>
                        <span className="text-xs text-muted-foreground">
                          React Native starter
                        </span>
                      </div>
                    </SelectItem>
                    <SelectItem value="api">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">API</span>
                        <span className="text-xs text-muted-foreground">
                          FastAPI or Express.js
                        </span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={isCreating}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={!isFormValid() || isCreating}
              >
                {isCreating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Project'
                )}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
