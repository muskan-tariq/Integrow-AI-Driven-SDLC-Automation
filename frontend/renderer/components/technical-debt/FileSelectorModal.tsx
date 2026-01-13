'use client';

import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Search, FileCode, Folder } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ProjectFile {
    path: string;
    name: string;
    extension: string;
    size: number;
}

interface FileSelectorModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    projectId: string;
    token: string;
    onSelect: (files: string[]) => void;
}

export function FileSelectorModal({ open, onOpenChange, projectId, token, onSelect }: FileSelectorModalProps) {
    const [files, setFiles] = useState<ProjectFile[]>([]);
    const [filteredFiles, setFilteredFiles] = useState<ProjectFile[]>([]);
    const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
    const [searchQuery, setSearchQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (open && projectId && token) {
            fetchFiles();
        }
    }, [open, projectId, token]);

    useEffect(() => {
        if (searchQuery) {
            const filtered = files.filter(f =>
                f.path.toLowerCase().includes(searchQuery.toLowerCase()) ||
                f.name.toLowerCase().includes(searchQuery.toLowerCase())
            );
            setFilteredFiles(filtered);
        } else {
            setFilteredFiles(files);
        }
    }, [searchQuery, files]);

    const fetchFiles = async () => {
        setIsLoading(true);
        try {
            const response = await axios.get(
                `${API_URL}/api/debt/project/${projectId}/files`,
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setFiles(response.data.files || []);
            setFilteredFiles(response.data.files || []);
        } catch (error) {
            console.error('Error fetching files:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const toggleFile = (path: string) => {
        const newSelected = new Set(selectedFiles);
        if (newSelected.has(path)) {
            newSelected.delete(path);
        } else {
            newSelected.add(path);
        }
        setSelectedFiles(newSelected);
    };

    const handleConfirm = () => {
        onSelect(Array.from(selectedFiles));
        onOpenChange(false);
        setSelectedFiles(new Set());
        setSearchQuery('');
    };

    const groupFilesByDirectory = (files: ProjectFile[]) => {
        const grouped: { [key: string]: ProjectFile[] } = {};

        files.forEach(file => {
            const dir = file.path.includes('/') ? file.path.substring(0, file.path.lastIndexOf('/')) : 'root';
            if (!grouped[dir]) {
                grouped[dir] = [];
            }
            grouped[dir].push(file);
        });

        return grouped;
    };

    const groupedFiles = groupFilesByDirectory(filteredFiles);

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-3xl max-h-[80vh] flex flex-col">
                <DialogHeader>
                    <DialogTitle>Select Files for Analysis</DialogTitle>
                </DialogHeader>

                <div className="space-y-4 flex-1 flex flex-col min-h-0">
                    {/* Search */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                        <Input
                            placeholder="Search files..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-10"
                        />
                    </div>

                    {/* File List */}
                    <ScrollArea className="flex-1 border rounded-lg">
                        {isLoading ? (
                            <div className="p-8 text-center text-slate-500">Loading files...</div>
                        ) : filteredFiles.length === 0 ? (
                            <div className="p-8 text-center text-slate-500">No files found</div>
                        ) : (
                            <div className="p-4 space-y-4">
                                {Object.entries(groupedFiles).map(([dir, dirFiles]) => (
                                    <div key={dir} className="space-y-2">
                                        <div className="flex items-center gap-2 text-sm font-semibold text-slate-700 sticky top-0 bg-white py-1">
                                            <Folder className="h-4 w-4 text-slate-400" />
                                            {dir}
                                        </div>
                                        <div className="ml-6 space-y-1">
                                            {dirFiles.map((file) => (
                                                <div
                                                    key={file.path}
                                                    className="flex items-center gap-2 p-2 hover:bg-slate-50 rounded cursor-pointer"
                                                    onClick={() => toggleFile(file.path)}
                                                >
                                                    <Checkbox
                                                        checked={selectedFiles.has(file.path)}
                                                        onCheckedChange={() => toggleFile(file.path)}
                                                        onClick={(e) => e.stopPropagation()}
                                                    />
                                                    <FileCode className="h-4 w-4 text-slate-400" />
                                                    <span className="text-sm flex-1">{file.name}</span>
                                                    <span className="text-xs text-slate-400">
                                                        {(file.size / 1024).toFixed(1)} KB
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </ScrollArea>

                    {/* Selection Summary */}
                    <div className="text-sm text-slate-600">
                        {selectedFiles.size} file(s) selected
                    </div>
                </div>

                <div className="flex justify-end gap-2 pt-4 border-t">
                    <Button variant="outline" onClick={() => onOpenChange(false)}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleConfirm}
                        disabled={selectedFiles.size === 0}
                        className="bg-amber-600 hover:bg-amber-700"
                    >
                        Select {selectedFiles.size} File(s)
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}
