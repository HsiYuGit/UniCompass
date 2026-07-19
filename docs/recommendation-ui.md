# Recommendation UI boundary

## What the frontend can decide

The frontend builds a transparent `ProgrammePrecheck` from the selected profile
and a programme record. It checks only the inputs already available in fixture
data:

- target degree and education level;
- estimated total credits; and
- the listed English proof threshold.

If all three pass, the programme appears in the **ready for agent** queue. A
failed check appears as a prerequisite to resolve, not as a final rejection.

## What remains with the backend agent

`backend/src/models/recommand_agent.py` is the authority for final
recommendations. It must:

1. classify each transcript course into a programme's required credit groups;
2. aggregate those groups and decide hard eligibility; then
3. rank eligible programmes using interests, experience, country preference,
   budget, verification status, and unmodeled requirements.

The current repository has no HTTP endpoint for `run_recommend_agent`. Until
one is introduced and documented in `docs/api-contract.md`, the frontend must
not present its local precheck as a final Safety, Match, or Reach result.
