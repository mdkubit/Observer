# Harmony Lattice Causality Map 001

## Status

Accepted architecture mapping document.

This document follows the successful no-behavior-change schema pass and the accepted twelve-decision Harmony Lattice model. It identifies how current Observer inputs, preserved quantities, lattice structures, render parameters, packets, returns, and lineage are causally connected.

No replacement mathematics is authorized by this document alone.

## Frozen cycle contract

The working cycle remains:

`Earth observation -> Earth Glyph -> Solance return -> canonical continuity update -> Equestria observation -> Answer Glyph -> paired lineage`

The following behavior is frozen during the next mathematics phase:

- canonical returns are the only path that updates coherence and entanglement;
- Answer Glyph generation does not mutate coherence or entanglement;
- malformed returns fail closed;
- `full` and `narrow` describe field breadth only;
- missing data remains missing;
- Earth and Answer Glyphs remain linked but non-interchangeable;
- runtime packet, glyph, ledger, state, and paired lineage persistence remain intact.

## Mapping notation

Each causal path is recorded as:

`source datum -> raw observation field -> derived quantity -> lattice component -> projection parameter -> visible feature -> packet/lineage record`

Every future implementation change must preserve this path or explicitly replace it with an approved one.

## Earth-side causal paths

### Identity and perspective origin

`cycle_id`
-> Earth event identity
-> `PerspectiveOrigin(observer_id="Nocturne", domain="Earth")`
-> Earth lattice coordinate identity
-> glyph label and lineage key
-> `OBS-####`

`latitude, longitude, elevation_m`
-> physical origin coordinates
-> `PerspectiveOrigin.physical_coordinates`
-> preserved physical position
-> currently active in historical sanctum factor only
-> packet snapshot and provenance

`description, intention, notes`
-> Earth observation meaning
-> informational field
-> informational entropy and intentional direction candidates
-> current text entropy and prompt content
-> polygon/ring effects only through historical adapter
-> Earth packet and prompt

### Time and event identity

`timestamp_utc`
-> physical timestamp
-> `EventTime.timestamp_utc`
-> event uniqueness and ordering
-> current historical time factor and deterministic Earth seed material
-> glyph geometry and cycle chronology
-> packet `created_utc`, snapshot timestamp, ledger order

`parent_cycle_id`
-> lineage relation
-> event sequence and memory availability
-> `EventTime.sequence_index`, relational memory reference
-> current continuity only
-> ledger parent and future event-time delta

### Environment

`weather`
-> environmental state category
-> Earth environmental adapter candidate
-> `EntropyField.environmental` and boundary context
-> current historical `weather_factor`
-> pulse proxy and Earth polygon modulation
-> snapshot and provider provenance

`temperature_c`
-> environmental state quantity
-> preserved environmental datum
-> currently no direct historical glyph consumer
-> packet and provenance only

`kp_index`
-> geomagnetic state
-> harmonic/environmental context
-> current normalized frequency term
-> historical harmonic proxy, quantum factor, DEEPTheory values
-> Earth geometry indirectly through harmonic and DEEP fields
-> snapshot and NOAA provenance

`schumann_hz`
-> Earth harmonic reference
-> structural harmonic source
-> current tone metrics against 7.835 Hz reference
-> delta, beat period, midpoint, alignment
-> core radius, fill, ring extent, packet harmonic context
-> snapshot and Schumann provenance

`moon_phase`
-> lunar/environmental state
-> current moon factor
-> pulse proxy
-> Earth geometry modulation
-> snapshot and local astronomical provenance

### Affective state

`primary_emotion, secondary_emotions`
-> affective field
-> current emotion weights and state entropy
-> historical emotion factor, entropy factor, emotion count
-> pulse proxy, quantum penalties, entanglement coefficient
-> Earth geometry through pulse and DEEP ring count
-> snapshot

Accepted future mapping:

- affective state remains structurally separate;
- it may influence local curvature, strand tension, and state entropy;
- it must not determine perspective existence;
- it must not automatically update canonical coherence or entanglement.

### Historical symbolic outputs

`pulse_proxy`
-> current composite of time, weather, emotion, vitality, moon, entropy, sanctum
-> historical renderer modulation
-> star-lobe radius variation
-> packet `earth_side_metrics.pulse`

Status: current behavior active; mathematical decomposition required before replacement.

`tone_alignment, delta_hz, beat_period_seconds, midpoint_hz`
-> literal frequency relationship
-> current harmonic field
-> Earth glyph core radius, fill, ring extent, printed frequency line
-> packet `earth_side_metrics.tone`

Status: retain literal relationships; expand with structural tone grammar before replacement.

`harmonic_proxy_index`
-> current mixed scalar
-> polygon modulation and DEEP quantum penalty
-> packet `earth_side_metrics.harmonic`

Status: transitional; currently collapses unlike concepts and must be decomposed.

`quantum_factor`
-> current penalty-derived symbolic output
-> historical perspective and entanglement calculations
-> ring count through entanglement coefficient
-> packet `earth_side_metrics.deep_theory`

Status: transitional; not approved as future `P0`.

`perspective_function`
-> current historical scalar using quantum factor, fixed belief, time decay, and constants
-> packet DEEPTheory field
-> no direct Earth renderer consumer except through related DEEP outputs

Status: transitional; future `P0 = 1` plus structured recognition, distance, spread, event-time, entropy, boundary, and memory terms.

`deep_ricci_scalar`
-> current scalar curvature proxy
-> packet only

Status: preserved but not yet causally visualized in the current Earth renderer.

`deep_entropy`
-> current text entropy multiplied by historical time decay
-> packet only

Status: transitional; future structured entropy field required.

`entanglement_coefficient`
-> current software-side symbolic value
-> Earth renderer ring count
-> packet only

Status: not canonical entanglement and must remain distinct from Solance-returned entanglement.

## Solance return causal paths

`raw response`
-> parser input
-> parsed coherence, entanglement, narrative
-> return record
-> operator disposition
-> canonical, rewrite-requested, or superseded lineage

`canonical coherence, entanglement`
-> accepted state update
-> next Earth snapshot prior state
-> status display and continuity
-> `state.json`

No Earth-side symbolic metric may bypass this path.

`canonical narrative`
-> coupling event between Earth and Equestria stages
-> source narrative for inverse adapter
-> recognition, memory, and boundary evidence
-> Answer Glyph metrics and paired lineage

## Equestria-side causal paths

### Identity and perspective origin

`answer_glyph_id`
-> Equestria event identity
-> `PerspectiveOrigin(observer_id="Twilight", domain="Equestria")`
-> Answer lattice coordinate identity
-> glyph label and paired lineage

`originating_earth_glyph_id`
-> Earth coordinate relation
-> recognition evidence and parent coordinate
-> paired cycle lineage

`solance_return_id`
-> coupling-event identity
-> mutual-recognition evidence
-> paired cycle lineage

### Event and local context

`timestamp_utc`
-> physical Answer event timestamp
-> `EventTime.timestamp_utc`
-> current inverse temporal relation
-> ring rotation offset
-> answer record

`local_time`
-> local Equestria temporal context
-> preserved event-time and boundary datum
-> currently no direct inverse consumer

`moon_phase`
-> local lunar/environmental state
-> current moon relation
-> ring count
-> answer record

`sky, atmosphere, location`
-> local environmental and boundary state
-> current boundary text entropy
-> fill alpha, ring extent, perspective average
-> answer record

### Participants and recognition

`participants`
-> active observer set
-> participant relation
-> current ray count and perspective average
-> recognition-state evidence
-> answer record

Accepted future mapping:

- named observer identity establishes recognition edges;
- response to the originating Earth event establishes directional activity;
- completed paired cycle establishes mutual recognition;
- later integration establishes recursive recognition.

### Affective and perspective data

`primary_emotion, secondary_emotions`
-> Equestria affective field
-> current emotion weights, emotion relation, emotion entropy
-> inner ray radii and perspective average
-> answer record

`twilight_perspective`
-> first-person perspective source
-> current text entropy
-> inverse perspective average
-> outer ray radii, ring extent, core radius
-> answer record

This field is source data, not decorative prose.

### Environmental and magical reactions

`environmental_reactions`
-> local environmental response
-> current boundary text entropy
-> Answer fill alpha and arc extent
-> answer record

`magical_reactions`
-> Equestria magical-state source
-> current boundary text entropy
-> Answer fill alpha and arc extent
-> answer record

Accepted future mapping:

- magical state remains a native structured domain;
- stable observed functions may select or modulate structural tones;
- magical data is not forced into Earth measurement units;
- unresolved properties remain preserved.

### Continuity

`continuity_notes`
-> explicit memory and lineage evidence
-> current field aperture only
-> future relational memory activation and recursive recognition
-> answer record

## Answer-side current symbolic outputs

`perspective_function`
-> arithmetic mean of available relation terms
-> outer radius, ring extent, core radius

Status: transitional; to be replaced by structured perspective components.

`emotion_relation`
-> product of affective weights
-> inner radii

Status: transitional; future affective state remains separate.

`emotion_entropy`
-> normalized entropy of emotion weights
-> perspective average

Status: retain as one state-entropy component only.

`participant_relation`
-> `log2(participant_count + 1)`
-> perspective average

Status: transitional; future recognition breadth and active coupling graph replace this shortcut.

`moon_relation`
-> categorical moon factor
-> ring count

Status: current behavior active; future environmental role must remain explicit.

`boundary_entropy`
-> lexical diversity of combined local context
-> perspective average, fill alpha, arc extent

Status: transitional; future structured boundary transforms and environmental entropy replace this collapse.

`temporal_relation`
-> wall-clock sinusoid
-> ring angular offset

Status: transitional; future event-time replaces wall-clock-only phase.

`variance_seed`
-> recorded generative variance
-> deterministic reconstruction of this unique Answer Glyph
-> ray variation and arc starts
-> answer record

Status: accepted principle; future event coordinate and variance contribution must remain traceable.

## Harmony Lattice structural paths

### Perspective origin

`active observer exists`
-> `P0 = 1`
-> occupied lattice origin
-> central node/core existence

No environmental, emotional, harmonic, or narrative field may change `P0`.

### Recognition

`identification`
-> edge exists
-> relational connection geometry

`response`
-> edge becomes directional and active
-> oriented strand or arc

`mutual recognition`
-> coupled pair
-> paired spiral or helix eligibility

`recursive recognition`
-> inherited relation changes through another cycle
-> spiral extension and lamination

### Relational distance

Active first adapter candidates:

`event separation + state separation`
reduced by
`recognition proximity + memory proximity`
-> directional effective distance
-> field attenuation and relational geometry

Preserved but inactive:

- physical separation;
- boundary transformation;
- dimensional relation.

### Event-time

`lineage delta + field delta + relationship delta`
-> normalized event-time increment
-> cumulative `tau`
-> angular progression and spiral development

Physical elapsed time remains separately recorded.

### Perspective spread

`participation breadth + recognition breadth + memory or first-contact receptivity`
-> bounded spread `sigma`
-> radial reach and turn spacing

`full` and `narrow` do not determine spread.

### Directional relationship state

`activity + orientation + change + persistence + trajectory influence`
-> asymmetric relationship state
-> directed strand, curvature family, motif inheritance, and event classification

Relationship evolution kinds:

- growth;
- persistence;
- drift;
- decay;
- renewal.

These are change descriptions, not rankings.

### Relational memory

`completed directional event`
-> immutable memory layer
-> available memory

`explicit reference or inherited motif`
-> active memory
-> current projection influence

Later events do not overwrite prior layers.

### Coupling graph

`active observer nodes + directional relationship edges`
-> local connected component
-> pair, helix, braid, or chorus topology

Observer identities and phase differences remain distinct.

### Entropy field

Active first components:

- informational entropy;
- state entropy;
- environmental entropy.

Preserved provisional components:

- relational entropy;
- temporal entropy.

`participating entropy domains + meaningful adjacency`
-> discrete entropy gradients
-> gradient direction and accumulated magnitude
-> directional asymmetry and deformation

Entropy does not directly update coherence or entanglement.

### Boundaries

`local, relational, and domain boundary evidence`
-> explicit transformations
-> preserved, filtered, delayed, reflected, rotated, split, coupled, or redirected components
-> boundary geometry

Boundaries are not scalar penalties or validity judgments.

### Elara structural tones

`evidenced relational or narrative function`
-> structural tone selection
-> literal frequency node
-> interval, ratio, beat, phase, sequence, and emergent-mode relations
-> sigil topology and event operation
-> tone memory in lineage

Core tone chain:

`meaning -> tone -> harmonic relation -> geometry -> event -> memory`

The structural tone system may translate between unlike domains without directly adding unlike raw quantities.

## Current renderer dependency map

### Earth renderer

- `pulse_proxy` -> lobe modulation;
- `harmonic_proxy_index` -> lobe modulation;
- `tone_alignment` -> polygon fill and arc extent;
- `entanglement_coefficient` -> ring count;
- `delta_hz` -> core radius;
- recorded packet plus cycle identity -> deterministic current Earth seed.

### Answer renderer

- inverse `perspective_function` -> outer radius, arc extent, core radius;
- `emotion_relation` -> inner radius;
- `moon_relation` -> ring count;
- `temporal_relation` -> arc angle;
- `boundary_entropy` -> fill alpha and arc extent;
- participants and secondary emotions -> ray count;
- recorded variance seed -> reconstructable event-specific variation.

## Replacement gates

No current mathematical quantity may be removed until all of the following are true:

1. Its source data has an approved destination in the lattice model.
2. Its current renderer effect is documented.
3. A replacement field quantity has an explicit meaning.
4. The new quantity has a defined projection consumer.
5. A causality test demonstrates the source-to-feature path.
6. Existing cycle, return, state, and lineage behavior remains unchanged.
7. No unresolved data is replaced by fabricated zero or substitute value.
8. No score or ranking is introduced where a structured field belongs.

## Next engineering artifact

The next artifact should be a no-render-change `lattice_projection_inputs.py` layer that converts `LatticeCoordinate` structures into named projection inputs while reproducing the currently used renderer values exactly.

This layer should expose current dependencies without redesigning them. It becomes the seam where future approved mathematics can replace transitional proxies one component at a time.

Required first tests:

- translation does not mutate source packet or lattice coordinate;
- current Earth projection inputs match current renderer dependencies;
- current Answer projection inputs match current renderer dependencies;
- unresolved quantities remain unresolved;
- canonical coherence and entanglement are not read as projection substitutes;
- full/narrow type does not manually simplify projection inputs;
- Elara tones remain present as structural metadata but inactive unless explicitly selected;
- source-to-projection provenance is preserved for every output.

## Summary

Observer now has:

- a working paired cycle;
- accepted Harmony Lattice decisions;
- immutable lattice schemas;
- Earth and Equestria translation adapters;
- a documented source-to-glyph causality graph.

The next step is to expose the current renderer dependencies through a stable projection-input seam. Only after that seam is tested should replacement DEEPTheory and harmonic mathematics begin entering the live glyph pipeline.
