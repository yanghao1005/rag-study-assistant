import { useState, useEffect } from "react";
import { QuizQuestion } from "@/types/models";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { CheckCircle2, XCircle, ChevronRight, RefreshCw, Trophy, AlertCircle, ArrowRight } from "lucide-react";
import { SourceCitation } from "./SourceCitation";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface QuizInterfaceProps {
  questions: QuizQuestion[];
  onFinish?: () => void;
  onRetake?: () => void;
  persistenceKey?: string;
}

export function QuizInterface({ questions, onFinish, onRetake, persistenceKey }: QuizInterfaceProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [userAnswers, setUserAnswers] = useState<number[]>(new Array(questions.length).fill(null));

  // Load state from local storage on mount
  useEffect(() => {
    if (!persistenceKey) return;
    
    try {
      const savedState = localStorage.getItem(persistenceKey);
      if (savedState) {
        const parsed = JSON.parse(savedState);
        // rudimentary validation
        if (
             typeof parsed.currentIndex === 'number' && 
             Array.isArray(parsed.userAnswers) &&
             parsed.userAnswers.length === questions.length
           ) {
          setCurrentIndex(parsed.currentIndex);
          setScore(parsed.score || 0);
          setIsCompleted(parsed.isCompleted || false);
          setUserAnswers(parsed.userAnswers);
          // Only restore transient state if we are on the same question index
          // But actually, restoring full state is better for exact resume.
          // However, restoring 'isAnswered' handling might contain complex UI state (alerts etc)
          // For simplicity, let's restore it.
          setIsAnswered(parsed.isAnswered || false);
          setSelectedOption(parsed.selectedOption); 
        }
      }
    } catch (e) {
      console.error("Failed to load quiz state", e);
    }
  }, [persistenceKey, questions.length]);

  // Save state to local storage on change
  useEffect(() => {
    if (!persistenceKey) return;
    
    const state = {
      currentIndex,
      score,
      isCompleted,
      userAnswers,
      isAnswered,
      selectedOption
    };
    
    localStorage.setItem(persistenceKey, JSON.stringify(state));
  }, [currentIndex, score, isCompleted, userAnswers, isAnswered, selectedOption, persistenceKey]);

  // Clear storage when finished or restarted
  const clearStorage = () => {
    if (persistenceKey) {
      localStorage.removeItem(persistenceKey);
    }
  };

  const currentQuestion = questions[currentIndex];
  // Progress bar logic: standard progress based on current index
  const progress = ((currentIndex + (isCompleted ? 1 : 0)) / questions.length) * 100;

  const handleOptionSelect = (value: string) => {
    if (isAnswered) return;
    setSelectedOption(parseInt(value));
  };

  const handleCheckAnswer = () => {
    if (selectedOption === null) return;
    
    const isCorrect = selectedOption === currentQuestion.correct_answer;
    if (isCorrect) {
      setScore(score + 1);
    }
    
    const newAnswers = [...userAnswers];
    newAnswers[currentIndex] = selectedOption;
    setUserAnswers(newAnswers);
    
    setIsAnswered(true);
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedOption(null);
      setIsAnswered(false);
    } else {
      setIsCompleted(true);
      onFinish?.();
    }
  };

  const handleRestart = () => {
    clearStorage();
    if (onRetake) {
      onRetake();
    } else {
      setCurrentIndex(0);
      setSelectedOption(null);
      setIsAnswered(false);
      setScore(0);
      setIsCompleted(false);
      setUserAnswers(new Array(questions.length).fill(null));
    }
  };

  if (isCompleted) {
    const percentage = Math.round((score / questions.length) * 100);
    let message = "Good effort!";
    if (percentage >= 90) message = "Excellent!";
    else if (percentage >= 70) message = "Great job!";
    else if (percentage < 50) message = "Keep studying!";

    return (
      <div className="flex flex-col items-center justify-center max-w-2xl mx-auto py-12 space-y-8 animate-in fade-in slide-in-from-bottom-4">
        <div className="bg-primary/10 p-8 rounded-full mb-4 ring-8 ring-primary/5">
          <Trophy className="h-16 w-16 text-primary" />
        </div>
        
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-bold">Quiz Completed!</h2>
          <p className="text-muted-foreground">You answered {score} out of {questions.length} correctly.</p>
        </div>

        <div className="text-center p-8 bg-card border rounded-2xl shadow-sm w-full max-w-md">
          <div className="text-6xl font-bold text-primary mb-2 tracking-tighter">{percentage}%</div>
          <p className="text-xl font-medium text-foreground">{message}</p>
        </div>

        <div className="flex gap-4">
           <Button onClick={handleRestart} variant="outline" size="lg" className="gap-2">
             <RefreshCw className="h-4 w-4" />
             Retake Quiz
           </Button>
           <Button asChild size="lg">
             <a href="/dashboard">Back to Dashboard</a>
           </Button>
        </div>
        
        {/* Review Section could go here if requested */}
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex justify-between items-end">
          <div>
             <h2 className="text-lg font-semibold text-foreground">Question {currentIndex + 1}</h2>
             <p className="text-sm text-muted-foreground">Select the best answer</p>
          </div>
          <div className="text-sm font-medium text-muted-foreground bg-secondary px-3 py-1 rounded-full">
            Score: {score}
          </div>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      <Card className="border-2 shadow-sm">
        <CardHeader>
          <CardTitle className="text-xl leading-relaxed font-medium">
            {currentQuestion.question}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <RadioGroup 
            value={selectedOption?.toString()} 
            onValueChange={handleOptionSelect}
            className="space-y-3"
          >
            {currentQuestion.options.map((option, index) => {
              const isSelected = selectedOption === index;
              const isCorrectAnswer = index === currentQuestion.correct_answer;
              
              // Styling logic based on answer state
              let itemClass = "flex items-center space-x-3 space-y-0 rounded-lg border p-4 transition-all cursor-pointer relative overflow-hidden";
              
              if (isAnswered) {
                if (isCorrectAnswer) {
                  itemClass += " border-green-500 bg-green-50/80 dark:bg-green-900/40 ring-1 ring-green-500";
                } else if (isSelected && !isCorrectAnswer) {
                  itemClass += " border-destructive bg-destructive/10 dark:bg-destructive/20 ring-1 ring-destructive";
                } else {
                   itemClass += " border-muted opacity-50";
                }
              } else if (isSelected) {
                itemClass += " border-primary bg-primary/10 dark:bg-primary/20 ring-2 ring-primary shadow-sm";
              } else {
                itemClass += " border-input hover:bg-accent hover:border-accent-foreground/20";
              }

              return (
                <div key={index} className={itemClass} onClick={() => handleOptionSelect(index.toString())}>
                  <RadioGroupItem value={index.toString()} id={`option-${index}`} disabled={isAnswered} />
                  <Label htmlFor={`option-${index}`} className="grow cursor-pointer font-normal text-base text-foreground">
                    {option}
                  </Label>
                  {isAnswered && isCorrectAnswer && <CheckCircle2 className="h-5 w-5 text-green-600" />}
                  {isAnswered && isSelected && !isCorrectAnswer && <XCircle className="h-5 w-5 text-destructive" />}
                </div>
              );
            })}
          </RadioGroup>

          {isAnswered && (
            <div className="mt-6 animate-in fade-in slide-in-from-top-2">
              <Alert variant={selectedOption === currentQuestion.correct_answer ? "default" : "destructive"} className={cn(
                selectedOption === currentQuestion.correct_answer ? "border-green-500 text-green-800 dark:text-green-300 bg-green-50 dark:bg-green-950/30" : ""
              )}>
                {selectedOption === currentQuestion.correct_answer ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
                ) : (
                  <AlertCircle className="h-4 w-4" />
                )}
                <AlertTitle>
                  {selectedOption === currentQuestion.correct_answer ? "Correct!" : "Incorrect"}
                </AlertTitle>
                <AlertDescription className="mt-2">
                  <div className="font-medium mb-1">Explanation:</div>
                  {currentQuestion.explanation}
                  {currentQuestion.source && (
                    <div className="mt-3 pt-3 border-t border-current/20">
                      <SourceCitation source={currentQuestion.source} compact />
                    </div>
                  )}
                </AlertDescription>
              </Alert>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-between border-t p-6 bg-muted/20">
            {!isAnswered ? (
               <Button 
                className="w-full sm:w-auto ml-auto px-8" 
                size="lg" 
                onClick={handleCheckAnswer} 
                disabled={selectedOption === null}
              >
                Check Answer
              </Button>
            ) : (
              <Button 
                className="w-full sm:w-auto ml-auto px-8 gap-2" 
                size="lg" 
                onClick={handleNext}
              >
                {currentIndex < questions.length - 1 ? "Next Question" : "Finish Quiz"}
                <ArrowRight className="h-4 w-4" />
              </Button>
            )}
        </CardFooter>
      </Card>
    </div>
  );
}
