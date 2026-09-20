import type { ComponentType } from "react";

import { makeSection } from "./slides/00-section";
import { CoverSlide } from "./slides/01-cover";
import { ProblemSlide } from "./slides/02-problem";
import { CycleSlide } from "./slides/03-cycle";
import { ObjectivesSlide } from "./slides/11-objectives";
import { ScopeSlide } from "./slides/30-scope";
import { SotaMarketSlide } from "./slides/08-sota-market";
import { PositioningSlide } from "./slides/09-positioning";
import { TechSlide } from "./slides/31-tech";
import { ArchitectureSlide } from "./slides/12-architecture";
import { ArchFlowSlide } from "./slides/12c-arch-flow";
import { DbSlide } from "./slides/32-db";
import { UseCasesSlide } from "./slides/33-usecases";
import { QueEsRagSlide } from "./slides/04-que-es-rag";
import { SotaRagSlide } from "./slides/04-sota-rag";
import { ComFuncionaRagSlide } from "./slides/05-com-funciona";
import { SotaChunkSlide } from "./slides/05-sota-chunk";
import { RagIngestSlide } from "./slides/14-rag-ingest";
import { AiIntegrateSlide } from "./slides/35-ai-integrate";
import { RagHybridSlide } from "./slides/17-rag-hybrid";
import { RagIntentSlide } from "./slides/16-rag-intent";
import { GroundednessLimitSlide } from "./slides/07b-groundedness-limit";
import { TrustSlide } from "./slides/12b-trust";
import { Sm2Slide } from "./slides/25b-sm2";
import { DemoSlide } from "./slides/20-demo";
import { DemoBeatsSlide } from "./slides/21-demo-beats";
import { ShotDocumentsSlide } from "./slides/22-shot-documents";
import { ShotChatSlide } from "./slides/23-shot-chat";
import { ShotQuizSlide } from "./slides/24b-shot-quiz";
import { ShotFlashcardsSlide } from "./slides/24-shot-flashcards";
import { ShotPlannerSlide } from "./slides/25-shot-planner";
import { EvalTestsSlide } from "./slides/26-eval-tests";
import { EvalLatencySlide } from "./slides/27-eval-latency";
import { LimitsSlide } from "./slides/28-limits";
import { PlanSlide } from "./slides/34-plan";
import { FutureSlide } from "./slides/36-future";
import { CloseSlide } from "./slides/29-close";

export type DeckItem = {
  section: string;
  View: ComponentType;
};

const SecMotivacio = makeSection("01", "Motivació", ["PDF propis", "Al·lucinar", "Quatre baules"], "50 s el problema, 50 s el cicle.");
const SecObjectius = makeSection("02", "Objectius", ["El producte", "Cites", "SM-2"], "");
const SecMercat = makeSection("03", "El que ja existeix", ["ChatGPT", "Anki", "NotebookLM"], "Taula 50 s. SM-2 vs ITS 50 s.");
const SecDisseny = makeSection(
  "04",
  "Disseny de la solució",
  ["Hexàgon", "Ingestió", "Híbrid", "SM-2"],
  "Aquesta secció són ~10 min. No passis títols. No saltis Gao, híbrid ni SM-2.",
);
const SecDemo = makeSection("05", "Demo", ["Listo", "Citar", "Practicar"], "5 min en viu. Si va, salta captures.");
const SecAvaluacio = makeSection(
  "06",
  "Avaluació",
  ["Tests", "p50", "Límits"],
  "90 s. Tests 30, p50 40, límits 20. No inventis nDCG ni groundedness.",
);
const SecGestio = makeSection("07", "Pla i pressupost", ["Git", "390 h", "API"], "60 s. Tres comptes: hores, allotjament, tokens.");
const SecConclusions = makeSection(
  "08",
  "Conclusions",
  ["El cicle", "Límits", "Futur"],
  "45 s futur, 50 s tancament. No recitis pytest: ja és a #/37.",
);

export const SLIDES: DeckItem[] = [
  { section: "00 · Portada", View: CoverSlide },
  { section: "01 · Motivació", View: SecMotivacio },
  { section: "01 · Motivació", View: ProblemSlide },
  { section: "01 · Motivació", View: CycleSlide },
  { section: "02 · Objectius", View: SecObjectius },
  { section: "02 · Objectius", View: ObjectivesSlide },
  { section: "02 · Objectius", View: ScopeSlide },
  { section: "03 · Mercat", View: SecMercat },
  { section: "03 · Mercat", View: SotaMarketSlide },
  { section: "03 · Mercat", View: PositioningSlide },
  { section: "04 · Disseny", View: SecDisseny },
  { section: "04 · Disseny", View: TechSlide },
  { section: "04 · Disseny", View: ArchitectureSlide },
  { section: "04 · Disseny", View: ArchFlowSlide },
  { section: "04 · Disseny", View: DbSlide },
  { section: "04 · Disseny", View: UseCasesSlide },
  { section: "04 · Disseny", View: QueEsRagSlide },
  { section: "04 · Disseny", View: SotaRagSlide },
  { section: "04 · Disseny", View: ComFuncionaRagSlide },
  { section: "04 · Disseny", View: SotaChunkSlide },
  { section: "04 · Disseny", View: RagIngestSlide },
  { section: "04 · Disseny", View: AiIntegrateSlide },
  { section: "04 · Disseny", View: RagHybridSlide },
  { section: "04 · Disseny", View: RagIntentSlide },
  { section: "04 · Disseny", View: GroundednessLimitSlide },
  { section: "04 · Disseny", View: TrustSlide },
  { section: "04 · Disseny", View: Sm2Slide },
  { section: "05 · Demo", View: SecDemo },
  { section: "05 · Demo", View: DemoSlide },
  { section: "05 · Demo", View: DemoBeatsSlide },
  { section: "05 · Demo", View: ShotDocumentsSlide },
  { section: "05 · Demo", View: ShotChatSlide },
  { section: "05 · Demo", View: ShotQuizSlide },
  { section: "05 · Demo", View: ShotFlashcardsSlide },
  { section: "05 · Demo", View: ShotPlannerSlide },
  { section: "06 · Avaluació", View: SecAvaluacio },
  { section: "06 · Avaluació", View: EvalTestsSlide },
  { section: "06 · Avaluació", View: EvalLatencySlide },
  { section: "06 · Avaluació", View: LimitsSlide },
  { section: "07 · Gestió", View: SecGestio },
  { section: "07 · Gestió", View: PlanSlide },
  { section: "08 · Conclusions", View: SecConclusions },
  { section: "08 · Conclusions", View: FutureSlide },
  { section: "08 · Conclusions", View: CloseSlide },
];
