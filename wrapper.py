import sys
import os
import time
import threading
import webbrowser

import cv2
import numpy as np
import webview
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def resource_path(rel):
    """PyInstaller 单文件模式下资源位于临时解包目录，否则在脚本同目录。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def get_save_dir():
    """照片保存目录：exe 同级的「照片」文件夹。"""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(base, "照片")
    os.makedirs(d, exist_ok=True)
    return d


class Camera:
    """摄像头采集 + 美颜/滤镜 + MJPEG 流。"""

    def __init__(self):
        self.cap = None
        self.running = False
        self.lock = threading.Lock()
        self.latest = None          # 最新的 JPEG 字节
        self.last_bgr = None        # 最新处理后的 BGR 帧，用于拍照
        self._shot_seq = 0          # 拍照序号，避免重名
        self.effect = "none"        # none/beauty/whiten/rosy/bw/vintage/cool/warm
        self.smooth_val = 20        # 磨皮 0..100
        self.bright_val = 0         # 亮度 -100..100
        self.capture_thread = None
        self.server = None
        self.server_thread = None
        self.port = None
        self.error = None

    # ---------- 采集循环 ----------
    def _capture_loop(self):
        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.05)
                continue
            frame = cv2.flip(frame, 1)          # 镜像，像照镜子
            frame = self._apply_effects(frame)
            ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
            if ok:
                with self.lock:
                    self.latest = buf.tobytes()
                    self.last_bgr = frame
            time.sleep(0.02)

    # ---------- 美颜 / 滤镜 ----------
    def _sepia(self, frame):
        b, g, r = cv2.split(frame)
        sr = (0.393 * r + 0.769 * g + 0.189 * b)
        sg = (0.349 * r + 0.686 * g + 0.168 * b)
        sb = (0.272 * r + 0.534 * g + 0.131 * b)
        return cv2.merge([
            np.clip(sb, 0, 255).astype(np.uint8),
            np.clip(sg, 0, 255).astype(np.uint8),
            np.clip(sr, 0, 255).astype(np.uint8),
        ])

    def _apply_effects(self, frame):
        effect = self.effect
        smooth = self.smooth_val
        bright = self.bright_val

        # 美颜预设额外提升磨皮强度
        if effect == "beauty":
            smooth = max(smooth, 60)

        # ---- 颜色 / 风格预设 ----
        if effect in ("beauty", "whiten"):
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv[..., 1] = np.clip(hsv[..., 1].astype(np.float32) * 0.82, 0, 255).astype(np.uint8)
            frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            frame = cv2.convertScaleAbs(frame, alpha=1.0, beta=22)
        elif effect == "rosy":
            b, g, r = cv2.split(frame)
            r = cv2.add(r, 18)
            g = cv2.add(g, 6)
            frame = cv2.merge([b, g, r])
        elif effect == "bw":
            g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        elif effect == "vintage":
            frame = self._sepia(frame)
        elif effect == "cool":
            b, g, r = cv2.split(frame)
            b = cv2.add(b, 20)
            r = cv2.subtract(r, 10)
            frame = cv2.merge([b, g, r])
        elif effect == "warm":
            b, g, r = cv2.split(frame)
            r = cv2.add(r, 18)
            b = cv2.subtract(b, 14)
            frame = cv2.merge([b, g, r])

        # ---- 磨皮（保边平滑，保留五官轮廓）----
        if smooth > 0:
            sigma = 10 + smooth * 0.9
            d = 9 if smooth < 50 else 13
            blurred = cv2.bilateralFilter(frame, d, sigma, sigma)
            alpha = (smooth / 100.0) * 0.85
            frame = cv2.addWeighted(frame, 1 - alpha, blurred, alpha, 0)

        # ---- 亮度 ----
        if bright != 0:
            frame = cv2.convertScaleAbs(frame, alpha=1.0, beta=float(bright))

        return frame

    # ---------- 对外控制 ----------
    def set_effect(self, name):
        self.effect = name

    def set_param(self, key, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return
        if key == "smooth":
            self.smooth_val = max(0, min(100, value))
        elif key == "brightness":
            self.bright_val = max(-100, min(100, value))

    def start(self):
        if self.running:
            return self.port
        self.error = None
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap.release()
            self.error = "无法打开摄像头"
            return None
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap = cap
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        self._start_server()
        return self.port

    def capture(self):
        """保存当前画面（含美颜/滤镜效果）为照片，返回保存路径；失败返回 None。"""
        with self.lock:
            frame = self.last_bgr
        if frame is None:
            return None
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if not ok:
            return None
        self._shot_seq += 1
        fname = "照片_%s_%02d.jpg" % (time.strftime("%Y%m%d_%H%M%S"), self._shot_seq)
        path = os.path.join(get_save_dir(), fname)
        with open(path, "wb") as f:
            f.write(buf.tobytes())
        return path

    def stop(self):
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
            self.capture_thread = None
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
        self.latest = None
        self.last_bgr = None

    # ---------- MJPEG 服务 ----------
    def _start_server(self):
        cam = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                if self.path != "/stream":
                    self.send_response(404)
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.end_headers()
                try:
                    while cam.running:
                        with cam.lock:
                            data = cam.latest
                        if data:
                            self.wfile.write(b"--frame\r\n")
                            self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                            self.wfile.write(data)
                            self.wfile.write(b"\r\n")
                            self.wfile.flush()
                        time.sleep(0.03)
                except (BrokenPipeError, ConnectionResetError, OSError):
                    pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.port = self.server.server_address[1]
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()


camera = Camera()


class Api:
    """暴露给前端 JS 调用的接口。"""

    def open_url(self, url):
        webbrowser.open(url)

    def start_mirror(self):
        port = camera.start()
        if port is None:
            return ""
        return "http://127.0.0.1:%d/stream" % port

    def stop_mirror(self):
        camera.stop()

    def set_effect(self, name):
        camera.set_effect(name)

    def set_param(self, key, value):
        camera.set_param(key, value)

    def capture(self):
        return camera.capture()

    def open_photos(self):
        webbrowser.open(get_save_dir())


def main():
    html_path = resource_path("app.html")
    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    webview.create_window(
        "浪里小神猫的能量小站",
        html=html,
        width=520,
        height=780,
        resizable=True,
        js_api=Api(),
    )
    webview.start()


if __name__ == "__main__":
    main()
