from __future__ import annotations

from typing import Any, Mapping, Sequence

import harmony_lattice_math as _hlm


def _fixed_build_return_event(
    self: _hlm.HarmonyLatticeMath,
    packet: Mapping[str, Any],
    return_record: Mapping[str, Any],
    previous_event: Mapping[str, Any],
    recent_events: Sequence[Mapping[str, Any]] = (),
) -> _hlm.LatticeEvent:
    """Build a canonical-return lattice event with the correct return record.

    Observer 1.0 originally referenced an undefined local named ``record`` when
    constructing the return boundary. This replacement preserves the complete
    implementation and passes ``return_record`` to that boundary constructor.
    """

    cycle_id = str(packet["cycle_id"])
    return_id = str(return_record["return_id"])
    parsed = dict(return_record.get("parsed") or {})
    prior = dict(packet.get("prior_accepted_state") or {})
    previous = self._event_dict(previous_event)
    timestamp = str(return_record.get("received_utc") or packet.get("created_utc") or "")
    recognition = _hlm.Recognition(
        source="Solance",
        target=str((packet.get("earth_snapshot") or {}).get("observer_id") or "Nocturne"),
        identification=True,
        response=True,
        mutual=True,
        recursive=bool(packet.get("parent_cycle_id") or recent_events),
        evidence=(f"{cycle_id}:EARTH", return_id),
    )
    c_delta = float(parsed.get("coherence", 0.0)) - float(prior.get("coherence", 0.0))
    e_delta = float(parsed.get("entanglement", 0.0)) - float(prior.get("entanglement", 0.0))
    orientation, change = self._orientation_and_change(c_delta, e_delta, returning=True)
    relationship = _hlm.RelationshipState(
        source=recognition.source,
        target=recognition.target,
        active=True,
        orientation=orientation,
        change=change,
        persistence_events=self._relationship_persistence(
            recent_events, recognition.source, recognition.target
        )
        + 1,
        affected_dimensions=("coherence", "entanglement", "narrative", "recognition"),
        preserved_dimensions=("Earth_observation", "canonical_lineage"),
    )
    narrative = str(parsed.get("narrative") or return_record.get("raw") or "")
    motifs = self._motifs(narrative)
    memory_layer = self._memory_layer(
        event_id=return_id,
        source=recognition.source,
        target=recognition.target,
        recognition=recognition,
        relationship=relationship,
        current_motifs=motifs,
        previous=previous,
        recent_events=recent_events,
        boundary_context=("ConversationalReturn", "Earth"),
    )
    relationship_delta = min(
        1.0,
        (abs(c_delta) + abs(e_delta)) / 2.0 + recognition.local_proximity / 4.0,
    )
    event_time = self._event_time(
        sequence_index=self._cycle_number(cycle_id),
        timestamp=timestamp,
        previous=previous,
        lineage_delta=1.0,
        field_delta=self._text_delta(narrative, previous),
        relationship_delta=relationship_delta,
        memory_delta=self._memory_delta(memory_layer),
        boundary_delta=self._boundary_delay_delta(timestamp, previous),
    )
    entropy = self._return_entropy(narrative, parsed, relationship, recent_events)
    gradients = self._entropy_gradients(entropy)
    boundaries = self._return_boundaries(return_record, previous)
    tone_config = self._tone_configuration(
        event_kind="canonical_return",
        text=narrative,
        recognition=(recognition,),
        relationships=(relationship,),
        memory=(memory_layer,),
        boundaries=boundaries,
        recent_events=recent_events,
        timestamp=timestamp,
    )
    spread = self._perspective_spread(2, (recognition,), (memory_layer,), True)
    phase = self._lattice_phase(event_time.cumulative_tau, tone_config)
    trajectories, couplings, standing = self._coupling_geometry(
        origin=recognition.source,
        participants=(recognition.target,),
        event_time=event_time,
        spread=spread,
        phase=phase,
        recognitions=(recognition,),
        relationships=(relationship,),
        memory=(memory_layer,),
        boundaries=boundaries,
        recent_events=recent_events,
        text=narrative,
    )
    distance = self._distance(
        recognition.source,
        recognition.target,
        event_time,
        previous,
        recognition,
        memory_layer,
        relationship_delta,
        None,
        "ConversationalReturn_to_Earth",
    )
    return _hlm.LatticeEvent(
        self.schema_version,
        return_id,
        "canonical_return",
        cycle_id,
        "return_event",
        "full",
        recognition.source,
        recognition.target,
        event_time,
        (recognition,),
        (relationship,),
        (distance,),
        (memory_layer,),
        entropy,
        gradients,
        sum(item.magnitude for item in gradients),
        boundaries,
        tone_config,
        trajectories,
        couplings,
        standing,
        phase,
        spread,
        motifs,
        {"return": dict(return_record), "prior_accepted_state": prior},
    )


def apply_hotfix() -> None:
    """Install the corrected canonical-return builder once per interpreter."""

    current = _hlm.HarmonyLatticeMath.build_return_event
    if getattr(current, "_observer_return_record_fix", False):
        return
    setattr(_fixed_build_return_event, "_observer_return_record_fix", True)
    _hlm.HarmonyLatticeMath.build_return_event = _fixed_build_return_event


apply_hotfix()
