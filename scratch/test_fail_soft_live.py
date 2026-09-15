import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

# 1. OPTIMIZATION_UNAVAILABLE: Upload real scan then query negative budget budget=-50000
print("--- 1. Testing OPTIMIZATION_UNAVAILABLE ---")
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
with open("sample-data/enterprise_perimeter_scan.nessus", "rb") as f:
    file_bytes = f.read()

body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="enterprise_perimeter_scan.nessus"\r\n'
    f"Content-Type: application/xml\r\n\r\n"
).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

req_up = urllib.request.Request(
    f"{BASE_URL}/scan/upload",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST"
)
with urllib.request.urlopen(req_up) as resp:
    up_res = json.loads(resp.read().decode("utf-8"))
    real_job_id = up_res["job_id"]

import time
time.sleep(0.5)

req = urllib.request.Request(f"{BASE_URL}/scan/{real_job_id}/results?budget=-50000")
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("Response status:", data.get("status"))
        print("Response message:", data.get("message"))
        print("Baseline EAL present:", "simulation_results" in data)
except Exception as e:
    print("Error:", e)


# 2. INGESTION_FAILED: Upload corrupt malformed XML
print("\n--- 2. Testing INGESTION_FAILED ---")
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="corrupt.xml"\r\n'
    f"Content-Type: application/xml\r\n\r\n"
    f"INVALID XML SYNTAX LINE 1"
    f"\r\n--{boundary}--\r\n"
).encode("utf-8")

req_up = urllib.request.Request(
    f"{BASE_URL}/scan/upload",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST"
)
with urllib.request.urlopen(req_up) as resp:
    up_res = json.loads(resp.read().decode("utf-8"))
    job_id = up_res["job_id"]

import time
time.sleep(0.3)
req_status = urllib.request.Request(f"{BASE_URL}/scan/{job_id}/status")
with urllib.request.urlopen(req_status) as resp:
    st_res = json.loads(resp.read().decode("utf-8"))
    print("Status:", st_res.get("status"))
    print("Message:", st_res.get("message"))
