import customtkinter as ctk
import threading
import os
import json
import tkinter.filedialog as filedialog
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

        CODING_LANGUAGES = ["Choose A Topic", "C", "C++", "C#", "Dart", "Go", "HTML/CSS", "Java", "JavaScript", "Kotlin", "PHP", "Python", "R", "Ruby", "Rust", "SQL", "Swift", "TypeScript"]

        self.topic_entry = ctk.CTkComboBox(
            input_frame,
            values=CODING_LANGUAGES,
            state="readonly",
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["card"],
            border_color=COLORS["accent"],
            border_width=0,
            corner_radius=8,
            dropdown_fg_color=COLORS["card"],
            dropdown_text_color=COLORS["text"],
            dropdown_hover_color=COLORS["accent"],
            button_color=COLORS["accent"],
            button_hover_color="#33D6FF",
        )
        self.topic_entry.set("Choose A Topic")
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
        if not topic or topic == "Choose A Topic":
            self._show_error_popup(
                "Input Required",
                "Please select a Language/Topic from the list. It is mandatory.",
            )
            return
            
        self.current_language = topic

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
            self._show_success_popup()
        else:
            self._log("⚠️ Generation failed. Please try again.")

    # ------------------------------------------------------------------
    # Success, Review, and Folder Generation Methods
    # ------------------------------------------------------------------
    def _show_success_popup(self):
        """Show a popup when question generation is successful."""
        popup = ctk.CTkToplevel(self)
        popup.title("Success")
        popup.geometry("380x200")
        popup.resizable(False, False)
        popup.configure(fg_color=COLORS["bg"])
        popup.transient(self)
        popup.grab_set()

        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - popup.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            popup, text="✅", font=ctk.CTkFont(size=42)
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            popup, text="Questions are Ready!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["success"]
        ).pack(pady=(0, 10))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        def on_review():
            popup.destroy()
            self._show_review_ui()

        def on_continue():
            popup.destroy()
            self._prompt_for_save_location()

        review_btn = ctk.CTkButton(
            btn_frame, text="Review", font=ctk.CTkFont(weight="bold"),
            fg_color=COLORS["card"], hover_color="#2A303C", text_color=COLORS["text"],
            command=on_review, width=120
        )
        review_btn.pack(side="left", expand=True, padx=5)

        continue_btn = ctk.CTkButton(
            btn_frame, text="Continue", font=ctk.CTkFont(weight="bold"),
            fg_color=COLORS["accent"], hover_color="#33D6FF", text_color="#000000",
            command=on_continue, width=120
        )
        continue_btn.pack(side="right", expand=True, padx=5)

    def _show_review_ui(self):
        """Show a read-friendly UI to review, edit, copy, and continue."""
        try:
            with open("current_assignment.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self._log(f"❌ Failed to load assignment for review: {e}")
            return

        review_win = ctk.CTkToplevel(self)
        review_win.title("Review Assignment")
        review_win.geometry("800x600")
        review_win.minsize(600, 500)
        review_win.configure(fg_color=COLORS["bg"])
        review_win.transient(self)
        review_win.grab_set()

        # Header
        header = ctk.CTkFrame(review_win, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title_val = data.get("assignment_title", "Assignment Title")
        ctk.CTkLabel(
            header, text=title_val,
            font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["text"]
        ).pack(side="left")

        # Scrollable area for questions
        scroll_frame = ctk.CTkScrollableFrame(review_win, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Track the textboxes
        self.question_textboxes = []

        def add_question_box(q_text=""):
            box = ctk.CTkTextbox(
                scroll_frame, height=80, font=ctk.CTkFont(size=14),
                fg_color=COLORS["card"], text_color=COLORS["text"],
                border_color=COLORS["accent"], border_width=1, corner_radius=8, wrap="word"
            )
            box.pack(fill="x", pady=(0, 10))
            if q_text:
                box.insert("1.0", q_text)
            self.question_textboxes.append(box)

        # Populate existing questions
        for q in data.get("questions", []):
            task_text = q.get("task", "")
            if task_text:
                add_question_box(task_text)

        # Footer Actions
        footer = ctk.CTkFrame(review_win, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=20)

        def add_empty_question():
            add_question_box("")
            # Scroll to bottom
            review_win.after(100, lambda: scroll_frame._parent_canvas.yview_moveto(1.0))

        add_btn = ctk.CTkButton(
            footer, text="➕ Add Question", font=ctk.CTkFont(weight="bold"),
            fg_color=COLORS["card"], hover_color="#2A303C", text_color=COLORS["text"],
            command=add_empty_question, width=140
        )
        add_btn.pack(side="left", padx=(0, 10))

        def on_copy():
            lines = [f"{title_val}\n"]
            for i, box in enumerate(self.question_textboxes):
                text = box.get("1.0", "end-1c").strip()
                if text:
                    lines.append(f"{i+1}. {text}")
            
            full_text = "\n\n".join(lines)
            review_win.clipboard_clear()
            review_win.clipboard_append(full_text)
            self._log("📋 Questions copied to clipboard.")

        copy_btn = ctk.CTkButton(
            footer, text="📋 Copy All", font=ctk.CTkFont(weight="bold"),
            fg_color=COLORS["card"], hover_color="#2A303C", text_color=COLORS["accent"],
            command=on_copy, width=120
        )
        copy_btn.pack(side="left")

        def on_continue():
            # Save final edited questions back to json
            new_questions = []
            for i, box in enumerate(self.question_textboxes):
                text = box.get("1.0", "end-1c").strip()
                if text:
                    new_questions.append({"id": i+1, "task": text})
            
            data["questions"] = new_questions
            try:
                with open("current_assignment.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                self._log("💾 Updated current_assignment.json with edited questions.")
            except Exception as e:
                self._log(f"❌ Failed to save edits: {e}")

            review_win.destroy()
            self._prompt_for_save_location()

        continue_btn = ctk.CTkButton(
            footer, text="Continue", font=ctk.CTkFont(weight="bold", size=16),
            fg_color=COLORS["accent"], hover_color="#33D6FF", text_color="#000000",
            command=on_continue, width=140, height=40
        )
        continue_btn.pack(side="right")

    def _prompt_for_save_location(self):
        """Prompt user for a directory, then create Assignment/Code structure inside."""
        self._log("📁 Waiting for user to select a save location...")
        
        # We need a small delay so the log updates visually before the dialog locks the thread
        self.after(50, self._open_directory_dialog)
        
    def _open_directory_dialog(self):
        chosen_dir = filedialog.askdirectory(title="Select Location to Save Assignment", parent=self)
        
        if not chosen_dir:
            self._log("⚠️ Folder selection cancelled by user.")
            return

        self._create_folders(chosen_dir)

    def _create_folders(self, base_path):
        """Creates the 'Assignment' and 'Assignment/Code' directories."""
        assignment_dir = os.path.join(base_path, "Assignment")
        code_dir = os.path.join(assignment_dir, "Code")
        img_dir = os.path.join(assignment_dir, "img")
        
        try:
            os.makedirs(code_dir, exist_ok=True)
            os.makedirs(img_dir, exist_ok=True)
            self._log(f"✅ Created folder structure successfully at:\n    {assignment_dir}")
            
            # Now switch to VS Code IDE view and start the AI Agent
            self.after(500, lambda: self._switch_to_ide_ui(assignment_dir, code_dir, img_dir))
        except Exception as e:
            self._log(f"❌ Failed to create folders: {e}")

    # ------------------------------------------------------------------
    # VS Code Looking IDE Interface
    # ------------------------------------------------------------------
    def _switch_to_ide_ui(self, assignment_dir, code_dir, img_dir):
        # Destroy existing layout
        for widget in self.winfo_children():
            if widget != self:
                widget.destroy()

        # Re-create Header
        self._create_header()

        # Create IDE Container
        self.ide_container = ctk.CTkFrame(self, fg_color="transparent")
        self.ide_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Paned Window logic (Left & Right)
        self.ide_left = ctk.CTkFrame(self.ide_container, fg_color="transparent")
        self.ide_left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.ide_right = ctk.CTkFrame(self.ide_container, fg_color=COLORS["card"], width=400, corner_radius=12)
        self.ide_right.pack(side="right", fill="y", padx=(10, 0))
        self.ide_right.pack_propagate(False)

        # -- Left Side: Editor Tabs --
        self.editor_tabs = ctk.CTkTabview(self.ide_left, fg_color=COLORS["card"], segmented_button_selected_color=COLORS["accent"], segmented_button_selected_hover_color="#33D6FF")
        self.editor_tabs.pack(fill="both", expand=True, pady=(0, 10))
        
        # -- Left Side: Bottom Terminal --
        term_frame = ctk.CTkFrame(self.ide_left, fg_color=COLORS["card"], height=200, corner_radius=8)
        term_frame.pack(fill="x", pady=(0, 0))
        term_frame.pack_propagate(False)
        ctk.CTkLabel(term_frame, text="TERMINAL", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["accent"]).pack(anchor="w", padx=10, pady=(5, 0))
        self.terminal_textbox = ctk.CTkTextbox(term_frame, font=ctk.CTkFont(family="Courier New", size=13), fg_color="#090C10", text_color="#C9D1D9", wrap="word", state="disabled")
        self.terminal_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # -- Right Side: Chill Mode --
        self.right_col = self.ide_right
        self._create_chill_panel()

        # -- Right Side: System Log --
        log_header = ctk.CTkFrame(self.ide_right, fg_color="transparent")
        log_header.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(log_header, text="SYSTEM LOG", font=ctk.CTkFont(weight="bold", size=14), text_color=COLORS["accent"]).pack(side="left")
        
        self.log_textbox = ctk.CTkTextbox(self.ide_right, font=ctk.CTkFont(family="Courier New", size=12), fg_color="#090C10", text_color="#3FB950", wrap="word", state="disabled")
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._log("IDE Initialized. Starting AI Coding Agent...")
        
        # Start the Agent loop in a background thread
        import threading
        t = threading.Thread(target=self._run_coding_agent, args=(assignment_dir, code_dir, img_dir))
        t.daemon = True
        t.start()

    def _ask_permission(self, cmd):
        self._permission_result = None
        event = threading.Event()

        def _show_dialog():
            popup = ctk.CTkToplevel(self)
            popup.title("Permission Required")
            popup.geometry("400x200")
            popup.resizable(False, False)
            popup.configure(fg_color=COLORS["bg"])
            popup.transient(self)
            popup.grab_set()

            popup.update_idletasks()
            x = self.winfo_x() + (self.winfo_width() - popup.winfo_width()) // 2
            y = self.winfo_y() + (self.winfo_height() - popup.winfo_height()) // 2
            popup.geometry(f"+{x}+{y}")

            ctk.CTkLabel(popup, text="Allow this command to run?", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["accent"]).pack(pady=(15, 10))
            
            cmd_box = ctk.CTkTextbox(popup, height=60, font=ctk.CTkFont(family="Courier New", size=12), fg_color="#090C10", text_color="#C9D1D9")
            cmd_box.pack(fill="x", padx=20)
            cmd_box.insert("1.0", cmd)
            cmd_box.configure(state="disabled")

            btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
            btn_frame.pack(fill="x", padx=20, pady=15)

            def on_allow():
                self._permission_result = True
                popup.destroy()
                event.set()
                
            def on_deny():
                self._permission_result = False
                popup.destroy()
                event.set()

            ctk.CTkButton(btn_frame, text="Deny", fg_color=COLORS["card"], hover_color=COLORS["error"], command=on_deny, width=100).pack(side="left", expand=True)
            ctk.CTkButton(btn_frame, text="Allow", fg_color=COLORS["accent"], hover_color="#33D6FF", text_color="#000", command=on_allow, width=100).pack(side="right", expand=True)
            
        self.after(0, _show_dialog)
        event.wait()
        return self._permission_result

    def _term_log(self, msg):
        self.terminal_textbox.configure(state="normal")
        self.terminal_textbox.insert("end", f"{msg}\n")
        self.terminal_textbox.see("end")
        self.terminal_textbox.configure(state="disabled")
        self.update_idletasks()

    def _run_coding_agent(self, assignment_dir, code_dir, img_dir):
        from agent import check_compiler, solve_question
        import subprocess
        from PIL import ImageGrab
        
        language = getattr(self, "current_language", "Python")
        self._log(f"Checking compiler for {language}...")
        
        is_available, lang_info = check_compiler(language)
        if not is_available:
            self._log(f"❌ Compiler for {language} not found on your system!")
            self.after(0, lambda: self._show_error_popup("Compiler Missing", f"Please download and install the compiler/runtime for {language}. The agent cannot run the code."))
            return
            
        self._log(f"✅ Compiler found! Starting task solving...")
        
        try:
            with open("current_assignment.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self._log(f"❌ Could not read questions: {e}")
            return
            
        questions = data.get("questions", [])
        ext = lang_info.get("extension", ".txt")
        run_commands = lang_info.get("run_commands", [])
        
        for idx, q in enumerate(questions):
            q_id = q.get("id", idx+1)
            task = q.get("task", "")
            if not task:
                continue
                
            filename = f"a{q_id}"
            file_path = os.path.join(code_dir, f"{filename}{ext}")
            
            self._log(f"🤖 AI is solving Question {q_id}...")
            
            error_context = ""
            max_retries = 2
            success = False
            
            for attempt in range(max_retries):
                # Call AI to solve
                result = solve_question(task, language, error_context)
                if "error" in result:
                    self._log(f"❌ AI Error: {result['error']}")
                    break
                    
                code = result.get("code", "")
                dependencies = result.get("dependencies", [])
                demo_input = result.get("demo_input", [])
                
                # Write file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                # Update UI tab
                self.after(0, lambda f_name=f"{filename}{ext}", c=code: self._add_or_update_editor_tab(f_name, c))
                
                self._log(f"💾 Saved {filename}{ext}.")
                
                # Install dependencies (ask user first)
                for dep in dependencies:
                    if not self._ask_permission(dep):
                        self._term_log(f"Skipped dependency: {dep}")
                        continue
                        
                    self._term_log(f"$ {dep}")
                    try:
                        subprocess.run(dep, shell=True, check=True)
                        self._term_log(f"Dependency installed successfully.")
                    except:
                        self._term_log(f"Warning: Failed to install dependency '{dep}'")
                        
                # Execute Code
                self._term_log(f"\n--- Running Question {q_id} ---")
                
                execution_failed = False
                for cmd_info in run_commands:
                    cmd_template = cmd_info.get("command", "")
                    cmd = cmd_template.replace("{filename}", filename)
                    
                    if not self._ask_permission(cmd):
                        self._term_log(f"Execution aborted by user for: {cmd}")
                        execution_failed = True
                        break
                        
                    self._term_log(f"$ {cmd}")
                    try:
                        # Feed input if needed
                        input_str = "\n".join(demo_input) + "\n" if demo_input else ""
                        process = subprocess.Popen(
                            cmd, shell=True, cwd=code_dir,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                        )
                        stdout, stderr = process.communicate(input=input_str, timeout=15)
                        
                        if stdout:
                            self._term_log(stdout)
                        if stderr:
                            self._term_log(stderr)
                            
                        if process.returncode != 0:
                            execution_failed = True
                            error_context = stderr if stderr else "Non-zero exit code"
                            self._term_log(f"Error: Process exited with code {process.returncode}")
                            break
                    except Exception as e:
                        execution_failed = True
                        error_context = str(e)
                        self._term_log(f"Execution Error: {str(e)}")
                        break
                        
                if execution_failed:
                    self._log(f"⚠️ Execution failed on attempt {attempt+1}. Asking AI to fix...")
                    continue # Try again
                else:
                    success = True
                    # Take screenshot
                    self.after(500, lambda qid=q_id, f=filename: self._take_screenshot(qid, img_dir, f))
                    break # Success! Move to next question
                    
            if not success:
                self._log(f"❌ Failed to solve Question {q_id} after {max_retries} attempts.")
                
        self._log("🎉 All questions processed!")
        self._term_log("\n--- All done! ---")

    def _add_or_update_editor_tab(self, tab_name, code_content):
        # Check if tab exists
        try:
            tab = self.editor_tabs.tab(tab_name)
        except ValueError:
            tab = self.editor_tabs.add(tab_name)
            # Create a text box inside the new tab
            textbox = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Courier New", size=14), fg_color="#1E1E1E", text_color="#D4D4D4", wrap="none")
            textbox.pack(fill="both", expand=True, padx=5, pady=5)
            # Store reference in the tab object
            tab.textbox = textbox
            
        # Update text
        tab.textbox.configure(state="normal")
        tab.textbox.delete("1.0", "end")
        tab.textbox.insert("1.0", code_content)
        
        self.editor_tabs.set(tab_name)

    def _take_screenshot(self, q_id, img_dir, filename):
        try:
            import time
            from PIL import ImageGrab
            
            # Target the terminal frame container
            target_widget = self.terminal_textbox.master
            
            x = target_widget.winfo_rootx()
            y = target_widget.winfo_rooty()
            w = target_widget.winfo_width()
            
            # Height:Width = 1:2 -> Height = Width / 2
            h = w // 2
            
            # Wait for UI to settle
            time.sleep(0.5)
            
            # Scroll to top
            self.terminal_textbox.yview_moveto(0)
            time.sleep(0.2)
            
            img_index = 1
            while True:
                img = ImageGrab.grab(bbox=(x, y, x+w, y+h))
                img_path = os.path.join(img_dir, f"{filename}{img_index}.png")
                img.save(img_path)
                self._log(f"📸 Saved screenshot {img_index} to {filename}{img_index}.png")
                
                top, bottom = self.terminal_textbox.yview()
                if bottom >= 1.0:
                    break
                    
                self.terminal_textbox.yview_moveto(bottom)
                img_index += 1
                time.sleep(0.3)
                
            # Clear terminal after execution and screenshots are done
            self.terminal_textbox.configure(state="normal")
            self.terminal_textbox.delete("1.0", "end")
            self.terminal_textbox.configure(state="disabled")
            
        except Exception as e:
            self._log(f"⚠️ Could not capture screenshot: {e}")



# ------------------------------
# Run Application
# ------------------------------
if __name__ == "__main__":
    app = AutoAssignProApp()
    app.mainloop()