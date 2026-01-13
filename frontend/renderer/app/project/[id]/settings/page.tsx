'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Settings } from 'lucide-react';

export default function SettingsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      const authData = await window.electron.getAuth();
      if (authData?.accessToken) {
        setIsLoading(false);
      } else {
        router.push('/');
      }
    } catch (error) {
      console.error('Auth error:', error);
      router.push('/');
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 text-gray-900">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4 shrink-0">
        <div className="max-w-5xl mx-auto w-full">
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">Project Settings</h1>
            <p className="text-gray-500 mt-1">
              Configure your project preferences and integrations.
            </p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto w-full">
            {isLoading ? (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
            ) : (
            <Card className="border-0 shadow-sm">
                <CardHeader className="pb-3 border-b border-gray-100">
                <CardTitle className="flex items-center gap-2 text-lg font-semibold text-gray-900">
                    <Settings className="h-5 w-5 text-gray-500" />
                    General Settings
                </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="rounded-full bg-gray-100 p-3 mb-4">
                    <Settings className="h-6 w-6 text-gray-400" />
                    </div>
                    <h3 className="font-semibold text-gray-900">Coming Soon</h3>
                    <p className="text-gray-500 mt-2 max-w-sm">
                    Project settings such as team management, integrations, and advanced configuration will be available in a future update.
                    </p>
                </div>
                </CardContent>
            </Card>
            )}
        </div>
      </div>
    </div>
  );
}
