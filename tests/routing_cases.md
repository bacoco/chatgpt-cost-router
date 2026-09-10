# Routing fixtures

The canonical executable inputs and expected outputs are in
[routing_cases.json](routing_cases.json). R01–R10 replace the original ten prose
examples; R11–R20 cover absent proof, authorization, bans, cost/time limits, unknown
cost, missing scheduler, expiry and no candidates.

Every case supplies the current execution context, authorized/required actions,
scoped synthetic observations, candidate steps and explicit expected status/route/
plan identity. Composite routes preserve scheduler and executor steps; transport
names are metadata, never extra route enums.

Run `python -m unittest discover -s tests -v` from the repository root. The tests use
explicit historical evaluation times so fixtures cannot silently become live
capability claims. Passing these deterministic cases does not measure LLM task
classification accuracy or real ChatGPT surface availability.
