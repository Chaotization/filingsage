"""Phase 5 TODO: agentic query decomposition for multi-hop questions.

Plan:
  1. One model call classifies the question: SIMPLE or MULTI_HOP, and if multi-hop,
     returns sub-queries as JSON, e.g.
     "compare Tesla's and Ford's EV competition risks" ->
       ["Tesla risk factors EV competition", "Ford risk factors EV competition"]
  2. Run each sub-query through retrieval (hybrid once Phase 4 is done).
  3. Final model call synthesizes across all retrieved sets with citations.

Cleaner variant: define a search_filings(query, ticker_filter) tool with OpenAI function
tool-calling and let the model decide how many searches to run.
"""
