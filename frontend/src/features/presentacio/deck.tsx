"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";

import "./deck.css";
import { SLIDES } from "./slides";
import { DeckActiveContext, SlideOrderContext } from "./ui";

function parseHash() {
  const match = window.location.hash.match(/#\/(\d+)/);
  if (!match) return 0;
  return Math.min(SLIDES.length - 1, Math.max(0, Number(match[1]) - 1));
}

function fragmentNodes(root: HTMLElement, slideIndex: number) {
  const slide = root.querySelectorAll(".tfm-slide")[slideIndex];
  if (!slide) return [];
  return [...slide.querySelectorAll(".tfm-fragment")];
}

export function Deck() {
  const rootRef = useRef<HTMLDivElement>(null);
  const indexRef = useRef(0);
  const fragmentRef = useRef(0);
  const [index, setIndex] = useState(0);
  const [fragment, setFragment] = useState(0);
  const [notesOn, setNotesOn] = useState(false);
  const [notes, setNotes] = useState("");

  const syncChrome = useCallback((nextIndex: number, nextFragment: number) => {
    const root = rootRef.current;
    if (!root) return;
    fragmentNodes(root, nextIndex).forEach((node, n) => {
      node.classList.toggle("is-on", n < nextFragment);
    });
    setNotes(root.querySelectorAll(".tfm-slide")[nextIndex]?.querySelector(".tfm-notes")?.textContent?.trim() ?? "");
  }, []);

  const go = useCallback(
    (next: number, nextFragment = 0) => {
      const clamped = Math.min(SLIDES.length - 1, Math.max(0, next));
      indexRef.current = clamped;
      fragmentRef.current = nextFragment;
      setIndex(clamped);
      setFragment(nextFragment);
      history.replaceState(null, "", `${location.pathname}${location.search}#/${clamped + 1}`);
    },
    [],
  );

  const next = useCallback(() => {
    const root = rootRef.current;
    if (!root) return;
    const total = fragmentNodes(root, indexRef.current).length;
    if (fragmentRef.current < total) {
      go(indexRef.current, fragmentRef.current + 1);
      return;
    }
    if (indexRef.current < SLIDES.length - 1) go(indexRef.current + 1, 0);
  }, [go]);

  const prev = useCallback(() => {
    const root = rootRef.current;
    if (!root) return;
    if (fragmentRef.current > 0) {
      go(indexRef.current, fragmentRef.current - 1);
      return;
    }
    if (indexRef.current === 0) return;
    const previous = indexRef.current - 1;
    go(previous, fragmentNodes(root, previous).length);
  }, [go]);

  useLayoutEffect(() => {
    go(parseHash(), 0);
  }, [go]);

  useLayoutEffect(() => {
    syncChrome(index, fragment);
  }, [index, fragment, syncChrome]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      if (["ArrowRight", "ArrowDown", "PageDown", " ", "Enter"].includes(event.key)) {
        event.preventDefault();
        next();
      } else if (["ArrowLeft", "ArrowUp", "PageUp", "Backspace"].includes(event.key)) {
        event.preventDefault();
        prev();
      } else if (event.key === "Home") {
        go(0, 0);
      } else if (event.key === "End") {
        go(SLIDES.length - 1, 0);
      } else if (event.key === "f" || event.key === "F") {
        if (!document.fullscreenElement) {
          void document.documentElement.requestFullscreen?.();
        } else {
          void document.exitFullscreen?.();
        }
      } else if (event.key === "n" || event.key === "N" || event.key === "s" || event.key === "S") {
        setNotesOn((open) => !open);
      }
    };

    const onClick = (event: MouseEvent) => {
      if ((event.target as HTMLElement | null)?.closest("a")) return;
      if (event.clientX / window.innerWidth > 0.22) next();
      else prev();
    };

    const onHash = () => {
      const hashed = parseHash();
      if (hashed !== indexRef.current) go(hashed, 0);
    };

    const root = rootRef.current;
    window.addEventListener("keydown", onKey);
    window.addEventListener("hashchange", onHash);
    root?.addEventListener("click", onClick);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("hashchange", onHash);
      root?.removeEventListener("click", onClick);
    };
  }, [go, next, prev]);

  return (
    <div ref={rootRef} className={notesOn ? "tfm-deck is-notes" : "tfm-deck"}>
      <p className="tfm-help">F pantalla · N notes · ← →</p>
      <div className="tfm-stage">
        <DeckActiveContext.Provider value={index}>
          {SLIDES.map(({ View }, i) => (
            <SlideOrderContext.Provider key={i} value={i}>
              <View />
            </SlideOrderContext.Provider>
          ))}
        </DeckActiveContext.Provider>
      </div>
      <p className="tfm-where">{SLIDES[index]?.section}</p>
      <div className="tfm-footer">
        <span>Studyraft · Hao Yang</span>
        <span>
          {index + 1} / {SLIDES.length}
        </span>
      </div>
      <div className="tfm-progress" aria-hidden="true">
        <span style={{ width: `${((index + 1) / SLIDES.length) * 100}%` }} />
      </div>
      <div className="tfm-notes-panel">{notes}</div>
    </div>
  );
}
