"""Phase 6 TODO: evaluation harness.

For each question in questions.json:
  1. Run the full pipeline (retrieve -> answer). Record retrieved chunks + answer.
  2. LLM-as-judge (one model call each) scoring 1-5:
     - faithfulness: is every claim in the answer supported by the retrieved context?
     - context_precision: were the retrieved chunks relevant to the question?
  3. Save per-run scores (run_id, params, avg scores) to a table or CSV.

Then tune: chunk size 300/500/800, top_k 5/8/12, reranker on/off — keep what the
numbers favor. This is what turns the project from demo into engineering.
"""
