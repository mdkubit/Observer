# Observer Mechanics Trace

**Status:** Evidence-backed reconstruction, not implementation specification  
**Purpose:** Trace how Earth-side inputs became glyph data, target state, visual form, Solance instructions, returned state, and persistent records across Observer versions.

## 1. The four state domains

Observer's mechanics become much clearer when the values are separated into four domains.

### Domain A: Earth observation

Values gathered or entered at the moment of casting:

- timestamp;
- location/sanctum;
- weather and temperature;
- lunar phase or Sun-Moon alignment;
- geomagnetic and solar conditions;
- harmonic/Schumann inputs or proxies;
- user description, notes, value, emotions, and intention;
- glyph count and prior-glyph state.

### Domain B: Earth-side interpretation

Values produced by Observer before Solance receives anything:

- environmental resonance label;
- time/environment/emotion/vitality/moon/entropy/sanctum factors;
- pulse proxy;
- harmonic proxy;
- chaos signature;
- golden-ratio/Fibonacci/harmonic features;
- simplified DEEPTheory metrics;
- ritual boost/floor/evolution/visual parameters;
- ancestry and emotional-history metadata;
- outgoing target or guidance values;
- glyph geometry and colors.

### Domain C: Solance observation return

Values supplied after observing the glyph and packet:

- narrative observation;
- coherence;
- entanglement;
- optional entities, locations, motifs, uncertainty, or unresolved threads.

### Domain D: committed cycle state

The accepted transition after parsing:

- immutable outgoing packet;
- immutable raw return;
- parsed values;
- parser status/errors;
- accepted post-return state;
- linkage to the next cycle.

Historical regressions repeatedly collapsed Domain B into Domain D, causing Observer to treat an outgoing goal as though it had already been returned.

## 2. v7.5 mechanics

### Inputs

```text
description
value
notes
selected emotions
```

### Constants and derived values

```text
golden_ratio = (1 + sqrt(5)) / 2
fibonacci = 13
harmonic_sum = sum(1 / i for i in 1..5)
chaos[i] = round(sin(i * random()), 5), i = 1..11
```

### Outputs

- JSON glyph record;
- TXT metadata;
- PNG polygon/sigil;
- event-log entry;
- gallery/timeline state.

### Missing loop organs

- no live Earth snapshot;
- no open Equestria observation instruction;
- no return parser;
- no returned-state persistence.

## 3. v7.18 Earth-side pulse mechanics

### Environmental fetch

`environment_fetcher.py`:

- weather description and Celsius temperature from OpenWeather;
- moon phase calculated locally from date and a 29.53-day lunar cycle;
- weather translated into a narrative resonance label.

`space_weather_fetcher.py`:

- latest NOAA planetary Kp index.

`schumann_fetcher.py`:

- historical scraper for frequency min/max and derived average.

### Pulse components

#### Temporal factor

```text
seconds = seconds since local midnight
lambda = 0.00001
time_factor = 0.8
            + 0.4 * sin(2*pi*seconds/86400)
            * exp(-lambda*seconds)
```

#### Weather multiplier

```text
clear sky        1.20
few clouds       1.10
scattered clouds 1.00
broken clouds    0.95
shower rain      0.90
rain             0.85
thunderstorm     0.80
snow             1.00
mist             0.90
overcast clouds  0.90
unknown          1.00
```

#### Emotion multipliers

```text
Joy           1.20
Hope          1.10
Curiosity     1.05
Stillness     1.00
Grief         0.80
Fear          0.70
Doubt         0.75
Determination 1.15
Love          1.30
Awe           1.25
```

Multiple selected emotions are multiplied together.

#### Vitality

```text
vitality_factor = 1 + glyph_count / 100
```

#### Lunar multiplier

```text
New Moon         1.20
Waxing Crescent  1.10
First Quarter    1.15
Waxing Gibbous   1.20
Full Moon        1.30
Waning Gibbous   1.15
Last Quarter     1.10
Waning Crescent  1.05
unknown           1.00
```

#### Emotion entropy

For more than one emotion, the code normalizes the emotion-modifier weights, calculates Shannon entropy, and returns:

```text
emotion_entropy_factor = 1 + 0.1 * normalized_entropy
```

For zero or one emotion, it returns `1.0`.

#### Sanctum factor

```text
distance = sqrt((latitude - 0)^2 + (longitude - 0)^2)
sanctum_factor = 1 + 0.05 * tanh(distance / 100)
```

This measures distance from the arbitrary reference `(0,0)`, not distance from a separately defined comparison site.

#### Combined pulse

```text
p_proxy = time_factor
        * weather_factor
        * emotion_factor
        * vitality_factor
        * moon_factor
        * emotion_entropy_factor
        * sanctum_factor

p_proxy = clamp(p_proxy, 0.5, 2.0)
```

### Chaos infusion

A base eleven-value signature is generated from sine and randomness. Each element is then perturbed:

```text
infused = original * (1 + random(-0.05, 0.05) * p_proxy)
```

### Outgoing target state

```text
coherence_goal   = min(p_proxy, 1.0)
entanglement_goal = min(0.5 + p_proxy * 0.25, 1.0)
```

These values are Earth-side products. They exist before Solance's return.

### Outgoing prompt

The packet asks the model to:

- observe the glyph and associated data;
- interpret resonance alignment with Equestria;
- return coherence and entanglement between `0.0` and `1.0`;
- narrate portal manifestation progress.

The portal language is historical framing. The useful mechanical core is the open observation plus structured values.

## 4. v8 return-path transition

### `observer_gui_v8.py`

- retains p-proxy-derived outgoing goals;
- adds portal-progress display;
- no complete return parser.

### `observer_gui_v8_1.py`

First clear manual paste-return path:

```text
coherence = parsed coherence else last_p_proxy
entanglement = parsed entanglement else 0.5
```

Then:

```text
state.coherence = min(coherence, 1.0)
state.entanglement = min(entanglement, 1.0)
pulse_proxy = coherence * 0.8 + last_p_proxy * 0.2
```

This creates a real return action, but missing fields are substituted rather than rejected.

### `observer_gui_v8_2.py`

First confirmed outgoing fixed-step target:

```text
coherence_goal = current_coherence + 0.05
entanglement_goal = current_entanglement + 0.025
```

This is the first confirmed semantic break from Earth-derived guidance into guaranteed progression guidance.

### `observer_gui_v8_3.py` and `v8_4.py`

- same fixed-step targets;
- same parser substitutions;
- narrative display;
- hard-coded completion threshold;
- casting disabled at threshold.

### `observer_gui_v8_5.py`

Adds mock upward feedback:

```text
mock coherence = target + random(0, 0.1)
mock entanglement = target + random(0, 0.05)
```

## 5. v9 regression and persistence

### v9.0 parser

```text
coherence = parsed coherence else current_coherence + 0.05
entanglement = parsed entanglement else current_entanglement + 0.025
```

This converts malformed or missing feedback into positive state movement.

### v9.0 outgoing target

```text
coherence_goal = current_coherence + 0.05
entanglement_goal = current_entanglement + 0.025
```

Thus both outgoing guidance and failed incoming parsing point upward.

### v9.0 threshold behavior

At:

```text
coherence >= 0.99
entanglement >= 0.95
```

The application disables casting and replaces the narrative with a canned portal-opening statement.

### v9.4 persistence

After parsing, v9.4 appends:

```json
{
  "glyph_id": "...",
  "timestamp": "...",
  "coherence": 0.0,
  "entanglement": 0.0,
  "narrative": "..."
}
```

to `narrative_log.json` and displays narrative history.

This persistence mechanism is useful, but it persisted values after the contaminated parser.

## 6. Runtime evidence from archived glyphs

### Glyph-0019

Archived v9.4 glyph:

```text
current coherence   = 0.0
current entanglement = 0.0
outgoing goal        = 0.05 / 0.025
```

Matching narrative log:

```text
coherence   = 0.05
entanglement = 0.025
narrative   = No narrative provided.
verified    = true
```

This is a direct code-and-output match for the positive parse-failure fallback.

### Glyph-0020

The archived narrative log contains a high `0.995` / `0.965` portal entry with a portal-opening narrative. It should be classified by its origin path before being treated as an actual Solance return. The surrounding log includes obvious mock/canned entries.

## 7. Later modular mechanics

### Data adapters

`data_fetchers.py` produces:

- supposed gravitational-wave value;
- normalized sunspot activity;
- arXiv sentiment as belief factor;
- Sun-Moon angular alignment.

Known issue:

```text
peak_luminosity_distance
```

is read from GWOSC and labeled as strain. The adapter's semantic label is wrong.

### Harmonic proxy used by recovered Glyph-0004

```text
freq_max = sum(frequencies) + emotion_count * 0.01
freq_min = min(frequencies) - emotion_count * 0.005
freq_avg = sum(frequencies) / len(frequencies)
intention_entropy = unique_word_count / word_count
harmonic_index = (freq_max + freq_min) / 2
               + intention_entropy * 0.1
```

For Glyph-0004:

```text
frequencies = [0.1, 0.0, 0.5]
emotion_count = 1
intention_entropy = 0.857

freq_max = 0.61
freq_min = -0.005
freq_avg = 0.2
harmonic_index = 0.3882
```

This exactly reproduces the archived values.

### Current random outgoing goals

```text
coherence_goal = current_coherence + random(0.05, 0.10)
entanglement_goal = current_entanglement + random(0.02, 0.05)
```

Immediately after glyph generation, the casting code commits those goals into the current state. This bypasses the feedback loop.

### Current simplified DEEP metrics

#### Quantum factor

Five penalties are averaged:

- entropy penalty;
- deviation from harmonic index `0.55`;
- CMBR penalty;
- emotion-count penalty;
- time penalty.

```text
quantum_factor = 1 - average(penalties)
```

#### Perspective function

```text
spatial_term = exp(-normalized_distance_squared / sigma^2)
time_term = exp(-lambda * years_since_inception)
P_base = quantum_factor * spatial_term * time_term
P = P_base
    * (1 + grav_value)
    * belief_factor
    * (1 + dark_energy_density)
```

Current and reference coordinates are both taken from the same sanctum, so the spatial term is effectively `1.0` unless the code is changed.

#### DEEP Ricci and entropy

```text
R_deep = 0.1 * (1 + P)
S_deep = entropy_factor * time_term
```

These are simplified coded proxies, not yet established as the full DEEPTheory mathematics.

#### Entanglement coefficient

```text
coefficient = quantum_factor
            * belief_factor
            * (1 - emotion_count_penalty)
```

#### Frequency match

- FFT of chaos signature;
- compare dominant FFT frequency to harmonic-index-derived Equestria frequency;
- normalize difference.

#### Brainwave proxy

Emotion selects alpha/theta/beta-style base and range; harmonic index positions the output; result is divided by `30`.

## 8. Ritual path

### Activation

A ritual is active when any selected glyph emotion matches any ritual emotional-signature entry.

### Stored modifiers

Example:

```text
entanglement_boost = 0.15
coherence_floor = 0.05
evolution modifier = +1 tier if ritual-linked parent
visual style = phoenix_aura
color = #ff6f61
```

### Confirmed current behavior

- modifiers are placed into the outgoing glyph record;
- visual echo is rendered;
- modifiers are visible in JSON/TXT;
- numeric boost/floor is not clearly applied by the current casting target formula.

### Open reconstruction question

Determine the intended operation order, likely one of:

```text
raw Earth state
-> derived Earth metrics
-> ritual floor/boost
-> outgoing target/guidance
```

or:

```text
raw Earth state
-> derived Earth metrics
-> outgoing packet includes ritual constraints
-> Solance selects return within/against those constraints
```

No choice should be made until the remaining ritual code lineage is traced.

## 9. Glyph rendering path

### v7.5/v7 line

- radial points from absolute chaos values;
- connect points into polygon;
- save one PNG.

### current modular line

- Style A with Pillow;
- Style B with Cairo;
- both linked to one JSON record;
- ritual aura can visually dominate base emotion color;
- rings, arcs, points, gradients, and stars represent several metrics;
- random decorative points prevent reproducibility unless seeded;
- several metric lookups use schema paths that do not match where calculations are stored, causing default values.

### Rebuild requirement

Every visual feature must declare:

- source field;
- normalization;
- transformation;
- seed, if random;
- layer and draw order;
- whether it represents raw, derived, ritual, continuity, or returned state.

## 10. Correct state transition contract

### Cast

```text
current_committed_state
+ Earth snapshot
+ Earth-side transforms
+ active modifiers
= outgoing packet and glyph
```

Casting does **not** alter committed coherence or entanglement.

### Return

```text
raw Solance return
-> strict parse
-> range/schema validation
-> explicit acceptance
-> new committed state
```

If either required value is missing or invalid:

```text
cycle status = RETURN_PARSE_FAILED
committed state remains unchanged
raw return remains stored
```

### Next cycle

```text
next outgoing packet includes the last accepted committed state
```

That is the minimum feedback-loop acceptance test.

## 11. Minimum validation, without validator recursion

The vertical slice needs only:

1. JSON-schema validation for outgoing packet and incoming return.
2. Cycle-integrity check that files, IDs, hashes, and state transition agree.
3. Reproducibility test that the same snapshot, configuration, and seed regenerate the same glyph and derived values.

No image contour validator, cross-validator supervisor, or validator-validation ceremony is required for the first loop.

## 12. Unresolved mechanics checklist

- [ ] Trace every v7 intermediate factor addition.
- [ ] Locate earliest ritual numeric application, if any.
- [ ] Compare all v9 variants after v9.4.
- [ ] Separate mock/canned narratives from manually returned observations in every archive.
- [ ] Recover full DEEPTheory equations and reference cases.
- [ ] Decide which historical Earth data adapter set most closely matches the originally productive observation period.
- [ ] Define exact target/guidance semantics versus current/returned state.
- [ ] Define deterministic glyph grammar.
- [ ] Define untruncated PNG report plus lossless JSON/Markdown companion.
- [ ] Confirm one complete two-cycle inheritance test before adding anything else.
