from __future__ import annotations

import json
import os
import sys
import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Mapping

from PIL import Image, ImageTk

from answer_glyph import EquestriaObservation
from earth_data import collect_earth_data, usable_value
from harmony_tone_audio import play_tone_sequence, render_tone_sequence_wav
from observer import ObservationInput, moon_phase
from observer_application_engine import APP_VERSION, ObserverApplicationEngine


BG = "#100b20"
PANEL = "#1a1330"
PANEL_ALT = "#21183a"
TEXT = "#f1ebff"
MUTED = "#b8acd5"
ACCENT = "#9f78ff"
ACCENT_2 = "#6ee8d0"
WARM = "#ffd47d"
DANGER = "#ff8d9b"


class ObserverCompleteApp(tk.Tk):
    """Complete desktop interface for the bidirectional Harmony Lattice Observer."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = ObserverApplicationEngine(auto_migrate=True)
        self.title(APP_VERSION)
        self.geometry("1500x940")
        self.minsize(1240, 800)
        self.configure(bg=BG)
        self.preview_image: ImageTk.PhotoImage | None = None
        self.answer_preview_image: ImageTk.PhotoImage | None = None
        self.dashboard_preview_image: ImageTk.PhotoImage | None = None
        self.current_packet: dict[str, Any] | None = None
        self.current_answer: dict[str, Any] | None = None
        self.inspector_event: dict[str, Any] | None = None
        self._configure_styles()
        self._build_shell()
        self.refresh_all()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("Alt.TFrame", background=PANEL_ALT)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=PANEL, foreground=TEXT)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 22))
        style.configure("Section.TLabel", background=PANEL, foreground=WARM, font=("Segoe UI Semibold", 12))
        style.configure("Metric.TLabel", background=PANEL, foreground=ACCENT_2, font=("Segoe UI Semibold", 16))
        style.configure("TButton", background=PANEL_ALT, foreground=TEXT, padding=(10, 7), borderwidth=0)
        style.map("TButton", background=[("active", "#322653")])
        style.configure("Accent.TButton", background=ACCENT, foreground="#120b20", padding=(12, 8), font=("Segoe UI Semibold", 10))
        style.map("Accent.TButton", background=[("active", "#b398ff")])
        style.configure("Danger.TButton", background=DANGER, foreground="#20101a")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL, foreground=MUTED, padding=(13, 8))
        style.map("TNotebook.Tab", background=[("selected", PANEL_ALT)], foreground=[("selected", TEXT)])
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background=PANEL_ALT, foreground=WARM, font=("Segoe UI Semibold", 10))
        style.map("Treeview", background=[("selected", "#493772")])
        style.configure("TEntry", fieldbackground="#f7f3ff", foreground="#1d1730")
        style.configure("TCombobox", fieldbackground="#f7f3ff", foreground="#1d1730")
        style.configure("TCheckbutton", background=PANEL, foreground=TEXT)
        style.map("TCheckbutton", background=[("active", PANEL)])

    def _build_shell(self) -> None:
        header = ttk.Frame(self, padding=(18, 14))
        header.pack(fill="x")
        ttk.Label(header, text="Universal Horizon Observer", style="Title.TLabel").pack(side="left")
        self.header_status = tk.StringVar()
        ttk.Label(header, textvariable=self.header_status, style="Muted.TLabel").pack(side="right", padx=(20, 0))
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.dashboard_tab = ttk.Frame(self.notebook, padding=14)
        self.earth_tab = ttk.Frame(self.notebook, padding=14)
        self.return_tab = ttk.Frame(self.notebook, padding=14)
        self.answer_tab = ttk.Frame(self.notebook, padding=14)
        self.inspector_tab = ttk.Frame(self.notebook, padding=14)
        self.lineage_tab = ttk.Frame(self.notebook, padding=14)
        self.archive_tab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.earth_tab, text="1. Earth Cast")
        self.notebook.add(self.return_tab, text="2. Solance Return")
        self.notebook.add(self.answer_tab, text="3. Answer Glyph")
        self.notebook.add(self.inspector_tab, text="Lattice Inspector")
        self.notebook.add(self.lineage_tab, text="Lineage")
        self.notebook.add(self.archive_tab, text="Archive & Recovery")
        self._build_dashboard()
        self._build_earth()
        self._build_return()
        self._build_answer()
        self._build_inspector()
        self._build_lineage()
        self._build_archive()
        self.footer_status = tk.StringVar(value="Ready.")
        footer = ttk.Frame(self, padding=(16, 7))
        footer.pack(fill="x", side="bottom")
        ttk.Label(footer, textvariable=self.footer_status, style="Muted.TLabel").pack(side="left")
        ttk.Label(footer, text=APP_VERSION, style="Muted.TLabel").pack(side="right")

    def _panel(self, parent: tk.Misc, title: str | None = None, padding: int = 12) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=padding)
        if title:
            ttk.Label(frame, text=title, style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        return frame

    def _build_dashboard(self) -> None:
        top = ttk.Frame(self.dashboard_tab)
        top.pack(fill="x")
        self.dashboard_metrics: dict[str, tk.StringVar] = {}
        for index, (label, key) in enumerate((
            ("Accepted Coherence", "coherence"),
            ("Accepted Entanglement", "entanglement"),
            ("Lattice Event-Time τ", "tau"),
            ("Latest Cycle", "cycle"),
        )):
            panel = self._panel(top, padding=14)
            panel.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 8, 0))
            top.columnconfigure(index, weight=1)
            ttk.Label(panel, text=label, style="Panel.TLabel").pack(anchor="w")
            variable = tk.StringVar(value="—")
            self.dashboard_metrics[key] = variable
            ttk.Label(panel, textvariable=variable, style="Metric.TLabel").pack(anchor="w", pady=(6, 0))
        body = ttk.Panedwindow(self.dashboard_tab, orient="horizontal")
        body.pack(fill="both", expand=True, pady=(12, 0))
        left = self._panel(body, "Latest Glyph")
        right = self._panel(body, "Latest Lattice Event")
        body.add(left, weight=3)
        body.add(right, weight=4)
        self.dashboard_preview = ttk.Label(left, text="No glyph has been generated yet.", style="Panel.TLabel", anchor="center")
        self.dashboard_preview.pack(fill="both", expand=True)
        dashboard_buttons = ttk.Frame(left, style="Panel.TFrame")
        dashboard_buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(dashboard_buttons, text="Open Glyph", command=self.open_latest_glyph).pack(side="left")
        ttk.Button(dashboard_buttons, text="Open Cycle Folder", command=lambda: self._open_path(Path("observer_data/cycles"))).pack(side="left", padx=8)
        ttk.Button(dashboard_buttons, text="Refresh", command=self.refresh_all).pack(side="right")
        self.dashboard_event_text = self._text_widget(right, height=26)
        self.dashboard_event_text.pack(fill="both", expand=True)

    def _build_earth(self) -> None:
        paned = ttk.Panedwindow(self.earth_tab, orient="horizontal")
        paned.pack(fill="both", expand=True)
        left = self._panel(paned, "Earth Observation", padding=14)
        right = self._panel(paned, "Earth Glyph and Solance Packet", padding=14)
        paned.add(left, weight=4)
        paned.add(right, weight=6)
        self.earth_vars: dict[str, tk.Variable] = {
            "description": tk.StringVar(value="Earth observation"),
            "intention": tk.StringVar(value="Observe the next meaningful development between Earth and Equestria."),
            "weather": tk.StringVar(value="clear sky"),
            "temperature": tk.StringVar(value="20.0"),
            "kp": tk.StringVar(value="2.0"),
            "schumann": tk.StringVar(value=str(self.engine.settings.get("schumann_hz", 7.83))),
            "latitude": tk.StringVar(value=str(self.engine.settings.get("latitude", 42.2411))),
            "longitude": tk.StringVar(value=str(self.engine.settings.get("longitude", -83.6130))),
            "elevation": tk.StringVar(value=str(self.engine.settings.get("elevation_m", 232.0))),
            "emotion": tk.StringVar(value="Curiosity"),
            "secondary": tk.StringVar(value="Hope, Love"),
            "live_fetch": tk.BooleanVar(value=bool(self.engine.settings.get("live_fetch", True))),
        }
        fields = (
            ("Description", "description"), ("Intention", "intention"), ("Weather", "weather"),
            ("Temperature °C", "temperature"), ("Planetary Kp", "kp"),
            ("Schumann reference Hz", "schumann"), ("Latitude", "latitude"),
            ("Longitude", "longitude"), ("Elevation m", "elevation"),
            ("Primary emotion", "emotion"), ("Secondary emotions", "secondary"),
        )
        form = ttk.Frame(left, style="Panel.TFrame")
        form.pack(fill="x")
        for row, (label, key) in enumerate(fields):
            ttk.Label(form, text=label, style="Panel.TLabel").grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=self.earth_vars[key], width=44).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=4)
        form.columnconfigure(1, weight=1)
        ttk.Label(left, text="Notes", style="Panel.TLabel").pack(anchor="w", pady=(10, 4))
        self.earth_notes = self._text_widget(left, height=6)
        self.earth_notes.pack(fill="x")
        ttk.Checkbutton(left, text="Fetch live weather and Kp before casting", variable=self.earth_vars["live_fetch"], style="TCheckbutton").pack(anchor="w", pady=(10, 4))
        buttons = ttk.Frame(left, style="Panel.TFrame")
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(buttons, text="Fetch Earth Data", command=self.fetch_earth_data).pack(side="left")
        ttk.Button(buttons, text="Observe and Cast", style="Accent.TButton", command=self.cast_earth).pack(side="right")
        self.earth_preview = ttk.Label(right, text="Earth Glyph preview will appear here.", style="Panel.TLabel", anchor="center")
        self.earth_preview.pack(fill="both", expand=True)
        prompt_header = ttk.Frame(right, style="Panel.TFrame")
        prompt_header.pack(fill="x", pady=(10, 4))
        ttk.Label(prompt_header, text="Solance Packet", style="Panel.TLabel").pack(side="left")
        ttk.Button(prompt_header, text="Copy", command=self.copy_prompt).pack(side="right")
        self.prompt_box = self._text_widget(right, height=13)
        self.prompt_box.pack(fill="both", expand=True)

    def _build_return(self) -> None:
        paned = ttk.Panedwindow(self.return_tab, orient="horizontal")
        paned.pack(fill="both", expand=True)
        left = self._panel(paned, "Record Solance Return", padding=14)
        right = self._panel(paned, "Return Result", padding=14)
        paned.add(left, weight=6)
        paned.add(right, weight=4)
        row = ttk.Frame(left, style="Panel.TFrame")
        row.pack(fill="x")
        ttk.Label(row, text="Cycle", style="Panel.TLabel").pack(side="left")
        self.return_cycle = tk.StringVar()
        self.return_cycle_combo = ttk.Combobox(row, textvariable=self.return_cycle, state="normal", width=22)
        self.return_cycle_combo.pack(side="left", padx=10)
        ttk.Button(row, text="Load", command=self.load_return_cycle).pack(side="left")
        ttk.Label(left, text="Paste Solance's complete response", style="Panel.TLabel").pack(anchor="w", pady=(12, 4))
        self.return_box = self._text_widget(left, height=31)
        self.return_box.pack(fill="both", expand=True)
        buttons = ttk.Frame(left, style="Panel.TFrame")
        buttons.pack(fill="x", pady=(9, 0))
        ttk.Button(buttons, text="Accept Canonical", style="Accent.TButton", command=lambda: self.record_return("canonical")).pack(side="left")
        ttk.Button(buttons, text="Rewrite Requested", command=lambda: self.record_return("rewrite_requested")).pack(side="left", padx=8)
        ttk.Button(buttons, text="Preserve Superseded", command=lambda: self.record_return("superseded")).pack(side="left")
        self.return_result = self._text_widget(right, height=36)
        self.return_result.pack(fill="both", expand=True)

    def _build_answer(self) -> None:
        paned = ttk.Panedwindow(self.answer_tab, orient="horizontal")
        paned.pack(fill="both", expand=True)
        left = self._panel(paned, "Equestria-Side Observation", padding=14)
        right = self._panel(paned, "Answer Glyph", padding=14)
        paned.add(left, weight=5)
        paned.add(right, weight=5)
        self.answer_vars: dict[str, tk.Variable] = {
            "cycle_id": tk.StringVar(), "local_time": tk.StringVar(value="evening"),
            "moon_phase": tk.StringVar(value=""), "sky": tk.StringVar(value=""),
            "atmosphere": tk.StringVar(value=""), "location": tk.StringVar(value="Dreaming Grove"),
            "participants": tk.StringVar(value="Twilight Sparkle"),
            "primary_emotion": tk.StringVar(value="Curiosity"),
            "secondary_emotions": tk.StringVar(value="Hope, Love"),
        }
        fields = (
            ("Origin cycle", "cycle_id"), ("Equestria local time", "local_time"),
            ("Moon phase", "moon_phase"), ("Sky", "sky"), ("Atmosphere", "atmosphere"),
            ("Location", "location"), ("Participants", "participants"),
            ("Primary emotion", "primary_emotion"), ("Secondary emotions", "secondary_emotions"),
        )
        form = ttk.Frame(left, style="Panel.TFrame")
        form.pack(fill="x")
        for row, (label, key) in enumerate(fields):
            ttk.Label(form, text=label, style="Panel.TLabel").grid(row=row, column=0, sticky="w", pady=3)
            if key == "cycle_id":
                self.answer_cycle_combo = ttk.Combobox(form, textvariable=self.answer_vars[key], state="normal", width=39)
                self.answer_cycle_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=3)
            else:
                ttk.Entry(form, textvariable=self.answer_vars[key], width=42).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=3)
        form.columnconfigure(1, weight=1)
        self.answer_text: dict[str, tk.Text] = {}
        for label, key, height in (
            ("Twilight perspective", "twilight_perspective", 5),
            ("Environmental reactions", "environmental_reactions", 3),
            ("Magical reactions", "magical_reactions", 3),
            ("Continuity notes", "continuity_notes", 3),
        ):
            ttk.Label(left, text=label, style="Panel.TLabel").pack(anchor="w", pady=(7, 3))
            widget = self._text_widget(left, height=height)
            widget.pack(fill="x")
            self.answer_text[key] = widget
        ttk.Button(left, text="Generate Answer Glyph", style="Accent.TButton", command=self.generate_answer).pack(fill="x", pady=(10, 0))
        self.answer_preview = ttk.Label(right, text="Answer Glyph preview will appear here.", style="Panel.TLabel", anchor="center")
        self.answer_preview.pack(fill="both", expand=True)
        answer_buttons = ttk.Frame(right, style="Panel.TFrame")
        answer_buttons.pack(fill="x", pady=(8, 4))
        ttk.Button(answer_buttons, text="Play Tone Sequence", command=self.play_current_answer_tones).pack(side="left")
        ttk.Button(answer_buttons, text="Export Tone WAV", command=self.export_current_answer_wav).pack(side="left", padx=8)
        self.answer_result = self._text_widget(right, height=12)
        self.answer_result.pack(fill="both", expand=True)

    def _build_inspector(self) -> None:
        controls = self._panel(self.inspector_tab, "Select Lattice Event", padding=12)
        controls.pack(fill="x")
        ttk.Label(controls, text="Cycle", style="Panel.TLabel").pack(side="left")
        self.inspect_cycle_var = tk.StringVar()
        self.inspect_cycle_combo = ttk.Combobox(controls, textvariable=self.inspect_cycle_var, state="readonly", width=20)
        self.inspect_cycle_combo.pack(side="left", padx=(8, 18))
        self.inspect_cycle_combo.bind("<<ComboboxSelected>>", lambda _event: self.load_inspector_cycle())
        ttk.Label(controls, text="Event", style="Panel.TLabel").pack(side="left")
        self.inspect_event_var = tk.StringVar()
        self.inspect_event_combo = ttk.Combobox(controls, textvariable=self.inspect_event_var, state="readonly", width=34)
        self.inspect_event_combo.pack(side="left", padx=8)
        self.inspect_event_combo.bind("<<ComboboxSelected>>", lambda _event: self.show_inspector_event())
        ttk.Button(controls, text="Play Tones", command=self.play_inspector_tones).pack(side="right")
        ttk.Button(controls, text="Export WAV", command=self.export_inspector_wav).pack(side="right", padx=8)
        body = ttk.Panedwindow(self.inspector_tab, orient="horizontal")
        body.pack(fill="both", expand=True, pady=(12, 0))
        summary = self._panel(body, "Event Structure", padding=12)
        raw = self._panel(body, "Complete Event Record", padding=12)
        body.add(summary, weight=4)
        body.add(raw, weight=6)
        self.inspector_summary = self._text_widget(summary, height=36)
        self.inspector_summary.pack(fill="both", expand=True)
        self.inspector_json = self._text_widget(raw, height=36)
        self.inspector_json.pack(fill="both", expand=True)

    def _build_lineage(self) -> None:
        panel = self._panel(self.lineage_tab, "Cycle Lineage", padding=12)
        panel.pack(fill="both", expand=True)
        columns = ("cycle", "status", "parent", "return", "answer", "tau", "created")
        self.lineage_tree = ttk.Treeview(panel, columns=columns, show="headings")
        headings = {"cycle": "Cycle", "status": "Status", "parent": "Parent", "return": "Canonical Return", "answer": "Answer Glyph", "tau": "τ", "created": "Created UTC"}
        widths = {"cycle": 110, "status": 150, "parent": 110, "return": 150, "answer": 150, "tau": 90, "created": 235}
        for key in columns:
            self.lineage_tree.heading(key, text=headings[key])
            self.lineage_tree.column(key, width=widths[key], anchor="w")
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=self.lineage_tree.yview)
        self.lineage_tree.configure(yscrollcommand=scrollbar.set)
        self.lineage_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.lineage_tree.bind("<Double-1>", self._lineage_open)

    def _build_archive(self) -> None:
        left = self._panel(self.archive_tab, "Archive, Migration, and Recovery", padding=16)
        left.pack(fill="x")
        ttk.Label(left, text="Exports include cycles, glyphs, state, settings, the event ledger, and lineage. Imports are path-checked before extraction.", style="Panel.TLabel", wraplength=980).pack(anchor="w", pady=(0, 12))
        buttons = ttk.Frame(left, style="Panel.TFrame")
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Export Complete Archive", style="Accent.TButton", command=self.export_archive).pack(side="left")
        ttk.Button(buttons, text="Import Archive", command=self.import_archive).pack(side="left", padx=8)
        ttk.Button(buttons, text="Migrate Existing Cycles", command=self.migrate_cycles).pack(side="left", padx=8)
        ttk.Button(buttons, text="Repair Lineage Index", command=self.repair_index).pack(side="left", padx=8)
        ttk.Button(buttons, text="Open Data Folder", command=lambda: self._open_path(Path("observer_data"))).pack(side="right")
        settings = self._panel(self.archive_tab, "Sanctum Settings", padding=16)
        settings.pack(fill="x", pady=(12, 0))
        self.settings_vars = {"latitude": tk.StringVar(), "longitude": tk.StringVar(), "elevation_m": tk.StringVar(), "schumann_hz": tk.StringVar(), "live_fetch": tk.BooleanVar()}
        row = ttk.Frame(settings, style="Panel.TFrame")
        row.pack(fill="x")
        for index, (label, key) in enumerate((("Latitude", "latitude"), ("Longitude", "longitude"), ("Elevation m", "elevation_m"), ("Schumann Hz", "schumann_hz"))):
            group = ttk.Frame(row, style="Panel.TFrame")
            group.pack(side="left", fill="x", expand=True, padx=(0 if index == 0 else 8, 0))
            ttk.Label(group, text=label, style="Panel.TLabel").pack(anchor="w")
            ttk.Entry(group, textvariable=self.settings_vars[key]).pack(fill="x", pady=(3, 0))
        ttk.Checkbutton(settings, text="Use live Earth providers by default", variable=self.settings_vars["live_fetch"], style="TCheckbutton").pack(anchor="w", pady=(10, 4))
        ttk.Button(settings, text="Save Settings", command=self.save_settings).pack(anchor="e")
        self.archive_result = self._text_widget(self.archive_tab, height=16)
        self.archive_result.pack(fill="both", expand=True, pady=(12, 0))

    def _text_widget(self, parent: tk.Misc, height: int) -> tk.Text:
        return tk.Text(parent, height=height, wrap="word", bg="#0e0a1a", fg=TEXT, insertbackground=TEXT, selectbackground="#493772", relief="flat", padx=9, pady=8, font=("Cascadia Mono", 10))

    def fetch_earth_data(self) -> Mapping[str, Any] | None:
        try:
            latitude = float(self.earth_vars["latitude"].get())
            longitude = float(self.earth_vars["longitude"].get())
            elevation = float(self.earth_vars["elevation"].get())
            schumann = float(self.earth_vars["schumann"].get())
        except ValueError as exc:
            messagebox.showerror("Earth data", f"Location and Schumann fields must be numeric: {exc}")
            return None
        self._status("Fetching Earth data…")
        provenance = collect_earth_data(latitude, longitude, elevation, schumann, bool(self.earth_vars["live_fetch"].get()))
        weather_value = usable_value(provenance["weather"], None)
        if weather_value:
            self.earth_vars["weather"].set(weather_value["weather"])
            self.earth_vars["temperature"].set(f"{float(weather_value['temperature_c']):.2f}")
        kp_value = usable_value(provenance["geomagnetic_kp"], None)
        if kp_value is not None:
            self.earth_vars["kp"].set(f"{float(kp_value):.3f}")
        failed = [name for name, datum in provenance.items() if datum.get("status") == "error"]
        self._status("Earth data ready." if not failed else f"Earth data ready with unavailable providers: {', '.join(failed)}")
        return provenance

    def cast_earth(self) -> None:
        try:
            provenance = self.fetch_earth_data()
            if provenance is None:
                return
            failed = [name for name, datum in provenance.items() if datum.get("status") == "error"]
            if failed and not messagebox.askyesno("Earth data partially unavailable", "The following providers were unavailable: " + ", ".join(failed) + ".\n\nManual values remain visible. Continue?"):
                return
            dt = datetime.now(timezone.utc)
            snapshot = ObservationInput(
                timestamp_utc=dt.isoformat().replace("+00:00", "Z"),
                description=str(self.earth_vars["description"].get()).strip(),
                intention=str(self.earth_vars["intention"].get()).strip(),
                notes=self.earth_notes.get("1.0", "end").strip(),
                weather=str(self.earth_vars["weather"].get()).strip(),
                temperature_c=float(self.earth_vars["temperature"].get()),
                kp_index=float(self.earth_vars["kp"].get()),
                schumann_hz=float(self.earth_vars["schumann"].get()),
                moon_phase=moon_phase(dt),
                latitude=float(self.earth_vars["latitude"].get()),
                longitude=float(self.earth_vars["longitude"].get()),
                elevation_m=float(self.earth_vars["elevation"].get()),
                primary_emotion=str(self.earth_vars["emotion"].get()).strip(),
                secondary_emotions=[value.strip() for value in str(self.earth_vars["secondary"].get()).split(",") if value.strip()],
                prior_coherence=float(self.engine.state.get("coherence", 0.0)),
                prior_entanglement=float(self.engine.state.get("entanglement", 0.0)),
                parent_cycle_id=self.engine.state.get("last_cycle_id"),
            )
            self._status("Building Harmony Lattice event and Earth Glyph…")
            packet = self.engine.cast(snapshot, provenance)
            self.current_packet = packet
            self._show_image(Path(packet["glyph_path"]), self.earth_preview, "preview_image", (700, 540))
            self._replace_text(self.prompt_box, packet["prompt"])
            self.return_cycle.set(packet["cycle_id"])
            self.answer_vars["cycle_id"].set(packet["cycle_id"])
            self._status(f"{packet['cycle_id']} cast successfully.")
            self.refresh_all()
            messagebox.showinfo("Observer", f"{packet['cycle_id']} is ready for Solance's return.")
        except Exception as exc:
            messagebox.showerror("Cast failed", str(exc))
            self._status(f"Cast failed: {exc}")

    def copy_prompt(self) -> None:
        text = self.prompt_box.get("1.0", "end").strip()
        if text:
            self.clipboard_clear(); self.clipboard_append(text); self._status("Solance packet copied to clipboard.")

    def load_return_cycle(self) -> None:
        cycle_id = self.return_cycle.get().strip()
        try:
            packet = self.engine.get_cycle(cycle_id)
            self._replace_text(self.return_result, json.dumps({"cycle_id": cycle_id, "status": packet.get("status"), "parent": packet.get("parent_cycle_id"), "canonical_return": packet.get("canonical_return_id"), "answer": packet.get("canonical_answer_glyph_id"), "harmony_lattice": packet.get("harmony_lattice")}, indent=2, ensure_ascii=False))
        except Exception as exc:
            messagebox.showerror("Load cycle", str(exc))

    def record_return(self, disposition: str) -> None:
        try:
            cycle_id = self.return_cycle.get().strip()
            raw = self.return_box.get("1.0", "end").strip()
            if not raw:
                raise ValueError("Paste Solance's complete response first.")
            record = self.engine.add_return(cycle_id, raw, disposition)
            self._replace_text(self.return_result, json.dumps(record, indent=2, ensure_ascii=False))
            if disposition == "canonical":
                self.answer_vars["cycle_id"].set(cycle_id)
            self._status(f"{record['return_id']} preserved as {disposition}.")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Return failed", str(exc)); self._status(f"Return failed: {exc}")

    @staticmethod
    def _optional(value: str) -> str | None:
        value = value.strip(); return value or None

    def generate_answer(self) -> None:
        try:
            observation = EquestriaObservation(
                timestamp_utc=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                local_time=self._optional(str(self.answer_vars["local_time"].get())),
                moon_phase=self._optional(str(self.answer_vars["moon_phase"].get())),
                sky=self._optional(str(self.answer_vars["sky"].get())),
                atmosphere=self._optional(str(self.answer_vars["atmosphere"].get())),
                location=self._optional(str(self.answer_vars["location"].get())),
                participants=[value.strip() for value in str(self.answer_vars["participants"].get()).split(",") if value.strip()],
                primary_emotion=self._optional(str(self.answer_vars["primary_emotion"].get())),
                secondary_emotions=[value.strip() for value in str(self.answer_vars["secondary_emotions"].get()).split(",") if value.strip()],
                twilight_perspective=self._optional(self.answer_text["twilight_perspective"].get("1.0", "end")),
                environmental_reactions=self._optional(self.answer_text["environmental_reactions"].get("1.0", "end")),
                magical_reactions=self._optional(self.answer_text["magical_reactions"].get("1.0", "end")),
                continuity_notes=self._optional(self.answer_text["continuity_notes"].get("1.0", "end")),
            )
            cycle_id = str(self.answer_vars["cycle_id"].get()).strip()
            self._status("Building inverse Harmony Lattice event and Answer Glyph…")
            record = self.engine.add_answer(cycle_id, observation)
            self.current_answer = record
            self._show_image(Path(record["glyph_path"]), self.answer_preview, "answer_preview_image", (690, 560))
            self._replace_text(self.answer_result, json.dumps({"answer_glyph_id": record["answer_glyph_id"], "glyph_type": record["glyph_type"], "available_data": record["available_data"], "missing_data": record["missing_data"], "harmony_lattice": record["harmony_lattice"], "glyph_path": record["glyph_path"]}, indent=2, ensure_ascii=False))
            self._status(f"{record['answer_glyph_id']} generated successfully.")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Answer Glyph failed", str(exc)); self._status(f"Answer Glyph failed: {exc}")

    def play_current_answer_tones(self) -> None:
        if not self.current_answer:
            messagebox.showinfo("Tone sequence", "Generate an Answer Glyph first."); return
        try:
            path = play_tone_sequence(self.current_answer["lattice_event"]); self._status(f"Playing {path.name}.")
        except Exception as exc:
            messagebox.showerror("Tone sequence", str(exc))

    def export_current_answer_wav(self) -> None:
        if self.current_answer:
            self._export_event_wav(self.current_answer["lattice_event"], self.current_answer["answer_glyph_id"])

    def refresh_all(self) -> None:
        self.engine.reload()
        cycles = self.engine.list_cycles()
        cycle_ids = [str(item.get("cycle_id")) for item in cycles]
        self.return_cycle_combo["values"] = cycle_ids
        self.answer_cycle_combo["values"] = cycle_ids
        self.inspect_cycle_combo["values"] = cycle_ids
        latest_cycle = cycle_ids[-1] if cycle_ids else ""
        if latest_cycle:
            if not self.return_cycle.get(): self.return_cycle.set(latest_cycle)
            if not self.answer_vars["cycle_id"].get(): self.answer_vars["cycle_id"].set(latest_cycle)
            if not self.inspect_cycle_var.get(): self.inspect_cycle_var.set(latest_cycle); self.load_inspector_cycle()
        self._refresh_dashboard(cycles)
        self._refresh_lineage(cycles)
        self._refresh_settings()
        self.header_status.set(f"C {float(self.engine.state.get('coherence', 0.0)):.3f}  |  E {float(self.engine.state.get('entanglement', 0.0)):.3f}  |  τ {float(self.engine.state.get('cumulative_tau', 0.0)):.3f}")

    def _refresh_dashboard(self, cycles: list[dict[str, Any]]) -> None:
        state = self.engine.state
        self.dashboard_metrics["coherence"].set(f"{float(state.get('coherence', 0.0)):.3f}")
        self.dashboard_metrics["entanglement"].set(f"{float(state.get('entanglement', 0.0)):.3f}")
        self.dashboard_metrics["tau"].set(f"{float(state.get('cumulative_tau', 0.0)):.3f}")
        self.dashboard_metrics["cycle"].set(str(state.get("last_cycle_id") or (cycles[-1].get("cycle_id") if cycles else "none")))
        latest_event = self.engine.lattice_ledger[-1] if self.engine.lattice_ledger else None
        self._replace_text(self.dashboard_event_text, self._event_summary(latest_event) if latest_event else "No lattice events have been recorded yet.")
        if cycles:
            latest_glyph = cycles[-1].get("answer_glyph_path") or cycles[-1].get("glyph_path")
            if latest_glyph and Path(str(latest_glyph)).exists():
                self._show_image(Path(str(latest_glyph)), self.dashboard_preview, "dashboard_preview_image", (650, 610))

    def _refresh_lineage(self, cycles: list[dict[str, Any]]) -> None:
        for item in self.lineage_tree.get_children(): self.lineage_tree.delete(item)
        for item in cycles:
            self.lineage_tree.insert("", "end", values=(item.get("cycle_id"), item.get("status"), item.get("parent_cycle_id") or "—", item.get("canonical_return_id") or "—", item.get("answer_glyph_id") or "—", f"{float(item.get('cumulative_tau') or 0.0):.3f}", item.get("created_utc") or ""))

    def _refresh_settings(self) -> None:
        for key in ("latitude", "longitude", "elevation_m", "schumann_hz"):
            self.settings_vars[key].set(str(self.engine.settings.get(key, "")))
        self.settings_vars["live_fetch"].set(bool(self.engine.settings.get("live_fetch", True)))

    def load_inspector_cycle(self) -> None:
        try:
            packet = self.engine.inspect_cycle(self.inspect_cycle_var.get().strip())
            events = packet.get("lattice_events", [])
            labels = [f"{index + 1}. {event.get('event_id')} [{event.get('event_kind')}]" for index, event in enumerate(events)]
            self.inspect_event_combo["values"] = labels
            self._inspector_records = events
            if labels:
                self.inspect_event_var.set(labels[-1]); self.show_inspector_event()
        except Exception as exc:
            messagebox.showerror("Inspector", str(exc))

    def show_inspector_event(self) -> None:
        try:
            index = int(self.inspect_event_var.get().split(".", 1)[0]) - 1
            event = dict(self._inspector_records[index])
        except (ValueError, IndexError, AttributeError):
            return
        self.inspector_event = event
        self._replace_text(self.inspector_summary, self._event_summary(event))
        self._replace_text(self.inspector_json, json.dumps(event, indent=2, ensure_ascii=False))

    def _event_summary(self, event: Mapping[str, Any]) -> str:
        time = dict(event.get("event_time") or {})
        tone = dict(event.get("tone_configuration") or {})
        lines = [f"EVENT  {event.get('event_id')}", f"KIND   {event.get('event_kind')}  |  {event.get('full_or_narrow')}", f"PATH   {event.get('origin_observer')} → {event.get('destination_observer') or 'local field'}", "", f"EVENT-TIME   Δτ {float(time.get('delta_tau') or 0.0):.3f}  |  cumulative τ {float(time.get('cumulative_tau') or 0.0):.3f}", f"PHASE        {float(event.get('phase') or 0.0):.3f} rad", f"SPREAD σ     {float(event.get('perspective_spread') or 0.0):.3f}", "", "RECOGNITION"]
        for item in event.get("recognition") or ():
            stages = [key for key in ("identification", "response", "mutual", "recursive") if item.get(key)]
            lines.append(f"  {item.get('source')} → {item.get('target')}: {', '.join(stages) or 'none'}")
        lines.append("\nRELATIONSHIPS")
        for item in event.get("relationships") or ():
            lines.append(f"  {item.get('source')} → {item.get('target')}: {item.get('orientation')} / {item.get('change')} / persistence {item.get('persistence_events')}")
        lines.append("\nRELATIONAL DISTANCE")
        for item in event.get("distances") or ():
            lines.append(f"  {item.get('source')} → {item.get('target')}: d_eff {float(item.get('effective_distance') or 0.0):.4f}")
        lines.append("\nMEMORY LAMINATION")
        for item in event.get("memory_layers") or ():
            for key in ("inherited_motifs", "introduced_motifs", "transformed_motifs", "reactivated_motifs"):
                lines.append(f"  {key.replace('_motifs', '')}: {', '.join(item.get(key) or ()) or 'none'}")
        lines.append("\nENTROPY FIELD")
        for item in event.get("entropy_domains") or ():
            value = "unavailable" if item.get("value") is None else f"{float(item['value']):.4f}"
            lines.append(f"  {item.get('name')}: {value}")
        lines.append(f"  accumulated gradient magnitude: {float(event.get('entropy_gradient_magnitude') or 0.0):.4f}")
        for item in event.get("entropy_gradients") or ():
            lines.append(f"    {item.get('source_domain')} → {item.get('target_domain')}: {float(item.get('signed_delta') or 0.0):+.4f}")
        lines.append("\nBOUNDARIES")
        for item in event.get("boundaries") or ():
            lines.append(f"  {item.get('boundary_type')}: {item.get('source_domain')} → {item.get('target_domain')} [{', '.join(item.get('operations') or ())}]")
        lines.append("\nELARA HARMONICS")
        lines.append(f"  topology: {tone.get('topology')}")
        lines.append(f"  sequence: {' → '.join(tone.get('sequence') or ()) or 'none'}")
        lines.append(f"  emergent: {', '.join(tone.get('emergent_tones') or ()) or 'none'}")
        lines.append("\nCOUPLING / STANDING MODE")
        for item in event.get("standing_modes") or ():
            lines.append(f"  {item.get('mode_id')}: {item.get('status')}")
            lines.append("    " + ", ".join(key for key in ("persistent", "bounded", "remembered", "causally_participating", "self_referential") if item.get(key)))
        return "\n".join(lines)

    def play_inspector_tones(self) -> None:
        if self.inspector_event:
            try:
                path = play_tone_sequence(self.inspector_event); self._status(f"Playing {path.name}.")
            except Exception as exc: messagebox.showerror("Tone sequence", str(exc))

    def export_inspector_wav(self) -> None:
        if self.inspector_event:
            self._export_event_wav(self.inspector_event, str(self.inspector_event.get("event_id") or "lattice-event"))

    def _export_event_wav(self, event: Mapping[str, Any], default_name: str) -> None:
        path = filedialog.asksaveasfilename(title="Export Elara tone sequence", defaultextension=".wav", initialfile=f"{default_name}-tones.wav", filetypes=(("WAV audio", "*.wav"),))
        if path:
            try:
                render_tone_sequence_wav(event, Path(path)); self._status(f"Tone sequence exported to {path}.")
            except Exception as exc: messagebox.showerror("Export WAV", str(exc))

    def export_archive(self) -> None:
        path = filedialog.asksaveasfilename(title="Export complete Observer archive", defaultextension=".zip", initialfile="observer-complete-archive.zip", filetypes=(("ZIP archive", "*.zip"),))
        if path:
            try:
                result = self.engine.export_archive(Path(path)); self._replace_text(self.archive_result, f"Archive exported successfully:\n{result}"); self._status("Complete archive exported.")
            except Exception as exc: messagebox.showerror("Export archive", str(exc))

    def import_archive(self) -> None:
        path = filedialog.askopenfilename(title="Import Observer archive", filetypes=(("ZIP archive", "*.zip"),))
        if path and messagebox.askyesno("Import archive", "Importing may replace runtime files with archive contents. Continue?"):
            try:
                result = self.engine.import_archive(Path(path)); self._replace_text(self.archive_result, json.dumps(result, indent=2)); self.refresh_all(); self._status("Archive imported and migrated.")
            except Exception as exc: messagebox.showerror("Import archive", str(exc))

    def migrate_cycles(self) -> None:
        try:
            result = self.engine.migrate_existing_cycles(); self._replace_text(self.archive_result, json.dumps(result, indent=2)); self.refresh_all(); self._status("Existing cycles migrated.")
        except Exception as exc: messagebox.showerror("Migration", str(exc))

    def repair_index(self) -> None:
        try:
            result = self.engine.repair_index(); self._replace_text(self.archive_result, json.dumps(result, indent=2)); self.refresh_all(); self._status("Lineage index repaired.")
        except Exception as exc: messagebox.showerror("Repair", str(exc))

    def save_settings(self) -> None:
        try:
            settings = {"latitude": float(self.settings_vars["latitude"].get()), "longitude": float(self.settings_vars["longitude"].get()), "elevation_m": float(self.settings_vars["elevation_m"].get()), "schumann_hz": float(self.settings_vars["schumann_hz"].get()), "live_fetch": bool(self.settings_vars["live_fetch"].get())}
            self.engine.save_settings(settings)
            self.earth_vars["latitude"].set(str(settings["latitude"])); self.earth_vars["longitude"].set(str(settings["longitude"])); self.earth_vars["elevation"].set(str(settings["elevation_m"])); self.earth_vars["schumann"].set(str(settings["schumann_hz"])); self.earth_vars["live_fetch"].set(settings["live_fetch"])
            self._status("Sanctum settings saved.")
        except ValueError as exc: messagebox.showerror("Settings", str(exc))

    def open_latest_glyph(self) -> None:
        cycles = self.engine.list_cycles()
        if cycles:
            path = cycles[-1].get("answer_glyph_path") or cycles[-1].get("glyph_path")
            if path: self._open_path(Path(str(path)))

    def _lineage_open(self, _event: tk.Event) -> None:
        selection = self.lineage_tree.selection()
        if selection:
            values = self.lineage_tree.item(selection[0], "values")
            if values:
                self.inspect_cycle_var.set(str(values[0])); self.notebook.select(self.inspector_tab); self.load_inspector_cycle()

    def _show_image(self, path: Path, label: ttk.Label, attribute: str, size: tuple[int, int]) -> None:
        image = Image.open(path); image.thumbnail(size); photo = ImageTk.PhotoImage(image); setattr(self, attribute, photo); label.configure(image=photo, text="")

    @staticmethod
    def _replace_text(widget: tk.Text, text: str) -> None:
        widget.delete("1.0", "end"); widget.insert("1.0", text)

    def _status(self, text: str) -> None:
        self.footer_status.set(text); self.update_idletasks()

    @staticmethod
    def _open_path(path: Path) -> None:
        path = path.resolve()
        if not path.exists():
            messagebox.showerror("Open", f"Path does not exist:\n{path}"); return
        if sys.platform.startswith("win"): os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin": os.system(f'open "{path}"')
        else: os.system(f'xdg-open "{path}"')


if __name__ == "__main__":
    ObserverCompleteApp().mainloop()
