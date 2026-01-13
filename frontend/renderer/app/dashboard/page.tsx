'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, type User, type Project } from '@/lib/api';
import Image from 'next/image';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ProjectCreateModal } from '@/components/project-create-modal';
import { DeleteProjectDialog } from '@/components/delete-project-dialog';
import { ActionSelectionModal } from '@/components/dashboard/ActionSelectionModal';
import {
  Github,
  Folder,
  Plus,
  LogOut,
  Calendar,
  Loader2,
  FileText,
  Sparkles,
  Trash2,
  ChevronRight,
  Code,
  GitBranch,
  Clock,
  TrendingUp,
  Zap,
  BookOpen,
  Settings,
  Bell,
  FileCheck,
  ClipboardCheck,
  AlertTriangle,
  Beaker
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [stats, setStats] = useState({
    total_requirements: 0,
    total_user_stories: 0,
    total_uml_diagrams: 0,
    total_code_sessions: 0,
    total_generated_files: 0,
    total_reviews: 0,
    total_debt_sessions: 0,
    total_test_cases: 0,
    requirements_change: 0,
    stories_change: 0,
  });

  const [activeQuickAction, setActiveQuickAction] = useState<{
    title: string;
    description: string;
    icon: any;
    targetRoute: string;
  } | null>(null);
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      setIsLoading(true);
      const authData = await window.electron.getAuth();

      if (!authData || !authData.accessToken) {
        router.push('/');
        return;
      }

      api.setToken(authData.accessToken);

      try {
        const userData = await api.getCurrentUser();
        setUser(userData);
        await loadProjects();
        await loadStats();
      } catch (apiError: any) {
        console.error('API error:', apiError);
        if (apiError.status === 401) {
          await window.electron.logout();
          api.clearToken();
          router.push('/');
          return;
        }
        throw apiError;
      }
    } catch (error) {
      console.error('Failed to load user data:', error);
      setIsLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

  const loadProjects = async () => {
    try {
      setIsLoadingProjects(true);
      const response = await api.getProjects({ limit: 10, sort: 'created_at', order: 'desc' });
      setProjects(response.projects || []);
    } catch (error) {
      console.error('Failed to load projects:', error);
      setProjects([]);
    } finally {
      setIsLoadingProjects(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/dashboard/stats', {
        headers: {
          'Authorization': `Bearer ${api.getToken()}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats);
        setRecentActivity(data.recent_activity || []);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
      api.clearToken();
      await window.electron.logout();
      router.push('/');
    } catch (error) {
      console.error('Logout error:', error);
      api.clearToken();
      await window.electron.logout();
      router.push('/');
    }
  };

  const handleNewProject = () => {
    setIsCreateModalOpen(true);
  };

  const handleProjectCreated = async () => {
    await loadProjects();
  };

  const handleOpenFolder = async (localPath: string) => {
    try {
      const result = await window.electron.openFolder(localPath);
      if (!result.success) {
        console.error('Failed to open folder:', result.error);
      }
    } catch (error) {
      console.error('Error opening folder:', error);
    }
  };

  const handleOpenGitHub = async (githubUrl: string) => {
    try {
      await window.electron.openExternal(githubUrl);
    } catch (error) {
      console.error('Error opening GitHub:', error);
    }
  };

  const handleOpenProject = (projectId: string) => {
    router.push(`/project/${projectId}/requirements`);
  };

  const handleQuickActionClick = (action: {
    title: string;
    description: string;
    icon: any;
    targetRoute: string;
  }) => {
    setActiveQuickAction(action);
    setIsActionModalOpen(true);
  };

  const handleDeleteProject = async (project: Project) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/projects/${project.id}?delete_local=true`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${api.getToken()}`,
          },
        }
      );

      if (response.ok) {
        await loadProjects();
      } else {
        throw new Error('Failed to delete project');
      }
    } catch (error) {
      console.error('Error deleting project:', error);
      throw error;
    }
  };

  const openDeleteDialog = (project: Project) => {
    setProjectToDelete(project);
    setIsDeleteDialogOpen(true);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  // Stats are now loaded from API via loadStats()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <>
      <ProjectCreateModal
        open={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
        onProjectCreated={handleProjectCreated}
      />

      <DeleteProjectDialog
        project={projectToDelete}
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        onDelete={handleDeleteProject}
      />

      {activeQuickAction && (
        <ActionSelectionModal
          open={isActionModalOpen}
          onOpenChange={setIsActionModalOpen}
          title={activeQuickAction.title}
          description={activeQuickAction.description}
          icon={activeQuickAction.icon}
          targetRoute={activeQuickAction.targetRoute}
          projects={projects}
          onNewProject={() => {
            setIsActionModalOpen(false);
            handleNewProject();
          }}
        />
      )}

      <div className="min-h-screen bg-background relative overflow-hidden">
        {/* Dotted Background Pattern */}
        <div className="absolute inset-0 z-0 opacity-[0.15]"
          style={{
            backgroundImage: 'radial-gradient(circle at 1px 1px, currentColor 1px, transparent 0)',
            backgroundSize: '24px 24px'
          }}
        />
        {/* Radial Gradient Overlay */}
        <div className="absolute inset-0 z-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/10 via-transparent to-transparent pointer-events-none" />

        {/* Top Navigation */}
        {/* Top Navigation */}
        <header className="sticky top-0 z-50 border-b bg-card/80 backdrop-blur-sm">
          <div className="container mx-auto px-6 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="relative h-8 w-8 rounded-lg overflow-hidden">
                  <Image
                    src="/images/integrow.png"
                    alt="InteGrow"
                    fill
                    className="object-cover"
                  />
                </div>
                <span className="text-xl font-bold">InteGrow</span>
              </div>

              <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" className="relative">
                  <Bell className="h-5 w-5" />
                </Button>

                {user && (
                  <div className="flex items-center gap-3">
                    <Avatar className="h-9 w-9 border-2 border-primary/20">
                      <AvatarImage src={user.avatar_url || undefined} />
                      <AvatarFallback className="bg-primary/10 text-primary">
                        {user.github_username.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="hidden md:block text-sm">
                      <p className="font-medium">{user.github_username}</p>
                    </div>
                  </div>
                )}

                <Button variant="ghost" size="sm" onClick={handleLogout} className="text-muted-foreground">
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-6 py-8 relative z-10">
          {/* Greeting */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-1">
              {getGreeting()}, {user?.github_username}!
            </h1>
            <p className="text-muted-foreground">
              Here's what's happening with your projects
            </p>
          </div>

          {/* Bento Grid */}
          <div className="grid grid-cols-12 gap-4 mb-8">
            {/* Projects Hero Card */}
            <Card className="col-span-12 md:col-span-4 row-span-2 relative overflow-hidden border-primary/20 bg-card">
              {/* Corner Gradients */}
              <div className="absolute -top-24 -right-24 h-64 w-64 bg-primary blur-[64px] rounded-full pointer-events-none opacity-60" />
              <div className="absolute -bottom-24 -left-24 h-64 w-64 bg-primary blur-[64px] rounded-full pointer-events-none opacity-60" />

              <div className="relative z-10">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-lg">Your Projects</span>
                    <Button onClick={handleNewProject} size="sm" className="gap-1">
                      <Plus className="h-4 w-4" />
                      New
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-6xl font-bold text-primary mb-2">
                    {projects.length}
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">Active Projects</p>

                  {isLoadingProjects ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    </div>
                  ) : projects.length === 0 ? (
                    <div className="text-center py-6">
                      <Folder className="h-12 w-12 mx-auto text-muted-foreground/50 mb-2" />
                      <p className="text-sm text-muted-foreground">No projects yet</p>
                      <Button onClick={handleNewProject} variant="outline" size="sm" className="mt-3">
                        Create your first project
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {projects.slice(0, 3).map((project) => (
                        <div
                          key={project.id}
                          className="flex items-center justify-between p-2 rounded-lg hover:bg-primary/5 cursor-pointer transition-colors group"
                          onClick={() => handleOpenProject(project.id)}
                        >
                          <div className="flex items-center gap-3">
                            <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center">
                              <Folder className="h-4 w-4 text-primary" />
                            </div>
                            <div>
                              <p className="font-medium text-sm">{project.name}</p>
                              <p className="text-xs text-muted-foreground">{formatDate(project.created_at)}</p>
                            </div>
                          </div>
                          <ChevronRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                      ))}
                      {projects.length > 3 && (
                        <Button variant="ghost" size="sm" className="w-full text-muted-foreground">
                          View all {projects.length} projects
                        </Button>
                      )}
                    </div>
                  )}
                </CardContent>
              </div>
            </Card>

            {/* Stats Cards Grid - 2 rows x 3 columns */}
            <div className="col-span-12 md:col-span-5 grid grid-cols-3 grid-rows-2 gap-4 row-span-2">
              {/* Row 1 */}
              <Card className="hover:shadow-md transition-shadow bg-card h-full flex flex-col justify-center">
                <CardContent className="pt-2">
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <FileText className="h-4 w-4" />
                    <span className="text-[10px] uppercase tracking-wider font-semibold">Requirements</span>
                  </div>
                  <div className="text-xl font-bold">{stats.total_requirements}</div>
                  {stats.requirements_change > 0 && (
                    <div className="flex items-center gap-1 text-[10px] text-green-600">
                      <TrendingUp className="h-2 w-2" />
                      +{stats.requirements_change}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow bg-card h-full flex flex-col justify-center">
                <CardContent className="pt-2">
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <BookOpen className="h-4 w-4" />
                    <span className="text-[10px] uppercase tracking-wider font-semibold">User Stories</span>
                  </div>
                  <div className="text-xl font-bold">{stats.total_user_stories}</div>
                  {stats.stories_change > 0 && (
                    <div className="flex items-center gap-1 text-[10px] text-green-600">
                      <TrendingUp className="h-2 w-2" />
                      +{stats.stories_change}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow bg-card h-full flex flex-col justify-center">
                <CardContent className="pt-2">
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <Zap className="h-4 w-4" />
                    <span className="text-[10px] uppercase tracking-wider font-semibold">Generated</span>
                  </div>
                  <div className="text-xl font-bold">{stats.total_generated_files}</div>
                  <p className="text-[10px] text-muted-foreground">files generated</p>
                </CardContent>
              </Card>

              {/* Row 2 */}
              <Card className="hover:shadow-md transition-shadow bg-card h-full flex flex-col justify-center">
                <CardContent className="pt-2">
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <ClipboardCheck className="h-4 w-4" />
                    <span className="text-[10px] uppercase tracking-wider font-semibold">Reviews</span>
                  </div>
                  <div className="text-xl font-bold">{stats.total_reviews}</div>
                  <p className="text-[10px] text-muted-foreground">code reviews</p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow bg-card h-full flex flex-col justify-center">
                <CardContent className="pt-2">
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <AlertTriangle className="h-4 w-4" />
                    <span className="text-[10px] uppercase tracking-wider font-semibold">Debt</span>
                  </div>
                  <div className="text-xl font-bold">{stats.total_debt_sessions}</div>
                  <p className="text-[10px] text-muted-foreground">debt sessions</p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-md transition-shadow bg-card h-full flex flex-col justify-center border-dashed border-muted-foreground/20">
                <CardContent className="pt-2">
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <Beaker className="h-4 w-4" />
                    <span className="text-[10px] uppercase tracking-wider font-semibold">Tests</span>
                  </div>
                  <div className="text-xl font-bold">{stats.total_test_cases}</div>
                  <p className="text-[10px] text-muted-foreground">test cases</p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity Card */}
            <Card className="col-span-12 md:col-span-3 row-span-2 bg-card">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Recent Activity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {recentActivity.slice(0, 5).map((activity, i) => (
                  <div key={activity.id} className="flex items-start gap-3">
                    <div className={`h-2 w-2 rounded-full mt-2 ${i === 0 ? 'bg-green-500' : 'bg-muted'}`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{activity.title}</p>
                      <p className="text-xs text-muted-foreground truncate" title={activity.description}>
                        {activity.project_name ? `${activity.project_name}` : activity.description} • {formatDate(activity.timestamp)}
                      </p>
                    </div>
                  </div>
                ))}
                {recentActivity.length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-4">No recent activity</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <Card
                className="cursor-pointer hover:shadow-md hover:border-primary/30 transition-all group"
                onClick={handleNewProject}
              >
                <CardContent className="pt-6 text-center">
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-primary/20 transition-colors">
                    <Plus className="h-6 w-6 text-primary" />
                  </div>
                  <p className="font-medium text-sm">New Project</p>
                </CardContent>
              </Card>

              <Card
                className="cursor-pointer hover:shadow-md hover:border-primary/30 transition-all group"
                onClick={() => handleQuickActionClick({
                  title: 'Analyze Requirements',
                  description: 'Start fresh with new requirements or refine existing ones.',
                  icon: FileText,
                  targetRoute: 'requirements'
                })}
              >
                <CardContent className="pt-6 text-center">
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-primary/20 transition-colors">
                    <FileText className="h-6 w-6 text-primary" />
                  </div>
                  <p className="font-medium text-sm">Analyze Requirements</p>
                </CardContent>
              </Card>

              <Card
                className="cursor-pointer hover:shadow-md hover:border-primary/30 transition-all group"
                onClick={() => handleQuickActionClick({
                  title: 'Generate UML',
                  description: 'Visualize your architecture with sequence, class, and flow diagrams.',
                  icon: GitBranch,
                  targetRoute: 'uml'
                })}
              >
                <CardContent className="pt-6 text-center">
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-primary/20 transition-colors">
                    <GitBranch className="h-6 w-6 text-primary" />
                  </div>
                  <p className="font-medium text-sm">Generate UML</p>
                </CardContent>
              </Card>

              <Card
                className="cursor-pointer hover:shadow-md hover:border-primary/30 transition-all group"
                onClick={() => handleQuickActionClick({
                  title: 'Generate Code',
                  description: 'Turn your user stories into production-ready code instantly.',
                  icon: Zap,
                  targetRoute: 'code'
                })}
              >
                <CardContent className="pt-6 text-center">
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-primary/20 transition-colors">
                    <Zap className="h-6 w-6 text-primary" />
                  </div>
                  <p className="font-medium text-sm">Generate Code</p>
                </CardContent>
              </Card>

              <Card
                className="cursor-pointer hover:shadow-md hover:border-primary/30 transition-all group"
                onClick={() => handleQuickActionClick({
                  title: 'Code Review',
                  description: 'Get deep AI insights on code quality, security, and performance.',
                  icon: ClipboardCheck,
                  targetRoute: 'review'
                })}
              >
                <CardContent className="pt-6 text-center">
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-primary/20 transition-colors">
                    <ClipboardCheck className="h-6 w-6 text-primary" />
                  </div>
                  <p className="font-medium text-sm">Code Review</p>
                </CardContent>
              </Card>

              <Card
                className="cursor-pointer hover:shadow-md hover:border-primary/30 transition-all group"
                onClick={() => handleQuickActionClick({
                  title: 'Technical Debt',
                  description: 'Find complexity, duplication, and architectural issues in your repo.',
                  icon: AlertTriangle,
                  targetRoute: 'debt'
                })}
              >
                <CardContent className="pt-6 text-center">
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-primary/20 transition-colors">
                    <AlertTriangle className="h-6 w-6 text-primary" />
                  </div>
                  <p className="font-medium text-sm">Tech Debt</p>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* All Projects */}
          {projects.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">All Projects</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {projects.map((project) => (
                  <Card key={project.id} className="hover:shadow-lg transition-shadow group">
                    <CardHeader className="pb-2">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Folder className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <CardTitle className="text-base">{project.name}</CardTitle>
                            <CardDescription className="text-xs">
                              {formatDate(project.created_at)}
                            </CardDescription>
                          </div>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded-full ${project.visibility === 'public'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-orange-100 text-orange-700'
                          }`}>
                          {project.visibility}
                        </span>
                      </div>
                    </CardHeader>

                    <CardContent>
                      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                        {project.description || 'No description'}
                      </p>

                      <div className="flex items-center gap-2">
                        <Button
                          onClick={() => handleOpenProject(project.id)}
                          className="flex-1"
                          size="sm"
                        >
                          <Sparkles className="h-4 w-4 mr-2" />
                          Open
                        </Button>

                        <Button
                          variant="outline"
                          size="icon"
                          className="h-9 w-9"
                          onClick={() => handleOpenFolder(project.local_path)}
                        >
                          <Folder className="h-4 w-4" />
                        </Button>

                        <Button
                          variant="outline"
                          size="icon"
                          className="h-9 w-9"
                          onClick={() => handleOpenGitHub(project.github_repo_url)}
                        >
                          <Github className="h-4 w-4" />
                        </Button>

                        <Button
                          variant="outline"
                          size="icon"
                          className="h-9 w-9 text-destructive hover:text-destructive"
                          onClick={() => openDeleteDialog(project)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  );
}
