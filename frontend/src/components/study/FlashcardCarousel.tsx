import { useState } from "react";
import { Flashcard } from "@/types/models";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ChevronLeft, ChevronRight, RotateCw, Shuffle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { SourceCitation } from "./SourceCitation";
import { cn } from "@/lib/utils";

interface FlashcardCarouselProps {
  flashcards: Flashcard[];
  onFinish?: () => void;
}

export function FlashcardCarousel({ flashcards, onFinish }: FlashcardCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [direction, setDirection] = useState(0);

  const currentCard = flashcards[currentIndex];
  const progress = ((currentIndex + 1) / flashcards.length) * 100;

  const handleNext = () => {
    if (currentIndex < flashcards.length - 1) {
      setIsFlipped(false);
      setDirection(1);
      setTimeout(() => setCurrentIndex(currentIndex + 1), 200);
    } else {
      onFinish?.();
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setIsFlipped(false);
      setDirection(-1);
      setTimeout(() => setCurrentIndex(currentIndex - 1), 200);
    }
  };

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  return (
    <div className="flex flex-col items-center w-full max-w-3xl mx-auto space-y-6">
      {/* Progress Header */}
      <div className="w-full space-y-2">
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>Card {currentIndex + 1} of {flashcards.length}</span>
          <span>{Math.round(progress)}% Complete</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Card Container */}
      <div className="relative w-full aspect-[3/2] perspective-1000">
        <motion.div
          className="w-full h-full relative preserve-3d cursor-pointer"
          animate={{ rotateY: isFlipped ? 180 : 0 }}
          transition={{ duration: 0.6, type: "spring", stiffness: 260, damping: 20 }}
          onClick={handleFlip}
          style={{ transformStyle: "preserve-3d" }}
        >
          {/* Front Side */}
          <Card className="absolute w-full h-full backface-hidden flex flex-col justify-center items-center p-8 text-center shadow-md hover:shadow-lg transition-shadow bg-card">
            <CardContent className="space-y-4">
              <h3 className="text-xl font-semibold text-muted-foreground uppercase tracking-wider text-xs mb-4">Question</h3>
              <p className="text-2xl font-medium leading-relaxed">{currentCard.front}</p>
            </CardContent>
            <div className="absolute bottom-4 text-xs text-muted-foreground">
              Click to flip
            </div>
          </Card>

          {/* Back Side */}
          <Card 
            className="absolute w-full h-full backface-hidden flex flex-col justify-center items-center p-8 text-center shadow-md bg-primary/5 border-primary/20" 
            style={{ transform: "rotateY(180deg)" }}
          >
            <CardContent className="space-y-4 w-full">
              <h3 className="text-xl font-semibold text-primary uppercase tracking-wider text-xs mb-4">Answer</h3>
              <p className="text-xl leading-relaxed">{currentCard.back}</p>
              
              {currentCard.source && (
                 <div className="pt-6 mt-4 border-t w-full flex justify-center">
                    <SourceCitation source={currentCard.source} compact />
                 </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4">
        <Button 
          variant="outline" 
          size="icon" 
          onClick={handlePrev} 
          disabled={currentIndex === 0}
          className="h-12 w-12 rounded-full"
        >
          <ChevronLeft className="h-6 w-6" />
        </Button>

        <Button 
          variant="default" 
          className="h-12 px-8 rounded-full text-lg"
          onClick={handleFlip}
        >
          {isFlipped ? "Show Question" : "Show Answer"}
        </Button>

        <Button 
          variant="outline" 
          size="icon" 
          onClick={handleNext} 
          disabled={currentIndex === flashcards.length - 1}
          className="h-12 w-12 rounded-full"
        >
          <ChevronRight className="h-6 w-6" />
        </Button>
      </div>

      <div className="flex gap-2">
        <Button variant="ghost" size="sm" onClick={() => {
            setCurrentIndex(0);
            setIsFlipped(false);
        }}>
            <RotateCw className="h-4 w-4 mr-2" />
            Reset
        </Button>
      </div>
    </div>
  );
}
