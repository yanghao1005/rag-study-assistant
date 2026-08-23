"""Hierarchical / citation helper tests."""

from __future__ import annotations

from app.application.retrieval_policy import build_index_context, enrich_citations, is_broad_query
from app.domain.entities.document import Document
from app.ports.retrieval import RetrievedChunk


def test_broad_query_detects_spanish_summary() -> None:
    assert is_broad_query("Haz un resumen del temario")
    assert is_broad_query("Resume el tema en una frase.")
    assert is_broad_query("de que se trata")
    assert not is_broad_query("¿Qué es el ciclo de Calvin?")


def test_classify_query_detects_numbered_chapter() -> None:
    from app.application.retrieval_policy import classify_query, documents_for_chapter

    intent = classify_query("Resume el capítulo 7")
    assert intent.kind == "chapter"
    assert intent.chapter_number == 7

    first = classify_query("Explícame el primer capítulo")
    assert first.kind == "chapter"
    assert first.chapter_number == 1

    docs = [
        Document(id="a", user_id="u", subject_id="s", filename="7_Management.pdf"),
        Document(id="b", user_id="u", subject_id="s", filename="2_Strategic_Plan.pdf"),
    ]
    assert [item.filename for item in documents_for_chapter(docs, 7)] == ["7_Management.pdf"]


def test_diversify_chunks_round_robins_documents() -> None:
    from app.application.retrieval_policy import diversify_chunks

    chunks = [
        RetrievedChunk(
            id=f"{doc}-{i}",
            document_id=doc,
            subject_id="s",
            chunk_index=i,
            content=f"{doc}-{i}",
        )
        for doc in ("d1", "d2", "d3")
        for i in range(4)
    ]
    picked = diversify_chunks(chunks, per_document=2, limit=6)
    assert [chunk.document_id for chunk in picked] == ["d1", "d2", "d3", "d1", "d2", "d3"]


def test_index_context_filters_to_retrieved() -> None:
    docs = [
        Document(id="a", user_id="u", subject_id="s", filename="uno.pdf", synopsis="Tema A"),
        Document(id="b", user_id="u", subject_id="s", filename="dos.pdf", synopsis="Tema B"),
    ]
    text = build_index_context(docs, retrieved_ids={"a"}, include_all=False)
    assert "uno.pdf" in text
    assert "dos.pdf" not in text


def test_citations_include_filename_and_snippet() -> None:
    docs = [Document(id="doc-1", user_id="u", subject_id="s", filename="bio.pdf")]
    chunks = [
        RetrievedChunk(
            id="c1",
            document_id="doc-1",
            subject_id="s",
            chunk_index=0,
            content="El ATP es la moneda energética de la célula.",
            page_start=3,
            score=0.9,
        )
    ]
    citations = enrich_citations(chunks, docs)
    assert citations[0]["filename"] == "bio.pdf"
    assert citations[0]["page_start"] == 3
    assert "ATP" in str(citations[0]["snippet"])


def test_merge_scoped_results_fuses_per_document_lists() -> None:
    from app.application.retrieval_policy import merge_scoped_hybrid_results
    from app.ports.retrieval import HybridRetrievalResult

    left = HybridRetrievalResult(
        chunks=[
            RetrievedChunk(
                id="a",
                document_id="d1",
                subject_id="s",
                chunk_index=0,
                content="alpha",
                score=0.2,
            )
        ],
        dense_ids=["a"],
        lexical_ids=[],
    )
    right = HybridRetrievalResult(
        chunks=[
            RetrievedChunk(
                id="b",
                document_id="d2",
                subject_id="s",
                chunk_index=0,
                content="beta",
                score=0.9,
            )
        ],
        dense_ids=["b"],
        lexical_ids=["b"],
    )
    merged = merge_scoped_hybrid_results([left, right], final_k=2, rrf_k=60)
    assert [chunk.id for chunk in merged.chunks] == ["a", "b"]
    assert merged.chunks[0].score is not None


def test_generation_skips_admin_documents_unless_scoped() -> None:
    from app.application.retrieval_policy import (
        generation_search_query,
        is_admin_document,
        is_course_admin_text,
        select_documents_for_generation,
    )

    assert is_admin_document("0_Subject_presentation.pdf")
    assert is_admin_document("Guia_docente.pdf")
    assert not is_admin_document("6_Evaluation_of_investment_alternatives.pdf")
    assert not is_admin_document("1_BMC_OBS.pdf")

    docs = [
        Document(id="pres", user_id="u", subject_id="s", filename="0_Subject_presentation.pdf"),
        Document(id="bmc", user_id="u", subject_id="s", filename="1_BMC_OBS.pdf"),
        Document(id="eval", user_id="u", subject_id="s", filename="6_Evaluation_of_investment.pdf"),
    ]
    picked = select_documents_for_generation(docs, scoped_ids=())
    assert [item.id for item in picked] == ["bmc", "eval"]

    scoped = select_documents_for_generation(docs, scoped_ids=("pres",))
    assert [item.id for item in scoped] == ["pres"]

    assert is_course_admin_text("How is the course evaluated?")
    assert is_course_admin_text("c\u00f3mo se eval\u00faa la asignatura")
    assert not is_course_admin_text("What are the nine blocks of the Business Model Canvas?")
    query = generation_search_query("Direccio d'empreses", None)
    assert "Conceptos clave" in query
    assert "temario" in query
    assert "curso" in query


def test_resolved_document_ids_dedupes() -> None:
    from app.ports.retrieval import RetrievalFilters

    filters = RetrievalFilters(
        user_id="u",
        document_id="d1",
        document_ids=("d2", "d1", "d2"),
    )
    assert filters.resolved_document_ids() == ("d2", "d1")
