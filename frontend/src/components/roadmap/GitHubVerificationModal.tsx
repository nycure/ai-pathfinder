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
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <GitBranch className="w-5 h-5" />
            Verify Capstone Project
          </DialogTitle>
          <DialogDescription>
            Paste the URL to your public GitHub repository so our AI can evaluate your codebase against this milestone's requirements.
          </DialogDescription>
        </DialogHeader>

        {!result ? (
          <div className="space-y-4 py-4">
            <Input 
              placeholder="https://github.com/username/repo" 
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              disabled={isLoading}
            />
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button 
              className="w-full" 
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
          <div className="space-y-4 py-4">
            <div className={`p-4 rounded-lg flex items-start gap-3 ${result.approved ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
              {result.approved ? (
                <CheckCircle2 className="w-6 h-6 text-green-500 shrink-0" />
              ) : (
                <XCircle className="w-6 h-6 text-red-500 shrink-0" />
              )}
              <div>
                <h4 className={`font-semibold ${result.approved ? 'text-green-500' : 'text-red-500'}`}>
                  {result.approved ? "Project Approved!" : "Needs Revision"}
                </h4>
                <p className="text-sm mt-1 leading-relaxed">
                  {result.feedback_summary}
                </p>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <h5 className="text-sm font-semibold text-green-500 mb-1">Strengths</h5>
                <ul className="list-disc pl-4 text-sm space-y-1">
                  {result.strengths.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
              <div>
                <h5 className="text-sm font-semibold text-red-500 mb-1">Areas for Improvement</h5>
                <ul className="list-disc pl-4 text-sm space-y-1">
                  {result.weaknesses.map((w, i) => <li key={i}>{w}</li>)}
                </ul>
              </div>
            </div>

            <Button className="w-full mt-4" onClick={handleReset} variant={result.approved ? "default" : "outline"}>
              {result.approved ? "Awesome!" : "Try Again Later"}
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
