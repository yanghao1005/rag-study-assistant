import { useState, useEffect, useCallback } from "react";
import { Flashcard } from "@/types/models";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ChevronLeft, ChevronRight, RotateCw, RefreshCw, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { SourceCitation } from "./SourceCitation";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface FlashcardCarouselProps {
  flashcards: Flashcard[];
  onFinish?: () => void;
}

export function FlashcardCarousel({ flashcards, onFinish }: FlashcardCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [direction, setDirection] = useState(0);
  const [isFinished, setIsFinished] = useState(false);

  // Reset state when flashcards change
  useEffect(() => {
    setCurrentIndex(0);
    setIsFlipped(false);
    setIsFinished(false);
  }, [flashcards]);

  const currentCard = flashcards[currentIndex];
  // Calculate progress including finished state (100% when finished)
  const progress = ((currentIndex + (isFinished ? 1 : 0)) / flashcards.length) * 100;

  const handleNext = useCallback(() => {
    if (currentIndex < flashcards.length - 1) {
      setIsFlipped(false);
      setDirection(1);
      setTimeout(() => setCurrentIndex((prev) => prev + 1), 150);
    } else {
      setIsFinished(true);
      onFinish?.();
    }
  }, [currentIndex, flashcards.length, onFinish]);

  const handlePrev = useCallback(() => {
    if (currentIndex > 0) {
      setIsFlipped(false);
      setDirection(-1);
      setTimeout(() => setCurrentIndex((prev) => prev - 1), 150);
    }
  }, [currentIndex]);

  const handleFlip = useCallback(() => {
    setIsFlipped((prev) => !prev);
  }, []);

  const handleRestart = () => {
    setCurrentIndex(0);
    setIsFlipped(false);
    setIsFinished(false);
    setDirection(0);
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't handle if finished or if editing something else (though unlikely here)
      if (isFinished) return;
      
      switch (e.key) {
        case "ArrowRight":
        case "ArrowDown":
          handleNext();
          break;
        case "ArrowLeft":
        case "ArrowUp":
          handlePrev();
          break;
        case " ":
        case "Enter":
          e.preventDefault(); // Prevent scrolling
          handleFlip();
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleNext, handlePrev, handleFlip, isFinished]);

  if (isFinished) {
    return (
      <div className="flex flex-col items-center justify-center max-w-2xl mx-auto py-12 space-y-8 animate-in fade-in slide-in-from-bottom-4">
        <div className="bg-primary/10 p-8 rounded-full mb-4">
          <CheckCircle2 className="h-16 w-16 text-primary" />
        </div>
        
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-bold">Session Complete!</h2>
          <p className="text-muted-foreground">You&apos;ve reviewed all {flashcards.length} cards.</p>
        </div>

        <div className="flex gap-4">
           <Button onClick={handleRestart} variant="outline" className="gap-2">
             <RefreshCw className="h-4 w-4" />
             Review Again
           </Button>
           <Button asChild>
             <Link href="/dashboard">Back to Dashboard</Link>
           </Button>
        </div>
      </div>
    );
  }

  if (!currentCard) return null;

  return (
    <div className="flex flex-col items-center w-full max-w-3xl mx-auto space-y-8">
      {/* Progress Header */}
      <div className="w-full space-y-2">
        <div className="flex justify-between text-sm font-medium text-muted-foreground">
          <span>Card {currentIndex + 1} of {flashcards.length}</span>
          <span>{Math.round(progress)}% Complete</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Card Container */}
      <div className="relative w-full aspect-3/2 perspective-1000 group">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, x: direction * 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: direction * -50 }}
            transition={{ duration: 0.2 }}
            className="w-full h-full"
          >
            <motion.div
              className="w-full h-full relative preserve-3d cursor-pointer"
              animate={{ rotateY: isFlipped ? 180 : 0 }}
              transition={{ duration: 0.6, type: "spring", stiffness: 260, damping: 20 }}
              onClick={handleFlip}
              style={{ transformStyle: "preserve-3d" }}
            >
              {/* Front Side */}
              <Card className="absolute w-full h-full backface-hidden flex flex-col justify-center items-center p-8 text-center shadow-lg hover:shadow-xl transition-shadow bg-card border-2">
                <CardContent className="space-y-6 max-w-lg">
                  <span className="inline-block px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-xs font-bold uppercase tracking-wider">
                    Question
                  </span>
                  <p className="text-2xl md:text-3xl font-medium leading-relaxed font-serif">
                    {currentCard.front}
                  </p>
                </CardContent>
                <div className="absolute bottom-6 text-xs text-muted-foreground flex items-center gap-1.5 opacity-50 group-hover:opacity-100 transition-opacity">
                  <RotateCw className="h-3 w-3" />
                  Click or Space to flip
                </div>
              </Card>

              {/* Back Side */}
              <Card 
                className="absolute w-full h-full backface-hidden flex flex-col justify-center items-center p-8 text-center shadow-lg bg-primary/5 border-primary/20" 
                style={{ transform: "rotateY(180deg)" }}
              >
                <CardContent className="space-y-6 w-full max-w-lg overflow-y-auto max-h-full scrollbar-thin">
                  <span className="inline-block px-3 py-1 rounded-full bg-primary text-primary-foreground text-xs font-bold uppercase tracking-wider">
                    Answer
                  </span>
                  <div className="text-xl md:text-2xl leading-relaxed">
                    {currentCard.back}
                  </div>
                  
                  {currentCard.source && (
                     <div className="pt-6 mt-4 border-t border-primary/10 w-full flex justify-center">
                        <SourceCitation source={currentCard.source} compact />
                     </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-6">
        <Button 
          variant="outline" 
          size="icon" 
          onClick={handlePrev} 
          disabled={currentIndex === 0}
          className="h-14 w-14 rounded-full border-2"
          aria-label="Previous card"
        >
          <ChevronLeft className="h-6 w-6" />
        </Button>

        <Button 
          variant="default" 
          className="h-14 px-10 rounded-full text-lg shadow-md hover:shadow-lg transition-shadow"
          onClick={handleFlip}
        >
          {isFlipped ? "Show Question" : "Show Answer"}
        </Button>

        <Button 
          variant="outline" 
          size="icon" 
          onClick={handleNext}
          className="h-14 w-14 rounded-full border-2"
          aria-label="Next card"
        >
          {currentIndex === flashcards.length - 1 ? (
             <CheckCircle2 className="h-6 w-6" />
          ) : (
             <ChevronRight className="h-6 w-6" />
          )}
        </Button>
      </div>
      
      <div className="text-xs text-muted-foreground hidden md:block">
        Tip: Use arrow keys to navigate, Space to flip
      </div>
    </div>
  );
}
