import { useState } from "react";
import { QuizQuestion } from "@/types/models";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { CheckCircle, XCircle, ChevronRight, RefreshCw, Trophy } from "lucide-react";
import { SourceCitation } from "./SourceCitation";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface QuizInterfaceProps {
  questions: QuizQuestion[];
  onFinish?: () => void;
  onRetake?: () => void;
}

export function QuizInterface({ questions, onFinish, onRetake }: QuizInterfaceProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);

  // Track answers for review
  const [userAnswers, setUserAnswers] = useState<number[]>(new Array(questions.length).fill(-1));

  const currentQuestion = questions[currentIndex];
  const progress = ((currentIndex) / questions.length) * 100;

  const handleSubmit = () => {
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

  if (isCompleted) {
    const percentage = Math.round((score / questions.length) * 100);
    
    return (
      <div className="flex flex-col items-center justify-center max-w-2xl mx-auto py-12 space-y-8 animate-in fade-in slide-in-from-bottom-4">
        <div className="bg-primary/10 p-8 rounded-full mb-4">
          <Trophy className="h-16 w-16 text-primary" />
        </div>
        
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-bold">Quiz Completed!</h2>
          <p className="text-muted-foreground">Here&apos;s how you did</p>
        </div>

        <div className="text-center p-8 bg-card border rounded-2xl shadow-sm w-full">
          <div className="text-6xl font-bold text-primary mb-2">{percentage}%</div>
          <p className="text-xl text-muted-foreground">
            You scored {score} out of {questions.length}
          </p>
        </div>

        <div className="flex gap-4">
           {onRetake && (
            <Button onClick={onRetake} variant="outline" className="gap-2">
              <RefreshCw className="h-4 w-4" />
              Retake Quiz
            </Button>
           )}
           <Button onClick={() => window.location.reload()} variant="default">
             Start New Topic
           </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm font-medium">
          <span>Question {currentIndex + 1} of {questions.length}</span>
          <span>Score: {score}</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      <Card className="border-2">
        <CardHeader>
          <CardTitle className="text-xl leading-relaxed">
            {currentQuestion.question}
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-6">
          <RadioGroup 
            value={selectedOption !== null ? selectedOption.toString() : ""} 
            onValueChange={(val) => !isAnswered && setSelectedOption(parseInt(val))}
            className="space-y-3"
          >
            {currentQuestion.options.map((option, index) => {
              const isCorrect = index === currentQuestion.correct_answer;
              const isSelected = index === selectedOption;
              
              let styles = "border-2 rounded-lg p-4 cursor-pointer hover:bg-muted/50 transition-colors flex items-center gap-3";
              
              if (isAnswered) {
                if (isCorrect) {
                  styles = "border-green-500 bg-green-50 dark:bg-green-950/20";
                } else if (isSelected && !isCorrect) {
                  styles = "border-destructive bg-destructive/10";
                } else {
                   styles = "border-transparent opacity-50"; 
                }
              } else if (isSelected) {
                styles = "border-primary bg-primary/5 shadow-sm";
              } else {
                 styles = "border-muted shadow-sm"; 
              }

              return (
                <div key={index} className={styles} onClick={() => !isAnswered && setSelectedOption(index)}>
                  <RadioGroupItem value={index.toString()} id={`opt-${index}`} className="sr-only" />
                  <div className={cn(
                    "w-6 h-6 rounded-full border flex items-center justify-center shrink-0",
                    isAnswered && isCorrect ? "border-green-500 text-green-600" :
                    isAnswered && isSelected && !isCorrect ? "border-destructive text-destructive" :
                    isSelected ? "border-primary text-primary" : "border-muted-foreground"
                  )}>
                    {isAnswered && isCorrect ? <CheckCircle className="h-4 w-4" /> :
                     isAnswered && isSelected && !isCorrect ? <XCircle className="h-4 w-4" /> :
                     <span className="text-xs font-medium">{String.fromCharCode(65 + index)}</span>}
                  </div>
                  <Label htmlFor={`opt-${index}`} className="flex-1 cursor-pointer font-normal text-base">
                    {option}
                  </Label>
                </div>
              );
            })}
          </RadioGroup>

          {isAnswered && (
             <div className="mt-6 p-4 bg-muted/50 rounded-lg animate-in fade-in slide-in-from-top-2">
               <div className="flex items-center gap-2 mb-2 font-semibold">
                 {selectedOption === currentQuestion.correct_answer ? (
                   <span className="text-green-600 flex items-center gap-2">
                    <CheckCircle className="h-5 w-5" /> Correct!
                   </span>
                 ) : (
                    <span className="text-destructive flex items-center gap-2">
                      <XCircle className="h-5 w-5" /> Incorrect
                    </span>
                 )}
               </div>
               
               <p className="text-muted-foreground mb-4">{currentQuestion.explanation}</p>
               
               {currentQuestion.source && (
                 <SourceCitation source={currentQuestion.source} />
               )}
             </div>
          )}
        </CardContent>

        <CardFooter className="flex justify-end p-6 pt-0">
          {!isAnswered ? (
            <Button onClick={handleSubmit} disabled={selectedOption === null} size="lg">
              Submit Answer
            </Button>
          ) : (
            <Button onClick={handleNext} size="lg">
              {currentIndex < questions.length - 1 ? "Next Question" : "View Results"}
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
