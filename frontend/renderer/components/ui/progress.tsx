"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
    value?: number
}

export const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
    ({ className, value = 0, ...props }, ref) => {
        return (
            <div
                ref={ref}
                role="progressbar"
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={value}
                className={cn(
                    "relative h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800",
                    className
                )}
                {...props}
            >
                <div
                    className="h-full w-full flex-1 bg-indigo-600 transition-all duration-300 ease-in-out dark:bg-indigo-400"
                    style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
                />
            </div>
        )
    }
)

Progress.displayName = "Progress"
