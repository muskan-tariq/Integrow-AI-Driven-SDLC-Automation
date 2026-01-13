'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
    Loader2,
    AlertTriangle,
    TrendingUp,
    TrendingDown,
    Minus,
    Plus,
    Github,
    Trash2,
    CheckCircle2
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { api } from '@/lib/api';
import { technicalDebtApi, DebtSession } from '@/lib/api/technical-debt';
import { DebtAnalysisModal, DebtDetailModal } from '@/components/technical-debt';

export default function TechnicalDebtPage() {
    const params = useParams();
    const router = useRouter();
    const searchParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
    const projectId = params.id as string;

    const [sessions, setSessions] = useState<DebtSession[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [token, setToken] = useState('');
    const [isAnalysisModalOpen, setIsAnalysisModalOpen] = useState(false);
    const [selectedSession, setSelectedSession] = useState<DebtSession | null>(null);

    useEffect(() => {
        initializeSession();
    }, []);

    useEffect(() => {
        if (token) {
            fetchSessions();

            // Handle autoStart
            if (searchParams?.get('autoStart') === 'true') {
                setIsAnalysisModalOpen(true);
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
            const data = await technicalDebtApi.getProjectSessions(projectId, token);
            setSessions(data || []);
        } catch (error) {
            console.error('Error fetching sessions:', error);
            setSessions([]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
        e.stopPropagation();
        if (!confirm('Are you sure you want to delete this debt analysis session?')) return;

        try {
            await technicalDebtApi.deleteSession(sessionId, token);
            setSessions(sessions.filter(s => s.id !== sessionId));
        } catch (error) {
            console.error('Error deleting session:', error);
        }
    };

    const handleSessionSelect = async (session: DebtSession) => {
        try {
            const fullSession = await technicalDebtApi.getSessionDetails(session.id, token);
            setSelectedSession(fullSession);
        } catch (error) {
            console.error('Error fetching session details:', error);
            setSelectedSession(session);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-emerald-500';
        if (score >= 60) return 'text-yellow-500';
        return 'text-rose-500';
    };

    const getScoreTrend = (score: number) => {
        if (score >= 80) return <TrendingUp className="h-4 w-4 text-emerald-500" />;
        if (score >= 60) return <Minus className="h-4 w-4 text-yellow-500" />;
        return <TrendingDown className="h-4 w-4 text-rose-500" />;
    };

    const latestSession = sessions[0];

    return (
        <div className="flex flex-col h-full bg-slate-50 text-slate-900">
            {/* Header */}
            <div className="bg-white border-b px-8 py-6 sticky top-0 z-10 shadow-sm">
                <div className="max-w-6xl mx-auto w-full flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 flex items-center gap-3">
                            <AlertTriangle className="h-8 w-8 text-amber-600" />
                            Technical Debt Analyzer
                        </h1>
                        <p className="text-slate-500 mt-1 text-lg">
                            Identify complexity, duplication, and architectural issues
                        </p>
                    </div>
                    <Button
                        className="bg-amber-600 hover:bg-amber-700 shadow-lg shadow-amber-200"
                        onClick={() => setIsAnalysisModalOpen(true)}
                    >
                        <Plus className="mr-2 h-4 w-4" /> Analyze Project
                    </Button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-y-auto p-8">
                <div className="max-w-6xl mx-auto w-full space-y-8">

                    {/* Quick Stats */}
                    {latestSession && (
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <Card className="border-none shadow-sm bg-gradient-to-br from-amber-50 to-white">
                                <CardContent className="pt-6">
                                    <div className="flex items-center gap-2 text-amber-600 mb-2">
                                        <AlertTriangle className="h-4 w-4" />
                                        <span className="text-xs font-semibold">Overall Score</span>
                                    </div>
                                    <div className="flex items-end gap-2">
                                        <div className={`text-3xl font-bold ${getScoreColor(latestSession.overall_score)}`}>
                                            {latestSession.overall_score}
                                        </div>
                                        {getScoreTrend(latestSession.overall_score)}
                                    </div>
                                    <Progress value={latestSession.overall_score} className="mt-2 h-1.5" />
                                </CardContent>
                            </Card>

                            <Card className="border-none shadow-sm">
                                <CardContent className="pt-6">
                                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                                        <AlertTriangle className="h-4 w-4" />
                                        <span className="text-xs">Total Issues</span>
                                    </div>
                                    <div className="text-2xl font-bold">{latestSession.total_issues}</div>
                                    <p className="text-xs text-rose-600 mt-1">{latestSession.critical_issues} critical</p>
                                </CardContent>
                            </Card>

                            <Card className="border-none shadow-sm">
                                <CardContent className="pt-6">
                                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                                        <TrendingUp className="h-4 w-4" />
                                        <span className="text-xs">Complexity</span>
                                    </div>
                                    <div className={`text-2xl font-bold ${getScoreColor(latestSession.complexity_score)}`}>
                                        {latestSession.complexity_score}
                                    </div>
                                    <Progress value={latestSession.complexity_score} className="mt-2 h-1.5" />
                                </CardContent>
                            </Card>

                            <Card className="border-none shadow-sm">
                                <CardContent className="pt-6">
                                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                                        <CheckCircle2 className="h-4 w-4" />
                                        <span className="text-xs">Est. Effort</span>
                                    </div>
                                    <div className="text-2xl font-bold">{latestSession.estimated_hours.toFixed(1)}h</div>
                                    <p className="text-xs text-muted-foreground mt-1">to resolve</p>
                                </CardContent>
                            </Card>
                        </div>
                    )}

                    {/* Sessions List */}
                    <div>
                        <h2 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                            <AlertTriangle className="h-5 w-5 text-amber-500" /> Analysis Sessions
                        </h2>

                        {isLoading ? (
                            <div className="flex items-center justify-center h-64 bg-white rounded-xl shadow-sm">
                                <Loader2 className="h-10 w-10 animate-spin text-amber-400" />
                            </div>
                        ) : sessions.length === 0 ? (
                            <Card className="border-dashed border-2 bg-transparent">
                                <CardContent className="flex flex-col items-center justify-center p-12 text-center">
                                    <div className="h-20 w-20 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                                        <AlertTriangle className="h-10 w-10 text-slate-300" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-slate-700">No analysis sessions yet</h3>
                                    <p className="text-slate-500 max-w-sm mt-2">
                                        Run your first technical debt analysis to identify issues in your codebase.
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
                                            <div className={`w-2 ${session.overall_score >= 80 ? 'bg-emerald-500' : session.overall_score >= 60 ? 'bg-yellow-500' : 'bg-rose-500'}`} />
                                            <CardContent className="flex-1 p-6 flex items-center justify-between">
                                                <div className="flex flex-col min-w-0">
                                                    <h3 className="font-bold text-lg text-slate-900 flex items-center gap-2">
                                                        Analysis V{session.version}
                                                        {session.github_exported && <Github className="h-4 w-4 text-emerald-500" />}
                                                    </h3>
                                                    <p className="text-slate-500 text-sm mt-1 line-clamp-1 italic">
                                                        "{session.summary}"
                                                    </p>
                                                    <div className="flex items-center gap-4 mt-3">
                                                        <span className="text-xs font-mono text-slate-400">
                                                            {new Date(session.created_at).toLocaleString()}
                                                        </span>
                                                        <Badge variant="secondary" className="bg-slate-100 text-slate-600 border-none text-[10px]">
                                                            {session.total_issues} issues
                                                        </Badge>
                                                        <Badge variant="secondary" className="bg-rose-100 text-rose-600 border-none text-[10px]">
                                                            {session.critical_issues} critical
                                                        </Badge>
                                                    </div>
                                                </div>

                                                <div className="flex items-center gap-6 pl-6 border-l">
                                                    <div className="text-center min-w-[60px]">
                                                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-tighter">Score</p>
                                                        <p className={`text-3xl font-black ${getScoreColor(session.overall_score)}`}>{session.overall_score}</p>
                                                    </div>
                                                    <div className="text-center min-w-[60px]">
                                                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-tighter">Effort</p>
                                                        <p className="text-2xl font-black text-slate-700">{session.estimated_hours.toFixed(1)}h</p>
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
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </div>
                                    </Card>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <DebtAnalysisModal
                open={isAnalysisModalOpen}
                onOpenChange={setIsAnalysisModalOpen}
                projectId={projectId}
                token={token}
                onAnalysisComplete={fetchSessions}
            />

            <DebtDetailModal
                session={selectedSession}
                open={!!selectedSession}
                onOpenChange={(open) => !open && setSelectedSession(null)}
            />
        </div>
    );
}
