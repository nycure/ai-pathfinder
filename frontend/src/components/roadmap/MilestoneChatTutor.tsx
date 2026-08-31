import React, { useState, useRef, useEffect } from 'react';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { createClient } from '@/lib/supabase/client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function MilestoneChatTutor() {
  const { activeNodeId, roadmap, profile } = useRoadmapStore();
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hi! I'm your AI Tutor. What would you like to know about this milestone?" }
  ]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  if (!activeNodeId || !roadmap || !profile) return null;

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage = input.trim();
    setInput('');
    const newMessages: Message[] = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setIsStreaming(true);

    try {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/tutor/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(session && { 'Authorization': `Bearer ${session.access_token}` })
        },
        body: JSON.stringify({
          messages: newMessages,
          node_id: activeNodeId,
          profile,
          roadmap
        })
      });

      if (!response.ok || !response.body) {
        throw new Error('Failed to connect to Tutor');
      }

      // Add a placeholder for the assistant's response
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        const chunkValue = decoder.decode(value);
        if (chunkValue) {
          setMessages(prev => {
            const updated = [...prev];
            updated[updated.length - 1].content += chunkValue;
            return updated;
          });
        }
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] max-h-[70vh] border rounded-lg bg-card overflow-hidden">
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4 pb-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                  <Bot className="w-5 h-5 text-primary" />
                </div>
              )}
              <div 
                className={`max-w-[85%] rounded-2xl px-4 py-2 ${
                  msg.role === 'user' 
                    ? 'bg-primary text-primary-foreground rounded-tr-sm' 
                    : 'bg-muted text-foreground rounded-tl-sm'
                }`}
              >
                <div className="text-sm whitespace-pre-wrap leading-relaxed">
                  {msg.content}
                </div>
              </div>
            </div>
          ))}
          {isStreaming && messages[messages.length - 1].role === 'user' && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                <Bot className="w-5 h-5 text-primary" />
              </div>
              <div className="bg-muted rounded-2xl rounded-tl-sm px-4 py-3 flex items-center">
                <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
              </div>
            </div>
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>
      
      <div className="p-3 border-t bg-background">
        <form onSubmit={handleSend} className="flex gap-2">
          <Input 
            value={input} 
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..." 
            className="flex-1"
            disabled={isStreaming}
          />
          <Button type="submit" size="icon" disabled={!input.trim() || isStreaming}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
