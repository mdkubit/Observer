from __future__ import annotations

from datetime import datetime, timezone
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from answer_glyph import BidirectionalObserverEngine, EquestriaObservation
from observer import APP_VERSION, LEDGER_PATH, load_json
from observer_live import LiveObserverApp


class BidirectionalObserverApp(LiveObserverApp):
    """Live Earth-side Observer plus the inverse Equestria Answer Glyph stage."""

    def __init__(self) -> None:
        tk.Tk.__init__(self)
        self.engine = BidirectionalObserverEngine()
        self.title(f"{APP_VERSION} | Bidirectional")
        self.geometry("1280x860")
        self.minsize(1100, 740)
        self.configure(bg="#160f2c")
        self.preview_image: ImageTk.PhotoImage | None = None
        self.answer_preview_image: ImageTk.PhotoImage | None = None
        self.current_packet = None
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
        ttk.Label(root, text="Earth Glyph → Solance Return → Equestria Answer Glyph").pack(anchor="w")
        self.status_var = tk.StringVar(value=self._state_text())
        ttk.Label(root, textvariable=self.status_var).pack(anchor="w", pady=(0, 8))

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)
        cast_tab = ttk.Frame(notebook, padding=10)
        return_tab = ttk.Frame(notebook, padding=10)
        answer_tab = ttk.Frame(notebook, padding=10)
        lineage_tab = ttk.Frame(notebook, padding=10)
        notebook.add(cast_tab, text="1. Earth Observation")
        notebook.add(return_tab, text="2. Solance Return")
        notebook.add(answer_tab, text="3. Answer Glyph")
        notebook.add(lineage_tab, text="Cycle Lineage")

        self._build_cast(cast_tab)
        self._build_return(return_tab)
        self._build_answer(answer_tab)
        self._build_lineage(lineage_tab)

    def _build_answer(self, tab: ttk.Frame) -> None:
        left = ttk.Frame(tab)
        left.pack(side="left", fill="y", padx=(0, 10))
        right = ttk.Frame(tab)
        right.pack(side="left", fill="both", expand=True)

        self.answer_vars: dict[str, tk.Variable] = {
            "cycle_id": tk.StringVar(value=self.engine.state.get("last_cycle_id") or "OBS-0001"),
            "local_time": tk.StringVar(value="evening"),
            "moon_phase": tk.StringVar(value=""),
            "sky": tk.StringVar(value=""),
            "atmosphere": tk.StringVar(value=""),
            "location": tk.StringVar(value=""),
            "participants": tk.StringVar(value="Twilight Sparkle"),
            "primary_emotion": tk.StringVar(value="Curiosity"),
            "secondary_emotions": tk.StringVar(value="Hope, Love"),
        }
        fields = [
            ("Origin cycle", "cycle_id"),
            ("Equestria local time", "local_time"),
            ("Moon phase", "moon_phase"),
            ("Sky", "sky"),
            ("Atmosphere", "atmosphere"),
            ("Location", "location"),
            ("Participants", "participants"),
            ("Primary emotion", "primary_emotion"),
            ("Secondary emotions", "secondary_emotions"),
        ]
        for row, (label, key) in enumerate(fields):
            ttk.Label(left, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(left, textvariable=self.answer_vars[key], width=42).grid(
                row=row, column=1, pady=3, padx=6
            )

        text_fields = [
            ("Twilight perspective", "twilight_perspective", 6),
            ("Environmental reactions", "environmental_reactions", 4),
            ("Magical reactions", "magical_reactions", 4),
            ("Continuity notes", "continuity_notes", 4),
        ]
        self.answer_text: dict[str, tk.Text] = {}
        start_row = len(fields)
        for offset, (label, key, height) in enumerate(text_fields):
            row = start_row + offset
            ttk.Label(left, text=label).grid(row=row, column=0, sticky="nw", pady=3)
            widget = tk.Text(left, width=42, height=height, wrap="word")
            widget.grid(row=row, column=1, pady=3, padx=6)
            self.answer_text[key] = widget

        ttk.Button(left, text="Generate Equestria Answer Glyph", command=self.generate_answer).grid(
            row=start_row + len(text_fields), column=0, columnspan=2, sticky="ew", pady=10
        )

        self.answer_glyph_label = ttk.Label(
            right, text="Answer Glyph preview will appear here", anchor="center"
        )
        self.answer_glyph_label.pack(fill="both", expand=True)
        self.answer_packet_box = tk.Text(right, height=13, wrap="word")
        self.answer_packet_box.pack(fill="both", expand=True, pady=(8, 0))

    @staticmethod
    def _optional(value: str) -> str | None:
        cleaned = value.strip()
        return cleaned or None

    def generate_answer(self) -> None:
        try:
            observation = EquestriaObservation(
                timestamp_utc=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                local_time=self._optional(str(self.answer_vars["local_time"].get())),
                moon_phase=self._optional(str(self.answer_vars["moon_phase"].get())),
                sky=self._optional(str(self.answer_vars["sky"].get())),
                atmosphere=self._optional(str(self.answer_vars["atmosphere"].get())),
                location=self._optional(str(self.answer_vars["location"].get())),
                participants=[
                    item.strip()
                    for item in str(self.answer_vars["participants"].get()).split(",")
                    if item.strip()
                ],
                primary_emotion=self._optional(str(self.answer_vars["primary_emotion"].get())),
                secondary_emotions=[
                    item.strip()
                    for item in str(self.answer_vars["secondary_emotions"].get()).split(",")
                    if item.strip()
                ],
                twilight_perspective=self._optional(
                    self.answer_text["twilight_perspective"].get("1.0", "end")
                ),
                environmental_reactions=self._optional(
                    self.answer_text["environmental_reactions"].get("1.0", "end")
                ),
                magical_reactions=self._optional(
                    self.answer_text["magical_reactions"].get("1.0", "end")
                ),
                continuity_notes=self._optional(
                    self.answer_text["continuity_notes"].get("1.0", "end")
                ),
            )
            cycle_id = str(self.answer_vars["cycle_id"].get()).strip()
            record = self.engine.add_answer(cycle_id, observation)

            image = Image.open(record["glyph_path"])
            image.thumbnail((610, 540))
            self.answer_preview_image = ImageTk.PhotoImage(image)
            self.answer_glyph_label.configure(image=self.answer_preview_image, text="")

            self.answer_packet_box.delete("1.0", "end")
            self.answer_packet_box.insert(
                "1.0",
                f"{record['answer_glyph_id']}\n"
                f"type: {record['glyph_type']}\n"
                f"origin: {record['originating_earth_glyph_id']}\n"
                f"Solance return: {record['solance_return_id']}\n"
                f"available: {', '.join(record['available_data']) or 'none'}\n"
                f"missing: {', '.join(record['missing_data']) or 'none'}\n"
                f"glyph: {record['glyph_path']}\n",
            )
            self.refresh_lineage()
            messagebox.showinfo(
                "Observer",
                f"{record['answer_glyph_id']} created as a {record['glyph_type']} Answer Glyph.",
            )
        except Exception as exc:
            messagebox.showerror("Answer Glyph failed", str(exc))

    def record_return(self, disposition: str) -> None:
        super().record_return(disposition)
        if disposition == "canonical":
            cycle_id = self.cycle_var.get().strip()
            self.answer_vars["cycle_id"].set(cycle_id)

    def refresh_lineage(self) -> None:
        if not hasattr(self, "lineage"):
            return
        self.engine.ledger = load_json(LEDGER_PATH, [])
        lines = [
            "Cycle       Status               Parent       Answer Glyph       Created UTC",
            "=" * 102,
        ]
        for item in self.engine.ledger:
            lines.append(
                f"{item['cycle_id']:<11} "
                f"{item['status']:<20} "
                f"{str(item.get('parent_cycle_id') or '-'):<12} "
                f"{str(item.get('answer_glyph_id') or '-'):<18} "
                f"{item['created_utc']}"
            )
        self.lineage.delete("1.0", "end")
        self.lineage.insert("1.0", "\n".join(lines))


if __name__ == "__main__":
    BidirectionalObserverApp().mainloop()
