"""Suggested starting points for retrieval and ranking methods."""

from __future__ import annotations

from typing import Any

from common.config import SUPPORTS_K
from index.access import LexicalIndex
from retrieval.baseline import b0_retrieve


def retrieve_and_rank(
    question: str,
    options: list[str],
    index: LexicalIndex,
    config: dict[str, Any],
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    """Return the final ranked supports for one survey question.

    Args:
        question: Exact question text from the configured question file.
        options: Exact answer-option strings in their original order.
        index: Already-open LexicalIndex supplied by the runner.
            It wraps the Whoosh index created by python -m index.build.
        config: Parsed settings from the INI file used for this run.
        api_key: Course API key, or ``None`` when the retrieval method does not need it.

    Returns:
        Exactly ``SUPPORTS_K`` dictionaries.
        Each dictionary must contain a unique corpus ``doc_id`` and a finite numeric ``score``.
        Scores must be in descending order.
        A method may search a larger internal pool before selecting these final supports.

        Example records from a full list of 100:
        [{"doc_id": "22E5PQJSLD", "score": 1.0}, ...]

    The runner checks the count, document IDs, uniqueness, scores, and order.
    You may replace this function or reorganise the internal pipeline.
    """
    # Keep B0 available for experiments. The INI setting selects which branch runs.
    method = str(config["retrieval"]["method"]).strip().lower()

    if method == "b0":
        return b0_retrieve(question, options, index, SUPPORTS_K)

    if method == "bm25":
        # TODO 1: Construct retrieval text from the question and answer options.
        # TODO 2: Use b0_retrieve in retrieval/baseline.py as a starting point for this branch.
        # Reuse its query parsing and index access. Canvas's "Local Search with Whoosh",
        # Steps 3-5, shows how to use BM25F and set K1 and B.
        # Replace B0's document-ID ordering with BM25F ranking and return hit.score
        # instead of the fixed score 1.0.
        # Use index.schema and index.searcher(...) with "text" in place of the example's "content".
        # The searchable "text" field combines title and content.
        # index.all_document_ids() lists IDs, and index.get_documents(ids) reads their text.
        # TODO 3: Return the ranked records described in Returns above.
        # Read hit["doc_id"] for the document ID. Week 08 calls this field "id".
        raise NotImplementedError("Implement the bm25 retrieval method")

    if method == "dense":
        # Import dense-only helpers here so B0 and BM25 do not load them.
        from api.embeddings import embed_texts
        from retrieval.vectors import (
            cosine_scores,
            get_document_batch,
            load_document_embeddings,
        )

        # Replace the final error with these steps as you implement them.
        # Select retrieval.method = dense after completing this branch.
        # The config points to supplied document vectors for either mini or full data.
        # Adapt the batched dense-search pattern from Week 08 Workshop, Checkpoint 3.
        # See dense_search and _merge_top_k in the workshop's utils/dense_utils.py.
        # The Week 08 live demo also shows query encoding and dense_search.
        # TODO 1: Construct query_text from the question and answer options.
        # TODO 2: Encode it with embed_texts. Row 0 of the returned matrix is the query vector.
        # query_vector = embed_texts(
        #     [query_text],
        #     api_key=api_key,
        #     base_url=str(config["api"]["base_url"]),
        # )[0]
        # document_vectors, document_ids = load_document_embeddings(config)
        # batch_size = config["retrieval"]["batch_size"]
        # for start in range(0, len(document_ids), batch_size):
        #     vector_batch, id_batch = get_document_batch(
        #         document_vectors, document_ids, start, batch_size
        #     )
        #     batch_scores = cosine_scores(query_vector, vector_batch)
        #     TODO 3: Retain candidate documents from this batch.
        # TODO 4: Merge candidates across batches and return the final SUPPORTS_K records.
        # Use unique doc_id values and finite scores in descending order.
        raise NotImplementedError("Implement the dense retrieval method")

    # If you add a method name in the config, implement its branch above too.
    raise ValueError(f"Unknown retrieval method: {method}")
