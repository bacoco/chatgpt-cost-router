# Isolated goal-fidelity prompt pilot

Experimental snapshot only. DO NOT MERGE THIS BRANCH INTO MAIN: application files are deliberately absent from this isolated tree.

12 synthetic cases, 6 use cases, 2 seeds, 3 arms (without, short, full): 72 planned independent completions on Qwen3-1.7B Q8_0, non-thinking. The full rule is the prompt approved in the conversation. No paid inference API. No production application changes. The workflow only triggers for the RUN file on this exact experimental branch, has a fixed timeout, and does not recur.

Primary metric: deterministic correctness of the structured answer. Secondary: formatting, truncation, tokens, latency, false success/unsupported-information task outcomes. This does not measure a general hallucination rate. Reference answers are not included in model inputs. Synthetic prior assistant messages test response to evidence; this is not a live autonomous-agent trajectory benchmark. Two seeds on the same case are not independent tasks. The small-model/convenience-sample result must not be generalized to frontier models.

Run locally with Python 3.11 and llama-cpp-python==0.3.16: `python benchmark/runner.py`. The model download is pinned to its official repository revision. Exact prompts, order, sampling, raw responses, model hash, grading details and completion status are recorded under benchmark/results/.
