"""tonecapture/player.py"""

import os
from typing import Optional
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf
import sounddevice as sd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class AudioStream:
    """A class to handle audio playback using sounddevice."""

    def __init__(self, signal: np.ndarray, sample_rate: float):
        self.signal: np.ndarray = signal.reshape(-1, 1)
        self.sample_rate: float = sample_rate
        self.position: int = 0
        self.paused: bool = False
        self.stream: Optional[sd.OutputStream] = None

    def _callback(self, outdata, frames, time, status) -> None:
        if status:
            print(status)
        chunksize = min(len(self.signal) - self.position, frames)
        outdata[:chunksize] = self.signal[self.position : self.position + chunksize]
        if chunksize < frames:
            outdata[chunksize:] = 0
            raise sd.CallbackStop
        self.position += chunksize
        print(
            f"status={status}, chunksize={chunksize}, position={self.position}, time={time.currenttime:.2f}"
        )

    def play(self):
        """Starts playback of the audio signal."""
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.signal.ndim,
            callback=self._callback,
        )
        self.stream.start()
        self.paused = False

    def pause(self):
        """Pauses the audio playback."""
        if self.stream and self.stream.active:
            self.stream.stop()
            self.paused = True

    def resume(self):
        """Resumes the audio playback."""
        if self.stream and not self.stream.active:
            self.stream.start()
            self.paused = False

    def stop(self):
        """Stops the audio playback and resets the position."""
        if self.stream and self.stream.active:
            self.stream.stop()
            self.stream.close()
            self.paused = False


def save_audio(signal: np.ndarray, sample_rate: int, output_path: str):
    """Saves an audio signal to a file."""
    sf.write(output_path, signal, sample_rate)


def load_impulse_response(ir_relative_path: str) -> tuple[np.ndarray, float]:
    """Loads an impulse response from a relative path."""
    project_dir = Path(__file__).parent.parent
    ir_file_path = project_dir / ir_relative_path
    impulse_response, sample_rate = librosa.load(str(ir_file_path), sr=None)
    return impulse_response, sample_rate


def resample_signal(
    signal: np.ndarray, original_sample_rate: float, target_sample_rate: float
) -> np.ndarray:
    """Resamples a signal to a target sample rate.
    If the original sample rate is the same as the target, returns the original signal.

    Args:
        signal (np.ndarray): The audio signal to resample.
        original_sample_rate (int): The original sample rate of the signal.
        target_sample_rate (int): The desired sample rate for the output signal.

    Returns:
        np.ndarray: The resampled audio signal.
    """
    if original_sample_rate == target_sample_rate:
        return signal
    return librosa.resample(
        signal, orig_sr=original_sample_rate, target_sr=target_sample_rate
    )


def average_impulse_responses(impulse_responses: list[np.ndarray]) -> np.ndarray:
    """Averages multiple impulse responses."""
    if not impulse_responses:
        raise ValueError("No impulse responses provided for averaging.")

    # Ensure all impulse responses are the same length
    max_length = max(len(ir) for ir in impulse_responses)
    padded_irs = [
        np.pad(ir, (0, max_length - len(ir)), mode="constant")
        for ir in impulse_responses
    ]

    averaged_ir = np.mean(padded_irs, axis=0)
    return averaged_ir / np.max(np.abs(averaged_ir))


def apply_ir(
    signal: np.ndarray,
    signal_sample_rate: float,
    impulse_response: np.ndarray,
    impulse_response_sample_rate: float,
) -> np.ndarray:
    """
    Applies an impulse response to an audio track.
    Resamples the impulse response if sample rates are different.

    Args:
        audio_track (np.ndarray): The audio track to which the impulse response will be applied.
        audio_track_sample_rate (float): The sample rate of the audio track.
        impulse_response (np.ndarray): The impulse response to apply.
        ir_sample_rate (int): The sample rate of the impulse response.

    Returns:
        np.ndarray: The convolved signal resulting from applying the impulse response to the audio track.
    """
    if signal_sample_rate != impulse_response_sample_rate:
        impulse_response = resample_signal(
            impulse_response,
            original_sample_rate=impulse_response_sample_rate,
            target_sample_rate=signal_sample_rate,
        )
    convolved_signal = np.convolve(a=signal, v=impulse_response, mode="full")
    return convolved_signal / np.max(np.abs(convolved_signal))


def load_audio_track(track_relative_path: str) -> tuple[np.ndarray, float]:
    """Loads an audio track from a relative path."""
    project_dir = Path(__file__).parent.parent
    track_file_path = project_dir / track_relative_path
    audio_track, sample_rate = librosa.load(str(track_file_path), sr=None)
    return audio_track, sample_rate


def plot_signals(original_signal, impulse_response, convolved_signal):
    """Plots the original, impulse response, and convolved signals."""
    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=("Original Signal", "Impulse Response", "Convolved Signal"),
    )
    fig.add_trace(
        go.Scatter(y=original_signal, mode="lines", name="Original Signal"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(y=impulse_response, mode="lines", name="Impulse Response"),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(y=convolved_signal, mode="lines", name="Convolved Signal"),
        row=3,
        col=1,
    )
    fig.update_layout(height=600, showlegend=False)
    fig.show()


def main():
    """
    Main function to demonstrate applying an impulse response.
    Example usage:
    Load a guitar track and apply an impulse response to it.
    """
    track_relative_path = "data/signal/Dry Guitar.wav"
    guitar_track, sample_rate = load_audio_track(track_relative_path)

    ir_path = "data/irs"
    ir_file = "Celestion Vintage 30 - Eminence 2x12 IR/V30 2x12 OR57 1.5in 0in OA30.wav"
    ir_relative_path = os.path.join(ir_path, ir_file)
    impulse_response, ir_sample_rate = load_impulse_response(ir_relative_path)

    convolved_signal = apply_ir(
        guitar_track, sample_rate, impulse_response, ir_sample_rate
    )

    plot_signals(guitar_track, impulse_response, convolved_signal)

    stream = AudioStream(convolved_signal, sample_rate)

    while True:
        command = input("Enter command (play, pause, resume, stop): ")
        if command == "play":
            stream.play()
        if command == "pause":
            stream.pause()
        elif command == "resume":
            stream.resume()
        elif command == "stop":
            stream.stop()
            break


if __name__ == "__main__":
    main()
