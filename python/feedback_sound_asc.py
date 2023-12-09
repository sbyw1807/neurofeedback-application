import numpy as np
import pyaudio
from timeflux.core.node import Node

class AuditoryFeedback(Node):

    def __init__(self, rate=44100, duration=0.5):
        super().__init__()

        self.rate = rate  # Sampling rate
        self.duration = duration  # Duration of the tone in seconds
        self.stream = None
        self.p = pyaudio.PyAudio()

    def _generate_sine_wave(self, frequency, amplitude=0.5, fade_duration=0.05):
        t = np.linspace(0, self.duration, int(self.rate * self.duration), endpoint=False)
        sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Apply fade-in and fade-out effects
        fade_samples = int(fade_duration * self.rate)
        if fade_samples > 0:
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            sine_wave[:fade_samples] *= fade_in
            sine_wave[-fade_samples:] *= fade_out
        
        return (sine_wave * (2**15 - 1)).astype(np.int16)

    def _play_wave(self, wave):
        if not self.stream:
            self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.rate, output=True, frames_per_buffer=1024)

        self.stream.write(wave.tobytes())

    def map_alpha_to_frequency(self, alpha_mean):
        min_alpha_mean = 70
        max_alpha_mean = 120
        min_frequency = 100
        max_frequency = 500

        # Calculate the frequency for a given alpha_mean
        return (alpha_mean - min_alpha_mean) * (max_frequency - min_frequency) / (max_alpha_mean - min_alpha_mean) + min_frequency

    def update(self):
        if self.i.ready():
            alpha_data = self.i.data
            if alpha_data is None:
                return

            # Calculate the mean alpha value for each timepoint
            alpha_mean_per_timepoint = np.mean(alpha_data, axis=1)

            # Map alpha_mean to the frequency range using linear mapping and clamp it
            frequencies = np.array([self.map_alpha_to_frequency(alpha_mean) for alpha_mean in alpha_mean_per_timepoint])

            # Create a continuous sine wave based on the frequencies
            continuous_wave = np.concatenate([self._generate_sine_wave(frequency) for frequency in frequencies])

            # Play the continuous sine wave
            self._play_wave(continuous_wave)

            # Print the alpha_mean values and corresponding frequencies
            for alpha_mean, frequency in zip(alpha_mean_per_timepoint, frequencies):
                print(f"Alpha Mean: {alpha_mean}, Frequency: {frequency:.2f} Hz")

            # Point output to the same data object as input
            self.o.data = alpha_data

    def terminate(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
