"""Screw CAD generator - Windows feasibility test.

Normal run : opens a window with a 3D preview and a "save STEP" button.
--selftest : no window; builds the screw, writes STEP next to the exe, re-imports and checks it.
"""
import os
import sys
import time
import traceback


def base_dir():
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def exe_dir():
    return os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))


def selftest():
    log = os.path.join(exe_dir(), "selftest.log")
    with open(log, "w", encoding="utf-8") as f:
        try:
            import cadquery as cq
            from geometry_test import build_m3_pan, export_step, mesh
            t = time.time()
            s = build_m3_pan()
            f.write(f"build ok valid={s.isValid()} volume={s.Volume():.3f} t={time.time() - t:.2f}s\n")
            out = os.path.join(exe_dir(), "M3x10_pan_PH1.step")
            export_step(s, out)
            r = cq.importers.importStep(out).val()
            v, tri = mesh(s)
            ok = s.isValid() and r.isValid() and abs(r.Volume() - s.Volume()) < 0.01 * s.Volume() and len(tri) > 0
            f.write(f"step reimport valid={r.isValid()} volume={r.Volume():.3f} triangles={len(tri) // 3}\n")
            f.write("SELFTEST PASS\n" if ok else "SELFTEST FAIL\n")
            return 0 if ok else 1
        except Exception:
            f.write(traceback.format_exc())
            f.write("SELFTEST FAIL\n")
            return 1


class Api:
    def __init__(self):
        self.shape = None
        self.window = None

    def generate(self):
        try:
            from geometry_test import build_m3_pan, mesh
            t = time.time()
            self.shape = build_m3_pan()
            v, tri = mesh(self.shape)
            return dict(ok=True, verts=v, tris=tri, volume=self.shape.Volume(), seconds=time.time() - t)
        except Exception:
            return dict(ok=False, error=traceback.format_exc())

    def save_step(self):
        import webview
        from geometry_test import export_step
        if self.shape is None:
            return dict(ok=False, error="請先產生模型")
        res = self.window.create_file_dialog(webview.SAVE_DIALOG, save_filename="M3x10_pan_PH1.step",
                                             file_types=("STEP (*.step;*.stp)",))
        if not res:
            return dict(ok=False, error="已取消")
        path = res if isinstance(res, str) else res[0]
        export_step(self.shape, path)
        return dict(ok=True, path=path)


def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    import webview
    api = Api()
    api.window = webview.create_window("螺絲 CAD 生成器 - 系統測試", os.path.join(base_dir(), "web", "index.html"),
                                       js_api=api, width=1100, height=760)
    webview.start(http_server=True)


if __name__ == "__main__":
    main()
