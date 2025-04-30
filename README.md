# Video Corruption Scanner (FFmpeg-based)
This is a lightweight Python script for scanning video files for frame-level corruption using FFmpeg. It detects frame decode errors, stream issues with full support for GPU acceleration


Features

Scans only using FFmpeg/FFprobe

GPU decoding (CUDA) with automatic fallback to CPU

Live progress bar based on actual video time

No dependencies beyond Python and FFmpeg


Requirements

Python 3.x (portable version supported)

FFmpeg and FFprobe (place ffmpeg.exe and ffprobe.exe in the same folder)
