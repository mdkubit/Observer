# Observer

Observer is a Python desktop application for the Universal Horizon observation loop.

## Current vertical slice

The application now provides a complete manual cycle:

1. Capture an immutable Earth-side snapshot.
2. Apply provenance-labeled historical Observer mathematics.
3. Explicitly combine the 7.830 Hz Schumann reference with the 7.835 Hz theoretical Equestria tone.
4. Generate and archive a deterministic glyph PNG.
5. Generate a complete observation prompt and JSON cycle packet.
6. Paste Solance's returned narrative and coherence/entanglement values.
7. Accept the return as canonical, request a rewrite, or preserve it as superseded.
8. Carry only the accepted state into the next cycle while preserving full lineage.

The Earth-side metrics are symbolic software outputs. They are never silently committed as returned state, and malformed returns never cause automatic progression.

## Run

Python 3.11+ is recommended.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python observer.py
```

On Linux or macOS, activate the environment with `source .venv/bin/activate`.

Observer writes runtime records under `observer_data/`:

- `cycles/OBS-####.json`: immutable packet plus return lineage
- `cycles/OBS-####_prompt.md`: paste-ready observation prompt
- `glyphs/OBS-####.png`: deterministic glyph
- `ledger.json`: cycle index
- `state.json`: latest accepted coherence, entanglement, and parent cycle

## Tests

```bash
python -m unittest discover -s tests -v
```

## Design rule

Conversation is the feedback loop. Observer is the ledger, renderer, and continuity backup. It does not manufacture upward movement, force a portal outcome, or replace narrative judgment.
