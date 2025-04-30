import subprocess
import os
import sys
import time

if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
    kernel32.SetConsoleMode(handle, mode.value | 0x0004)

RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"

def get_video_duration(ffprobe_path, file_path):
    try:
        result = subprocess.run(
            [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return float(result.stdout.strip())
    except Exception:
        return None

def draw_progress_bar(percent, width=40):
    filled = int(width * percent // 100)
    bar = "[" + "=" * filled + "-" * (width - filled) + f"] {percent:.1f}%"
    return bar

def scan_file(ffmpeg_path, ffprobe_path, file_path):
    print(f"{CYAN}Scanning: {file_path}{RESET}")
    duration = get_video_duration(ffprobe_path, file_path)
    use_gpu = True

    base_args = [ffmpeg_path]
    if use_gpu:
        base_args += ["-hwaccel", "cuda"]
    base_args += ["-v", "error", "-stats", "-i", file_path, "-f", "null", "NUL"]

    try:
        proc = subprocess.Popen(
            base_args,
            stderr=subprocess.PIPE,
            text=True
        )

        last_percent = -1
        error_lines = []

        while True:
            line = proc.stderr.readline()
            if line == "" and proc.poll() is not None:
                break

            if "hwaccel" in line.lower() or "not supported" in line.lower():
                print(f"{YELLOW}GPU failed, retrying with CPU...{RESET}")
                use_gpu = False
                proc.kill()

                base_args = [ffmpeg_path, "-v", "error", "-stats", "-i", file_path, "-f", "null", "NUL"]
                proc = subprocess.Popen(base_args, stderr=subprocess.PIPE, text=True)
                continue

            if "time=" in line and duration:
                timestamp = line.split("time=")[-1].split(" ")[0]
                h, m, s = 0, 0, 0
                try:
                    parts = timestamp.split(":")
                    if len(parts) == 3:
                        h, m, s = map(float, parts)
                    elif len(parts) == 2:
                        m, s = map(float, parts)
                    current_sec = h * 3600 + m * 60 + s
                    percent = min(100, (current_sec / duration) * 100)
                    if int(percent) != last_percent:
                        print(draw_progress_bar(percent), end="\r", flush=True)
                        last_percent = int(percent)
                except:
                    pass

            if "error" in line.lower() or "corrupt" in line.lower() or "invalid" in line.lower():
                error_lines.append(line.strip())

        print()

        if error_lines:
            print(f"{RED}Result: Errors found in file:{RESET}")
            for e in error_lines[:5]:
                print(f"{RED}{e}{RESET}")
        else:
            print(f"{GREEN}Result: OK. No errors detected.{RESET}")

    except Exception as e:
        print(f"{RED}Failed to scan {file_path}: {e}{RESET}")

def main():
    ffmpeg_path = "./ffmpeg.exe"
    ffprobe_path = "./ffprobe.exe"
    video_extensions = [".mp4", ".mkv", ".avi", ".mov", ".webm"]

    files = [f for f in os.listdir(".") if any(f.lower().endswith(ext) for ext in video_extensions)]

    if not files:
        print(f"{YELLOW}No video files found.{RESET}")
        return

    for i, file in enumerate(files, 1):
        print(f"{WHITE}[{i}/{len(files)}]{RESET}")
        scan_file(ffmpeg_path, ffprobe_path, file)
        print()

if __name__ == "__main__":
    main()
