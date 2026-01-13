'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
    Loader2,
    Search,
    FileCheck,
    AlertCircle,
    CheckCircle2,
    ShieldAlert,
    Zap,
    Layout,
    ArrowRight,
    ClipboardCheck,
    Plus,
    Trash2
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Progress } from '../../../../components/ui/progress';
import { api } from '@/lib/api';
import { codeReviewApi, ReviewSession, CodeReviewReport } from '@/lib/api/code-review';
// removing date-fns import
import { FileReviewModal } from '@/components/code-review/FileReviewModal';
import { ReviewDetailModal } from '@/components/code-review/ReviewDetailModal';

export default function CodeReviewPage() {
    const params = useParams();
    const router = useRouter();
    const searchParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
    const projectId = params.id as string;

    const [sessions, setSessions] = useState<ReviewSession[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [token, setToken] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedSession, setSelectedSession] = useState<ReviewSession | null>(null);
    const [isDetailsLoading, setIsDetailsLoading] = useState(false);

    useEffect(() => {
        initializeSession();
    }, []);

    useEffect(() => {
        if (token) {
            fetchSessions();

            // Handle autoStart
            if (searchParams?.get('autoStart') === 'true') {
                setIsModalOpen(true);
                // Clean up URL
                const newUrl = window.location.pathname;
                window.history.replaceState({}, '', newUrl);
            }
        }
    }, [token]);

    const initializeSession = async () => {
        try {
            const authData = await window.electron.getAuth();
            if (authData?.accessToken) {
                setToken(authData.accessToken);
                api.setToken(authData.accessToken);
            } else {
                router.push('/');
            }
        } catch (error) {
            console.error('Auth error:', error);
            router.push('/');
        }
    };

    const fetchSessions = async () => {
        setIsLoading(true);
        try {
            const data = await codeReviewApi.getProjectSessions(projectId, token);
            setSessions(data || []);
        } catch (error) {
            console.error('Error fetching sessions:', error);
            setSessions([]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSessionSelect = async (session: ReviewSession) => {
        setIsDetailsLoading(true);
        try {
            const fullSession = await codeReviewApi.getSessionDetails(session.id, token);
            setSelectedSession(fullSession);
        } catch (error) {
            console.error('Error fetching session details:', error);
            setSelectedSession(session);
        } finally {
            setIsDetailsLoading(false);
        }
    };

    const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
        e.stopPropagation();
        if (!confirm('Are you sure you want to delete this review session? All associated reports will be removed.')) return;

        try {
            await codeReviewApi.deleteReviewSession(sessionId, token);
            setSessions(sessions.filter(s => s.id !== sessionId));
        } catch (error) {
            console.error('Error deleting session:', error);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 90) return 'text-green-500';
        if (score >= 70) return 'text-yellow-500';
        return 'text-red-500';
    };

    const getSeverityBadge = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'critical':
                return <Badge className="bg-red-600 text-white border-none">Critical</Badge>;
            case 'high':
                return <Badge className="bg-red-400 text-white border-none">High</Badge>;
            case 'medium':
                return <Badge className="bg-yellow-500 text-white border-none">Medium</Badge>;
            case 'low':
                return <Badge className="bg-blue-400 text-white border-none">Low</Badge>;
            default:
                return <Badge variant="outline">{severity}</Badge>;
        }
    };

    return (
        <div className="flex flex-col h-full bg-slate-50 text-slate-900">
            {/* Header */}
            <div className="bg-white border-b px-8 py-6 sticky top-0 z-10 shadow-sm">
                <div className="max-w-6xl mx-auto w-full flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 flex items-center gap-3">
                            <ClipboardCheck className="h-8 w-8 text-indigo-600" />
                            Code Review Assistant
                        </h1>
                        <p className="text-slate-500 mt-1 text-lg">
                            AI-powered analysis for security, performance, and best practices.
                        </p>
                    </div>
                    <Button
                        className="bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-200"
                        onClick={() => setIsModalOpen(true)}
                    >
                        <Plus className="mr-2 h-4 w-4" /> New Review
                    </Button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-y-auto p-8">
                <div className="max-w-6xl mx-auto w-full space-y-8">

                    {/* Quick Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <Card className="border-none shadow-sm bg-indigo-50/50">
                            <CardContent className="pt-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-indigo-600 uppercase tracking-wider">Total Sessions</p>
                                        <p className="text-4xl font-bold text-slate-900 mt-1">{sessions.length}</p>
                                    </div>
                                    <div className="h-12 w-12 bg-white rounded-full flex items-center justify-center shadow-sm">
                                        <FileCheck className="h-6 w-6 text-indigo-600" />
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="border-none shadow-sm bg-emerald-50/50">
                            <CardContent className="pt-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-emerald-600 uppercase tracking-wider">Avg. Quality Score</p>
                                        <p className="text-4xl font-bold text-slate-900 mt-1">
                                            {sessions.length > 0 ? Math.round(sessions.reduce((acc, s) => acc + s.score, 0) / sessions.length) : 'N/A'}
                                        </p>
                                    </div>
                                    <div className="h-12 w-12 bg-white rounded-full flex items-center justify-center shadow-sm">
                                        <Zap className="h-6 w-6 text-emerald-600" />
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="border-none shadow-sm bg-rose-50/50">
                            <CardContent className="pt-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-rose-600 uppercase tracking-wider">Historical Versions</p>
                                        <p className="text-4xl font-bold text-slate-900 mt-1">
                                            V{sessions.length > 0 ? sessions[0].version : 0}
                                        </p>
                                    </div>
                                    <div className="h-12 w-12 bg-white rounded-full flex items-center justify-center shadow-sm">
                                        <ShieldAlert className="h-6 w-6 text-rose-600" />
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Reviews List */}
                        <div className="lg:col-span-2 space-y-4">
                            <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                                <Layout className="h-5 w-5 text-indigo-500" /> Review Sessions
                            </h2>

                            {isLoading ? (
                                <div className="flex items-center justify-center h-64 bg-white rounded-xl shadow-sm">
                                    <Loader2 className="h-10 w-10 animate-spin text-indigo-400" />
                                </div>
                            ) : sessions.length === 0 ? (
                                <Card className="border-dashed border-2 bg-transparent">
                                    <CardContent className="flex flex-col items-center justify-center p-12 text-center">
                                        <div className="h-20 w-20 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                                            <Search className="h-10 w-10 text-slate-300" />
                                        </div>
                                        <h3 className="text-lg font-semibold text-slate-700">No review sessions yet</h3>
                                        <p className="text-slate-500 max-w-sm mt-2">
                                            Start by analyzing files to get insights on your project quality.
                                        </p>
                                    </CardContent>
                                </Card>
                            ) : (
                                <div className="space-y-4">
                                    {sessions.map((session) => (
                                        <Card
                                            key={session.id}
                                            className="group transition-all duration-300 hover:shadow-md border-none shadow-sm hover:translate-x-1 cursor-pointer overflow-hidden"
                                            onClick={() => handleSessionSelect(session)}
                                        >
                                            <div className="flex items-stretch h-32">
                                                <div className={`w-2 ${session.score >= 80 ? 'bg-emerald-500' : session.score >= 60 ? 'bg-yellow-500' : 'bg-rose-500'}`} />
                                                <CardContent className="flex-1 p-6 flex items-center justify-between">
                                                    <div className="flex flex-col min-w-0">
                                                        <h3 className="font-bold text-lg text-slate-900 truncate flex items-center gap-2">
                                                            Review Session V{session.version}
                                                            {session.score >= 90 && <CheckCircle2 className="h-4 w-4 text-emerald-500" />}
                                                        </h3>
                                                        <p className="text-slate-500 text-sm mt-1 line-clamp-1 italic">
                                                            "{session.summary}"
                                                        </p>
                                                        <div className="flex items-center gap-4 mt-3">
                                                            <span className="text-xs font-mono text-slate-400">
                                                                {new Date(session.created_at).toLocaleString()}
                                                            </span>
                                                            <Badge variant="secondary" className="bg-slate-100 text-slate-600 border-none text-[10px]">
                                                                {/* @ts-ignore */}
                                                                {session.code_reviews?.length || 0} Files
                                                            </Badge>
                                                        </div>
                                                    </div>

                                                    <div className="flex items-center gap-4 pl-6 border-l">
                                                        <div className="text-center min-w-[60px]">
                                                            <p className="text-xs font-semibold text-slate-400 uppercase tracking-tighter">Batch Score</p>
                                                            <p className={`text-3xl font-black ${getScoreColor(session.score)}`}>{session.score}</p>
                                                        </div>
                                                        <div className="flex flex-col gap-1">
                                                            <Button
                                                                variant="ghost"
                                                                size="icon"
                                                                className="h-8 w-8 text-slate-400 hover:text-rose-600 hover:bg-rose-50"
                                                                onClick={(e) => handleDeleteSession(e, session.id)}
                                                            >
                                                                <Trash2 className="h-4 w-4" />
                                                            </Button>
                                                            <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 group-hover:text-indigo-600">
                                                                <ArrowRight className="h-4 w-4" />
                                                            </Button>
                                                        </div>
                                                    </div>
                                                </CardContent>
                                            </div>
                                        </Card>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Sidebar info / Legend */}
                        <div className="space-y-6">
                            <Card className="border-none shadow-sm overflow-hidden">
                                <CardHeader className="bg-indigo-600 text-white pb-6">
                                    <CardTitle className="text-lg">AI Analysis Model</CardTitle>
                                    <CardDescription className="text-indigo-100">
                                        We use multi-agent LLMs to scan your code across 4 dimensions.
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="pt-6 space-y-6">
                                    <div className="space-y-2">
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="font-medium">Security</span>
                                            <span className="text-slate-400">OWASP Top 10</span>
                                        </div>
                                        <Progress value={95} className="h-1.5" />
                                    </div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="font-medium">Performance</span>
                                            <span className="text-slate-400">Space/Time O(n)</span>
                                        </div>
                                        <Progress value={80} className="h-1.5" />
                                    </div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="font-medium">Style</span>
                                            <span className="text-slate-400">PEP8 / Airbnb</span>
                                        </div>
                                        <Progress value={60} className="h-1.5" />
                                    </div>

                                    <div className="pt-4 border-t">
                                        <h4 className="text-sm font-bold text-slate-800 mb-3">Severity Key</h4>
                                        <div className="flex flex-wrap gap-2">
                                            <Badge className="bg-red-600">Critical</Badge>
                                            <Badge className="bg-red-400">High</Badge>
                                            <Badge className="bg-yellow-500">Medium</Badge>
                                            <Badge className="bg-blue-400">Low</Badge>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </div>
            </div>
            <FileReviewModal
                open={isModalOpen}
                onOpenChange={setIsModalOpen}
                projectId={projectId}
                token={token}
                onReviewComplete={fetchSessions}
            />
            <ReviewDetailModal
                session={selectedSession}
                open={!!selectedSession}
                onOpenChange={(open) => !open && setSelectedSession(null)}
            />
        </div>
    );
}
