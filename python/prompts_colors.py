from timeflux.core.node import Node
import random
import tkinter as tk
import pandas as pd
import pylsl
import time

class RandomPrompt(Node):
    def __init__(self, interval=30000):
        super().__init__()
        self.interval = interval
        self._next_prompt_time = time.time() + 30  # Initialize with a 30-second delay
        self.prompt_window = None
        self.info = pylsl.StreamInfo('Prompts', 'Markers', 1, 0, 'string', 'myprompts1234')
        self.outlet = pylsl.StreamOutlet(self.info)
        self.start_time = time.time()  

    def _open_new_window(self, prompt):
        window = tk.Tk()
        window.title("Neurofeedback Prompt")
        window.configure(bg='white')
        
        # Set text color based on the prompt
        text_color = "green" if "increase" in prompt else "red"

        label = tk.Label(window, text=prompt, font=("Arial", 40, "bold"), bg="white", fg=text_color)
        label.pack(padx=50, pady=50)
        window.after(10000, lambda: self._safe_destroy(window))
        return window

    def _safe_destroy(self, window):
        if window:
            window.destroy()
            self.prompt_window = None
            
    def update(self):
        current_time = time.time()
        if self._next_prompt_time is None:
            self._next_prompt_time = current_time + self.interval / 1000.0
            
        if current_time >= self._next_prompt_time:
            prompt = random.choice(["Try to increase your alpha power", "Try to decrease your alpha power"])
            self.prompt_window = self._open_new_window(prompt)
            
            # Send only the prompt statement as the LSL marker (timestamp will be added by LSL)
            self.outlet.push_sample([prompt])
            
            # Create the DataFrame for output (without timestamp)
            df = pd.DataFrame({'prompt': [prompt]})
            self.o.set(df)
            
            self._next_prompt_time = current_time + self.interval / 1000.0

        if current_time - self.start_time >= 310:  # 300 seconds = 5 minutes
            print("5 minutes elapsed. Initiating shutdown.")
            self._shutdown_random_prompt()

        if self._next_prompt_time is None:
            self._next_prompt_time = current_time + self.interval / 1000.0

        if self.prompt_window:
            self.prompt_window.update()

    def _shutdown_random_prompt(self):
        print("Shutting down Random Prompt.")
        if self.prompt_window:
            self.prompt_window.destroy()
        exit(0)
