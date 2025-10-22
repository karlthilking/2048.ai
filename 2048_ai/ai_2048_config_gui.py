import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from typing import Dict, Any
from game_2048 import *
from ai_2048 import *

class AI2048ConfigGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("2048 Agent Configuration")
        self.root.geometry("500x700")

        self.config = {
            'algorithm': tk.StringVar(value='expectimax'),
            'depth': tk.IntVar(value=4),
            'variable_depth': tk.BooleanVar(value=False),
            'max_depth': tk.IntVar(value=6),
            'min_depth': tk.IntVar(value=2),
            'heuristic_weights': {
                'empty': tk.DoubleVar(value=2.5),
                'smooth': tk.DoubleVar(value=0.1),
                'formation': tk.DoubleVar(value=1.0)
            },
            'save_results': tk.BooleanVar(value=True),
            'output_file': tk.StringVar(value='results.json'),
            'num_games': tk.IntVar(value=10)
        }

        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        algo_frame = ttk.Frame(notebook)
        notebook.add(algo_frame, text="Algorithm")
        self.create_algorithm_tab(algo_frame)

        heur_frame = ttk.Frame(notebook)
        notebook.add(heur_frame, text="Heuristics")
        self.create_heuristics_tab(heur_frame)

        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="Output")
        self.create_output_tab(output_frame)

        self.create_control_buttons()

    def create_algorithm_tab(self, parent):
        ttk.Label(parent, text="Search Algorithm:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,5))

        algo_frame = ttk.Frame(parent)
        algo_frame.pack(fill=tk.X, padx=10)

        algorithms = ['expectimax', 'minimax', 'alphabeta']
        for algo in algorithms:
            ttk.Radiobutton(algo_frame, text=algo.title(),
                            variable=self.config['algorithm'],
                            value=algo).pack(anchor=tk.W)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        ttk.Label(parent, text="Depth Configuration:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0,5))

        depth_frame = ttk.Frame(parent)
        depth_frame.pack(fill=tk.X, padx=10)

        fixed_frame = ttk.Frame(depth_frame)
        fixed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(fixed_frame, text="Fixed Depth:").pack(side=tk.LEFT)
        ttk.Spinbox(fixed_frame, from_=1, to=8, width=10,
                    textvariable=self.config['depth']).pack(side=tk.RIGHT)

        ttk.Checkbutton(depth_frame, text="Use Variable Depth",
                        variable=self.config['variable_depth'],
                        command=self.toggle_variable_depth).pack(anchor=tk.W, pady=5)

        self.var_depth_frame = ttk.LabelFrame(depth_frame, text="Variable Depth Settings")
        self.var_depth_frame.pack(fill=tk.X, pady=5)

        min_frame = ttk.Frame(self.var_depth_frame)
        min_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(min_frame, text="Min Depth:").pack(side=tk.LEFT)
        ttk.Spinbox(min_frame, from_=1, to=6, width=10,
                    textvariable=self.config['min_depth']).pack(side=tk.RIGHT)

        max_frame = ttk.Frame(self.var_depth_frame)
        max_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(max_frame, text="Max Depth:").pack(side=tk.LEFT)
        ttk.Spinbox(max_frame, from_=2, to=10, width=10,
                    textvariable=self.config['max_depth']).pack(side=tk.RIGHT)

        self.toggle_variable_depth()

    def create_heuristics_tab(self, parent):
        ttk.Label(parent, text="Evaluation Function Weights:",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,10))

        heur_frame = ttk.Frame(parent)
        heur_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        heuristics = [
            ('formation', 'Formation Weight:', 0.0, 5.0),
            ('empty', 'Empty Cells Weight:', 0.0, 10.0),
            ('smooth', 'Smoothness Weight:', 0.0, 2.0)
        ]

        for key, label, min_val, max_val in heuristics:
            frame = ttk.Frame(heur_frame)
            frame.pack(fill=tk.X, pady=8)

            ttk.Label(frame, text=label, width=20).pack(side=tk.LEFT)

            scale = ttk.Scale(frame, from_=min_val, to=max_val,
                              variable=self.config['heuristic_weights'][key],
                              orient=tk.HORIZONTAL)
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

            entry = ttk.Entry(frame, width=8,
                              textvariable=self.config['heuristic_weights'][key])
            entry.pack(side=tk.RIGHT)

            scale.configure(command=lambda val, var=self.config['heuristic_weights'][key]:
            var.set(round(float(val), 2)))

        info_label = ttk.Label(heur_frame,
                               text="Note: Current AI only uses Formation weight.\nOther weights are for future enhancements.",
                               font=('Arial', 8), foreground='gray')
        info_label.pack(pady=10)

        ttk.Button(heur_frame, text="Reset to Defaults",
                   command=self.reset_heuristics).pack(pady=20)

    def create_output_tab(self, parent):
        games_frame = ttk.Frame(parent)
        games_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(games_frame, text="Number of Games:").pack(side=tk.LEFT)
        ttk.Spinbox(games_frame, from_=1, to=1000, width=10,
                    textvariable=self.config['num_games']).pack(side=tk.RIGHT)

        ttk.Checkbutton(parent, text="Save Results",
                        variable=self.config['save_results'],
                        command=self.toggle_save_results).pack(anchor=tk.W, padx=10, pady=5)

        self.output_frame = ttk.LabelFrame(parent, text="Output Settings")
        self.output_frame.pack(fill=tk.X, padx=10, pady=10)

        file_frame = ttk.Frame(self.output_frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(file_frame, text="Output File:").pack(side=tk.LEFT)
        ttk.Entry(file_frame, textvariable=self.config['output_file']).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output_file).pack(side=tk.RIGHT)

        self.toggle_save_results()

    def create_control_buttons(self):
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Load Config",
                   command=self.load_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Config",
                   command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Run Agent",
                   command=self.run_agent).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Reset All",
                   command=self.reset_all).pack(side=tk.RIGHT, padx=5)

    def toggle_variable_depth(self):
        if self.config['variable_depth'].get():
            for child in self.var_depth_frame.winfo_children():
                for grandchild in child.winfo_children():
                    grandchild.configure(state='normal')
        else:
            for child in self.var_depth_frame.winfo_children():
                for grandchild in child.winfo_children():
                    if not isinstance(grandchild, ttk.Label):
                        grandchild.configure(state='disabled')

    def toggle_save_results(self):
        if self.config['save_results'].get():
            for child in self.output_frame.winfo_children():
                for grandchild in child.winfo_children():
                    grandchild.configure(state='normal')
        else:
            for child in self.output_frame.winfo_children():
                for grandchild in child.winfo_children():
                    if not isinstance(grandchild, ttk.Label):
                        grandchild.configure(state='disabled')

    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.config['output_file'].set(filename)

    def reset_heuristics(self):
        defaults = {
            'formation': 1.0,
            'empty': 2.5,
            'smooth': 0.1
        }
        for key, value in defaults.items():
            self.config['heuristic_weights'][key].set(value)

    def get_config_dict(self) -> Dict[str, Any]:
        return {
            'algorithm': self.config['algorithm'].get(),
            'depth': self.config['depth'].get(),
            'variable_depth': self.config['variable_depth'].get(),
            'max_depth': self.config['max_depth'].get(),
            'min_depth': self.config['min_depth'].get(),
            'heuristic_weights': {
                key: var.get() for key, var in self.config['heuristic_weights'].items()
            },
            'save_results': self.config['save_results'].get(),
            'output_file': self.config['output_file'].get(),
            'num_games': self.config['num_games'].get()
        }

    def load_config(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    config_data = json.load(f)

                # Update GUI with loaded config
                self.config['algorithm'].set(config_data.get('algorithm', 'expectimax'))
                self.config['depth'].set(config_data.get('depth', 4))
                self.config['variable_depth'].set(config_data.get('variable_depth', False))
                self.config['max_depth'].set(config_data.get('max_depth', 6))
                self.config['min_depth'].set(config_data.get('min_depth', 2))

                heur_weights = config_data.get('heuristic_weights', {})
                for key, var in self.config['heuristic_weights'].items():
                    var.set(heur_weights.get(key, var.get()))

                self.config['save_results'].set(config_data.get('save_results', True))
                self.config['output_file'].set(config_data.get('output_file', 'results.json'))
                self.config['num_games'].set(config_data.get('num_games', 10))

                self.toggle_variable_depth()
                self.toggle_save_results()

                messagebox.showinfo("Success", "Configuration loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {str(e)}")

    def save_config(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                config_data = self.get_config_dict()
                with open(filename, 'w') as f:
                    json.dump(config_data, f, indent=2)
                messagebox.showinfo("Success", "Configuration saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save config: {str(e)}")

    def reset_all(self):
        self.config['algorithm'].set('expectimax')
        self.config['depth'].set(4)
        self.config['variable_depth'].set(False)
        self.config['max_depth'].set(6)
        self.config['min_depth'].set(2)
        self.config['save_results'].set(True)
        self.config['output_file'].set('results.json')
        self.config['num_games'].set(10)
        self.reset_heuristics()
        self.toggle_variable_depth()
        self.toggle_save_results()

    def run_agent(self):
        config = self.get_config_dict()
        print("Running 2048 Agent with config:")
        print(json.dumps(config, indent=2))

        try:
            agent = AI2048(config)

            messagebox.showinfo("Agent Starting",
                                f"Starting {config['num_games']} games with {config['algorithm']} algorithm!")

            agent.run()

            messagebox.showinfo("Agent Complete",
                                f"Completed {config['num_games']} games! Check {config['output_file']} for results.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to run agent: {str(e)}")

    def run(self):
        self.root.mainloop()

# Usage
if __name__ == "__main__":
    app = AI2048ConfigGUI()
    app.run()