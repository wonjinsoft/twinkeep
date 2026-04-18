"""
TwinKeep Device Monitor Extension
- 백그라운드 스레드: TwinKeep API HTTP 폴링만 담당
- Kit 업데이트 이벤트(메인 스레드): USD Prim 색상 갱신
"""
import threading
import urllib.request
import json
import carb
import omni.ext
import omni.kit.app
import omni.usd
from pxr import UsdGeom, Gf

TWINKEEP_API = "http://localhost:8000"
POLL_INTERVAL = 2.0  # 초

DEVICE_ID = "b8051d49-58e7-4bdf-87a7-a397bfea4ca7"
PRIM_PATH  = "/World/MyPhone"


class TwinKeepDeviceMonitor(omni.ext.IExt):

    def on_startup(self, _ext_id):
        carb.log_info("[TwinKeep] Extension 시작")

        # 스레드와 메인 스레드가 공유하는 최신 상태
        self._latest_state: list[float] | None = None
        self._lock = threading.Lock()

        # 백그라운드 폴링 스레드 (HTTP만)
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

        # Kit 업데이트 이벤트 구독 (메인 스레드, 매 프레임)
        self._update_sub = (
            omni.kit.app.get_app()
            .get_update_event_stream()
            .create_subscription_to_pop(self._on_update, name="twinkeep_update")
        )

    def on_shutdown(self):
        carb.log_info("[TwinKeep] Extension 종료")
        self._running = False
        self._update_sub = None

    # ── 백그라운드: HTTP 폴링 ──────────────────────────

    def _poll_loop(self):
        import time
        while self._running:
            try:
                url = f"{TWINKEEP_API}/devices/{DEVICE_ID}/state"
                res = urllib.request.urlopen(url, timeout=3)
                data = json.loads(res.read())
                if data and "v" in data:
                    with self._lock:
                        self._latest_state = data["v"]
            except Exception as e:
                carb.log_warn(f"[TwinKeep] 상태 조회 실패: {e}")
            time.sleep(POLL_INTERVAL)

    # ── 메인 스레드: USD Prim 갱신 ────────────────────

    def _on_update(self, _event):
        with self._lock:
            state = self._latest_state

        if state is None:
            return

        stage = omni.usd.get_context().get_stage()
        if stage is None:
            return

        # Prim이 없으면 Sphere 생성
        prim = stage.GetPrimAtPath(PRIM_PATH)
        if not prim.IsValid():
            UsdGeom.Sphere.Define(stage, PRIM_PATH)
            carb.log_info(f"[TwinKeep] Prim 생성: {PRIM_PATH}")
            return

        # 첫 번째 값(0~1)을 색상으로 변환 (0=빨강, 1=초록)
        value = max(0.0, min(1.0, state[0]))
        color = Gf.Vec3f(1.0 - value, value, 0.0)
        UsdGeom.Gprim(prim).GetDisplayColorAttr().Set([color])
