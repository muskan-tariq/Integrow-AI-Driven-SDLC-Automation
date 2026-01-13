'use client';

import React, { useState } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    Search,
    Folder,
    Plus,
    ChevronRight,
    Loader2,
    LucideIcon
} from 'lucide-react';
import { Project } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface ActionSelectionModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    title: string;
    description: string;
    icon: LucideIcon;
    targetRoute: string; // e.g., 'debt', 'requirements'
    projects: Project[];
    onNewProject: () => void;
}

export function ActionSelectionModal({
    open,
    onOpenChange,
    title,
    description,
    icon: Icon,
    targetRoute,
    projects,
    onNewProject,
}: ActionSelectionModalProps) {
    const router = useRouter();
    const [searchQuery, setSearchQuery] = useState('');

    const filteredProjects = projects.filter((p) =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const handleSelectProject = (projectId: string) => {
        router.push(`/project/${projectId}/${targetRoute}?autoStart=true`);
        onOpenChange(false);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl max-h-[85vh] flex flex-col p-0 overflow-hidden border-primary/20">
                <div className="p-6 pb-4">
                    <DialogHeader>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center">
                                <Icon className="h-6 w-6 text-primary" />
                            </div>
                            <DialogTitle className="text-xl">{title}</DialogTitle>
                        </div>
                        <DialogDescription>{description}</DialogDescription>
                    </DialogHeader>

                    <div className="mt-6 flex flex-col md:flex-row gap-4 items-center justify-between">
                        <div className="relative w-full md:max-w-xs">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Search projects..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-9 bg-muted/50 border-transparent focus:bg-background transition-all"
                            />
                        </div>
                        <Button onClick={onNewProject} className="w-full md:w-auto gap-2">
                            <Plus className="h-4 w-4" />
                            New Project & {title.split(' ').pop()}
                        </Button>
                    </div>
                </div>

                <ScrollArea className="flex-1 px-6 pb-6">
                    <div className="space-y-2">
                        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                            Select Existing Project
                        </h3>
                        {filteredProjects.length === 0 ? (
                            <div className="text-center py-10 bg-muted/20 rounded-xl border border-dashed">
                                <Folder className="h-10 w-10 mx-auto text-muted-foreground/30 mb-2" />
                                <p className="text-sm text-muted-foreground">No projects found</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {filteredProjects.map((project) => (
                                    <div
                                        key={project.id}
                                        onClick={() => handleSelectProject(project.id)}
                                        className="group flex items-center justify-between p-4 rounded-xl border border-transparent bg-muted/30 hover:bg-primary/5 hover:border-primary/20 cursor-pointer transition-all"
                                    >
                                        <div className="flex items-center gap-3 min-w-0">
                                            <div className="h-10 w-10 rounded-lg bg-background border flex items-center justify-center shrink-0">
                                                <Folder className="h-5 w-5 text-primary/60 group-hover:text-primary transition-colors" />
                                            </div>
                                            <div className="min-w-0">
                                                <p className="font-medium text-sm truncate">{project.name}</p>
                                                <p className="text-[10px] text-muted-foreground truncate uppercase">
                                                    {project.github_repo_url.split('/').pop()}
                                                </p>
                                            </div>
                                        </div>
                                        <ChevronRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all" />
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </ScrollArea>
            </DialogContent>
        </Dialog>
    );
}
