from __future__ import annotations

from typing import Any

from answer_glyph import BidirectionalObserverEngine, EquestriaObservation
from lattice_projection_inputs import (
    AnswerProjectionInputs,
    EarthProjectionInputs,
    projection_snapshot,
)
from lattice_schema import translate_answer_record, translate_earth_packet
from observer import CYCLES_DIR, load_json, save_json


LATTICE_METADATA_VERSION = 1


class LatticePersistentObserverEngine(BidirectionalObserverEngine):
    """Bidirectional engine that persists additive Harmony Lattice provenance.

    The current packet contract, symbolic mathematics, canonical-return behavior,
    and renderer outputs remain unchanged. This class only appends auditable
    lattice-coordinate and renderer-input snapshots to completed records.
    """

    def cast(self, snapshot: Any) -> dict[str, Any]:
        packet = super().cast(snapshot)
        coordinate = translate_earth_packet(packet)
        projection = EarthProjectionInputs.from_packet(packet)
        packet["lattice_metadata"] = {
            "schema_version": LATTICE_METADATA_VERSION,
            "coordinate": coordinate.to_dict(),
            "projection_inputs": projection_snapshot(projection),
        }
        save_json(CYCLES_DIR / f"{packet['cycle_id']}.json", packet)
        return packet

    def add_answer(self, cycle_id: str, observation: EquestriaObservation) -> dict[str, Any]:
        record = super().add_answer(cycle_id, observation)
        cycle_path = CYCLES_DIR / f"{cycle_id}.json"
        packet = load_json(cycle_path, None)
        if not packet:
            raise FileNotFoundError(f"Cycle not found after Answer Glyph creation: {cycle_id}")

        stored_record = next(
            (
                item
                for item in packet.get("answer_glyphs", [])
                if item.get("answer_glyph_id") == record.get("answer_glyph_id")
            ),
            None,
        )
        if stored_record is None:
            raise ValueError("Created Answer Glyph record could not be resolved for lattice persistence.")

        coordinate = translate_answer_record(packet, stored_record)
        projection = AnswerProjectionInputs.from_record(packet, stored_record)
        lattice_metadata = {
            "schema_version": LATTICE_METADATA_VERSION,
            "coordinate": coordinate.to_dict(),
            "projection_inputs": projection_snapshot(projection),
        }
        stored_record["lattice_metadata"] = lattice_metadata
        save_json(cycle_path, packet)

        result = dict(record)
        result["lattice_metadata"] = lattice_metadata
        return result
