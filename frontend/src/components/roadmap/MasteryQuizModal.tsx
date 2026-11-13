import React, { useState, useEffect } from 'react';
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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Loader2, Brain, CheckCircle2, XCircle } from 'lucide-react';

interface MasteryQuizModalProps {
  isOpen: boolean;
  onClose: () => void;
  nodeId: string;
}

interface QuizQuestion {
  text: string;
  options: string[];
  correct_option_index: number;
  explanation: string;
}

export function MasteryQuizModal({ isOpen, onClose, nodeId }: MasteryQuizModalProps) {
  const { profile, roadmap, completeNode } = useRoadmapStore();
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  // Fetch quiz when modal opens
  useEffect(() => {
    if (isOpen && questions.length === 0) {
      generateQuiz();
    }
  }, [isOpen]);

  const generateQuiz = async () => {
    if (!profile || !roadmap) return;
    setIsLoading(true);
    setError('');
    
    try {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/verify/quiz/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(session && { 'Authorization': `Bearer ${session.access_token}` })
        },
        body: JSON.stringify({
          node_id: nodeId,
          profile,
          roadmap
        })
      });

      if (!response.ok) throw new Error('Failed to generate quiz');

      const data = await response.json();
      setQuestions(data.questions);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (val: string) => {
    if (isSubmitted) return;
    setSelectedAnswers(prev => ({ ...prev, [currentQuestionIdx]: parseInt(val) }));
  };

  const handleNext = () => {
    if (currentQuestionIdx < questions.length - 1) {
      setCurrentQuestionIdx(prev => prev + 1);
    } else {
      // Calculate score
      let correct = 0;
      questions.forEach((q, idx) => {
        if (selectedAnswers[idx] === q.correct_option_index) correct++;
      });
      setScore(correct);
      setIsSubmitted(true);

      // If passing (>= 2/3), mark as completed
      if (correct >= 2) {
        completeNode(nodeId);
      }
    }
  };

  const handleReset = () => {
    setQuestions([]);
    setCurrentQuestionIdx(0);
    setSelectedAnswers({});
    setIsSubmitted(false);
    setScore(0);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleReset()}>
      <DialogContent className="sm:max-w-[500px] bg-card border-border rounded-2xl shadow-xs">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-foreground">
            <Brain className="w-5 h-5 text-foreground" />
            Mastery Validation
          </DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            {isSubmitted 
              ? `You scored ${score} out of ${questions.length}.`
              : "Let's verify your conceptual understanding before marking this milestone complete."}
          </DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground gap-3">
            <Loader2 className="w-7 h-7 animate-spin text-foreground" />
            <p className="text-xs">Generating AI Micro-Quiz...</p>
          </div>
        ) : error ? (
          <div className="py-4 text-center text-destructive">
            <p className="text-xs">{error}</p>
            <Button variant="outline" className="mt-4" onClick={handleReset}>Close</Button>
          </div>
        ) : questions.length > 0 && !isSubmitted ? (
          <div className="py-3 space-y-5">
            <div>
              <p className="text-[10px] font-semibold text-muted-foreground tracking-wider uppercase mb-1.5">
                Question {currentQuestionIdx + 1} of {questions.length}
              </p>
              <h3 className="text-base font-semibold leading-snug text-foreground">
                {questions[currentQuestionIdx].text}
              </h3>
            </div>

            <RadioGroup 
              value={selectedAnswers[currentQuestionIdx]?.toString() || ""}
              onValueChange={handleSelect}
              className="space-y-2.5"
            >
              {questions[currentQuestionIdx].options.map((opt, i) => (
                <div key={i} className="flex items-center space-x-2.5 border border-border rounded-xl p-3 hover:bg-muted/40 transition-colors bg-background">
                  <RadioGroupItem value={i.toString()} id={`opt-${i}`} />
                  <Label htmlFor={`opt-${i}`} className="flex-1 cursor-pointer text-xs leading-relaxed font-normal text-foreground">
                    {opt}
                  </Label>
                </div>
              ))}
            </RadioGroup>

            <div className="flex justify-between items-center pt-3 border-t border-border/60">
              <span className="text-[11px] text-muted-foreground">
                Answer required
              </span>
              <Button 
                onClick={handleNext}
                disabled={selectedAnswers[currentQuestionIdx] === undefined}
                className="bg-primary text-primary-foreground hover:bg-primary/90 text-xs px-4 py-2 rounded-lg"
              >
                {currentQuestionIdx === questions.length - 1 ? 'Submit & Grade' : 'Next Question'}
              </Button>
            </div>
          </div>
        ) : isSubmitted ? (
          <div className="py-3 space-y-5">
            <div className={`p-4 rounded-xl flex items-start gap-3 ${score >= 2 ? 'bg-emerald-50 border border-emerald-200 text-emerald-950' : 'bg-muted/60 border border-border text-foreground'}`}>
              {score >= 2 ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
              )}
              <div>
                <h4 className={`text-sm font-bold ${score >= 2 ? 'text-emerald-800' : 'text-destructive'}`}>
                  {score >= 2 ? "Milestone Mastered!" : "Review Required"}
                </h4>
                <p className="text-xs mt-1 leading-relaxed text-muted-foreground">
                  {score >= 2 
                    ? "Great work! You demonstrated strong conceptual understanding." 
                    : "You need a score of 2 out of 3 to pass. Please review the resources and try again."}
                </p>
              </div>
            </div>

            <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2">
              {questions.map((q, idx) => (
                <div key={idx} className="text-sm space-y-1 pb-4 border-b last:border-0">
                  <p className="font-medium">{q.text}</p>
                  <p className="text-muted-foreground">Your answer: {q.options[selectedAnswers[idx]]}</p>
                  <p className={selectedAnswers[idx] === q.correct_option_index ? 'text-green-500' : 'text-red-500'}>
                    {selectedAnswers[idx] === q.correct_option_index ? 'Correct!' : `Incorrect. Correct answer: ${q.options[q.correct_option_index]}`}
                  </p>
                  <p className="bg-muted/50 p-2 rounded text-muted-foreground mt-2 text-xs">
                    {q.explanation}
                  </p>
                </div>
              ))}
            </div>

            <Button className="w-full mt-4" onClick={handleReset}>
              {score >= 2 ? "Continue Roadmap" : "Review Concepts"}
            </Button>
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
