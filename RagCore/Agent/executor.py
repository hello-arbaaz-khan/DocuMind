import re

from RagCore.Agent.state import AgentState
from RagCore.Agent.tools import DocumentSearchTool
from RagCore.ErrorsHandle.exceptions import AgentError
from RagCore.Retrieval.retrieval import RetrievalResult


class AgentExecutor:
    def __init__(
        self,
        search_tool: DocumentSearchTool,
        max_steps: int = 5,
        retrieval_top_k: int = 20,
        reranking_top_k: int = 5,
    ) -> None:
        self.search_tool = search_tool
        self.max_steps = max_steps
        self.retrieval_top_k = retrieval_top_k
        self.reranking_top_k = reranking_top_k

    
    def execute(
        self,
        queries: list[str],
        state: AgentState,
    ) -> list[RetrievalResult]:
        if not queries:
            raise AgentError(
                "Executor received no queries."
            )
    
        if len(queries) > self.max_steps:
            raise AgentError(
                "Agent exceeded maximum execution steps."
            )
    
        all_results: list[RetrievalResult] = []
        seen_chunk_ids: set[str] = set()
    
        for query in queries:
            state.retrieval_attempts += 1
    
            query_results = self.search_tool.search(
                query,
                document_ids=state.document_ids,
                retrieval_top_k=self.retrieval_top_k,
                reranking_top_k=self.reranking_top_k,
            )
    
            state.completed_queries.append(query)
    
            for result in query_results:
                if result.chunk_id not in seen_chunk_ids:
                    seen_chunk_ids.add(result.chunk_id)
                    all_results.append(result)
    
        state.candidates_count = len(all_results)
    
        return all_results

    @staticmethod
    def _normalize_content(
        content: str,
    ) -> str:
        return re.sub(
            r"\s+",
            " ",
            content,
        ).strip().casefold()

    @classmethod
    def _deduplicate(
        cls,
        candidates: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        unique_by_id: dict[
            str,
            RetrievalResult,
        ] = {}

        seen_content: set[str] = set()

        for candidate in candidates:
            if candidate.chunk_id in unique_by_id:
                continue

            normalized_content = cls._normalize_content(
                candidate.content
            )

            if not normalized_content:
                continue

            if normalized_content in seen_content:
                continue

            unique_by_id[
                candidate.chunk_id
            ] = candidate

            seen_content.add(
                normalized_content
            )

        return list(
            unique_by_id.values()
        )