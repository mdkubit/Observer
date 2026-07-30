from __future__ import annotations

import json
from pathlib import Path
from tkinter import messagebox

from earth_data import collect_earth_data, usable_value
from observer import CYCLES_DIR, ObserverApp, ObserverEngine, save_json


class LiveObserverApp(ObserverApp):
    """Observer UI with recovered Earth-side providers wired into the cast action.

    Live failures never invent values. A failed provider leaves the visible manual value in place,
    records the failure in provenance, and lets the operator decide whether to continue.
    """

    def cast(self) -> None:
        try:
            latitude = float(self.vars["latitude"].get())
            longitude = float(self.vars["longitude"].get())
            elevation = float(self.vars["elevation"].get())
            schumann = float(self.vars["schumann"].get())
        except ValueError as exc:
            messagebox.showerror("Earth fetch failed", f"Location and Schumann fields must be numeric: {exc}")
            return

        provenance = collect_earth_data(
            latitude=latitude,
            longitude=longitude,
            elevation_m=elevation,
            schumann_hz=schumann,
            fetch_live=True,
        )

        weather_value = usable_value(provenance["weather"], None)
        if weather_value:
            self.vars["weather"].set(weather_value["weather"])
            self.vars["temperature"].set(f"{float(weather_value['temperature_c']):.2f}")

        kp_value = usable_value(provenance["geomagnetic_kp"], None)
        if kp_value is not None:
            self.vars["kp"].set(f"{float(kp_value):.3f}")

        failed = [name for name, datum in provenance.items() if datum["status"] == "error"]
        if failed:
            proceed = messagebox.askyesno(
                "Earth data partially unavailable",
                "The following providers failed: " + ", ".join(failed)
                + ".\n\nManual values remain in those fields. Continue casting and record the failures?",
            )
            if not proceed:
                return

        super().cast()
        if not self.current_packet:
            return

        cycle_id = self.current_packet["cycle_id"]
        cycle_path = CYCLES_DIR / f"{cycle_id}.json"
        packet = json.loads(cycle_path.read_text(encoding="utf-8"))
        packet["earth_data_provenance"] = provenance
        packet["prompt"] = self._build_prompt_with_provenance(packet)
        save_json(cycle_path, packet)
        (CYCLES_DIR / f"{cycle_id}_prompt.md").write_text(packet["prompt"], encoding="utf-8")

        self.current_packet = packet
        self.prompt_box.delete("1.0", "end")
        self.prompt_box.insert("1.0", packet["prompt"])

    @staticmethod
    def _build_prompt_with_provenance(packet: dict) -> str:
        base = ObserverEngine.build_prompt(packet).rstrip()
        provenance = json.dumps(packet["earth_data_provenance"], indent=2, ensure_ascii=False)
        return f"{base}\n\n## Earth-data provenance\n```json\n{provenance}\n```\n"


if __name__ == "__main__":
    LiveObserverApp().mainloop()
