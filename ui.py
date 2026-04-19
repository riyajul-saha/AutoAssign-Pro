import customtkinter as ctk
import threading
from backend import generate_assignment  # Backend logic (API, parsing, saving)

# ------------------------------
# App Configuration
# ------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # We'll override with custom colors

# Color palette (matches the draft)
COLORS = {
    "bg": "#0D1117",
    "card": "#161B22",
    "accent": "#00C8FF",
    "success": "#3FB950",
    "error": "#F85149",
    "text": "#C9D1D9",
    "text_secondary": "#8B949E",
}


class AutoAssignProApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("AutoAssign Pro")
        self.geometry("1100x750")
        self.minsize(1000, 650)
        self.configure(fg_color=COLORS["bg"])

        # State variables
        self.is_processing = False
        self.chill_mode = ctk.BooleanVar(value=True)

        # Build UI
        self._create_header()
        self._create_main_layout()
        self._create_chill_panel()

        # Initial log entry
        self._log("System ready...")

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(20, 10))

        # Left: App name + icon
        left_frame = ctk.CTkFrame(header, fg_color="transparent")
        left_frame.pack(side="left")

        brain_label = ctk.CTkLabel(
            left_frame,
            text="🧠",
            font=ctk.CTkFont(size=28),
            text_color=COLORS["accent"],
        )
        brain_label.pack(side="left", padx=(0, 10))

        title_label = ctk.CTkLabel(
            left_frame,
            text="AutoAssign Pro",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=COLORS["text"],
        )
        title_label.pack(side="left")

        # Right: Status indicator
        self.status_frame = ctk.CTkFrame(header, fg_color="transparent")
        self.status_frame.pack(side="right")

        self.status_dot = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["success"],
        )
        self.status_dot.pack(side="left", padx=(0, 5))

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Idle",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
        )
        self.status_label.pack(side="left")
        
        # Subtle underline divider
        divider = ctk.CTkFrame(self, fg_color="#1F2937", height=2)
        divider.pack(fill="x", padx=20, pady=(0, 15))

    # ------------------------------------------------------------------
    # Main Layout (two columns: left for core, right for Chill Mode)
    # ------------------------------------------------------------------
    def _create_main_layout(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Left column: Inputs + Button + Log
        left_col = ctk.CTkFrame(main_container, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self._create_input_section(left_col)
        self._create_action_button(left_col)
        self._create_log_section(left_col)

        # Right column: Chill Mode panel (will be added later)
        self.right_col = ctk.CTkFrame(
            main_container,
            width=260,
            fg_color=COLORS["card"],
            corner_radius=12,
        )
        self.right_col.pack(side="right", fill="y", padx=(15, 0))
        self.right_col.pack_propagate(False)

    # ------------------------------------------------------------------
    # Input Section
    # ------------------------------------------------------------------
    def _create_input_section(self, parent):
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 15))

        # Topic Entry
        topic_label = ctk.CTkLabel(
            input_frame,
            text="Language / Topic",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"],
        )
        topic_label.pack(anchor="w", pady=(0, 5))

        CODING_LANGUAGES = [
            "C", "C++", "C#", "Dart", "Go", "HTML/CSS",
            "Java", "JavaScript", "Kotlin", "PHP",
            "Python", "R", "Ruby", "Rust", "SQL",
            "Swift", "TypeScript",
        ]

        self.topic_entry = ctk.CTkOptionMenu(
            input_frame,
            values=CODING_LANGUAGES,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["card"],
            text_color=COLORS["text"],
            button_color="#1F2937",
            button_hover_color=COLORS["accent"],
            dropdown_fg_color=COLORS["card"],
            dropdown_text_color=COLORS["text"],
            dropdown_hover_color=COLORS["accent"],
            corner_radius=8,
        )
        self.topic_entry.set("Select Language")
        self.topic_entry.pack(fill="x", pady=(0, 15))

        # Row frame for Description & Number
        row_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 15))

        # Description / Specific Field Entry
        desc_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        desc_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        desc_label = ctk.CTkLabel(
            desc_frame,
            text="Description / Specific Field",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"],
        )
        desc_label.pack(anchor="w", pady=(0, 5))

        self.desc_entry = ctk.CTkEntry(
            desc_frame,
            placeholder_text="OS, ML, Basic, etc.",
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["card"],
            border_color=COLORS["accent"],
            border_width=0,
            corner_radius=8,
        )
        self.desc_entry.insert(0, "Basic")
        self.desc_entry.pack(fill="x")
        self._add_focus_glow(self.desc_entry)

        # Assignment Number Entry
        num_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        num_frame.pack(side="right", fill="both", expand=False)
        
        num_label = ctk.CTkLabel(
            num_frame,
            text="No. Questions",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"],
        )
        num_label.pack(anchor="w", pady=(0, 5))

        self.num_entry = ctk.CTkEntry(
            num_frame,
            width=120,
            placeholder_text="5",
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["card"],
            border_color=COLORS["accent"],
            border_width=0,
            corner_radius=8,
        )
        self.num_entry.insert(0, "5")
        self.num_entry.pack(fill="x")
        self._add_focus_glow(self.num_entry)

        # Questions Textbox
        questions_label = ctk.CTkLabel(
            input_frame,
            text="Assignment Questions",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"],
        )
        questions_label.pack(anchor="w", pady=(0, 5))

        self.questions_textbox = ctk.CTkTextbox(
            input_frame,
            height=140,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["card"],
            border_color=COLORS["accent"],
            border_width=0,
            corner_radius=8,
            wrap="word",
        )
        self.questions_textbox.pack(fill="x", pady=(0, 5))
        
        # Initial placeholder state
        self.questions_placeholder = "Paste questions (one per line)"
        self.questions_textbox.insert("1.0", self.questions_placeholder)
        self.questions_textbox.configure(text_color=COLORS["text_secondary"])
        
        self.questions_textbox.bind("<FocusIn>", self._clear_placeholder)
        self.questions_textbox.bind("<FocusOut>", self._restore_placeholder)
        self._add_focus_glow(self.questions_textbox)

        # Smart Hint
        hint_label = ctk.CTkLabel(
            input_frame,
            text="💡 Tip: Language / Topic is mandatory. You can also paste existing questions below.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        )
        hint_label.pack(anchor="w", pady=(5, 0))

    def _add_focus_glow(self, widget):
        """Add a soft neon border when widget is focused."""
        def on_focus_in(event):
            widget.configure(border_width=2)

        def on_focus_out(event):
            widget.configure(border_width=0)

        widget.bind("<FocusIn>", on_focus_in)
        widget.bind("<FocusOut>", on_focus_out)

    def _clear_placeholder(self, event):
        if self.questions_textbox.get("1.0", "end-1c").strip() == self.questions_placeholder:
            self.questions_textbox.delete("1.0", "end")
            self.questions_textbox.configure(text_color=COLORS["text"])

    def _restore_placeholder(self, event):
        if not self.questions_textbox.get("1.0", "end-1c").strip():
            self.questions_textbox.delete("1.0", "end")
            self.questions_textbox.insert("1.0", self.questions_placeholder)
            self.questions_textbox.configure(text_color=COLORS["text_secondary"])

    # ------------------------------------------------------------------
    # Action Button + Spinner
    # ------------------------------------------------------------------
    def _create_action_button(self, parent):
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 15))

        # Centered big button with visual power
        self.start_button = ctk.CTkButton(
            button_frame,
            text="🚀 Start Generation",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=54,
            fg_color=COLORS["accent"],
            hover_color="#33D6FF",
            text_color="#000000",
            corner_radius=12,
            border_color="#0088AA", # Subtle dark border for depth before glow
            border_width=2,
            command=self.start_generation,
        )
        # Width 60-70% (via padx)
        self.start_button.pack(pady=10, fill="x", padx=80)
        
        # Micro-interactions: hover zoom and glow effect
        def on_enter(e):
            self.start_button.configure(
                font=ctk.CTkFont(size=19, weight="bold"), # Slight zoom
                border_color="#00C8FF" # Glow pop effect (neon blue)
            )

        def on_leave(e):
            self.start_button.configure(
                font=ctk.CTkFont(size=18, weight="bold"),
                border_color="#0088AA"
            )

        self.start_button.bind("<Enter>", on_enter)
        self.start_button.bind("<Leave>", on_leave)

        # Indeterminate progress bar (spinner)
        self.progress_bar = ctk.CTkProgressBar(
            button_frame,
            mode="indeterminate",
            height=4,
            fg_color=COLORS["card"],
            progress_color=COLORS["accent"],
            corner_radius=2,
        )
        self.progress_bar.pack(fill="x", pady=(5, 0))
        self.progress_bar.stop()
        self.progress_bar.set(0)

    # ------------------------------------------------------------------
    # Log / Console Area
    # ------------------------------------------------------------------
    def _create_log_section(self, parent):
        log_frame = ctk.CTkFrame(parent, fg_color="transparent")
        log_frame.pack(fill="both", expand=True)

        # Header
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            log_header,
            text="SYSTEM LOG",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(side="left")

        ctk.CTkLabel(
            log_header,
            text="───────────────────────────────",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=10)

        # Log textbox (read-only terminal style)
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Courier New", size=13),
            fg_color="#090C10", # Darker terminal background
            text_color="#3FB950", # Terminal green
            corner_radius=8,
            wrap="word",
            state="disabled",
            padx=15, # Extra padding for terminal feel
            pady=15,
        )
        self.log_textbox.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Chill Mode Panel (Right Side)
    # ------------------------------------------------------------------
    def _create_chill_panel(self):
        # Header inside panel
        panel_header = ctk.CTkFrame(self.right_col, fg_color="transparent")
        panel_header.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            panel_header,
            text="🎬 Chill Mode",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        # Toggle switch
        self.chill_switch = ctk.CTkSwitch(
            panel_header,
            text="",
            variable=self.chill_mode,
            onvalue=True,
            offvalue=False,
            command=self._toggle_chill_mode,
            width=40,
            height=20,
            progress_color=COLORS["accent"],
        )
        self.chill_switch.pack(side="right")

        # "Reel" placeholder (simulated video area)
        self.reel_frame = ctk.CTkFrame(
            self.right_col,
            fg_color="#0A0E14",
            corner_radius=8,
            height=180,
        )
        self.reel_frame.pack(fill="x", padx=15, pady=(0, 15))
        self.reel_frame.pack_propagate(False)

        self.reel_label = ctk.CTkLabel(
            self.reel_frame,
            text="🎥 Reel playing...\n(Chill beats 🎵)",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
            justify="center",
        )
        self.reel_label.pack(expand=True)

        # Small description
        desc_label = ctk.CTkLabel(
            self.right_col,
            text="Anti-bored mode keeps you\nentertained while AI works.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            wraplength=220,
            justify="left",
        )
        desc_label.pack(padx=15, pady=(0, 15))
        
    def _toggle_chill_mode(self):
        if self.chill_mode.get():
            self.reel_label.configure(text="🎥 Reel playing...\n(Chill beats 🎵)")
            self._log("🎬 Chill Mode enabled.")
        else:
            self.reel_label.configure(text="⏸️ Chill Mode paused")
            self._log("⏸️ Chill Mode disabled.")

    # ------------------------------------------------------------------
    # Logging Helper
    # ------------------------------------------------------------------
    def _log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"> {message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
        self.update_idletasks()

    # ------------------------------------------------------------------
    # Status Management
    # ------------------------------------------------------------------
    def _set_status(self, status, color):
        status_map = {
            "idle": ("Idle", COLORS["success"]),
            "processing": ("Processing", COLORS["accent"]),
            "error": ("Error", COLORS["error"]),
        }
        text, dot_color = status_map.get(status, ("Idle", COLORS["success"]))
        self.status_label.configure(text=text)
        self.status_dot.configure(text_color=dot_color)

    # ------------------------------------------------------------------
    # Error Popup — Shown when user leaves both inputs empty
    # ------------------------------------------------------------------
    def _show_error_popup(self, title, message):
        """Display a styled modal error dialog centered on the main window."""
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("340x180")
        popup.resizable(False, False)
        popup.configure(fg_color=COLORS["bg"])
        popup.transient(self)   # Keep popup above the main window
        popup.grab_set()        # Make it modal (block interaction below)
        
        # Center the popup relative to the main window
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - popup.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")
        
        # Warning icon
        lbl_icon = ctk.CTkLabel(
            popup, text="⚠️", font=ctk.CTkFont(size=36),
            text_color=COLORS["error"],
        )
        lbl_icon.pack(pady=(20, 5))
        
        # Error message
        lbl_msg = ctk.CTkLabel(
            popup, text=message, font=ctk.CTkFont(size=14),
            text_color=COLORS["text"], wraplength=300,
        )
        lbl_msg.pack(pady=(0, 15))
        
        # Dismiss button
        btn = ctk.CTkButton(
            popup, text="Got it", font=ctk.CTkFont(weight="bold"),
            command=popup.destroy, fg_color=COLORS["error"],
            hover_color="#C0392B", width=100,
        )
        btn.pack(pady=(0, 20))

    # ------------------------------------------------------------------
    # Invalid Input Popup — Shown when AI rejects the input
    # ------------------------------------------------------------------
    def _show_invalid_input_popup(self):
        """Display a premium-styled modal popup when the AI detects
        the user's input is not a valid topic or question."""
        popup = ctk.CTkToplevel(self)
        popup.title("Invalid Input")
        popup.geometry("420x260")
        popup.resizable(False, False)
        popup.configure(fg_color=COLORS["bg"])
        popup.transient(self)
        popup.grab_set()

        # Center the popup relative to the main window
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - popup.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")

        # Styled card container
        card = ctk.CTkFrame(
            popup, fg_color=COLORS["card"], corner_radius=16,
            border_color="#F85149", border_width=2,
        )
        card.pack(fill="both", expand=True, padx=12, pady=12)

        # Icon
        ctk.CTkLabel(
            card, text="🚫", font=ctk.CTkFont(size=42),
        ).pack(pady=(18, 4))

        # Title
        ctk.CTkLabel(
            card, text="Not a Valid Topic or Question",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["error"],
        ).pack(pady=(0, 6))

        # Description
        ctk.CTkLabel(
            card,
            text="The AI could not recognize your input as a legitimate\n"
                 "topic or assignment question. Please enter a real\n"
                 "academic topic or valid questions and try again.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
            justify="center",
            wraplength=360,
        ).pack(pady=(0, 14))

        # Dismiss button
        btn = ctk.CTkButton(
            card, text="Try Again",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"], hover_color="#33D6FF",
            text_color="#000000", corner_radius=10,
            width=140, height=36,
            command=popup.destroy,
        )
        btn.pack(pady=(0, 16))

    # ------------------------------------------------------------------
    # Start Generation — Input validation + thread launch
    # ------------------------------------------------------------------
    def start_generation(self):
        """Validate inputs and kick off the backend in a worker thread."""
        if self.is_processing:
            return

        # Read and sanitize inputs
        topic = self.topic_entry.get().strip()
        questions = self.questions_textbox.get("1.0", "end-1c").strip()
        
        description = self.desc_entry.get().strip()
        if not description:
            description = "Basic"
            
        num_questions_str = self.num_entry.get().strip()
        try:
            num_questions = int(num_questions_str) if num_questions_str else 5
            if num_questions <= 0:
                num_questions = 5
        except ValueError:
            num_questions = 5

        # Ignore the placeholder text as valid input
        if questions == self.questions_placeholder:
            questions = ""

        # Topic is now compulsory
        if not topic:
            self._show_error_popup(
                "Input Required",
                "Please select or enter a Language/Topic. It is mandatory.",
            )
            return

        # Lock the UI while processing
        self.is_processing = True
        self.start_button.configure(text="⏳ Processing...", state="disabled")
        self.topic_entry.configure(state="disabled")
        self.desc_entry.configure(state="disabled")
        self.num_entry.configure(state="disabled")
        self.questions_textbox.configure(state="disabled")
        self._set_status("processing", COLORS["accent"])
        self.progress_bar.start()

        # Clear previous log entries
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

        # Launch the backend on a daemon thread (keeps UI responsive)
        thread = threading.Thread(
            target=self._run_generation, args=(topic, questions, description, num_questions),
        )
        thread.daemon = True
        thread.start()

    # ------------------------------------------------------------------
    # Worker Thread — Delegates to backend.generate_assignment()
    # ------------------------------------------------------------------
    def _run_generation(self, topic, questions, description, num_questions):
        """
        Runs on a background thread.
        Calls the backend orchestrator and routes its log messages
        back to the UI via self.after().
        """
        # Thread-safe log helper: schedules _log on the main thread
        def log_to_ui(msg):
            self.after(0, self._log, msg)

        # Call the backend (all API / parsing / saving happens here)
        result = generate_assignment(
            topic=topic,
            questions=questions,
            description=description,
            num_questions=num_questions,
            log_callback=log_to_ui,
        )

        # Schedule UI completion on the main thread
        self.after(0, self._generation_complete, result)

    # ------------------------------------------------------------------
    # Generation Complete — Re-enable the UI
    # ------------------------------------------------------------------
    def _generation_complete(self, result):
        """Restore all UI controls after generation finishes."""
        success = result["success"]
        message = result.get("message", "")

        self.is_processing = False
        self.start_button.configure(text="🚀 Start Generation", state="normal")
        self.topic_entry.configure(state="normal")
        self.desc_entry.configure(state="normal")
        self.num_entry.configure(state="normal")
        self.questions_textbox.configure(state="normal")

        # Stop the progress bar animation
        self.progress_bar.stop()
        self.progress_bar.set(0)

        # Handle invalid input specifically
        if message == "INVALID_INPUT":
            self._set_status("error", COLORS["error"])
            self._log("─" * 40)
            self._log("🚫 Input rejected — not a valid topic or question.")
            self._show_invalid_input_popup()
            return

        # Update status indicator based on result
        if success:
            self._set_status("idle", COLORS["success"])
        else:
            self._set_status("error", COLORS["error"])

        # Final log messages
        self._log("─" * 40)
        if success:
            self._log("✨ Done! current_assignment.json has been created.")
        else:
            self._log("⚠️ Generation failed. Please try again.")



# ------------------------------
# Run Application
# ------------------------------
if __name__ == "__main__":
    app = AutoAssignProApp()
    app.mainloop()