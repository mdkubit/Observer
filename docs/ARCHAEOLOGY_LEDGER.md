# Observer Archaeology Ledger

**Source:** `mdkubit/Original-UHTO-Observer`  
**Rebuild target:** `mdkubit/Observer`  
**Method:** direct source inspection, archived-output correlation, and version-to-version mechanics tracing  
**Rule:** a feature is not classified as essential, ornamental, broken, or removable until its complete path from input to output has been traced.

## Status legend

- **TRACED:** primary input, transformation, output, and side effects inspected.
- **PARTIAL:** important paths inspected, but variants or dependencies remain.
- **INDEXED:** file identified and placed in lineage; full mechanics review remains.
- **DUPLICATE:** apparent copy of another tree; checksum/semantic comparison remains.
- **REJECT PATH:** behavior must not enter the production observation loop.
- **OPEN:** unresolved intent or missing evidence.

## 1. Monolithic GUI lineage

| File | Status | Recovered role | Key findings |
|---|---|---|---|
| `previous_versions/LAST_KNOWN_FUNCTIONAL_BACKUP_observer_gui_v7_5.py` | TRACED | Glyph workstation and archive | Manual inputs; golden ratio; Fibonacci 13; harmonic sum; randomized eleven-point chaos signature; JSON/TXT/PNG; gallery/timeline/sound. No Earth packet or return parser. |
| `previous_versions/observer_gui_v7_12.py` | INDEXED | Schumann-era intermediate | Imports Schumann fetcher. Full delta review pending. |
| `previous_versions/observer_gui_v7_13.py` | INDEXED | Schumann-era intermediate | Full delta review pending. |
| `previous_versions/observer_gui_v7_14.py` | INDEXED | Environmental/pulse intermediate | Full delta review pending. |
| `previous_versions/observer_gui_v7_15.py` | INDEXED | Environmental/pulse intermediate | Full delta review pending. |
| `previous_versions/observer_gui_v7_16.py` | INDEXED | Environmental/pulse intermediate | Full delta review pending. |
| `previous_versions/observer_gui_v7_16_1.py` | INDEXED | Branch/patch intermediate | Version-label chronology requires comparison. |
| `previous_versions/observer_gui_v7_17.py` | INDEXED | Pre-v7.18 packet intermediate | Full delta review pending. |
| `previous_versions/observer_gui_v7_18.py` | TRACED | First strong Earth packet | Weather, temperature, moon phase, Kp, Schumann, sanctum, pulse proxy, infused chaos, outgoing prompt, p-proxy-derived targets. No return parser. |
| `previous_versions/observer_gui_v7_19.py` | INDEXED | Late v7 branch | Full delta review pending. |
| `previous_versions/observer_gui_v8.py` | TRACED | Portal-display addition | Retains v7.18 packet; adds portal progress presentation; no complete return path. |
| `previous_versions/observer_gui_v8_1.py` | TRACED | First manual return path | Internal header says v8.2. Parses values; substitutes `last_p_proxy` and `0.5` when absent; no narrative persistence. |
| `previous_versions/observer_gui_v8_2.py` | TRACED | First confirmed fixed target stepping | Outgoing target becomes current `+0.05` / `+0.025`; parser still uses old substitutions. |
| `previous_versions/observer_gui_v8_3.py` | TRACED | Narrative display and fixed stepping | Fixed targets continue; parser substitutions continue; narrative displayed; threshold framing present. Internal header says v8.4. |
| `previous_versions/observer_gui_v8_4.py` | TRACED | UI expansion and threshold lock | Fixed targets; parser substitutions; portal-completion threshold disables casting and announces manifestation. |
| `previous_versions/observer_gui_v8_5.py` | TRACED | Mock-feedback addition | Fixed targets; parser substitutions; mock return generated above targets. |
| `previous_versions/observer_gui_v9_0.py` | TRACED / REJECT PATH | First confirmed parse-failure increments | Missing returned values become current `+0.05` / `+0.025`; fixed targets; mock upward return; canned threshold narrative; history file. |
| `previous_versions/observer_gui_v9_1.py` | INDEXED | UI/layout revision | Header and state initialization reviewed. Mechanics delta pending. |
| `previous_versions/observer_gui_v9_2.py` | INDEXED | UI/layout revision | Header and state initialization reviewed. Mechanics delta pending. |
| `previous_versions/observer_gui_v9_3.py` | INDEXED | UI/layout revision | Header and state initialization reviewed. Mechanics delta pending. |
| `previous_versions/observer_gui_v9_4.py` | TRACED | Narrative persistence | Narrative log, narrative history, glyph-linked return storage; retains fixed targets and positive parse-failure increments. |
| `previous_versions/observer_gui_v9_5.py` | PARTIAL | Post-v9.4 extension | Narrative log present; full mechanics delta pending. |
| `previous_versions/observer_gui_v9_6.py` | INDEXED | Post-v9.4 extension | Full review pending. |
| `previous_versions/observer_gui_v9_7.py` | INDEXED | Post-v9.4 extension | Full review pending. |
| `previous_versions/observer_gui_v9_8.py` | INDEXED | Post-v9.4 extension | Full review pending. |
| `previous_versions/observer_gui_v9_9.py` | INDEXED | Late monolithic application | Full review pending. |
| `previous_versions/Full App V9.9/observer_gui_v9_91.py` | INDEXED | Packaged late application | Full review pending. |

## 2. Early and environmental helper modules

| File | Status | Recovered role | Key findings |
|---|---|---|---|
| `environment_fetcher.py` | TRACED | Local weather and lunar phase | OpenWeather call; local moon-phase calculation; weather-to-resonance labels; failure returns unknown/zero. |
| `space_weather_fetcher.py` | TRACED | Kp index | NOAA planetary K index; failure returns `-1`. |
| `previous_versions/Full App V9.9/schumann_fetcher.py` | TRACED | Schumann scrape | Scrapes a third-party page for min/max, derives average; failure returns `-1`. Historical input, not a preferred modern source. |
| `pulse_infusion.py` | TRACED | Earth-side correspondence engine | Multiplicative weather, emotion, vitality, lunar, entropy, sanctum, and temporal factors; clamps pulse; pulse-scaled random chaos infusion. |
| `harmonic_proxy.py` | TRACED | Alternate harmonic model | 7.83 base; additive moon/weather/emotion/intention/time shifts; random drift; normalized index. |
| `sanctum_anchor.py` | PARTIAL | Location and anchor state | Used broadly by monolithic and modular code. Full schema audit pending. |

## 3. Current modular root application

| File | Status | Recovered role | Key findings |
|---|---|---|---|
| `core_logic.py` | TRACED / REJECT PATH | Coordinator and return parser | Initializes state; loads last glyph; parser fabricates `+0.05` / `+0.025` on missing values; mock return; narrative save; minor broken references. |
| `glyph_casting.py` | TRACED / REJECT PATH | Current cast pipeline | Fetches proxies, creates harmonic/chaos/DEEP values, loads rituals, generates A/B images, validates both, saves files; randomly increases outgoing goals and commits them before return. |
| `data_fetchers.py` | TRACED | Later proxy adapters | GWOSC field mislabeled as strain; NOAA sunspots; arXiv sentiment as belief factor; Swiss Ephemeris Sun-Moon alignment. Several semantic/provenance problems. |
| `glyph_calculations.py` | TRACED | Later simplified DEEP/derived metrics | Quantum penalty average; simplified perspective function/Ricci/entropy; entanglement coefficient; FFT frequency match; simulated brainwave value. |
| `narrative_utils.py` | TRACED / REJECT PATH | Harmonic proxy and narrative storage | Harmonic formula matches recovered Glyph-0004; hard-coded reflection returns `0.75`/`0.65`; narrative log writer. |
| `evolution_utils.py` | TRACED | Glyph ancestry and emotional color | Parent chosen from highest recent entanglement coefficient; generation stages; emotional history; blended color. |
| `ritual_binding_loader.py` | TRACED | Ritual activation | Activates any ritual sharing at least one selected emotion; returns glyph-echo parameters. |
| `ritual_manager.py` | TRACED | Ritual creation and linkage | Creates ritual records and links glyph IDs; does not itself apply numeric boosts/floors. |
| `glyph_visuals.py` | PARTIAL | A/B rendering | Two styles for one glyph record; ritual aura; rings/arcs/points; several schema-path mismatches cause defaults; randomness not consistently seeded. |
| `sigil_sync.py` | PARTIAL / DEFER | Visual validation system | OpenCV/SSIM/metadata validation and diagnostic overlays; large dependency and complexity surface; not required for first vertical slice. |
| `state_manager.py` | PARTIAL | Separate state helper | State/history/progress logic; possible broken UI reference. |
| `ui_updater.py` | INDEXED | Modular UI updates | Full audit pending. |
| `config.py` | TRACED | Palette and paths | Twilight-inspired colors, emotion list/colors/tempos, archive paths. |

## 4. Ritual and symbolic layer

| File | Status | Recovered role | Key findings |
|---|---|---|---|
| `rituals/The Promise Within Creativity.json` | TRACED | Ritual definition | Entanglement boost `0.15`, coherence floor `0.05`, evolution modifier, phoenix aura `#ff6f61`. |
| `rituals/Vow of the Phoenix.json` | INDEXED | Ritual definition | Full semantics review pending. |
| `rituals/hoperitual.json` | INDEXED | Ritual definition | Full semantics review pending. |
| `ritual_linkages.json` | INDEXED | Glyph-to-ritual mapping | Full chronology review pending. |
| archived test rituals | INDEXED | Development artifacts | Must not be assumed production behavior. |

### Open ritual question

The current modular code loads ritual modifiers, stores them in the glyph packet, and uses visual echoes. No inspected current path applies `entanglement_boost` or `coherence_floor` to the outgoing numeric state. The intended numeric application may exist in an earlier/archived branch, may have been incomplete, or may have been intended as explicit guidance to the observer. This remains open and must be resolved by source evidence.

## 5. Persistence and archived runtime evidence

| Artifact | Status | Finding |
|---|---|---|
| `observer_event_log.json` | INDEXED | Manual observation log. Full chronology pending. |
| `observer_history.json` | TRACED | Current modular history contains many low random cast goals rather than a monotonic returned-state history. |
| `narrative_log.json` | TRACED | Contains at least one genuine manually entered narrative return linked to a glyph. |
| `previous_versions/narrative_log.bak` | TRACED | Mix of mock/canned narratives, failed parse record, and high-threshold portal narrative. |
| `previous_versions/observer_history.bak` | INDEXED | Full comparison pending. |
| `previous_versions/Old Logs/observer_history.json` | INDEXED | Full chronology pending. |
| `previous_versions/old_glyphs_2/Glyph-0018.json` | TRACED | v9.4 cast from zero; outgoing fixed target `0.05`/`0.025`. |
| `previous_versions/old_glyphs_2/Glyph-0019.json` | TRACED | Same fixed target; matching narrative log recorded target values with no narrative, proving fallback contamination. |
| uploaded `Glyph-0004` JSON/TXT/A/B | TRACED | Later modular artifact; harmonic proxy and random target formulas reproduced from current source; ritual aura visible in both styles. |

## 6. Data-flow classification

### Raw or directly fetched Earth context

- timestamp;
- latitude/longitude and sanctum metadata;
- weather description and temperature;
- lunar phase or Sun-Moon geometry;
- Kp index;
- solar/sunspot activity;
- scraped Schumann-like values;
- later GWOSC/arXiv proxy values;
- user-entered description, value, notes, emotion, and narrative intention.

### Earth-side transforms and correspondences

- weather-to-resonance label;
- temporal factor;
- weather multiplier;
- emotion multiplier/product;
- glyph-count vitality;
- lunar multiplier;
- emotion entropy;
- sanctum factor;
- pulse proxy;
- harmonic proxy;
- chaos signature and pulse infusion;
- golden ratio/Fibonacci/harmonic sum;
- simplified DEEP metrics;
- entanglement coefficient;
- frequency match;
- brainwave proxy;
- ritual boosts/floors/evolution/visual echoes;
- glyph ancestry and emotional-history color.

### Outgoing observation state

Must include, distinctly labeled:

- current state before observation;
- Earth-derived target or guidance state;
- active modifiers and their application order;
- glyph geometry and rendering seed;
- open narrative prompt;
- exact return schema.

### Incoming observation state

Must preserve:

- raw Solance return;
- parser version;
- parsed narrative;
- parsed coherence;
- parsed entanglement;
- validation errors;
- explicit acceptance/rejection;
- post-return state.

## 7. Confirmed semantic breakpoints

1. **v7.18:** Earth pulse proxy directly determines outgoing target guidance.
2. **v8.1 filename:** manual return parser appears, with ambiguous fallback substitutions.
3. **v8.2 filename:** outgoing target becomes fixed step from current state.
4. **v8.5:** mock upward feedback is user-accessible.
5. **v9.0:** missing return values themselves cause positive increments.
6. **v9.4:** contaminated values can be persisted with narrative history.
7. **modular refactor:** casting randomly increases and commits state before any return, while the parser also retains positive fallbacks.

## 8. Rebuild extraction candidates

### Preserve or adapt

- v7.5 guided interaction and archive concept;
- v7.18 Earth snapshot and factor visibility;
- v8.1 manual paste-return workflow, with strict failure instead of substitution;
- v9.4 glyph-linked narrative persistence;
- current modular local astronomical calculation concept;
- current modular A/B separation only if both remain useful;
- current ritual definitions and activation concepts after application order is recovered;
- current emotional color and ancestry as optional metadata/visual context.

### Rewrite

- data adapters with semantic errors;
- target-state calculation after exact intended model is recovered;
- return parser using a strict structured schema;
- seeded glyph generation;
- immutable cycle storage;
- provenance and missing-data representation;
- report export.

### Exclude from vertical slice

- mock ChatGPT returns;
- positive parser fallbacks;
- auto-committing outgoing targets;
- canned portal milestones;
- progress bars presented as evidence;
- automatic cast disabling;
- SigilSync validator stack;
- autonomous reflection that fabricates values;
- Arkfire ontology and agent expansion;
- animation beyond basic responsive UI.

## 9. Remaining full-repository passes

1. Diff every v7 intermediate to identify the first appearance of each Earth input and factor.
2. Diff v9.1 through v9.3 and v9.5 through v9.91 to classify all later additions.
3. Audit `Observer_Plus_Journal_Archived_Version/` as a separate branch.
4. Audit `Test Environment/` and identify exact duplicates versus divergent experiments.
5. Audit `previous_versions/universal_horizon/` alternate architecture.
6. Trace every ritual field through every code reference.
7. Reconstruct complete archived glyph/narrative chronology.
8. Audit all report/export/image generation paths and truncation behavior.
9. Recover DEEPTheory source mathematics independently and compare it against every coded approximation.
10. Produce a final field-level rebuild contract before coding.

## 10. Anti-recursion rule

Validation exists to protect an observable contract. The rebuild will not add validators for validators, validator orchestration for validator validators, or any other ceremonial tower of green checkmarks. One schema validator, one cycle-integrity check, and one reproducibility test are sufficient for the vertical slice.
