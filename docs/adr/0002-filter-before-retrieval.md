# ADR 0002: access filtering happens before retrieval

**Status:** accepted

**Context.** Restricted documents (hr_only, finance_only) must never reach a user without clearance. Two designs:
filter the top k after retrieval, or restrict the search space first.

**Decision.** Filter before retrieval, in both stores. The Qdrant query carries a payload filter on
`access_level`. BM25 is built only over the chunks the caller may see, so restricted text cannot influence scores or
inverse document frequencies either. The semantic cache key includes the caller's allowed levels.

**Why not filter after.** Filtering the top k after retrieval wastes result slots on chunks the user cannot see,
which lowers recall for permitted answers, and it relies on every later stage (reranker, cache, prompt builder) to
remember to apply the filter. One missed stage leaks restricted text into the LLM context. The eval measures the
recall cost and leak counts of `none`, `post` and `pre` filtering side by side.

**Consequences.** One BM25 index per distinct allowed level set (four roles, so at most four, built lazily).
Ingesting a document invalidates them and the cache.
