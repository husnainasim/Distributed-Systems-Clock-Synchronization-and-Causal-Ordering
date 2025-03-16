# # gui.py

import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import causal_ordering

class CausalOrderingGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Distributed Causal Ordering Simulation")

        # Frame for controls
        control_frame = tk.Frame(master)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Radio buttons to select the algorithm
        self.algo_var = tk.StringVar(value="BSS")
        tk.Radiobutton(control_frame, text="BSS", variable=self.algo_var, value="BSS").pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="SES", variable=self.algo_var, value="SES").pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="Matrix", variable=self.algo_var, value="Matrix").pack(side=tk.LEFT)

        # Run button
        self.run_button = tk.Button(control_frame, text="Run Simulation", command=self.start_simulation)
        self.run_button.pack(side=tk.LEFT, padx=10)

        # Scrolled text area for logs
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=10)
        self.text_area.pack(padx=5, pady=5)

        # Canvas for processes
        self.canvas = tk.Canvas(master, width=600, height=300, bg="white")
        self.canvas.pack(padx=5, pady=5)

        # Positions for the 3 processes (for animation)
        self.process_positions = {
            0: (100, 150),
            1: (300, 150),
            2: (500, 150)
        }

        # Keep track of text items for clock labels
        self.process_labels = {}

        # Thread-safe lock for text output
        self.text_lock = threading.Lock()

        # Draw the processes in their initial state
        self.draw_processes()

        # Will store references to the "Process" objects for each simulation
        self.processes = []

    def draw_processes(self):
        """
        Draw each process as a circle with a label inside,
        plus a separate label for clock state (initially (0,0,0)).
        """
        radius = 30
        for pid, (x, y) in self.process_positions.items():
            # Circle for the process
            self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill="lightblue"
            )
            # Text label for process name, e.g., "P0"
            self.canvas.create_text(
                x, y,
                text=f"P{pid}",
                font=("Helvetica", 12, "bold")
            )
            # Clock state label below the circle
            label_id = self.canvas.create_text(
                x, y + radius + 15,
                text="(0,0,0)",
                font=("Helvetica", 10)
            )
            self.process_labels[pid] = label_id

    def reset_gui(self):
        """
        Clear the canvas entirely and re-draw the processes
        so that everything starts at zero again.
        """
        self.canvas.delete("all")
        self.process_labels.clear()
        self.draw_processes()

    def clear_output(self):
        """Clear the text area logs."""
        self.text_area.delete(1.0, tk.END)

    def start_simulation(self):
        """
        Called when the user clicks "Run Simulation".
        This method clears the output, resets the GUI,
        forces a reload of the simulation module, and then
        starts a new simulation in a background thread.
        """
        # Clear logs and canvas completely
        self.clear_output()
        self.reset_gui()

        # Force a reload of the simulation module to clear any persistent state.
        import importlib
        import causal_ordering
        importlib.reload(causal_ordering)

        # Override print to capture simulation output in our text area.
        import builtins
        original_print = builtins.print

        def print_to_gui(*args, **kwargs):
            with self.text_lock:
                message = " ".join(str(arg) for arg in args) + "\n"
                self.text_area.insert(tk.END, message)
                self.text_area.see(tk.END)

        builtins.print = print_to_gui

        # Decide which algorithm to run.
        algo = self.algo_var.get()

        def run_sim():
            try:
                # Create new process objects and run the chosen simulation.
                if algo == "BSS":
                    self.run_BSS()
                elif algo == "SES":
                    self.run_SES()
                else:  # Matrix
                    self.run_Matrix()
            finally:
                # Restore the original print function.
                builtins.print = original_print

        # Run the simulation in a new background thread.
        threading.Thread(target=run_sim).start()

    # -----------------------
    # BSS Simulation
    # -----------------------
    def run_BSS(self):
        """
        Create brand-new BSS process objects,
        then run the BSS scenario.
        """
        self.processes = [
            causal_ordering.ProcessBSS(
                pid=i,
                total_processes=3,
                on_deliver_callback=self.animate_message_delivery,
                on_clock_update_callback=self.update_clock_label
            )
            for i in range(3)
        ]
        # Now run the simulation logic
        causal_ordering.simulate_BSS(self.processes)

    # -----------------------
    # SES Simulation
    # -----------------------
    def run_SES(self):
        self.processes = [
            causal_ordering.ProcessSES(
                pid=i,
                total_processes=3,
                on_deliver_callback=self.animate_message_delivery,
                on_clock_update_callback=self.update_clock_label
            )
            for i in range(3)
        ]
        causal_ordering.simulate_SES(self.processes)

    # -----------------------
    # Matrix Simulation
    # -----------------------
    def run_Matrix(self):
        self.processes = [
            causal_ordering.ProcessMatrix(
                pid=i,
                total_processes=3,
                on_deliver_callback=self.animate_message_delivery,
                on_clock_update_callback=self.update_clock_label
            )
            for i in range(3)
        ]
        causal_ordering.simulate_Matrix(self.processes)

    # -----------------------
    # GUI Callbacks
    # -----------------------
    def update_clock_label(self, pid, clock_str):
        """
        Update the clock label text for the given process ID.
        For BSS/SES, clock_str might be (0,1,0).
        For Matrix, it might be the local row, e.g. (1,0,0).
        """
        label_id = self.process_labels[pid]
        self.canvas.itemconfig(label_id, text=clock_str)

    def animate_message_delivery(self, sender_pid, receiver_pid, content):
        """
        Animate a small circle traveling from sender to receiver.
        """
        (x1, y1) = self.process_positions[sender_pid]
        (x2, y2) = self.process_positions[receiver_pid]

        # Create a small red oval at the sender
        r = 8
        msg_ball = self.canvas.create_oval(x1 - r, y1 - r, x1 + r, y1 + r, fill="red")

        steps = 20
        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps

        for _ in range(steps):
            self.canvas.move(msg_ball, dx, dy)
            self.canvas.update()
            time.sleep(0.05)

        # Remove the ball
        self.canvas.delete(msg_ball)
