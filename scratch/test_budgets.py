import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

# First upload file
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
with open("sample-data/enterprise_perimeter_scan.nessus", "rb") as f:
    file_bytes = f.read()

body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="enterprise_perimeter_scan.nessus"\r\n'
    f"Content-Type: application/xml\r\n\r\n"
).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

req = urllib.request.Request(
    f"{BASE_URL}/scan/upload",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST"
)

with urllib.request.urlopen(req) as resp:
    upload_res = json.loads(resp.read().decode("utf-8"))
    job_id = upload_res["job_id"]

import time
time.sleep(0.5)

for budget in [50000.0, 150000.0, 300000.0]:
    url = f"{BASE_URL}/scan/{job_id}/results?budget={budget}"
    with urllib.request.urlopen(url) as r_resp:
        data = json.loads(r_resp.read().decode("utf-8"))
        opt = data.get("optimization_results", {})
        post_sim = data.get("post_opt_simulation_results", {})
        print(f"\n--- Budget INR {budget:,.2f} ---")
        print("Selected CVEs:", opt.get("selected_cves"))
        print(f"Total Patch Cost: INR {opt.get('total_cost'):,.2f}")
        post_eal_val = post_sim.get('eal') if post_sim else 0.0
        post_var_val = post_sim.get('var_95') if post_sim else 0.0
        print(f"Post-Opt Simulated EAL: INR {post_eal_val:,.2f}")
        print(f"Post-Opt Simulated VaR95: INR {post_var_val:,.2f}")

