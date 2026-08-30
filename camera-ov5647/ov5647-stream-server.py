#!/usr/bin/env python3
"""Small single-camera MJPEG server for the Allwinner sunxi-vin OV5647."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import signal
import subprocess
import tempfile
import threading
import time

HOST = os.environ.get("OV5647_STREAM_HOST", "0.0.0.0")
PORT = int(os.environ.get("OV5647_STREAM_PORT", "8081"))
DEVICE = os.environ.get("OV5647_DEVICE", "/dev/video8")
WIDTH = int(os.environ.get("OV5647_STREAM_WIDTH", "1280"))
HEIGHT = int(os.environ.get("OV5647_STREAM_HEIGHT", "720"))
FPS = int(os.environ.get("OV5647_STREAM_FPS", "25"))
BUFFERS = int(os.environ.get("OV5647_STREAM_BUFFERS", "3"))

if BUFFERS != 3:
    raise ValueError("OV5647_STREAM_BUFFERS must be 3 for the sunxi-vin driver")

capture_lock = threading.Lock()
stats_lock = threading.Lock()
stats = {
    "active": False,
    "started_at": 0.0,
    "frames": 0,
    "bytes": 0,
    "client": None,
    "capture_pid": None,
    "encoder_pid": None,
    "last_error": None,
}

INDEX = """<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OV5647 live</title>
<style>html,body{margin:0;background:#111;color:#ddd;font:16px sans-serif}
main{display:grid;place-items:center;gap:12px;min-height:100vh;padding:12px;box-sizing:border-box}
img{max-width:100%;height:auto;background:#000;border-radius:8px}
pre{width:min(900px,100%);box-sizing:border-box;margin:0;padding:12px;border-radius:8px;
background:#1b1b1b;color:#9ee493;white-space:pre-wrap;font:14px/1.4 monospace}</style>
</head><body><main><img src="/stream.mjpg" alt="OV5647 live"><pre id="debug">Loading…</pre></main>
<script>
const debug = document.getElementById('debug');
async function updateDebug() {
  try {
    const s = await fetch('/status.json', {cache: 'no-store'}).then(r => r.json());
    debug.textContent = [
      `State:           ${s.active ? 'STREAMING' : 'IDLE'}`,
      `Device:          ${s.device}`,
      `Format:          ${s.width}x${s.height} NV12`,
      `DMA buffers:     ${s.buffers}`,
      `Camera FPS:      ${s.camera_fps}`,
      `Output FPS:      ${s.configured_fps} (actual: ${s.actual_fps})`,
      `Frames sent:     ${s.frames}`,
      `MJPEG bitrate:   ${s.mbit_s} Mbit/s`,
      `Data sent:       ${s.mib} MiB`,
      `Stream uptime:   ${s.elapsed_s} s`,
      `Client:          ${s.client || '-'}`,
      `Capture PID:     ${s.capture_pid || '-'}`,
      `Encoder PID:     ${s.encoder_pid || '-'}`,
      `Last error:      ${s.last_error || 'none'}`,
    ].join('\\n');
  } catch (e) { debug.textContent = 'status.json error: ' + e; }
}
updateDebug(); setInterval(updateDebug, 1000);
</script></body></html>""".encode("utf-8")


def status_snapshot():
    with stats_lock:
        current = stats.copy()
    elapsed = time.monotonic() - current["started_at"] if current["active"] else 0.0
    frames = current["frames"]
    byte_count = current["bytes"]
    return {
        "active": current["active"],
        "device": DEVICE,
        "width": WIDTH,
        "height": HEIGHT,
        "buffers": BUFFERS,
        "camera_fps": 31.25,
        "configured_fps": FPS,
        "actual_fps": round(frames / elapsed, 2) if elapsed else 0.0,
        "frames": frames,
        "mbit_s": round(byte_count * 8 / elapsed / 1_000_000, 2) if elapsed else 0.0,
        "mib": round(byte_count / 1024 / 1024, 2),
        "elapsed_s": round(elapsed, 1),
        "client": current["client"],
        "capture_pid": current["capture_pid"],
        "encoder_pid": current["encoder_pid"],
        "last_error": current["last_error"],
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(INDEX)))
            self.end_headers()
            self.wfile.write(INDEX)
            return

        if self.path == "/status.json":
            payload = json.dumps(status_snapshot(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path != "/stream.mjpg":
            self.send_error(404)
            return

        if not capture_lock.acquire(blocking=False):
            self.send_error(503, "Camera is already in use")
            return

        capture = None
        encoder = None
        fifo_dir = None
        boundary_tail = b""
        try:
            print(
                f"Starting capture: {DEVICE} {WIDTH}x{HEIGHT}, "
                f"buffers={BUFFERS}, output_fps={FPS}",
                flush=True,
            )
            fifo_dir = tempfile.TemporaryDirectory(prefix="ov5647-stream-")
            raw_fifo = os.path.join(fifo_dir.name, "capture.nv12")
            os.mkfifo(raw_fifo, 0o600)

            encoder = subprocess.Popen(
                [
                    "ffmpeg", "-hide_banner", "-loglevel", "warning",
                    "-f", "rawvideo", "-pixel_format", "nv12",
                    "-video_size", f"{WIDTH}x{HEIGHT}", "-framerate", "30",
                    "-i", raw_fifo, "-vf", f"fps={FPS}",
                    "-c:v", "mjpeg", "-q:v", "7",
                    "-f", "mpjpeg", "-boundary_tag", "frame", "pipe:1",
                ],
                stdout=subprocess.PIPE,
            )
            capture = subprocess.Popen(
                [
                    "v4l2-ctl", "-d", DEVICE,
                    "--set-input=0",
                    f"--set-fmt-video=width={WIDTH},height={HEIGHT},pixelformat=NV12",
                    f"--stream-mmap={BUFFERS}", "--stream-count=0",
                    f"--stream-to={raw_fifo}",
                ],
            )
            with stats_lock:
                stats.update({
                    "active": True,
                    "started_at": time.monotonic(),
                    "frames": 0,
                    "bytes": 0,
                    "client": self.client_address[0],
                    "capture_pid": capture.pid,
                    "encoder_pid": encoder.pid,
                    "last_error": None,
                })

            self.send_response(200)
            self.send_header("Cache-Control", "no-store, no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()

            while chunk := encoder.stdout.read(64 * 1024):
                self.wfile.write(chunk)
                boundary_data = boundary_tail + chunk
                frame_count = boundary_data.count(b"--frame\r\n")
                boundary_tail = boundary_data[-8:]
                with stats_lock:
                    stats["frames"] += frame_count
                    stats["bytes"] += len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as error:
            with stats_lock:
                stats["last_error"] = f"{type(error).__name__}: {error}"
            raise
        finally:
            for process in (encoder, capture):
                if process is None:
                    continue
                if process.poll() is None:
                    process.send_signal(signal.SIGTERM)
            for process in (encoder, capture):
                if process is None:
                    continue
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
            if fifo_dir is not None:
                fifo_dir.cleanup()
            with stats_lock:
                stats.update({
                    "active": False,
                    "client": None,
                    "capture_pid": None,
                    "encoder_pid": None,
                })
            capture_lock.release()
            print("Capture stopped", flush=True)

    def log_message(self, fmt, *args):
        print(f"{self.client_address[0]} - {fmt % args}", flush=True)


if __name__ == "__main__":
    print(f"OV5647 stream: http://0.0.0.0:{PORT}/", flush=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.daemon_threads = True
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping OV5647 stream server", flush=True)
    finally:
        server.server_close()
