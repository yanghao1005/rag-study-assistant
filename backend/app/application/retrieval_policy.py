"""Hierarchical index + optional agentic retrieval expansion."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any, Literal

from app.domain.entities.document import Document, DocumentChunk
from app.ports.llm import ChatCompletionMessage, EmbeddingPort, LLMPort
from app.ports.retrieval import (
    HybridRetrievalResult,
    RetrievalFilters,
    RetrievedChunk,
    VectorSearchPort,
)

QueryKind = Literal["summary", "chapter", "factual"]

_SUMMARY_QUERY = re.compile(
    r"\b(resumen|resumir|resum[ea]|overview|summar(y|ise|ize)|[ií]ndice|"
    r"de qu[eé]( se)? trata|de qu[eé] va|qu[eé] cubre|tema general|temario|"
    r"visi[oó]n general|en conjunto|asignatura|"
    r"todo el (material|contenido|curso|temario)|introduce)\b",
    re.IGNORECASE,
)
_CHAPTER_QUERY = re.compile(
    r"(primer[oa]?s?\s+cap[ií]tulo|"
    r"cap[ií]tulo\s*(\d+)|"
    r"chapter\s*(\d+)|"
    r"tema\s*(\d+)|"
    r"unidad\s*(\d+)|"
    r"introducci[oó]n)\b",
    re.IGNORECASE,
)
_LEADING_DOC_NUMBER = re.compile(r"^(\d+)[_\-\s.]")
_ADMIN_FILENAME = re.compile(
    r"(subject[_\s.-]*presentation|presentaci[oó]n[_\s.-]*(de[_\s.-]*)?(la[_\s.-]*)?(asignatura|curso|subject)|"
    r"syllabus|gu[ií]a[_\s.-]*docente|programa[_\s.-]*(de[_\s.-]*)?(la[_\s.-]*)?asignatura|"
    r"course[_\s.-]*guide|welcome[_\s.-]*session|bienvenida)",
    re.IGNORECASE,
)
_ADMIN_STUDY_TEXT = re.compile(
    r"(how is the (course|subject|module) evaluated|"
    r"c[oó]mo se eval[uú]a (el curso|la asignatura|la materia|este curso)|"
    r"evaluaci[oó]n de (la )?asignatura|"
    r"grading (scheme|policy|criteria) of the (course|subject)|"
    r"criterios de evaluaci[oó]n del (curso|m[oó]dulo)|"
    r"\bECTS\b|"
    r"gu[ií]a docente|course syllabus|"
    r"resultados de aprendizaje de (la )?asignatura|"
    r"learning outcomes of (this |the )?(course|subject)|"
    r"horario (de clase|del curso)|class schedule|"
    r"profesor (responsable|de la asignatura)|"
    r"who (teaches|is the teacher)|"
    r"fecha(s)? de (examen|entrega) del curso)",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class QueryIntent:
    kind: QueryKind
    chapter_number: int | None = None
    wants_intro: bool = False


def classify_query(question: str) -> QueryIntent:
    text = question.strip()
    chapter = _CHAPTER_QUERY.search(text)
    if chapter:
        number: int | None = None
        for group in chapter.groups():
            if group and str(group).isdigit():
                number = int(group)
                break
        intro = "introduc" in chapter.group(0).lower()
        if number is None and re.search(r"primer", chapter.group(0), re.IGNORECASE):
            number = 1
        return QueryIntent(kind="chapter", chapter_number=number, wants_intro=intro)
    if _SUMMARY_QUERY.search(text):
        return QueryIntent(kind="summary")
    return QueryIntent(kind="factual")


def is_broad_query(question: str) -> bool:
    return classify_query(question).kind == "summary"


def leading_document_number(filename: str) -> int | None:
    match = _LEADING_DOC_NUMBER.match(filename.strip())
    return int(match.group(1)) if match else None


def sort_course_documents(documents: list[Document]) -> list[Document]:
    def key(document: Document) -> tuple[bool, int, str]:
        number = leading_document_number(document.filename)
        return (number is None, number or 0, document.filename.lower())

    return sorted(documents, key=key)


def documents_for_chapter(documents: list[Document], chapter_number: int) -> list[Document]:
    return [
        document
        for document in documents
        if leading_document_number(document.filename) == chapter_number
    ]


def is_admin_document(filename: str) -> bool:
    """True for syllabus / course-presentation PDFs, not for numbered content chapters."""
    name = filename.strip()
    if leading_document_number(name) == 0:
        return True
    return bool(_ADMIN_FILENAME.search(name))


def is_course_admin_text(text: str) -> bool:
    """True when a card/question is about course logistics instead of the subject matter."""
    return bool(_ADMIN_STUDY_TEXT.search(text.strip()))


def select_documents_for_generation(
    documents: list[Document],
    *,
    scoped_ids: tuple[str, ...],
) -> list[Document]:
    """Prefer lecture notes over the course presentation unless the user scoped PDFs."""
    if scoped_ids:
        allowed = set(scoped_ids)
        picked = [document for document in documents if document.id in allowed]
        return sort_course_documents(picked)
    study = [document for document in documents if not is_admin_document(document.filename)]
    chosen = study if study else list(documents)
    return sort_course_documents(chosen)


def generation_search_query(subject_name: str, query: str | None) -> str:
    focus = (query or "").strip()
    base = (
        f"Conceptos clave, definiciones, modelos, marcos, procesos, fórmulas y técnicas de "
        f"{subject_name}. Material de estudio del temario."
    )
    if focus:
        return (
            f"{focus}. {base} "
            "No uses la guía docente, la presentación de la asignatura ni la evaluación del curso."
        )
    return (
        f"{base} "
        "No uses la guía docente, la presentación de la asignatura, créditos ECTS "
        "ni cómo se evalúa el curso."
    )


def search_query_for_intent(question: str, *, subject_name: str, intent: QueryIntent) -> str:
    if intent.kind == "summary":
        return (
            f"Temario, objetivos, introducción y visión general de {subject_name}. "
            "Contenidos principales de cada documento del curso."
        )
    if intent.kind == "chapter" and intent.chapter_number is not None:
        return (
            f"Capítulo {intent.chapter_number} tema {intent.chapter_number} "
            f"unidad {intent.chapter_number}. {question}"
        )
    if intent.kind == "chapter" and intent.wants_intro:
        return f"Introducción, presentación y primeros contenidos de {subject_name}. {question}"
    return question


def retrieved_from_stored(
    chunk: DocumentChunk, *, score: float | None = 0.2
) -> RetrievedChunk:
    return RetrievedChunk(
        id=chunk.id,
        document_id=chunk.document_id,
        subject_id=chunk.subject_id,
        chunk_index=chunk.chunk_index,
        content=chunk.content,
        chapter_name=chunk.chapter_name,
        page_start=chunk.page_start,
        page_end=chunk.page_end,
        metadata=chunk.metadata,
        score=score,
    )


def diversify_chunks(
    chunks: list[RetrievedChunk],
    *,
    per_document: int,
    limit: int,
) -> list[RetrievedChunk]:
    """Round-robin across documents so one PDF cannot dominate a summary."""
    buckets: dict[str, list[RetrievedChunk]] = {}
    order: list[str] = []
    for chunk in chunks:
        if chunk.document_id not in buckets:
            order.append(chunk.document_id)
            buckets[chunk.document_id] = []
        if len(buckets[chunk.document_id]) < per_document:
            buckets[chunk.document_id].append(chunk)
    picked: list[RetrievedChunk] = []
    depth = 0
    while len(picked) < limit:
        progressed = False
        for document_id in order:
            bucket = buckets[document_id]
            if depth < len(bucket):
                picked.append(bucket[depth])
                progressed = True
                if len(picked) >= limit:
                    break
        if not progressed:
            break
        depth += 1
    return picked


def merge_with_opening_chunks(
    result: HybridRetrievalResult,
    openings: list[DocumentChunk],
    *,
    per_document: int,
    limit: int,
) -> HybridRetrievalResult:
    combined: list[RetrievedChunk] = [
        retrieved_from_stored(chunk, score=0.25) for chunk in openings
    ]
    seen = {chunk.id for chunk in combined}
    for chunk in result.chunks:
        if chunk.id not in seen:
            combined.append(chunk)
            seen.add(chunk.id)
    fused = diversify_chunks(combined, per_document=per_document, limit=limit)
    return HybridRetrievalResult(
        chunks=fused,
        dense_ids=result.dense_ids,
        lexical_ids=result.lexical_ids,
    )


def build_index_context(
    documents: list[Document],
    *,
    retrieved_ids: set[str],
    include_all: bool = False,
) -> str:
    """Assemble a hierarchical document index for the LLM prompt."""
    lines: list[str] = []
    for document in sort_course_documents(documents):
        if not include_all and retrieved_ids and document.id not in retrieved_ids:
            continue
        synopsis = (document.synopsis or "").strip()
        if synopsis:
            lines.append(f"- {document.filename}: {synopsis}")
        else:
            lines.append(f"- {document.filename}")
    if not lines:
        return ""
    return "Índice de documentos (usa este mapa para no centrarte en un solo PDF):\n" + "\n".join(
        lines
    )


def format_context_blocks(chunks: list[RetrievedChunk], documents: list[Document]) -> str:
    names = {item.id: item.filename for item in documents}
    blocks: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        name = names.get(chunk.document_id, "documento")
        chapter = f" · {chunk.chapter_name}" if chunk.chapter_name else ""
        page = f" · pág. {chunk.page_start}" if chunk.page_start else ""
        blocks.append(f"[{index}] {name}{chapter}{page}\n{chunk.content}")
    return "\n\n".join(blocks) if blocks else "No retrieved context."


def system_prompt_for_intent(intent: QueryIntent) -> str:
    if intent.kind == "summary":
        return (
            "You are a study assistant. The user wants a high-level synthesis of the subject. "
            "Treat the document index as the syllabus and cover ALL listed documents. "
            "Do not zoom into a single chapter or PDF unless the user asked for it. "
            "Retrieved passages are supporting evidence, not the whole course. "
            "Cite sources as [n] when you use a passage."
        )
    if intent.kind == "chapter":
        target = (
            f"chapter {intent.chapter_number}"
            if intent.chapter_number is not None
            else "the introduction"
        )
        return (
            "You are a study assistant. The user asked about "
            f"{target}. Prefer that section. Answer using only the provided context. "
            "Cite sources as [n]."
        )
    return (
        "You are a study assistant. Answer using only the provided context. "
        "If the context is insufficient, say so. Cite sources as [n]."
    )


def enrich_citations(
    chunks: list[RetrievedChunk],
    documents: list[Document],
) -> list[dict[str, Any]]:
    names = {item.id: item.filename for item in documents}
    citations: list[dict[str, Any]] = []
    for index, chunk in enumerate(chunks, start=1):
        snippet = chunk.content.strip().replace("\n", " ")
        citations.append(
            {
                "index": index,
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "filename": names.get(chunk.document_id, "documento"),
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "chapter_name": chunk.chapter_name,
                "snippet": snippet[:280],
                "score": chunk.score,
            }
        )
    return citations


async def maybe_expand_agentic(
    *,
    question: str,
    first: HybridRetrievalResult,
    llm: LLMPort,
    embeddings: EmbeddingPort,
    retrieval: VectorSearchPort,
    filters: RetrievalFilters,
) -> HybridRetrievalResult:
    """Second-pass retrieval if the model judges context insufficient."""
    preview = "\n".join(f"- {chunk.content[:240]}" for chunk in first.chunks[:5]) or "(vacío)"
    plan = await llm.complete_json(
        messages=[
            ChatCompletionMessage(
                role="system",
                content=(
                    "Decide if the retrieved study context is enough to answer the question. "
                    'Return JSON: {"need_more": bool, "rewritten_query": string|null, '
                    '"reason": string}.'
                ),
            ),
            ChatCompletionMessage(
                role="user",
                content=f"Question: {question}\n\nContext preview:\n{preview}",
            ),
        ],
        schema_name="agentic_plan",
        temperature=0.0,
        max_tokens=200,
    )
    data = plan.data
    need_more = bool(data.get("need_more"))
    rewritten = str(data.get("rewritten_query") or "").strip()
    if not need_more or not rewritten:
        return first

    query_embedding = (await embeddings.embed([rewritten]))[0]
    second = await retrieval.hybrid_search(
        query_text=rewritten,
        query_embedding=query_embedding,
        filters=filters,
    )
    merged: dict[str, RetrievedChunk] = {chunk.id: chunk for chunk in first.chunks}
    for chunk in second.chunks:
        merged.setdefault(chunk.id, chunk)
    dense_ids = list(dict.fromkeys([*first.dense_ids, *second.dense_ids]))
    lexical_ids = list(dict.fromkeys([*first.lexical_ids, *second.lexical_ids]))
    return HybridRetrievalResult(
        chunks=list(merged.values()),
        dense_ids=dense_ids,
        lexical_ids=lexical_ids,
    )


def merge_scoped_hybrid_results(
    parts: list[HybridRetrievalResult],
    *,
    final_k: int,
    rrf_k: int,
) -> HybridRetrievalResult:
    """Fuse per-document hybrid lists when the user scoped several PDFs."""
    if not parts:
        return HybridRetrievalResult(chunks=[], dense_ids=[], lexical_ids=[])
    if len(parts) == 1:
        only = parts[0]
        return HybridRetrievalResult(
            chunks=only.chunks[:final_k],
            dense_ids=only.dense_ids,
            lexical_ids=only.lexical_ids,
        )
    ranks: dict[str, float] = {}
    by_id: dict[str, RetrievedChunk] = {}
    dense_ids: list[str] = []
    lexical_ids: list[str] = []
    for part in parts:
        dense_ids.extend(part.dense_ids)
        lexical_ids.extend(part.lexical_ids)
        for rank, chunk in enumerate(part.chunks, start=1):
            by_id.setdefault(chunk.id, chunk)
            ranks[chunk.id] = ranks.get(chunk.id, 0.0) + 1.0 / (rrf_k + rank)
    ordered = sorted(ranks, key=lambda cid: ranks[cid], reverse=True)[:final_k]
    fused = [replace(by_id[cid], score=ranks[cid]) for cid in ordered]
    return HybridRetrievalResult(
        chunks=fused,
        dense_ids=list(dict.fromkeys(dense_ids)),
        lexical_ids=list(dict.fromkeys(lexical_ids)),
    )
