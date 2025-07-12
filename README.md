# tonecapture
ToneCapture Studio intends to be a manager of Impulse Response files (for cabinet simulation and reverb) and other types of capture files, like NAM captures. The main objectives are:
- to store and manage these tone files with extra meta information about them (like the speaker and microphone used in an IR, or the amplifier for a NAM capture)
- to retrieve these files based on filters
- to be able to find and cluster those files by similarity (perhaps using embeddings)

## Installation

### System Dependencies

- **PortAudio**: Required for audio playback.

  - On Debian-based Linux (like Ubuntu), you can install it with:
    ```bash
    sudo apt-get update && sudo apt-get install -y libportaudio2 portaudio19-dev
    ```
