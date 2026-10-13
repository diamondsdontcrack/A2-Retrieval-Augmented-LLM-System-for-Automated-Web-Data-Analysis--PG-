"""Suggested starting points for evidence-judging methods."""

from __future__ import annotations

from typing import Any

from common.config import config_path, judging_count
from api.chat import chat
from judging.baseline import b0_judge


def judge_evidence(
    question: str,
    options: list[str],
    ranked_documents: list[dict[str, Any]],
    config: dict[str, Any],
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    """Return document-level judgments for one survey question.

    Args:
        question: Exact question text from the configured question file.
        options: Exact answer-option strings in their original order.
        ranked_documents: The 100 supports produced by retrieval.
            Each record contains ``rank``, ``doc_id``, ``score``, ``title``, ``text``, ``source``, ``group``, and ``url``.
        config: Parsed settings from the INI file used for this run.
            The ``judging.judge_k`` value is an integer from 1 to 100. The default is 20.
        api_key: Course API key, or ``None`` when the judging method does not need it.

    Returns:
        Exactly ``judge_k`` dictionaries for distinct documents selected from ``ranked_documents``.
        Each dictionary must contain ``doc_id`` and ``option``.
        The option must be one exact string from ``options`` or ``non_relevant``.
        A short ``reason`` is optional.

        Example record:
        {"doc_id": "2WZHJKU27B", "option": "Mobile", "reason": "B0 token overlap"}

    The runner checks the count, document IDs, uniqueness, and option strings.
    You may replace this function or reorganise the internal pipeline.
    """
    # Retrieval and judging have separate method settings, so either can be tested with B0.
    method = str(config["judging"]["method"]).strip().lower()
    judge_k = judging_count(config)

    if method == "b0":
        # B0 always takes the first judge_k supports. Your own method may select another subset.
        return b0_judge(options, ranked_documents[:judge_k])

    if method == "llm_judge":
        # TODO 1: Select exactly judge_k documents from the 100 ranked supports.
        # TODO 2: Construct the system and user prompts from the question, options, and selected documents.
        # TODO 3: Call call_judging_model(...) for your selected documents.
        # Start with batch judging in Week 08's demo: "Batch judge: one request for the selected reviews".
        # Its chat_many_in_one_prompt helper is in the demo's utils/judge_utils.py.
        # For a batch, request one JSON object containing a "judgments" list.
        # Example entry: {"doc_id": "2WZHJKU27B", "option": "Mobile"}.
        # The call is: reply = call_judging_model(system_prompt, user_prompt, config, api_key)
        # Set judging.max_tokens in the INI file to allow enough output for every judgment in a batch.
        # TODO 4: Interpret the returned text and produce one valid judgment per selected document.
        # Week 08's "id" and "label" keys correspond to "doc_id" and "option" here.
        # The helper prints the original API or cached response so you can inspect it while debugging.
        # More judged documents usually cost more. Change judge_k in the INI file to control the count.
        raise NotImplementedError("Implement the llm_judge method")

    raise ValueError(f"Unknown judging method: {method}")


def call_judging_model(
    system_prompt: str,
    user_prompt: str,
    config: dict[str, Any],
    api_key: str | None,
) -> str:
    """Send two prompt strings using the judging model and cache settings.

    Args:
        system_prompt: Your instructions for judging evidence.
        user_prompt: Your question, options and selected evidence text.
        config: Uses judging.model, judging.max_tokens, api.base_url, api.use_cache and paths.api_cache.
            max_tokens limits the requested output tokens for this call.
        api_key: Course key passed to the command.

    Returns:
        The model's original reply as a string. The API helper also prints it.

    The helper sends the two prompt strings exactly as supplied.
    judge_evidence selects the documents and decides which fields to put in those strings.
    """
    # Keep gateway, model and cache settings in the INI file. Prompts come from your method.
    return chat(
        api_key=api_key,
        base_url=str(config["api"]["base_url"]),
        cache_path=config_path(config, "api_cache"),
        model=str(config["judging"]["model"]),
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=int(config["judging"]["max_tokens"]),
        use_cache=bool(config["api"]["use_cache"]),
    )
