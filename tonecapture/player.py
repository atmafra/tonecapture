
import numpy as np
import librosa
import soundfile as sf
import sounddevice as sd


def play_audio(signal, sample_rate):
    """Plays an audio signal."""
    print("Playing audio...")
    sd.play(signal, sample_rate)
    sd.wait()
    print("Playback finished.")


def generate_sine_wave(frequency, duration, sample_rate):
    """Generates a sine wave."""
    t = np.linspace(0.0, duration, int(sample_rate * duration), endpoint=False)
    amplitude = 0.5
    return amplitude * np.sin(2.0 * np.pi * frequency * t)


def apply_ir_and_play(guitar_track, sr_guitar, ir_path: str):
    """
    Applies an impulse response to a guitar track and plays the result.
    """
    print("Loading impulse response...")
    ir, sr_ir = librosa.load(ir_path, sr=None)

    # Resample if sample rates are different
    if sr_guitar != sr_ir:
        print("Resampling impulse response...")
        ir = librosa.resample(ir, orig_sr=sr_ir, target_sr=sr_guitar)

    print("Applying impulse response...")
    convolved_signal = np.convolve(guitar_track, ir, mode="full")

    play_audio(convolved_signal, sr_guitar)


def apply_ir(guitar_track, sr_guitar, ir_path: str, output_path: str):
    """
    Applies an impulse response to a guitar track and saves the result.
    """
    print("Loading impulse response...")
    ir, sr_ir = librosa.load(ir_path, sr=None)

    # Resample if sample rates are different
    if sr_guitar != sr_ir:
        print("Resampling impulse response...")
        ir = librosa.resample(ir, orig_sr=sr_ir, target_sr=sr_guitar)

    print("Applying impulse response...")
    convolved_signal = np.convolve(guitar_track, ir, mode="full")

    print(f"Saving output to {output_path}...")
    sf.write(output_path, convolved_signal, sr_guitar)
    print("Done.")


if __name__ == "__main__":
    # Example usage:
    # Generate a sine wave as a placeholder for the guitar track
    sr = 44100
    duration = 5
    frequency = 440  # A4 note
    guitar_track = generate_sine_wave(frequency, duration, sr)

    ir = "/home/amafra/projects/lab/tonecapture/data/irs/Celestion Vintage 30 - Eminence 2x12 IR/V30 2x12 OR57 1.5in 0in OA30.wav"

    # To save the output file
    # output = "/home/amafra/projects/lab/tonecapture/data/output.wav"
    # apply_ir(guitar_track, sr, ir, output)

    # To play the output directly
    apply_ir_and_play(guitar_track, sr, ir)
