import httpx

DEVICE_ID = input("device_id 입력: ").strip()

payload = {"eid": DEVICE_ID, "v": [0.9, 0.5, 0.1]}
r = httpx.put(f"http://localhost:8000/devices/{DEVICE_ID}/state", json=payload)
print("응답:", r.status_code, r.json())
