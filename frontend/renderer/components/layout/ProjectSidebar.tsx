'use client';

import { useParams, usePathname } from 'next/navigation';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import {
  FileText,
  BookOpen,
  GitBranch,
  Code,
  Settings,
  ChevronLeft,
  Home,
  ClipboardCheck,
  AlertTriangle
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

export function ProjectSidebar() {
  const params = useParams();
  const pathname = usePathname();
  const projectId = params.id as string;

  const navItems: NavItem[] = [
    {
      label: 'Requirements',
      href: `/project/${projectId}/requirements`,
      icon: <FileText className="h-5 w-5" />,
    },
    {
      label: 'User Stories',
      href: `/project/${projectId}/stories`,
      icon: <BookOpen className="h-5 w-5" />,
    },
    {
      label: 'UML Diagrams',
      href: `/project/${projectId}/uml`,
      icon: <GitBranch className="h-5 w-5" />,
    },
    {
      label: 'Code Generation',
      href: `/project/${projectId}/code`,
      icon: <Code className="h-5 w-5" />,
    },
    {
      label: 'Code Review',
      href: `/project/${projectId}/review`,
      icon: <ClipboardCheck className="h-5 w-5" />,
    },
    {
      label: 'Technical Debt',
      href: `/project/${projectId}/debt`,
      icon: <AlertTriangle className="h-5 w-5" />,
    },
    {
      label: 'Settings',
      href: `/project/${projectId}/settings`,
      icon: <Settings className="h-5 w-5" />,
    },
  ];

  const isActive = (href: string) => {
    return pathname.startsWith(href);
  };

  return (
    <div className="flex flex-col h-full w-64 bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="text-gray-400 hover:bg-white/10 hover:text-white gap-2">
            <ChevronLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
              isActive(item.href)
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            {item.icon}
            <span className="font-medium">{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <div className="text-xs text-gray-500">
          InteGrow AI Suite
        </div>
      </div>
    </div>
  );
}
