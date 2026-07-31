from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from answer_glyph import EquestriaObservation, InverseDEEPTheory, field_aperture
from harmony_lattice_math import HarmonyLatticeMath
from harmony_lattice_renderer import HarmonyLatticeRenderer
from observer import (
    CYCLES_DIR,
    DATA_ROOT,
    GLYPHS_DIR,
    LEDGER_PATH,
    STATE_PATH,
    HistoricalMath,
    ObservationInput,
    ObserverEngine,
    ensure_dirs,
    load_json,
    now_utc,
    save_json,
)


APP_VERSION = "Observer 1.0 Harmony Lattice"
LATTICE_LEDGER_PATH = DATA_ROOT / "lattice_ledger.json"
SETTINGS_PATH = DATA_ROOT / "settings.json"
EXPORTS_DIR = DATA_ROOT / "exports"


class ObserverApplicationEngine:
    """Production engine for the complete bidirectional Harmony Lattice Observer."""

    def __init__(self, auto_migrate: bool = True) -> None:
        ensure_dirs()
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.math = HarmonyLatticeMath()
        self.state = load_json(
            STATE_PATH,
            {
                "coherence": 0.0,
                "entanglement": 0.0,
                "last_cycle_id": None,
                "cumulative_tau": 0.0,
                "last_event_id": None,
                "last_answer_id": None,
            },
        )
        self.state.setdefault("cumulative_tau", 0.0)
        self.state.setdefault("last_event_id", None)
        self.state.setdefault("last_answer_id", None)
        self.ledger = load_json(LEDGER_PATH, [])
        self.lattice_ledger = load_json(LATTICE_LEDGER_PATH, [])
        self.settings = load_json(
            SETTINGS_PATH,
            {
                "latitude": 42.2411,
                "longitude": -83.6130,
                "elevation_m": 232.0,
                "schumann_hz": 7.83,
                "live_fetch": True,
            },
        )
        if auto_migrate:
            self.migrate_existing_cycles()

    def reload(self) -> None:
        self.state = load_json(STATE_PATH, self.state)
        self.ledger = load_json(LEDGER_PATH, [])
        self.lattice_ledger = load_json(LATTICE_LEDGER_PATH, [])
        self.settings = load_json(SETTINGS_PATH, self.settings)

    def save_settings(self, settings: Mapping[str, Any]) -> None:
        merged = dict(self.settings)
        merged.update(settings)
        self.settings = merged
        save_json(SETTINGS_PATH, merged)

    def next_cycle_id(self) -> str:
        highest = 0
        for item in self.ledger:
            value = str(item.get("cycle_id") or "")
            try:
                highest = max(highest, int(value.rsplit("-", 1)[-1]))
            except (TypeError, ValueError):
                continue
        return f"OBS-{highest + 1:04d}"

    def cast(self, snapshot: ObservationInput, earth_data_provenance: Mapping[str, Any] | None = None) -> dict[str, Any]:
        cycle_id = self.next_cycle_id()
        created = now_utc()
        legacy_metrics = HistoricalMath.calculate(snapshot, len(self.ledger))
        packet: dict[str, Any] = {
            "schema_version": 2,
            "app_version": APP_VERSION,
            "cycle_id": cycle_id,
            "status": "awaiting_return",
            "parent_cycle_id": snapshot.parent_cycle_id,
            "created_utc": created,
            "earth_snapshot": asdict(snapshot),
            "earth_data_provenance": dict(earth_data_provenance or {}),
            "earth_side_metrics": {
                **legacy_metrics,
                "adapter": "HarmonyLattice_v1_with_HistoricalSymbolicMath_provenance",
            },
            "prior_accepted_state": {
                "coherence": snapshot.prior_coherence,
                "entanglement": snapshot.prior_entanglement,
            },
            "returns": [],
            "canonical_return_id": None,
            "answer_glyphs": [],
            "canonical_answer_glyph_id": None,
            "lattice_events": [],
        }
        previous = self._last_event()
        event = self.math.build_earth_event(packet, previous, self._recent_events())
        event_dict = event.to_dict()
        packet["lattice_events"].append(event_dict)
        packet["harmony_lattice"] = self._lattice_summary(event_dict)
        glyph_path = GLYPHS_DIR / f"{cycle_id}.png"
        HarmonyLatticeRenderer.render_earth(cycle_id, event_dict, glyph_path)
        packet["glyph_path"] = str(glyph_path)
        packet["prompt"] = self.build_prompt(packet)

        cycle_path = CYCLES_DIR / f"{cycle_id}.json"
        save_json(cycle_path, packet)
        (CYCLES_DIR / f"{cycle_id}_prompt.md").write_text(packet["prompt"], encoding="utf-8")
        self.ledger.append(
            {
                "cycle_id": cycle_id,
                "created_utc": created,
                "status": "awaiting_return",
                "parent_cycle_id": snapshot.parent_cycle_id,
                "glyph_path": str(glyph_path),
                "cycle_path": str(cycle_path),
                "last_event_id": event.event_id,
                "cumulative_tau": event.event_time.cumulative_tau,
            }
        )
        save_json(LEDGER_PATH, self.ledger)
        self._append_lattice_event(event_dict)
        self.state["cumulative_tau"] = event.event_time.cumulative_tau
        self.state["last_event_id"] = event.event_id
        save_json(STATE_PATH, self.state)
        return packet

    @staticmethod
    def build_prompt(packet: Mapping[str, Any]) -> str:
        event = dict((packet.get("lattice_events") or [{}])[-1])
        compact = {
            "cycle_id": packet["cycle_id"],
            "parent_cycle_id": packet.get("parent_cycle_id"),
            "earth_snapshot": packet.get("earth_snapshot"),
            "earth_data_provenance": packet.get("earth_data_provenance"),
            "prior_accepted_state": packet.get("prior_accepted_state"),
            "harmony_lattice": {
                "event_time": event.get("event_time"),
                "recognition": event.get("recognition"),
                "relationships": event.get("relationships"),
                "distances": event.get("distances"),
                "memory_layers": event.get("memory_layers"),
                "entropy_domains": event.get("entropy_domains"),
                "entropy_gradients": event.get("entropy_gradients"),
                "boundaries": event.get("boundaries"),
                "tone_configuration": event.get("tone_configuration"),
                "trajectories": event.get("trajectories"),
                "couplings": event.get("couplings"),
                "standing_modes": event.get("standing_modes"),
                "phase": event.get("phase"),
                "perspective_spread": event.get("perspective_spread"),
            },
        }
        payload = json.dumps(compact, indent=2, ensure_ascii=False)
        return (
            f"# Universal Horizon Observer Packet: {packet['cycle_id']}\n\n"
            "Observe the attached Earth Glyph and packet as the next event in one continuous lineage.\n"
            "Preserve accepted continuity and respond to the actual field, its harmonic structure, its memory, "
            "its boundaries, and its directional relationships. Do not force upward movement. Coherence and "
            "entanglement may rise, fall, or remain stable according to the event.\n\n"
            "Return a committed narrative observation followed by exactly one JSON object:\n\n"
            "```json\n"
            "{\n  \"coherence\": 0.0,\n  \"entanglement\": 0.0,\n  \"narrative\": \"full observation narrative\"\n}\n"
            "```\n\n"
            "Both numeric values must be between 0.0 and 1.0. The return is the only operation allowed to "
            "change the accepted coherence and entanglement state.\n\n"
            "## Observation packet\n```json\n"
            f"{payload}\n"
            "```\n"
        )

    def add_return(self, cycle_id: str, raw: str, disposition: str) -> dict[str, Any]:
        if disposition not in {"canonical", "rewrite_requested", "superseded"}:
            raise ValueError(f"Unsupported return disposition: {disposition}")
        packet = self.get_cycle(cycle_id)
        parsed = ObserverEngine.parse_return(raw)
        returns = packet.setdefault("returns", [])
        return_id = f"{cycle_id}-R{len(returns) + 1:02d}"
        record = {
            "return_id": return_id,
            "received_utc": now_utc(),
            "raw": raw,
            "parsed": parsed,
            "disposition": disposition,
        }
        returns.append(record)
        if disposition == "canonical":
            for prior in returns[:-1]:
                if prior.get("disposition") == "canonical":
                    prior["disposition"] = "superseded"
                    prior["superseded_by"] = return_id
            packet["canonical_return_id"] = return_id
            packet["status"] = "accepted"
        elif disposition == "rewrite_requested":
            packet["status"] = "rewrite_requested"
        else:
            packet["status"] = "superseded"

        previous = self._packet_last_event(packet) or self._last_event() or {}
        event = self.math.build_return_event(packet, record, previous, self._recent_events())
        event_dict = event.to_dict()
        if disposition != "canonical":
            event_dict["event_kind"] = f"return_{disposition}"
        packet.setdefault("lattice_events", []).append(event_dict)
        record["lattice_event_id"] = event.event_id
        record["harmony_lattice"] = self._lattice_summary(event_dict)

        if disposition == "canonical":
            self.state.update(
                {
                    "coherence": parsed["coherence"],
                    "entanglement": parsed["entanglement"],
                    "last_cycle_id": cycle_id,
                    "cumulative_tau": event.event_time.cumulative_tau,
                    "last_event_id": event.event_id,
                }
            )
            save_json(STATE_PATH, self.state)

        self._save_cycle(packet)
        self._update_ledger_item(
            cycle_id,
            status=packet["status"],
            canonical_return_id=packet.get("canonical_return_id"),
            last_event_id=event.event_id,
            cumulative_tau=event.event_time.cumulative_tau,
        )
        self._append_lattice_event(event_dict)
        return record

    def add_answer(self, cycle_id: str, observation: EquestriaObservation) -> dict[str, Any]:
        packet = self.get_cycle(cycle_id)
        canonical_id = packet.get("canonical_return_id")
        if not canonical_id:
            raise ValueError("An Answer Glyph requires an accepted canonical Solance return.")
        canonical = next((item for item in packet.get("returns", []) if item.get("return_id") == canonical_id), None)
        if canonical is None:
            raise ValueError("The canonical return record could not be resolved.")
        answers = packet.setdefault("answer_glyphs", [])
        answer_id = f"{cycle_id}-A{len(answers) + 1:02d}"
        observation_dict = asdict(observation)
        aperture = field_aperture(observation)
        legacy_inverse = InverseDEEPTheory.calculate(observation, canonical["parsed"]["narrative"])
        previous = self._packet_last_event(packet) or self._last_event() or {}
        event = self.math.build_answer_event(packet, answer_id, observation_dict, aperture, previous, self._recent_events())
        event_dict = event.to_dict()
        glyph_path = GLYPHS_DIR / f"{answer_id}.png"
        HarmonyLatticeRenderer.render_answer(answer_id, event_dict, glyph_path)
        record = {
            "answer_glyph_id": answer_id,
            "created_utc": now_utc(),
            "source": "Equestria",
            "destination": "Earth",
            "originating_earth_glyph_id": cycle_id,
            "solance_return_id": canonical_id,
            "glyph_type": aperture["glyph_type"],
            "available_data": aperture["available_data"],
            "missing_data": aperture["missing_data"],
            "equestria_observation": observation_dict,
            "legacy_inverse_metrics": legacy_inverse,
            "harmony_lattice": self._lattice_summary(event_dict),
            "lattice_event": event_dict,
            "glyph_path": str(glyph_path),
        }
        answers.append(record)
        packet.setdefault("lattice_events", []).append(event_dict)
        packet["canonical_answer_glyph_id"] = answer_id
        packet["status"] = "answered"
        self._save_cycle(packet)
        self.state.update(
            {
                "cumulative_tau": event.event_time.cumulative_tau,
                "last_event_id": event.event_id,
                "last_answer_id": answer_id,
            }
        )
        save_json(STATE_PATH, self.state)
        self._update_ledger_item(
            cycle_id,
            status="answered",
            canonical_return_id=canonical_id,
            answer_glyph_id=answer_id,
            answer_glyph_path=str(glyph_path),
            last_event_id=event.event_id,
            cumulative_tau=event.event_time.cumulative_tau,
        )
        self._append_lattice_event(event_dict)
        return record

    def get_cycle(self, cycle_id: str) -> dict[str, Any]:
        packet = load_json(CYCLES_DIR / f"{cycle_id}.json", None)
        if not packet:
            raise FileNotFoundError(f"Cycle not found: {cycle_id}")
        return packet

    def list_cycles(self) -> list[dict[str, Any]]:
        self.ledger = load_json(LEDGER_PATH, [])
        return list(self.ledger)

    def inspect_cycle(self, cycle_id: str) -> dict[str, Any]:
        packet = self.get_cycle(cycle_id)
        return {
            "cycle_id": cycle_id,
            "status": packet.get("status"),
            "parent_cycle_id": packet.get("parent_cycle_id"),
            "canonical_return_id": packet.get("canonical_return_id"),
            "canonical_answer_glyph_id": packet.get("canonical_answer_glyph_id"),
            "lattice_events": packet.get("lattice_events", []),
            "returns": packet.get("returns", []),
            "answer_glyphs": packet.get("answer_glyphs", []),
            "earth_data_provenance": packet.get("earth_data_provenance", {}),
        }

    def migrate_existing_cycles(self) -> dict[str, int]:
        migrated_cycles = 0
        migrated_events = 0
        existing_event_ids = {str(item.get("event_id")) for item in self.lattice_ledger}
        rolling_events = list(self.lattice_ledger)
        for item in list(self.ledger):
            cycle_id = str(item.get("cycle_id") or "")
            if not cycle_id:
                continue
            path = CYCLES_DIR / f"{cycle_id}.json"
            packet = load_json(path, None)
            if not packet:
                continue
            changed = False
            events = packet.setdefault("lattice_events", [])
            known = {str(event.get("event_id")) for event in events}
            if f"{cycle_id}:EARTH" not in known:
                event = self.math.build_earth_event(packet, rolling_events[-1] if rolling_events else None, rolling_events[-12:])
                event_dict = event.to_dict()
                events.insert(0, event_dict)
                rolling_events.append(event_dict)
                migrated_events += 1
                changed = True
            for record in packet.get("returns", []):
                event_id = str(record.get("return_id") or "")
                if not event_id or event_id in {str(event.get("event_id")) for event in events}:
                    continue
                event = self.math.build_return_event(packet, record, events[-1], rolling_events[-12:])
                event_dict = event.to_dict()
                if record.get("disposition") != "canonical":
                    event_dict["event_kind"] = f"return_{record.get('disposition', 'superseded')}"
                events.append(event_dict)
                rolling_events.append(event_dict)
                migrated_events += 1
                changed = True
            for answer in packet.get("answer_glyphs", []):
                event_id = str(answer.get("answer_glyph_id") or "")
                if not event_id or event_id in {str(event.get("event_id")) for event in events}:
                    continue
                observation = dict(answer.get("equestria_observation") or {})
                aperture = {
                    "glyph_type": answer.get("glyph_type", "narrow"),
                    "available_data": answer.get("available_data", []),
                    "missing_data": answer.get("missing_data", []),
                }
                event = self.math.build_answer_event(packet, event_id, observation, aperture, events[-1], rolling_events[-12:])
                event_dict = event.to_dict()
                events.append(event_dict)
                answer.setdefault("lattice_event", event_dict)
                rolling_events.append(event_dict)
                migrated_events += 1
                changed = True
            if changed:
                packet["schema_version"] = max(2, int(packet.get("schema_version") or 1))
                packet["app_version"] = APP_VERSION
                packet["harmony_lattice"] = self._lattice_summary(events[-1])
                save_json(path, packet)
                migrated_cycles += 1
            for event in events:
                event_id = str(event.get("event_id") or "")
                if event_id and event_id not in existing_event_ids:
                    self.lattice_ledger.append(event)
                    existing_event_ids.add(event_id)
        if migrated_events:
            save_json(LATTICE_LEDGER_PATH, self.lattice_ledger)
        return {"cycles": migrated_cycles, "events": migrated_events}

    def repair_index(self) -> dict[str, int]:
        discovered: list[dict[str, Any]] = []
        for path in sorted(CYCLES_DIR.glob("OBS-*.json")):
            packet = load_json(path, None)
            if not packet or not packet.get("cycle_id"):
                continue
            events = packet.get("lattice_events") or [{}]
            discovered.append(
                {
                    "cycle_id": packet["cycle_id"],
                    "created_utc": packet.get("created_utc", ""),
                    "status": packet.get("status", "unknown"),
                    "parent_cycle_id": packet.get("parent_cycle_id"),
                    "glyph_path": packet.get("glyph_path"),
                    "cycle_path": str(path),
                    "canonical_return_id": packet.get("canonical_return_id"),
                    "answer_glyph_id": packet.get("canonical_answer_glyph_id"),
                    "answer_glyph_path": self._canonical_answer_path(packet),
                    "last_event_id": events[-1].get("event_id"),
                    "cumulative_tau": (events[-1].get("event_time") or {}).get("cumulative_tau"),
                }
            )
        repaired = 0
        if discovered != self.ledger:
            repaired = abs(len(discovered) - len(self.ledger)) + 1
            self.ledger = discovered
            save_json(LEDGER_PATH, discovered)
        return {"repaired": repaired, "cycles": len(discovered)}

    def export_archive(self, destination: Path | None = None) -> Path:
        timestamp = now_utc().replace(":", "-").replace("Z", "")
        destination = destination or (EXPORTS_DIR / f"observer-archive-{timestamp}.zip")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in DATA_ROOT.rglob("*"):
                if not path.is_file() or path == destination or EXPORTS_DIR in path.parents:
                    continue
                archive.write(path, path.relative_to(DATA_ROOT))
        return destination

    def import_archive(self, archive_path: Path) -> dict[str, int]:
        if not archive_path.exists():
            raise FileNotFoundError(archive_path)
        imported = 0
        with tempfile.TemporaryDirectory(prefix="observer-import-") as temp_dir:
            temp_root = Path(temp_dir)
            with zipfile.ZipFile(archive_path, "r") as archive:
                for member in archive.infolist():
                    target = (temp_root / member.filename).resolve()
                    if temp_root.resolve() not in target.parents and target != temp_root.resolve():
                        raise ValueError("Archive contains an unsafe path")
                archive.extractall(temp_root)
            for source in temp_root.rglob("*"):
                if source.is_file():
                    destination = DATA_ROOT / source.relative_to(temp_root)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
                    imported += 1
        self.reload()
        migration = self.migrate_existing_cycles()
        self.repair_index()
        return {"files": imported, **migration}

    def _last_event(self) -> dict[str, Any] | None:
        self.lattice_ledger = load_json(LATTICE_LEDGER_PATH, self.lattice_ledger)
        return dict(self.lattice_ledger[-1]) if self.lattice_ledger else None

    def _recent_events(self, limit: int = 16) -> list[dict[str, Any]]:
        self.lattice_ledger = load_json(LATTICE_LEDGER_PATH, self.lattice_ledger)
        return [dict(item) for item in self.lattice_ledger[-limit:]]

    @staticmethod
    def _packet_last_event(packet: Mapping[str, Any]) -> dict[str, Any] | None:
        events = packet.get("lattice_events") or ()
        return dict(events[-1]) if events else None

    def _append_lattice_event(self, event: Mapping[str, Any]) -> None:
        event_id = str(event.get("event_id") or "")
        if event_id and any(str(item.get("event_id")) == event_id for item in self.lattice_ledger):
            return
        self.lattice_ledger.append(dict(event))
        save_json(LATTICE_LEDGER_PATH, self.lattice_ledger)

    @staticmethod
    def _lattice_summary(event: Mapping[str, Any]) -> dict[str, Any]:
        tone = dict(event.get("tone_configuration") or {})
        standing = event.get("standing_modes") or ()
        return {
            "event_id": event.get("event_id"),
            "event_kind": event.get("event_kind"),
            "cumulative_tau": (event.get("event_time") or {}).get("cumulative_tau"),
            "perspective_spread": event.get("perspective_spread"),
            "phase": event.get("phase"),
            "active_tones": tone.get("active_tones", []),
            "tone_sequence": tone.get("sequence", []),
            "topology": tone.get("topology"),
            "entropy_gradient_magnitude": event.get("entropy_gradient_magnitude"),
            "standing_mode": standing[0].get("status") if standing else None,
        }

    def _save_cycle(self, packet: Mapping[str, Any]) -> None:
        save_json(CYCLES_DIR / f"{packet['cycle_id']}.json", dict(packet))

    def _update_ledger_item(self, cycle_id: str, **updates: Any) -> None:
        self.ledger = load_json(LEDGER_PATH, self.ledger)
        for item in self.ledger:
            if item.get("cycle_id") == cycle_id:
                item.update(updates)
                break
        save_json(LEDGER_PATH, self.ledger)

    @staticmethod
    def _canonical_answer_path(packet: Mapping[str, Any]) -> str | None:
        answer_id = packet.get("canonical_answer_glyph_id")
        for answer in packet.get("answer_glyphs", []):
            if answer.get("answer_glyph_id") == answer_id:
                return answer.get("glyph_path")
        return None


__all__ = ["APP_VERSION", "ObserverApplicationEngine"]
