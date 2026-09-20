(() => {
  const slides = [...document.querySelectorAll(".slide")];
  const progress = document.querySelector(".progress span");
  const counter = document.querySelector("[data-slide-num]");
  const notesPanel = document.querySelector(".notes-panel");
  let index = 0;
  let fragment = 0;

  const fragmentsOn = (i) => [...slides[i].querySelectorAll(".fragment")];

  const showFragments = (i, count) => {
    fragmentsOn(i).forEach((el, n) => {
      el.classList.toggle("visible", n < count);
    });
  };

  const setHash = (i) => {
    const url = `${location.pathname}${location.search}#/${i + 1}`;
    history.replaceState(null, "", url);
  };

  const parseHash = () => {
    const m = location.hash.match(/#\/(\d+)/);
    if (!m) return 0;
    return Math.min(slides.length - 1, Math.max(0, Number(m[1]) - 1));
  };

  const renderNotes = () => {
    const aside = slides[index].querySelector("aside.notes");
    notesPanel.textContent = aside ? aside.textContent.trim() : "";
  };

  const go = (next) => {
    const prev = index;
    index = Math.min(slides.length - 1, Math.max(0, next));
    fragment = fragmentsOn(index).filter((el) => el.classList.contains("visible")).length;
    if (index !== prev) {
      slides[prev].classList.remove("active");
      showFragments(index, 0);
      fragment = 0;
    }
    slides[index].classList.add("active");
    showFragments(index, fragment);
    progress.style.width = `${((index + 1) / slides.length) * 100}%`;
    counter.textContent = `${index + 1} / ${slides.length}`;
    setHash(index);
    renderNotes();
  };

  const next = () => {
    const frags = fragmentsOn(index);
    if (fragment < frags.length) {
      fragment += 1;
      showFragments(index, fragment);
      return;
    }
    go(index + 1);
  };

  const prev = () => {
    if (fragment > 0) {
      fragment -= 1;
      showFragments(index, fragment);
      return;
    }
    const target = index - 1;
    if (target < 0) return;
    go(target);
    fragment = fragmentsOn(index).length;
    showFragments(index, fragment);
  };

  document.addEventListener("keydown", (e) => {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    if (["ArrowRight", "ArrowDown", "PageDown", " ", "Enter"].includes(e.key)) {
      e.preventDefault();
      next();
    } else if (["ArrowLeft", "ArrowUp", "PageUp", "Backspace"].includes(e.key)) {
      e.preventDefault();
      prev();
    } else if (e.key === "Home") {
      go(0);
    } else if (e.key === "End") {
      go(slides.length - 1);
    } else if (e.key === "f" || e.key === "F") {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen?.();
      } else {
        document.exitFullscreen?.();
      }
    } else if (e.key === "n" || e.key === "N" || e.key === "s" || e.key === "S") {
      document.body.classList.toggle("show-notes");
      renderNotes();
    }
  });

  document.addEventListener("click", (e) => {
    if (e.target.closest("a")) return;
    const x = e.clientX / window.innerWidth;
    if (x > 0.22) next();
    else prev();
  });

  window.addEventListener("hashchange", () => {
    const nextIndex = parseHash();
    if (nextIndex !== index) go(nextIndex);
  });

  go(parseHash());
})();
