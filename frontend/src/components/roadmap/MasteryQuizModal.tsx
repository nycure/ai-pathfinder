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
import { Loader2, Brain, CheckCircle2, XCircle, RotateCcw } from 'lucide-react';

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

function formatCodeIfNeeded(code: string): string {
  const cleaned = code.trim();
  if (cleaned.includes('\n')) {
    return cleaned;
  }
  let formatted = '';
  let indent = 0;
  const tokens = cleaned.split(/([{};])/g);
  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i].trim();
    if (!token) continue;
    if (token === '{') {
      formatted += ' {\n' + '  '.repeat(++indent);
    } else if (token === '}') {
      indent = Math.max(0, indent - 1);
      formatted += '\n' + '  '.repeat(indent) + '}';
    } else if (token === ';') {
      formatted += ';\n' + '  '.repeat(indent);
    } else {
      if (formatted.length > 0 && !formatted.endsWith('\n') && !formatted.endsWith('  ')) {
        formatted += ' ';
      }
      formatted += token;
    }
  }
  return formatted.trim();
}

function FormattedInlineText({ text }: { text: string }) {
  if (!text) return null;
  const parts = text.split(/(`[^`]+`)/g);
  return (
    <span>
      {parts.map((part, i) => {
        if (part.startsWith('`') && part.endsWith('`') && part.length > 2) {
          return (
            <code 
              key={i} 
              className="font-mono text-[11px] bg-muted/80 text-foreground px-1.5 py-0.5 rounded border border-border/60 mx-0.5"
            >
              {part.slice(1, -1)}
            </code>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </span>
  );
}

function FormattedQuizText({ text }: { text: string }) {
  if (!text) return null;

  const codeBlockRegex = /```(?:([a-zA-Z0-9_#+-]+)\s*)?\n?([\s\S]*?)```/g;
  const elements: React.ReactNode[] = [];
  let lastIndex = 0;
  let match;

  while ((match = codeBlockRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      const prose = text.slice(lastIndex, match.index).trim();
      if (prose) {
        elements.push(
          <div key={`prose-${lastIndex}`} className="text-sm font-semibold leading-relaxed text-foreground mb-2">
            <FormattedInlineText text={prose} />
          </div>
        );
      }
    }

    const lang = (match[1] || 'code').trim();
    const rawCode = match[2] || '';
    const formattedCode = formatCodeIfNeeded(rawCode);

    elements.push(
      <div 
        key={`code-${match.index}`} 
        className="my-3 rounded-xl border border-neutral-800 bg-neutral-900 text-neutral-100 overflow-hidden shadow-xs"
      >
        <div className="px-3.5 py-2 border-b border-neutral-800 bg-neutral-950/80 flex items-center justify-between text-[10px] font-mono text-neutral-400">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-neutral-700"></span>
            <span className="w-2 h-2 rounded-full bg-neutral-700"></span>
            <span className="w-2 h-2 rounded-full bg-neutral-700"></span>
            <span className="ml-1 uppercase tracking-wider font-semibold text-neutral-300">
              {lang}
            </span>
          </div>
        </div>
        <pre className="p-3.5 font-mono text-xs text-neutral-200 overflow-x-auto leading-relaxed whitespace-pre selection:bg-neutral-800">
          <code>{formattedCode}</code>
        </pre>
      </div>
    );

    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    const remaining = text.slice(lastIndex).trim();
    if (remaining) {
      elements.push(
        <div key={`prose-end`} className="text-sm font-semibold leading-relaxed text-foreground mt-2">
          <FormattedInlineText text={remaining} />
        </div>
      );
    }
  }

  if (elements.length === 0) {
    return (
      <div className="text-sm font-semibold leading-relaxed text-foreground">
        <FormattedInlineText text={text} />
      </div>
    );
  }

  return <div>{elements}</div>;
}

interface QuizSession {
  questions: QuizQuestion[];
  currentQuestionIdx: number;
  selectedAnswers: Record<number, number>;
  isSubmitted: boolean;
  score: number;
}

// In-memory cache preserving active quiz sessions per milestone node
const quizSessionCache: Record<string, QuizSession> = {};

export function MasteryQuizModal({ isOpen, onClose, nodeId }: MasteryQuizModalProps) {
  const { profile, roadmap, completeNode } = useRoadmapStore();
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  // Restore from cache or fetch when modal opens
  useEffect(() => {
    if (!isOpen || !nodeId) return;

    const cached = quizSessionCache[nodeId];
    if (cached && cached.questions.length > 0) {
      // Instant restore from cache without AI latency!
      setQuestions(cached.questions);
      setCurrentQuestionIdx(cached.currentQuestionIdx);
      setSelectedAnswers(cached.selectedAnswers);
      setIsSubmitted(cached.isSubmitted);
      setScore(cached.score);
      setIsLoading(false);
      setError('');
    } else {
      generateQuiz(false);
    }
  }, [isOpen, nodeId]);

  const generateQuiz = async (forceRefresh: boolean = false) => {
    if (!profile || !roadmap || !nodeId) return;
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
          roadmap,
          force_refresh: forceRefresh
        })
      });

      if (!response.ok) throw new Error('Failed to generate quiz');

      const data = await response.json();
      setQuestions(data.questions);
      setCurrentQuestionIdx(0);
      setSelectedAnswers({});
      setIsSubmitted(false);
      setScore(0);

      // Save to node session cache
      quizSessionCache[nodeId] = {
        questions: data.questions,
        currentQuestionIdx: 0,
        selectedAnswers: {},
        isSubmitted: false,
        score: 0,
      };
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (val: string) => {
    if (isSubmitted) return;
    const newAnswers = { ...selectedAnswers, [currentQuestionIdx]: parseInt(val) };
    setSelectedAnswers(newAnswers);
    if (nodeId && quizSessionCache[nodeId]) {
      quizSessionCache[nodeId].selectedAnswers = newAnswers;
    }
  };

  const handleNext = () => {
    if (currentQuestionIdx < questions.length - 1) {
      const nextIdx = currentQuestionIdx + 1;
      setCurrentQuestionIdx(nextIdx);
      if (nodeId && quizSessionCache[nodeId]) {
        quizSessionCache[nodeId].currentQuestionIdx = nextIdx;
      }
    } else {
      // Calculate score
      let correct = 0;
      questions.forEach((q, idx) => {
        if (selectedAnswers[idx] === q.correct_option_index) correct++;
      });
      setScore(correct);
      setIsSubmitted(true);
      if (nodeId && quizSessionCache[nodeId]) {
        quizSessionCache[nodeId].isSubmitted = true;
        quizSessionCache[nodeId].score = correct;
      }

      // If passing (>= 2/3), mark as completed
      if (correct >= 2) {
        completeNode(nodeId);
      }
    }
  };

  const handleRetakeQuiz = async () => {
    if (nodeId) {
      delete quizSessionCache[nodeId];
    }
    setQuestions([]);
    setCurrentQuestionIdx(0);
    setSelectedAnswers({});
    setIsSubmitted(false);
    setScore(0);
    await generateQuiz(true);
  };

  const handleModalClose = () => {
    if (isSubmitted && score >= 2 && nodeId) {
      delete quizSessionCache[nodeId];
    }
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleModalClose()}>
      <DialogContent className="sm:max-w-[580px] max-h-[92vh] overflow-y-auto bg-card border-border rounded-2xl shadow-xs">
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
            <Button variant="outline" className="mt-4" onClick={handleModalClose}>Close</Button>
          </div>
        ) : questions.length > 0 && !isSubmitted ? (
          <div className="py-3 space-y-5">
            <div>
              <p className="text-[10px] font-semibold text-muted-foreground tracking-wider uppercase mb-1.5">
                Question {currentQuestionIdx + 1} of {questions.length}
              </p>
              <div className="text-foreground">
                <FormattedQuizText text={questions[currentQuestionIdx].text} />
              </div>
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
                    <FormattedInlineText text={opt} />
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
                <div key={idx} className="space-y-2 pb-4 border-b border-border/60 last:border-0">
                  <div className="font-medium text-foreground">
                    <FormattedQuizText text={q.text} />
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Your answer: <FormattedInlineText text={q.options[selectedAnswers[idx]] || 'None'} />
                  </div>
                  <div className={`text-xs font-semibold ${selectedAnswers[idx] === q.correct_option_index ? 'text-emerald-700' : 'text-rose-700'}`}>
                    {selectedAnswers[idx] === q.correct_option_index 
                      ? '✓ Correct' 
                      : <span>✗ Incorrect. Correct: <FormattedInlineText text={q.options[q.correct_option_index]} /></span>}
                  </div>
                  <div className="bg-muted/50 p-2.5 rounded-lg text-muted-foreground mt-2 text-xs leading-relaxed">
                    <FormattedQuizText text={q.explanation} />
                  </div>
                </div>
              ))}
            </div>

            {score >= 2 ? (
              <Button className="w-full mt-4" onClick={handleModalClose}>
                Continue Roadmap
              </Button>
            ) : (
              <div className="flex gap-2.5 mt-4">
                <Button 
                  onClick={handleRetakeQuiz}
                  className="flex-1 bg-foreground text-background hover:bg-foreground/90 text-xs py-2 rounded-lg flex items-center justify-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Retake Quiz (New Questions)</span>
                </Button>
                <Button 
                  variant="outline" 
                  onClick={handleModalClose}
                  className="px-4 text-xs"
                >
                  Review Materials
                </Button>
              </div>
            )}
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
