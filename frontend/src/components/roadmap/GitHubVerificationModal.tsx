import React, { useState } from 'react';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import { createClient } from '@/lib/supabase/client';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2, GitBranch, CheckCircle2, XCircle } from 'lucide-react';

interface GitHubVerificationModalProps {
  isOpen: boolean;
  onClose: () => void;
  nodeId: string;
}

interface VerificationResult {
  approved: boolean;
  strengths: string[];
  weaknesses: string[];
  feedback_summary: string;
}

export function GitHubVerificationModal({ isOpen, onClose, nodeId }: GitHubVerificationModalProps) {
  const { profile, roadmap, completeNode } = useRoadmapStore();
  const [repoUrl, setRepoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [error, setError] = useState('');

  const handleVerify = async () => {
    if (!repoUrl.trim() || !profile || !roadmap) return;
    
    setIsLoading(true);
    setError('');
    
    try {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/verify/github`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(session && { 'Authorization': `Bearer ${session.access_token}` })
        },
        body: JSON.stringify({
          repo_url: repoUrl.trim(),
          node_id: nodeId,
          profile,
          roadmap
        })
      });

      if (!response.ok) {
        throw new Error('Failed to verify repository');
      }

      const data = await response.json();
      setResult(data);

      if (data.approved) {
        // Automatically complete the node if approved!
        await completeNode(nodeId);
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during verification');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setRepoUrl('');
    setError('');
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleReset()}>
      <DialogContent className="sm:max-w-[500px] bg-card border-border rounded-2xl shadow-xs">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-foreground">
            <GitBranch className="w-5 h-5 text-foreground" />
            Verify Capstone Project
          </DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            Paste the URL to your public GitHub repository so our AI can evaluate your codebase against this milestone&apos;s requirements.
          </DialogDescription>
        </DialogHeader>

        {!result ? (
          <div className="space-y-4 py-3">
            <Input 
              placeholder="https://github.com/username/repo" 
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              disabled={isLoading}
              className="bg-background border-border rounded-xl text-xs h-10"
            />
            {error && <p className="text-xs text-destructive">{error}</p>}
            <Button 
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl text-xs font-semibold py-2.5 shadow-xs" 
              onClick={handleVerify} 
              disabled={!repoUrl.trim() || isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing Repository...
                </>
              ) : (
                "Verify Codebase"
              )}
            </Button>
          </div>
        ) : (
          <div className="space-y-4 py-3">
            <div className={`p-4 rounded-xl flex items-start gap-3 ${result.approved ? 'bg-emerald-50 border border-emerald-200 text-emerald-950' : 'bg-muted/60 border border-border text-foreground'}`}>
              {result.approved ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
              )}
              <div>
                <h4 className={`text-sm font-bold ${result.approved ? 'text-emerald-800' : 'text-destructive'}`}>
                  {result.approved ? "Project Approved!" : "Needs Revision"}
                </h4>
                <p className="text-xs mt-1 leading-relaxed text-muted-foreground">
                  {result.feedback_summary}
                </p>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <h5 className="text-xs font-bold text-emerald-800 mb-1">Strengths</h5>
                <ul className="list-disc pl-4 text-xs space-y-1 text-muted-foreground">
                  {result.strengths.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
              <div>
                <h5 className="text-xs font-bold text-foreground mb-1">Areas for Improvement</h5>
                <ul className="list-disc pl-4 text-xs space-y-1 text-muted-foreground">
                  {result.weaknesses.map((w, i) => <li key={i}>{w}</li>)}
                </ul>
              </div>
            </div>

            <Button className="w-full mt-2 rounded-xl text-xs font-semibold" onClick={handleReset} variant={result.approved ? "default" : "outline"}>
              {result.approved ? "Awesome!" : "Try Again Later"}
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
