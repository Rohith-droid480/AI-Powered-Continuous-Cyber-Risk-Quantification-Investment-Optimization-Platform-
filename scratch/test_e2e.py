import urllib.request
import urllib.parse
import json
import time
import os

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    req = urllib.request.Request(f"{BASE_URL}/")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("Root response:", data)
        assert data["status"] == "ok"

def test_full_pipeline(nessus_path, budget=150000.0):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    with open(nessus_path, "rb") as f:
        file_bytes = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(nessus_path)}"\r\n'
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
        print("Upload response:", upload_res)
        job_id = upload_res["job_id"]

    # Poll status
    for _ in range(20):
        time.sleep(0.2)
        req_status = urllib.request.Request(f"{BASE_URL}/scan/{job_id}/status")
        with urllib.request.urlopen(req_status) as s_resp:
            s_data = json.loads(s_resp.read().decode("utf-8"))
            print("Status response:", s_data)
            if s_data["status"] in ("PARSED", "INGESTION_FAILED"):
                break

    # Get results
    req_results = urllib.request.Request(f"{BASE_URL}/scan/{job_id}/results?budget={budget}")
    with urllib.request.urlopen(req_results) as r_resp:
        raw_body = r_resp.read()
        payload_size_bytes = len(raw_body)
        results = json.loads(raw_body.decode("utf-8"))
        print(f"Results payload size: {payload_size_bytes} bytes ({payload_size_bytes / 1024:.2f} KB)")
        return results, payload_size_bytes

if __name__ == "__main__":
    test_root()
    res1, size1 = test_full_pipeline("sample-data/enterprise_perimeter_scan.nessus")
    print("\n--- Pipeline Run #1 Summary ---")
    print("Job Status:", res1.get("status"))
    sim = res1.get("simulation_results", {})
    opt = res1.get("optimization_results", {})
    post_sim = res1.get("post_opt_simulation_results", {})
    print(f"Baseline EAL: INR {sim.get('eal'):,.2f}")
    print(f"Baseline VaR95: INR {sim.get('var_95'):,.2f}")
    print(f"Baseline CVaR95: INR {sim.get('cvar_95'):,.2f}")
    print(f"Baseline P10-P90: P10 INR {sim.get('p10'):,.2f} — P90 INR {sim.get('p90'):,.2f}")
    print(f"Selected CVEs: {opt.get('selected_cves')}")
    print(f"Total Cost: INR {opt.get('total_cost'):,.2f}")
    print(f"Post-Opt EAL: INR {opt.get('post_opt_eal'):,.2f}")
    print(f"Post-Opt Simulated EAL: INR {post_sim.get('eal'):,.2f}")
    print(f"Post-Opt VaR95: INR {post_sim.get('var_95'):,.2f}")
    print(f"Post-Opt CVaR95: INR {post_sim.get('cvar_95'):,.2f}")
    print(f"Baseline LEC points count: {len(res1.get('baseline_lec', []))}")
    print(f"Post-Opt LEC points count: {len(res1.get('post_opt_lec', []))}")
    print(f"Raw loss_distribution length in HTTP payload: {len(sim.get('loss_distribution', []))}")

    # Run #2 (Phase 10 verification)
    res2, size2 = test_full_pipeline("sample-data/enterprise_perimeter_scan.nessus")
    print("\n--- Pipeline Run #2 Summary ---")
    print("Job Status:", res2.get("status"))
    print(f"Baseline EAL: INR {res2.get('simulation_results', {}).get('eal'):,.2f}")
    print(f"Selected CVEs: {res2.get('optimization_results', {}).get('selected_cves')}")


    # Malformed file test (Phase 6)
    print("\n--- Testing Malformed Scan File (Phase 6) ---")
    res_malformed, _ = test_full_pipeline("sample-data/malformed_corrupt.nessus")
    print("Malformed file status:", res_malformed.get("status"))
    print("Malformed file message:", res_malformed.get("message"))
