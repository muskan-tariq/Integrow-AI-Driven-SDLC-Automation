'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Github, Loader2, Info, Sparkles } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuthStatus();
    setupAuthListeners();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const { isAuthenticated } = await window.electron.checkAuth();
      
      if (isAuthenticated) {
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Auth check error:', error);
    } finally {
      setIsCheckingAuth(false);
    }
  };

  const setupAuthListeners = () => {
    // Listen for OAuth callback
    window.electron.onAuthCallback(async ({ code }) => {
      try {
        setIsLoading(true);
        setError(null);

        // Exchange code for token
        const result = await window.electron.exchangeCode(code);

        if (result.success) {
          // Redirect to dashboard
          router.push('/dashboard');
        } else {
          console.error('Auth failed:', result.error);
          setError(result.error || 'Authentication failed');
        }
      } catch (error) {
        console.error('Auth callback error:', error);
        setError('Authentication failed. Please try again.');
      } finally {
        setIsLoading(false);
      }
    });
  };

  const handleGitHubLogin = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await window.electron.openGitHubOAuth();
    } catch (error) {
      console.error('OAuth error:', error);
      setError('Failed to open GitHub login. Please try again.');
      setIsLoading(false);
    }
  };

  if (isCheckingAuth) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full flex overflow-hidden bg-background">
      {/* Left Panel - Visual */}
      <div className="hidden md:flex md:w-1/2 relative" style={{ backgroundColor: '#FCF5EB' }}>
        <div className="absolute inset-0">
          <Image
            src="/images/login-pix.png"
            alt="SDLC Automation"
            fill
            className="object-cover"
            priority
            quality={100}
          />
        </div>
        
        {/* Content Overlay */}
        <div className="absolute bottom-0 left-0 p-12 w-full z-10 space-y-6">
          <div className="space-y-2">
            <h2 className="text-4xl font-bold tracking-tight text-gray-900">Build Faster with AI</h2>
            <p className="text-lg text-gray-600 max-w-md leading-relaxed">
              Accelerate your development lifecycle with InteGrow's intelligent agents and seamless workflow automation.
            </p>
          </div>
          
          <div className="flex gap-4 pt-4">
            <div className="flex items-center gap-2 text-sm text-gray-700 bg-black/5 px-3 py-1.5 rounded-full backdrop-blur-sm border border-black/10">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              System Operational
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-700 bg-black/5 px-3 py-1.5 rounded-full backdrop-blur-sm border border-black/10">
              <span>v1.0.0</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="w-full md:w-1/2 flex items-center justify-center p-8 relative bg-background">
        {/* Textured Pattern */}
        <div className="absolute inset-0 h-full w-full bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
        {/* Absolute Background Elements for Right Side (Subtle) */}
        <div className="absolute top-0 right-0 p-8 flex gap-4">
           {/* Optional: Language switcher or Help link could go here */}
        </div>

        <div className="w-full max-w-[400px] space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000 relative z-10">
          {/* Brand Header */}
          <div className="flex flex-col items-center text-center space-y-8">
            <div className="flex items-center justify-center ">
              <div className="w-32 h-32 relative group">
                <div className="absolute inset-0 bg-primary/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-500" />
                <div className="relative w-full h-full bg-transparent flex items-center justify-center overflow-hidden transition-transform duration-500 hover:scale-105">
                  <Image
                    src="/images/integrow.png"
                    alt="InteGrow Logo"
                    width={128}
                    height={128}
                    className="rounded-2xl object-cover"
                    priority
                  />
                </div>
              </div>
              <span className="text-5xl font-bold tracking-tight text-foreground">InteGrow</span>
            </div>
            
            <div className="space-y-2">
              <h1 className="text-2xl font-semibold text-muted-foreground">Welcome Back to Antigravity</h1>
              <p className="text-muted-foreground/80 text-sm">
                Sign in to your workspace
              </p>
            </div>
          </div>

          {/* Form Content */}
          <div className="space-y-6">
            <div className="space-y-4 text-center">
              {error && (
                <div className="p-4 rounded-lg bg-destructive/5 border border-destructive/20 text-destructive text-sm flex items-start gap-3 text-left">
                  <Info className="w-5 h-5 shrink-0" />
                  <p>{error}</p>
                </div>
              )}

              <Button
                onClick={handleGitHubLogin}
                disabled={isLoading}
                size="lg"
                className="w-full max-w-[280px] mx-auto h-12 text-base font-medium transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Github className="mr-2 h-5 w-5" />
                    Continue with GitHub
                  </>
                )}
              </Button>
            </div>


          </div>
        </div>
      </div>
    </div>
  );
}
