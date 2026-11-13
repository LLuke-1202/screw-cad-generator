"""Screw CAD generator - feasibility test v2 (Windows + macOS).

Normal run          : window with 3D preview + "save STEP".
--selftest [--out D]: no window; build, write STEP, re-import, write selftest.log to D.
Log file            : Windows -> next to the exe ; macOS -> ~/Library/Logs/ScrewGen/
"""
import base64
import logging
import os
import platform
import sys
import threading
import time
import traceback

APP_VERSION = "test-v3"


def base_dir():
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def log_dir():
    if sys.platform == "darwin":
        d = os.path.expanduser("~/Library/Logs/ScrewGen")
    elif getattr(sys, "frozen", False):
        d = os.path.dirname(sys.executable)
    else:
        d = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(d, exist_ok=True)
    return d


LOG_PATH = os.path.join(log_dir(), "screwgen.log")
logging.basicConfig(filename=LOG_PATH, filemode="w", level=logging.INFO, encoding="utf-8",
                    format="%(asctime)s.%(msecs)03d [%(threadName)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("screwgen")


def selftest(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "selftest.log")
    with open(path, "w", encoding="utf-8") as f:
        def w(msg):
            f.write(msg + "\n")
            f.flush()
        try:
            w(f"version={APP_VERSION} os={platform.platform()} python={platform.python_version()}")
            t = time.time()
            import cadquery as cq
            w(f"import cadquery {time.time() - t:.2f}s")
            from geometry_test import build_m3_pan, export_step, mesh
            t = time.time()
            s = build_m3_pan()
            w(f"build valid={s.isValid()} volume={s.Volume():.3f} {time.time() - t:.2f}s")
            out = os.path.join(out_dir, "M3x10_pan_PH1.step")
            t = time.time()
            export_step(s, out)
            r = cq.importers.importStep(out).val()
            w(f"step write+reimport valid={r.isValid()} volume={r.Volume():.3f} {time.time() - t:.2f}s")
            t = time.time()
            v, tri = mesh(s)
            w(f"tessellate triangles={len(tri) // 3} {time.time() - t:.2f}s")
            ok = s.isValid() and r.isValid() and abs(r.Volume() - s.Volume()) < 0.01 * s.Volume() and len(tri) > 0
            w("SELFTEST PASS" if ok else "SELFTEST FAIL")
            return 0 if ok else 1
        except Exception:
            w(traceback.format_exc())
            w("SELFTEST FAIL")
            return 1


class Api:
    def __init__(self):
        self._shape = None
        self._window = None
        self._kernel_ready = threading.Event()
        self._kernel_error = None
        self._kernel_seconds = None

    # --- background warm-up: importing the CAD kernel is the slowest part of start-up
    def warm_up(self):
        t = time.time()
        log.info("kernel import start")
        try:
            import cadquery  # noqa: F401
            import geometry_test  # noqa: F401
            self._kernel_seconds = time.time() - t
            log.info("kernel import done %.2fs", self._kernel_seconds)
        except Exception:
            self._kernel_error = traceback.format_exc()
            log.error("kernel import FAILED\n%s", self._kernel_error)
        self._kernel_ready.set()

    def status(self):
        return dict(ready=self._kernel_ready.is_set(), error=self._kernel_error, seconds=self._kernel_seconds,
                    log=LOG_PATH, version=APP_VERSION, os=platform.platform())

    def generate(self):
        log.info("generate called")
        try:
            if not self._kernel_ready.wait(timeout=600):
                return dict(ok=False, error="CAD 核心載入超過 10 分鐘仍未完成", log=LOG_PATH)
            if self._kernel_error:
                return dict(ok=False, error="CAD 核心載入失敗：\n" + self._kernel_error, log=LOG_PATH)
            from geometry_test import build_m3_pan, mesh_arrays
            t0 = time.time()
            self._shape = build_m3_pan()
            t1 = time.time()
            log.info("build done %.2fs valid=%s", t1 - t0, self._shape.isValid())
            verts, tris = mesh_arrays(self._shape)
            t2 = time.time()
            log.info("tessellate done %.2fs triangles=%d", t2 - t1, len(tris) // 3)
            res = dict(ok=True, verts=base64.b64encode(verts.tobytes()).decode("ascii"),
                       tris=base64.b64encode(tris.tobytes()).decode("ascii"),
                       ntri=len(tris) // 3, volume=self._shape.Volume(), build_s=t1 - t0, mesh_s=t2 - t1)
            log.info("payload ready, %d KB -> sending to window", (len(res["verts"]) + len(res["tris"])) // 1024)
            return res
        except Exception:
            err = traceback.format_exc()
            log.error("generate FAILED\n%s", err)
            return dict(ok=False, error=err, log=LOG_PATH)

    def js_log(self, msg):
        log.info("[window] %s", msg)

    def save_step(self):
        import webview
        from geometry_test import export_step
        if self._shape is None:
            return dict(ok=False, error="請先產生模型")
        try:
            dlg = getattr(webview, "FileDialog", None)
            mode = dlg.SAVE if dlg else webview.SAVE_DIALOG
            res = self._window.create_file_dialog(mode, save_filename="M3x10_pan_PH1.step",
                                                 file_types=("STEP (*.step;*.stp)",))
            if not res:
                return dict(ok=False, error="已取消")
            path = res if isinstance(res, str) else res[0]
            t = time.time()
            export_step(self._shape, path)
            log.info("STEP saved %s %.2fs", path, time.time() - t)
            return dict(ok=True, path=path)
        except Exception:
            err = traceback.format_exc()
            log.error("save FAILED\n%s", err)
            return dict(ok=False, error=err)


def main():
    if "--selftest" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else log_dir()
        sys.exit(selftest(out))
    log.info("start version=%s os=%s python=%s frozen=%s", APP_VERSION, platform.platform(),
             platform.python_version(), getattr(sys, "frozen", False))
    import webview
    api = Api()
    threading.Thread(target=api.warm_up, name="warmup", daemon=True).start()
    api._window = webview.create_window("螺絲 CAD 生成器 - 系統測試 v3", os.path.join(base_dir(), "web", "index.html"),
                                       js_api=api, width=1100, height=760)
    webview.start(http_server=True)
    log.info("window closed")


if __name__ == "__main__":
    main()
