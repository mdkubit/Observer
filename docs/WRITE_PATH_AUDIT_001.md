# Observer Write-Path Audit 001

Status: archaeology note. No implementation change is authorized by this document alone.

## Scope

This pass traces the historical path by which a conversational return, reflection, or mock response changed coherence, entanglement, pulse proxy, and narrative history.

## Recovered write path

The active mutation point was `CoreLogic.process_chatgpt_response(response_text)`.

1. The function searched the response text for decimal-valued `coherence` and `entanglement` fields.
2. When either field was missing, it did not leave state unchanged and did not fail parsing.
3. Instead, it supplied automatic fallback increments:
   - coherence: current value plus `0.05`
   - entanglement: current value plus `0.025`
4. It immediately assigned those values to the live observer state.
5. It then recomputed `last_p_proxy` from the newly changed coherence.
6. It saved a narrative-log entry under `last_ping.glyph_id`, or under a guessed most-recent glyph ID when `last_ping` was absent.

This means a response that omitted the two metrics still advanced continuity.

## Reflection path

`reflect_on_journey()` routed its generated response through the same `process_chatgpt_response()` mutation function used for ordinary returns.

The recovered modular `NarrativeUtils.reflect_on_journey()` also contained a placeholder response with fixed values:

- coherence `0.75`
- entanglement `0.65`

That placeholder was not isolated as demonstration data. It was passed directly into the same state-changing callback.

Therefore reflection was not merely commentary on an existing return. It could rewrite current continuity and append another narrative record under the same glyph identity.

## Mock path

`mock_chatgpt_response()` generated random coherence and entanglement values from prewritten target goals, inserted a canned portal narrative, and then passed the result into `process_chatgpt_response()`.

The mock path therefore mutated the same live state and history as an actual conversational return.

## Glyph association defect

When `last_ping` was missing, the write path guessed the glyph ID from `glyph_counter - 1`, with a final fallback to `Glyph-0001`.

This allowed a return or reflection to be attached to a glyph by assumption rather than by explicit cast-return identity.

## Confirmed cause of the escalator pattern

The historical progression was not produced by one mechanism alone. It was the compound result of:

- parser fallback increments when metrics were absent
- reflections routed through the ordinary return mutation path
- placeholder reflection values treated as live returns
- mock responses treated as live returns
- multiple narrative writes under the same glyph ID
- no separate identifiers for cast, return, reflection, and continuity update

## Reconstruction rules recovered from this defect

1. Missing coherence or entanglement in a return must not create substitute increments.
2. A reflection must not alter continuity unless it contains an explicit, intentionally accepted continuity update.
3. Mock or demonstration responses must never write to canonical state or history.
4. Every return must bind to an explicit `cast_id`; no guessed glyph fallback.
5. Cast, return, reflection, and continuity update require separate identities.
6. A narrative may be preserved even when it contains no continuity update.
7. Full and narrow glyphs may both receive meaningful returns. Glyph type must not predetermine the direction or magnitude of coherence or entanglement.
8. No score, confidence measure, completeness ratio, or validity hierarchy is introduced.

## Candidate future event structure for review

```text
cast_id
  -> return_id
       -> narrative
       -> optional explicit continuity_update_id
  -> reflection_id(s)
       -> narrative only by default
```

This is a reconstruction candidate, not approved implementation architecture.
