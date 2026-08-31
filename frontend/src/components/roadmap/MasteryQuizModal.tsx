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
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary" />
            Mastery Validation
          </DialogTitle>
          <DialogDescription>
            {isSubmitted 
              ? `You scored ${score} out of ${questions.length}.`
              : "Let's make sure you fully grasp these concepts before moving on."}
          </DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground gap-4">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <p className="text-sm">Generating AI Micro-Quiz...</p>
          </div>
        ) : error ? (
          <div className="py-4 text-center text-destructive">
            <p>{error}</p>
            <Button variant="outline" className="mt-4" onClick={handleReset}>Close</Button>
          </div>
        ) : questions.length > 0 && !isSubmitted ? (
          <div className="py-4 space-y-6">
            <div>
              <p className="text-xs font-semibold text-muted-foreground tracking-wider uppercase mb-2">
                Question {currentQuestionIdx + 1} of {questions.length}
              </p>
              <h3 className="text-lg font-medium leading-tight">
                {questions[currentQuestionIdx].text}
              </h3>
            </div>

            <RadioGroup 
              value={selectedAnswers[currentQuestionIdx]?.toString() || ""}
              onValueChange={handleSelect}
              className="space-y-3"
            >
              {questions[currentQuestionIdx].options.map((opt, i) => (
                <div key={i} className="flex items-center space-x-2 border rounded-lg p-3 hover:bg-muted/50 transition-colors">
                  <RadioGroupItem value={i.toString()} id={`opt-${i}`} />
                  <Label htmlFor={`opt-${i}`} className="flex-1 cursor-pointer leading-relaxed font-normal">
                    {opt}
                  </Label>
                </div>
              ))}
            </RadioGroup>

            <div className="flex justify-between items-center pt-4">
              <span className="text-sm text-muted-foreground">
                Answer required
              </span>
              <Button 
                onClick={handleNext}
                disabled={selectedAnswers[currentQuestionIdx] === undefined}
              >
                {currentQuestionIdx === questions.length - 1 ? 'Submit & Grade' : 'Next Question'}
              </Button>
            </div>
          </div>
        ) : isSubmitted ? (
          <div className="py-4 space-y-6">
            <div className={`p-4 rounded-lg flex items-start gap-3 ${score >= 2 ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
              {score >= 2 ? (
                <CheckCircle2 className="w-6 h-6 text-green-500 shrink-0" />
              ) : (
                <XCircle className="w-6 h-6 text-red-500 shrink-0" />
              )}
              <div>
                <h4 className={`font-semibold ${score >= 2 ? 'text-green-500' : 'text-red-500'}`}>
                  {score >= 2 ? "Milestone Mastered!" : "Review Required"}
                </h4>
                <p className="text-sm mt-1 leading-relaxed">
                  {score >= 2 
                    ? "Great job! You demonstrated strong conceptual understanding." 
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
