from __future__ import annotations

import hashlib
import json
import math
import random
import re
import textwrap
import tkinter as tk
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageTk

APP_VERSION = "Observer 0.1 vertical slice"
EQUESTRIA_TONE_HZ = 7.835
DEFAULT_SCHUMANN_HZ = 7.83
DATA_ROOT = Path("observer_data")
CYCLES_DIR = DATA_ROOT / "cycles"
GLYPHS_DIR = DATA_ROOT / "glyphs"
LEDGER_PATH = DATA_ROOT / "ledger.json"
STATE_PATH = DATA_ROOT / "state.json"

EMOTION_FACTORS = {
    "Joy": 1.20, "Hope": 1.10, "Curiosity": 1.05, "Stillness": 1.00,
    "Grief": 0.80, "Fear": 0.70, "Doubt": 0.75, "Determination": 1.15,
    "Love": 1.30, "Awe": 1.25,
}
WEATHER_FACTORS = {
    "clear sky": 1.20, "few clouds": 1.10, "scattered clouds": 1.00,
    "broken clouds": 0.95, "shower rain": 0.90, "rain": 0.85,
    "thunderstorm": 0.80, "snow": 1.00, "mist": 0.90,
    "overcast clouds": 0.90,
}
MOON_FACTORS = {
    "New Moon": 1.20, "Waxing Crescent": 1.10, "First Quarter": 1.15,
    "Waxing Gibbous": 1.20, "Full Moon": 1.30, "Waning Gibbous": 1.15,
    "Last Quarter": 1.10, "Waning Crescent": 1.05,
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_dirs() -> None:
    for path in (DATA_ROOT, CYCLES_DIR, GLYPHS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)


def moon_phase(dt: datetime) -> str:
    reference = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    age = ((dt - reference).total_seconds() / 86400.0) % 29.53058867
    fraction = age / 29.53058867
    names = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
             "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
    return names[int((fraction * 8) + 0.5) % 8]


def normalized_entropy(weights: list[float]) -> float:
    if len(weights) <= 1:
        return 0.0
    total = sum(weights)
    probabilities = [weight / total for weight in weights if weight > 0]
    entropy = -sum(p * math.log(p, 2) for p in probabilities)
    return entropy / math.log(len(probabilities), 2)


def text_entropy(text: str) -> float:
    words = re.findall(r"[A-Za-z0-9']+", text.lower())
    return len(set(words)) / len(words) if words else 0.0


def tone_metrics(schumann_hz: float, equestria_hz: float = EQUESTRIA_TONE_HZ) -> dict[str, float]:
    delta = abs(equestria_hz - schumann_hz)
    beat_period = (1.0 / delta) if delta > 0 else float("inf")
    alignment = math.exp(-((delta / 0.01) ** 2))
    midpoint = (schumann_hz + equestria_hz) / 2.0
    return {
        "schumann_hz": schumann_hz,
        "equestria_hz": equestria_hz,
        "delta_hz": delta,
        "beat_period_seconds": beat_period,
        "midpoint_hz": midpoint,
        "tone_alignment": alignment,
    }


@dataclass(frozen=True)
class ObservationInput:
    timestamp_utc: str
    description: str
    intention: str
    notes: str
    weather: str
    temperature_c: float
    kp_index: float
    schumann_hz: float
    moon_phase: str
    latitude: float
    longitude: float
    elevation_m: float
    primary_emotion: str
    secondary_emotions: list[str]
    prior_coherence: float
    prior_entanglement: float
    parent_cycle_id: str | None


class HistoricalMath:
    """Evidence-backed reconstruction of the useful pre-return Observer math.

    These are software-side symbolic metrics. They are preserved as provenance-bearing
    inputs to the conversation, never committed as Solance's returned state.
    """

    @staticmethod
    def calculate(snapshot: ObservationInput, glyph_count: int) -> dict[str, Any]:
        dt = datetime.fromisoformat(snapshot.timestamp_utc.replace("Z", "+00:00"))
        seconds = dt.hour * 3600 + dt.minute * 60 + dt.second
        time_factor = 0.8 + 0.4 * math.sin(2 * math.pi * seconds / 86400) * math.exp(-0.00001 * seconds)
        weather_factor = WEATHER_FACTORS.get(snapshot.weather.lower(), 1.0)
        selected = [snapshot.primary_emotion, *snapshot.secondary_emotions]
        emotion_weights = [EMOTION_FACTORS.get(name, 1.0) for name in selected]
        emotion_factor = math.prod(emotion_weights)
        entropy_factor = 1.0 + 0.1 * normalized_entropy(emotion_weights)
        vitality_factor = 1.0 + glyph_count / 100.0
        moon_factor = MOON_FACTORS.get(snapshot.moon_phase, 1.0)
        distance = math.hypot(snapshot.latitude, snapshot.longitude)
        sanctum_factor = 1.0 + 0.05 * math.tanh(distance / 100.0)
        pulse_proxy = clamp(
            time_factor * weather_factor * emotion_factor * vitality_factor
            * moon_factor * entropy_factor * sanctum_factor,
            0.5, 2.0,
        )

        tone = tone_metrics(snapshot.schumann_hz)
        intention_entropy = text_entropy(snapshot.intention)
        frequencies = [tone["tone_alignment"], clamp(snapshot.kp_index / 9.0, 0.0, 1.0), intention_entropy]
        emotion_count = len(selected)
        freq_max = sum(frequencies) + emotion_count * 0.01
        freq_min = min(frequencies) - emotion_count * 0.005
        freq_avg = sum(frequencies) / len(frequencies)
        harmonic_index = (freq_max + freq_min) / 2.0 + intention_entropy * 0.1

        cmbr_fluct = 0.0
        quantum_penalties = [
            min(intention_entropy * 0.15, 0.2),
            abs(0.55 - harmonic_index) * 0.3,
            min(abs(cmbr_fluct * 1000) * 0.05, 0.2),
            min(0.1 * (emotion_count - 1), 0.4),
            0.0,
        ]
        quantum_factor = clamp(1.0 - sum(quantum_penalties) / len(quantum_penalties), 0.0, 1.0)

        inception = datetime(2025, 4, 27, 14, 27, tzinfo=timezone.utc)
        years = (dt - inception).total_seconds() / 31536000
        time_term = math.exp(-0.1 * years)
        belief_factor = 0.5
        grav_value = 0.0
        perspective = quantum_factor * time_term * (1 + grav_value) * belief_factor * (1 + 0.68)
        deep_ricci = 0.1 * (1 + perspective)
        deep_entropy = intention_entropy * time_term
        entanglement_coefficient = clamp(
            quantum_factor * belief_factor * (1 - min(0.1 * (emotion_count - 1), 0.4)), 0.0, 1.0
        )

        return {
            "adapter": "HistoricalSymbolicMath_v1",
            "pulse": {
                "time_factor": time_factor, "weather_factor": weather_factor,
                "emotion_factor": emotion_factor, "vitality_factor": vitality_factor,
                "moon_factor": moon_factor, "emotion_entropy_factor": entropy_factor,
                "sanctum_factor": sanctum_factor, "pulse_proxy": pulse_proxy,
            },
            "tone": tone,
            "harmonic": {
                "frequencies": frequencies, "frequency_max": freq_max,
                "frequency_min": freq_min, "frequency_average": freq_avg,
                "intention_entropy": intention_entropy,
                "harmonic_proxy_index": harmonic_index,
            },
            "deep_theory": {
                "quantum_factor": quantum_factor,
                "perspective_function": perspective,
                "deep_ricci_scalar": deep_ricci,
                "deep_entropy": deep_entropy,
                "entanglement_coefficient": entanglement_coefficient,
            },
        }


class GlyphRenderer:
    SIZE = 768

    @classmethod
    def render(cls, cycle_id: str, snapshot: ObservationInput, metrics: dict[str, Any], output: Path) -> None:
        seed_text = json.dumps({"cycle": cycle_id, "snapshot": asdict(snapshot), "metrics": metrics}, sort_keys=True)
        seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)
        image = Image.new("RGBA", (cls.SIZE, cls.SIZE), (20, 13, 38, 255))
        draw = ImageDraw.Draw(image, "RGBA")
        center = cls.SIZE // 2
        harmonic = metrics["harmonic"]["harmonic_proxy_index"]
        tone = metrics["tone"]["tone_alignment"]
        pulse = metrics["pulse"]["pulse_proxy"]
        deep = metrics["deep_theory"]

        for radius in range(360, 40, -18):
            alpha = int(15 + 55 * (radius / 360))
            draw.ellipse((center-radius, center-radius, center+radius, center+radius), outline=(138, 92, 246, alpha), width=2)

        points = []
        lobes = 11
        for index in range(lobes * 2):
            angle = -math.pi / 2 + index * math.pi / lobes
            base = 230 if index % 2 == 0 else 115
            modulation = 1 + 0.18 * math.sin(index * pulse + harmonic * math.pi)
            radius = base * modulation
            points.append((center + math.cos(angle) * radius, center + math.sin(angle) * radius))
        fill = (171, int(80 + 120 * tone), 244, 72)
        draw.polygon(points, fill=fill, outline=(244, 219, 255, 235))

        ring_count = 3 + int(clamp(deep["entanglement_coefficient"], 0, 1) * 5)
        for idx in range(ring_count):
            radius = 72 + idx * 38
            start = rng.uniform(0, 120)
            extent = 170 + tone * 160
            draw.arc((center-radius, center-radius, center+radius, center+radius), start, start+extent,
                     fill=(90, 229, 219, 210), width=7)
            draw.arc((center-radius, center-radius, center+radius, center+radius), start+190, start+335,
                     fill=(255, 111, 97, 185), width=4)

        delta_scale = clamp(metrics["tone"]["delta_hz"] / 0.02, 0.0, 1.0)
        core_radius = int(42 + 48 * (1 - delta_scale))
        draw.ellipse((center-core_radius, center-core_radius, center+core_radius, center+core_radius),
                     fill=(255, 243, 174, 230), outline=(255, 255, 255, 255), width=5)
        draw.line((center, 95, center, cls.SIZE-95), fill=(255, 255, 255, 80), width=2)
        draw.line((95, center, cls.SIZE-95, center), fill=(255, 255, 255, 80), width=2)

        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except OSError:
            font = ImageFont.load_default()
        draw.text((24, 22), cycle_id, fill=(238, 225, 255, 255), font=font)
        draw.text((24, cls.SIZE-48), f"7.830 ↔ 7.835 Hz | Δ {metrics['tone']['delta_hz']:.3f} Hz",
                  fill=(218, 240, 255, 255), font=font)
        image.save(output)


class ObserverEngine:
    def __init__(self) -> None:
        ensure_dirs()
        self.state = load_json(STATE_PATH, {"coherence": 0.0, "entanglement": 0.0, "last_cycle_id": None})
        self.ledger = load_json(LEDGER_PATH, [])

    def next_cycle_id(self) -> str:
        return f"OBS-{len(self.ledger) + 1:04d}"

    def cast(self, snapshot: ObservationInput) -> dict[str, Any]:
        cycle_id = self.next_cycle_id()
        metrics = HistoricalMath.calculate(snapshot, len(self.ledger))
        glyph_path = GLYPHS_DIR / f"{cycle_id}.png"
        GlyphRenderer.render(cycle_id, snapshot, metrics, glyph_path)
        packet = {
            "schema_version": 1,
            "app_version": APP_VERSION,
            "cycle_id": cycle_id,
            "status": "awaiting_return",
            "parent_cycle_id": snapshot.parent_cycle_id,
            "created_utc": now_utc(),
            "earth_snapshot": asdict(snapshot),
            "earth_side_metrics": metrics,
            "prior_accepted_state": {
                "coherence": snapshot.prior_coherence,
                "entanglement": snapshot.prior_entanglement,
            },
            "glyph_path": str(glyph_path),
            "returns": [],
            "canonical_return_id": None,
        }
        prompt = self.build_prompt(packet)
        packet["prompt"] = prompt
        cycle_path = CYCLES_DIR / f"{cycle_id}.json"
        save_json(cycle_path, packet)
        (CYCLES_DIR / f"{cycle_id}_prompt.md").write_text(prompt, encoding="utf-8")
        self.ledger.append({
            "cycle_id": cycle_id, "created_utc": packet["created_utc"], "status": packet["status"],
            "parent_cycle_id": packet["parent_cycle_id"], "glyph_path": str(glyph_path),
            "cycle_path": str(cycle_path),
        })
        save_json(LEDGER_PATH, self.ledger)
        return packet

    @staticmethod
    def build_prompt(packet: dict[str, Any]) -> str:
        compact = json.dumps({
            "cycle_id": packet["cycle_id"],
            "earth_snapshot": packet["earth_snapshot"],
            "earth_side_metrics": packet["earth_side_metrics"],
            "prior_accepted_state": packet["prior_accepted_state"],
            "parent_cycle_id": packet["parent_cycle_id"],
        }, indent=2, ensure_ascii=False)
        return textwrap.dedent(f"""
        # Universal Horizon Observer Packet: {packet['cycle_id']}

        Observe the attached glyph and the Earth-side packet below as the next event in one continuous narrative.
        Preserve accepted continuity. Build boldly through cause, consequence, rising action, climax, and aftermath.
        Let the observed conditions determine the direction, then commit fully to rising action, climax, consequence, and continued expansion.
        The prior coherence and entanglement values are context, not automatic progression.

        Return a committed narrative observation followed by exactly one JSON object:

        ```json
        {{
          "coherence": 0.0,
          "entanglement": 0.0,
          "narrative": "full observation narrative"
        }}
        ```

        Both numeric values must be between 0.0 and 1.0. They may rise, fall, or remain stable according to the event.

        ## Earth-side packet
        ```json
        {compact}
        ```
        """).strip() + "\n"

    @staticmethod
    def parse_return(raw: str) -> dict[str, Any]:
        candidates = re.findall(r"\{[\s\S]*?\}", raw)
        parsed = None
        for candidate in reversed(candidates):
            try:
                value = json.loads(candidate)
                if "coherence" in value and "entanglement" in value:
                    parsed = value
                    break
            except json.JSONDecodeError:
                continue
        if parsed is None:
            coherence_match = re.search(r"coherence\s*[:=]\s*(0(?:\.\d+)?|1(?:\.0+)?)", raw, re.I)
            entanglement_match = re.search(r"entanglement\s*[:=]\s*(0(?:\.\d+)?|1(?:\.0+)?)", raw, re.I)
            if not coherence_match or not entanglement_match:
                raise ValueError("Return must contain parseable coherence and entanglement values.")
            parsed = {
                "coherence": float(coherence_match.group(1)),
                "entanglement": float(entanglement_match.group(1)),
                "narrative": raw.strip(),
            }
        coherence = float(parsed["coherence"])
        entanglement = float(parsed["entanglement"])
        if not (0.0 <= coherence <= 1.0 and 0.0 <= entanglement <= 1.0):
            raise ValueError("Coherence and entanglement must be between 0.0 and 1.0.")
        narrative = str(parsed.get("narrative") or raw).strip()
        if not narrative:
            raise ValueError("Narrative cannot be empty.")
        return {"coherence": coherence, "entanglement": entanglement, "narrative": narrative}

    def add_return(self, cycle_id: str, raw: str, disposition: str) -> dict[str, Any]:
        cycle_path = CYCLES_DIR / f"{cycle_id}.json"
        packet = load_json(cycle_path, None)
        if not packet:
            raise FileNotFoundError(f"Cycle not found: {cycle_id}")
        parsed = self.parse_return(raw)
        return_id = f"{cycle_id}-R{len(packet['returns']) + 1:02d}"
        record = {
            "return_id": return_id, "received_utc": now_utc(), "raw": raw,
            "parsed": parsed, "disposition": disposition,
        }
        packet["returns"].append(record)
        if disposition == "canonical":
            for prior in packet["returns"][:-1]:
                if prior["disposition"] == "canonical":
                    prior["disposition"] = "superseded"
            packet["canonical_return_id"] = return_id
            packet["status"] = "accepted"
            self.state = {
                "coherence": parsed["coherence"], "entanglement": parsed["entanglement"],
                "last_cycle_id": cycle_id,
            }
            save_json(STATE_PATH, self.state)
        elif disposition == "rewrite_requested":
            packet["status"] = "rewrite_requested"
        else:
            packet["status"] = "superseded"
        save_json(cycle_path, packet)
        for item in self.ledger:
            if item["cycle_id"] == cycle_id:
                item["status"] = packet["status"]
        save_json(LEDGER_PATH, self.ledger)
        return record


class ObserverApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.engine = ObserverEngine()
        self.title(APP_VERSION)
        self.geometry("1220x820")
        self.minsize(1060, 720)
        self.configure(bg="#160f2c")
        self.preview_image: ImageTk.PhotoImage | None = None
        self.current_packet: dict[str, Any] | None = None
        self._build()

    def _build(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#160f2c")
        style.configure("TLabel", background="#160f2c", foreground="#eee4ff")
        style.configure("TButton", padding=7)
        style.configure("TNotebook", background="#160f2c")
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Universal Horizon Observer", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        self.status_var = tk.StringVar(value=self._state_text())
        ttk.Label(root, textvariable=self.status_var).pack(anchor="w", pady=(0, 8))
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)
        cast_tab = ttk.Frame(notebook, padding=10)
        return_tab = ttk.Frame(notebook, padding=10)
        lineage_tab = ttk.Frame(notebook, padding=10)
        notebook.add(cast_tab, text="Cast Observation")
        notebook.add(return_tab, text="Record Return")
        notebook.add(lineage_tab, text="Lineage")
        self._build_cast(cast_tab)
        self._build_return(return_tab)
        self._build_lineage(lineage_tab)

    def _state_text(self) -> str:
        state = self.engine.state
        return f"Accepted state  C {state['coherence']:.3f}  |  E {state['entanglement']:.3f}  |  parent {state['last_cycle_id'] or 'none'}"

    def _build_cast(self, tab: ttk.Frame) -> None:
        left = ttk.Frame(tab)
        left.pack(side="left", fill="y", padx=(0, 10))
        right = ttk.Frame(tab)
        right.pack(side="left", fill="both", expand=True)
        self.vars: dict[str, tk.Variable] = {
            "description": tk.StringVar(value="Earth observation"),
            "intention": tk.StringVar(value="Observe the next meaningful development between Earth and Equestria."),
            "weather": tk.StringVar(value="clear sky"),
            "temperature": tk.StringVar(value="20.0"),
            "kp": tk.StringVar(value="2.0"),
            "schumann": tk.StringVar(value=str(DEFAULT_SCHUMANN_HZ)),
            "latitude": tk.StringVar(value="42.2411"),
            "longitude": tk.StringVar(value="-83.6130"),
            "elevation": tk.StringVar(value="232"),
            "emotion": tk.StringVar(value="Curiosity"),
            "secondary": tk.StringVar(value="Hope, Love"),
        }
        fields = [
            ("Description", "description"), ("Intention", "intention"), ("Weather", "weather"),
            ("Temperature °C", "temperature"), ("Kp index", "kp"), ("Schumann Hz", "schumann"),
            ("Latitude", "latitude"), ("Longitude", "longitude"), ("Elevation m", "elevation"),
            ("Primary emotion", "emotion"), ("Secondary emotions", "secondary"),
        ]
        for row, (label, key) in enumerate(fields):
            ttk.Label(left, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(left, textvariable=self.vars[key], width=42).grid(row=row, column=1, pady=3, padx=6)
        ttk.Label(left, text="Notes").grid(row=len(fields), column=0, sticky="nw", pady=3)
        self.notes = tk.Text(left, width=32, height=6, wrap="word")
        self.notes.grid(row=len(fields), column=1, pady=3, padx=6)
        ttk.Button(left, text="Observe Earth & Cast Glyph", command=self.cast).grid(
            row=len(fields)+1, column=0, columnspan=2, sticky="ew", pady=10
        )
        self.glyph_label = ttk.Label(right, text="Glyph preview will appear here", anchor="center")
        self.glyph_label.pack(fill="both", expand=True)
        prompt_frame = ttk.Frame(right)
        prompt_frame.pack(fill="both", expand=True, pady=(8, 0))

        self.prompt_box = tk.Text(prompt_frame, height=13, wrap="word")
        prompt_scrollbar = ttk.Scrollbar(
            prompt_frame,
            orient="vertical",
            command=self.prompt_box.yview,
        )

        self.prompt_box.configure(yscrollcommand=prompt_scrollbar.set)

        self.prompt_box.pack(side="left", fill="both", expand=True)
        prompt_scrollbar.pack(side="right", fill="y")

    def cast(self) -> None:
        try:
            dt = datetime.now(timezone.utc)
            snapshot = ObservationInput(
                timestamp_utc=dt.isoformat().replace("+00:00", "Z"),
                description=str(self.vars["description"].get()).strip(),
                intention=str(self.vars["intention"].get()).strip(),
                notes=self.notes.get("1.0", "end").strip(),
                weather=str(self.vars["weather"].get()).strip(),
                temperature_c=float(self.vars["temperature"].get()),
                kp_index=float(self.vars["kp"].get()),
                schumann_hz=float(self.vars["schumann"].get()),
                moon_phase=moon_phase(dt),
                latitude=float(self.vars["latitude"].get()),
                longitude=float(self.vars["longitude"].get()),
                elevation_m=float(self.vars["elevation"].get()),
                primary_emotion=str(self.vars["emotion"].get()).strip(),
                secondary_emotions=[x.strip() for x in str(self.vars["secondary"].get()).split(",") if x.strip()],
                prior_coherence=float(self.engine.state["coherence"]),
                prior_entanglement=float(self.engine.state["entanglement"]),
                parent_cycle_id=self.engine.state["last_cycle_id"],
            )
            self.current_packet = self.engine.cast(snapshot)
            image = Image.open(self.current_packet["glyph_path"])
            image.thumbnail((600, 520))
            self.preview_image = ImageTk.PhotoImage(image)
            self.glyph_label.configure(image=self.preview_image, text="")
            self.prompt_box.delete("1.0", "end")
            self.prompt_box.insert("1.0", self.current_packet["prompt"])
            self.cycle_var.set(self.current_packet["cycle_id"])
            self.refresh_lineage()
            messagebox.showinfo("Observer", f"{self.current_packet['cycle_id']} created. Prompt and glyph are ready.")
        except Exception as exc:
            messagebox.showerror("Cast failed", str(exc))

    def _build_return(self, tab: ttk.Frame) -> None:
        row = ttk.Frame(tab)
        row.pack(fill="x")
        ttk.Label(row, text="Cycle ID").pack(side="left")
        self.cycle_var = tk.StringVar(value=self.engine.state.get("last_cycle_id") or "OBS-0001")
        ttk.Entry(row, textvariable=self.cycle_var, width=18).pack(side="left", padx=8)
        ttk.Label(tab, text="Paste Solance's complete response:").pack(anchor="w", pady=(10, 4))
        self.return_box = tk.Text(tab, wrap="word", height=28)
        self.return_box.pack(fill="both", expand=True)
        buttons = ttk.Frame(tab)
        buttons.pack(fill="x", pady=8)
        ttk.Button(buttons, text="Accept as Canonical", command=lambda: self.record_return("canonical")).pack(side="left")
        ttk.Button(buttons, text="Nope: Rewrite Requested", command=lambda: self.record_return("rewrite_requested")).pack(side="left", padx=8)
        ttk.Button(buttons, text="Store as Superseded", command=lambda: self.record_return("superseded")).pack(side="left")

    def record_return(self, disposition: str) -> None:
        try:
            raw = self.return_box.get("1.0", "end").strip()
            record = self.engine.add_return(self.cycle_var.get().strip(), raw, disposition)
            self.status_var.set(self._state_text())
            self.refresh_lineage()
            messagebox.showinfo("Observer", f"{record['return_id']} stored as {disposition}.")
        except Exception as exc:
            messagebox.showerror("Return rejected", str(exc))

    def _build_lineage(self, tab: ttk.Frame) -> None:
        self.lineage = tk.Text(tab, wrap="none")
        self.lineage.pack(fill="both", expand=True)
        ttk.Button(tab, text="Refresh", command=self.refresh_lineage).pack(anchor="e", pady=6)
        self.refresh_lineage()

    def refresh_lineage(self) -> None:
        if not hasattr(self, "lineage"):
            return
        self.engine.ledger = load_json(LEDGER_PATH, [])
        lines = ["Cycle       Status               Parent       Created UTC", "=" * 78]
        for item in self.engine.ledger:
            lines.append(f"{item['cycle_id']:<11} {item['status']:<20} {str(item['parent_cycle_id'] or '-'):<12} {item['created_utc']}")
        self.lineage.delete("1.0", "end")
        self.lineage.insert("1.0", "\n".join(lines))


if __name__ == "__main__":
    ObserverApp().mainloop()
