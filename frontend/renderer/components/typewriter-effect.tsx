import React, { useState, useEffect } from 'react';

interface TypewriterEffectProps {
  text: string;
  speed?: number;
  onComplete?: () => void;
}

export function TypewriterEffect({ 
  text, 
  speed = 15, 
  onComplete 
}: TypewriterEffectProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    // Reset if text changes
    setDisplayedText('');
    setIsComplete(false);
    
    let index = 0;
    const intervalId = setInterval(() => {
      if (index < text.length) {
        setDisplayedText((prev) => prev + text.charAt(index));
        index++;
      } else {
        clearInterval(intervalId);
        setIsComplete(true);
        if (onComplete) onComplete();
      }
    }, speed);

    return () => clearInterval(intervalId);
  }, [text, speed, onComplete]);

  return (
    <span className="break-words whitespace-pre-wrap leading-relaxed">
      {displayedText}
      {!isComplete && (
        <span className="animate-pulse inline-block w-1.5 h-4 align-middle bg-purple-400 ml-0.5" />
      )}
    </span>
  );
}
