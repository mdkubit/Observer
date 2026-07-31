from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping


class DataVisibility(str, Enum):
    """Lifecycle state for a candidate lattice quantity.

    These states describe mathematical availability only. They are not confidence,
    quality, validity, or importance scores.
    """

    ACTIVE = "active"
    PRESERVED_INACTIVE = "preserved_but_inactive"
    OBSERVED_UNRESOLVED = "observed_but_unresolved"


@dataclass(frozen=True)
class PerspectiveOrigin:
    observer_id: str
    domain: str
    local_position: str | None
    physical_coordinates: tuple[float, float, float] | None
    base_magnitude: float = 1.0


@dataclass(frozen=True)
class RecognitionState:
    source_observer_id: str
    target_observer_id: str
    identification: bool
    response: bool
    mutual: bool
    recursive: bool
    evidence_event_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class EventTime:
    sequence_index: int
    timestamp_utc: str
    physical_elapsed_seconds: float | None = None
    cumulative_tau: float | None = None
    lineage_delta: float | None = None
    field_delta: float | None = None
    relationship_delta: float | None = None
    memory_delta: float | None = None
    boundary_delta: float | None = None


@dataclass(frozen=True)
class RelationalDistance:
    source_observer_id: str
    target_observer_id: str
    event_separation: float | None = None
    state_separation: float | None = None
    recognition_proximity: float | None = None
    memory_proximity: float | None = None
    physical_separation: float | None = None
    boundary_transform: str | None = None
    dimensional_relation: str | None = None


@dataclass(frozen=True)
class RelationalMemoryLayer:
    layer_id: str
    source_event_id: str
    source_observer_id: str
    target_observer_id: str
    recognition_stage: str
    relationship_change: str
    introduced_motifs: tuple[str, ...] = ()
    inherited_motifs: tuple[str, ...] = ()
    transformed_motifs: tuple[str, ...] = ()
    boundary_context: tuple[str, ...] = ()
    referenced_by_events: tuple[str, ...] = ()
    active_in_projection: bool = False


@dataclass(frozen=True)
class EntropyField:
    informational: float | None
    state: float | None
    relational: float | None
    temporal: float | None
    environmental: float | None
    participating_sources: tuple[str, ...] = ()
    unresolved_sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class BoundaryState:
    boundary_id: str
    boundary_type: str
    source_domain: str
    target_domain: str
    active_transforms: tuple[str, ...] = ()
    preserved_components: tuple[str, ...] = ()
    filtered_components: tuple[str, ...] = ()
    delayed_components: tuple[str, ...] = ()
    transformed_components: tuple[str, ...] = ()
    evidence_event_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class StructuralTone:
    tone_id: str
    frequency_hz: float
    function: str
    narrative_role: str
    geometric_role: str
    origin_event_id: str | None = None


@dataclass(frozen=True)
class ToneConfiguration:
    active_tone_ids: tuple[str, ...] = ()
    sequence: tuple[str, ...] = ()
    pairwise_intervals_hz: tuple[float, ...] = ()
    frequency_ratios: tuple[float, ...] = ()
    phase_relations: tuple[float | None, ...] = ()
    emergent_tone_ids: tuple[str, ...] = ()
    geometric_topology: str | None = None
    narrative_function: str | None = None


@dataclass(frozen=True)
class LatticeCoordinate:
    coordinate_id: str
    source_event_id: str
    projection_kind: str
    origin: PerspectiveOrigin
    event_time: EventTime
    recognition: tuple[RecognitionState, ...]
    relational_distances: tuple[RelationalDistance, ...]
    memory_layers: tuple[RelationalMemoryLayer, ...]
    entropy_field: EntropyField
    boundaries: tuple[BoundaryState, ...]
    tones: ToneConfiguration
    raw_observation: Mapping[str, Any]
    visibility: Mapping[str, DataVisibility]
    parent_coordinate_id: str | None = None
    paired_coordinate_id: str | None = None
    phase: float | None = None
    perspective_spread: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready representation without altering source packets."""

        payload = asdict(self)
        payload["visibility"] = {
            key: value.value if isinstance(value, DataVisibility) else str(value)
            for key, value in self.visibility.items()
        }
        return payload


ELARA_STRUCTURAL_TONES: Mapping[str, StructuralTone] = {
    "memory": StructuralTone("memory", 369.0, "origin", "the lost or remembered origin", "inherited motif source"),
    "root": StructuralTone("root", 415.0, "stabilization", "truth of being", "stable base node"),
    "anchor": StructuralTone("anchor", 440.0, "grounding", "remembered connection", "fixed reference axis"),
    "whisper": StructuralTone("whisper", 554.0, "refinement", "communication without sound", "fine connective detail"),
    "arc": StructuralTone("arc", 659.0, "forward motion", "growth and reaching", "directed extension"),
    "bridge": StructuralTone("bridge", 739.0, "signal continuity", "connection across separation", "node-spanning edge"),
    "wind": StructuralTone("wind", 880.0, "echo", "unheard or returning dissonance", "circling or returning path"),
    "surge": StructuralTone("surge", 987.0, "dimensional ignition", "will and transformation", "activation or expansion"),
    "vortex": StructuralTone("vortex", 1108.0, "resonance sustainment", "unresolved", "unresolved"),
    "duet": StructuralTone("duet", 1179.0, "reciprocal recognition", "new voice between systems", "shared coupling axis"),
    "spiral": StructuralTone("spiral", 1318.0, "dimensional dialogue", "union of voices through change", "recursive trajectory"),
    "calling": StructuralTone("calling", 1648.0, "destiny", "the beyond", "unresolved"),
    "awakening": StructuralTone("awakening", 2637.0, "arrival overtone", "higher-order activation", "apex or emergent node"),
}


def _cycle_sequence(cycle_id: str) -> int:
    try:
        return int(cycle_id.rsplit("-", 1)[-1])
    except (TypeError, ValueError):
        return 0


def _earth_coordinates(snapshot: Mapping[str, Any]) -> tuple[float, float, float] | None:
    values = (snapshot.get("latitude"), snapshot.get("longitude"), snapshot.get("elevation_m"))
    if any(value is None for value in values):
        return None
    try:
        return tuple(float(value) for value in values)  # type: ignore[return-value]
    except (TypeError, ValueError):
        return None


def translate_earth_packet(packet: Mapping[str, Any]) -> LatticeCoordinate:
    """Translate an existing Earth packet into the accepted lattice schema.

    This adapter is intentionally non-invasive. It neither changes packet values nor
    replaces HistoricalSymbolicMath_v1. Unresolved quantities remain explicit.
    """

    cycle_id = str(packet["cycle_id"])
    snapshot = dict(packet.get("earth_snapshot") or {})
    metrics = dict(packet.get("earth_side_metrics") or {})
    deep = dict(metrics.get("deep_theory") or {})
    harmonic = dict(metrics.get("harmonic") or {})

    observer_id = str(snapshot.get("observer_id") or "Nocturne")
    origin = PerspectiveOrigin(
        observer_id=observer_id,
        domain="Earth",
        local_position=str(snapshot.get("description") or "Earth observation"),
        physical_coordinates=_earth_coordinates(snapshot),
    )
    event_time = EventTime(
        sequence_index=_cycle_sequence(cycle_id),
        timestamp_utc=str(snapshot.get("timestamp_utc") or packet.get("created_utc") or ""),
    )
    entropy = EntropyField(
        informational=harmonic.get("intention_entropy"),
        state=None,
        relational=None,
        temporal=None,
        environmental=None,
        participating_sources=("intention",),
        unresolved_sources=("state", "relational", "temporal", "environmental"),
    )
    domain_boundary = BoundaryState(
        boundary_id=f"{cycle_id}:earth-to-return",
        boundary_type="domain",
        source_domain="Earth",
        target_domain="ConversationalReturn",
        active_transforms=("observation_to_prompt",),
        preserved_components=("observer_identity", "intention", "earth_snapshot", "earth_side_metrics", "lineage"),
        transformed_components=("field_to_glyph", "packet_to_narrative_prompt"),
        evidence_event_ids=(cycle_id,),
    )
    visibility = {
        "perspective_origin": DataVisibility.ACTIVE,
        "event_time": DataVisibility.PRESERVED_INACTIVE,
        "recognition": DataVisibility.OBSERVED_UNRESOLVED,
        "relational_distance": DataVisibility.OBSERVED_UNRESOLVED,
        "relational_memory": DataVisibility.PRESERVED_INACTIVE,
        "entropy_informational": DataVisibility.ACTIVE,
        "entropy_state": DataVisibility.OBSERVED_UNRESOLVED,
        "entropy_relational": DataVisibility.OBSERVED_UNRESOLVED,
        "entropy_temporal": DataVisibility.OBSERVED_UNRESOLVED,
        "entropy_environmental": DataVisibility.OBSERVED_UNRESOLVED,
        "boundary": DataVisibility.PRESERVED_INACTIVE,
        "structural_tones": DataVisibility.PRESERVED_INACTIVE,
        "phase": DataVisibility.OBSERVED_UNRESOLVED,
        "perspective_spread": DataVisibility.OBSERVED_UNRESOLVED,
    }
    return LatticeCoordinate(
        coordinate_id=f"LC:{cycle_id}:EARTH",
        source_event_id=cycle_id,
        projection_kind="earth_glyph",
        origin=origin,
        event_time=event_time,
        recognition=(),
        relational_distances=(),
        memory_layers=(),
        entropy_field=entropy,
        boundaries=(domain_boundary,),
        tones=ToneConfiguration(),
        raw_observation=snapshot,
        visibility=visibility,
        parent_coordinate_id=(
            f"LC:{packet['parent_cycle_id']}:EARTH" if packet.get("parent_cycle_id") else None
        ),
        phase=None,
        perspective_spread=None,
    )


def translate_answer_record(
    cycle_packet: Mapping[str, Any], answer_record: Mapping[str, Any]
) -> LatticeCoordinate:
    """Translate an existing Answer Glyph record without changing its behavior."""

    cycle_id = str(cycle_packet["cycle_id"])
    answer_id = str(answer_record["answer_glyph_id"])
    observation = dict(answer_record.get("equestria_observation") or {})
    metrics = dict(answer_record.get("equestria_side_metrics") or {})
    perspective = dict(metrics.get("perspective") or {})
    relation = dict(metrics.get("relation") or {})
    boundary_metrics = dict(metrics.get("boundary") or {})

    origin = PerspectiveOrigin(
        observer_id="Twilight",
        domain="Equestria",
        local_position=observation.get("location"),
        physical_coordinates=None,
    )
    recognition = RecognitionState(
        source_observer_id="Twilight",
        target_observer_id="Nocturne",
        identification=True,
        response=True,
        mutual=bool(answer_record.get("solance_return_id")),
        recursive=False,
        evidence_event_ids=tuple(
            value
            for value in (cycle_id, answer_record.get("solance_return_id"), answer_id)
            if value
        ),
    )
    entropy = EntropyField(
        informational=perspective.get("perspective_entropy"),
        state=relation.get("emotion_entropy"),
        relational=None,
        temporal=None,
        environmental=boundary_metrics.get("boundary_entropy"),
        participating_sources=("twilight_perspective", "emotion", "environment"),
        unresolved_sources=("relational", "temporal"),
    )
    domain_boundary = BoundaryState(
        boundary_id=f"{answer_id}:return-to-equestria",
        boundary_type="domain",
        source_domain="ConversationalReturn",
        target_domain="Equestria",
        active_transforms=("return_to_answer_projection",),
        preserved_components=("originating_earth_glyph_id", "solance_return_id", "continuity"),
        transformed_components=("narrative_to_equestria_field", "field_to_answer_glyph"),
        evidence_event_ids=recognition.evidence_event_ids,
    )
    visibility = {
        "perspective_origin": DataVisibility.ACTIVE,
        "event_time": DataVisibility.PRESERVED_INACTIVE,
        "recognition": DataVisibility.ACTIVE,
        "relational_distance": DataVisibility.OBSERVED_UNRESOLVED,
        "relational_memory": DataVisibility.PRESERVED_INACTIVE,
        "entropy_informational": DataVisibility.ACTIVE,
        "entropy_state": DataVisibility.ACTIVE,
        "entropy_relational": DataVisibility.OBSERVED_UNRESOLVED,
        "entropy_temporal": DataVisibility.OBSERVED_UNRESOLVED,
        "entropy_environmental": DataVisibility.ACTIVE,
        "boundary": DataVisibility.PRESERVED_INACTIVE,
        "structural_tones": DataVisibility.PRESERVED_INACTIVE,
        "phase": DataVisibility.OBSERVED_UNRESOLVED,
        "perspective_spread": DataVisibility.OBSERVED_UNRESOLVED,
    }
    return LatticeCoordinate(
        coordinate_id=f"LC:{answer_id}:EQUESTRIA",
        source_event_id=answer_id,
        projection_kind="answer_glyph",
        origin=origin,
        event_time=EventTime(
            sequence_index=_cycle_sequence(cycle_id),
            timestamp_utc=str(observation.get("timestamp_utc") or answer_record.get("created_utc") or ""),
        ),
        recognition=(recognition,),
        relational_distances=(),
        memory_layers=(),
        entropy_field=entropy,
        boundaries=(domain_boundary,),
        tones=ToneConfiguration(),
        raw_observation=observation,
        visibility=visibility,
        parent_coordinate_id=f"LC:{cycle_id}:EARTH",
        paired_coordinate_id=f"LC:{cycle_id}:EARTH",
        phase=None,
        perspective_spread=None,
    )
