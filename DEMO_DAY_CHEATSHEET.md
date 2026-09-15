# ⚡ DEMO DAY CHEATSHEET — SIH INTERNAL ROUND PRESENTATION

---

## 1. SERVER STARTUP COMMANDS

### Terminal 1 — Backend Server (FastAPI)
```bash
.\venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000
```

### Terminal 2 — Frontend Application (Vite / React)
```bash
cd frontend
npm run dev
```

---

## 2. DASHBOARD URL
```
http://localhost:5173
```

---

## 3. PRIMARY DEMO PATH (3 CLICKS IN ORDER)

1. **CLICK 1: Upload Enterprise Perimeter Scan**
   - Click **Scan & Ingestion** in sidebar ➔ Click **🏢 Enterprise Perimeter Scan (5 CVEs)**.
   - *Result:* Processes Layer 1–5 pipeline in ~1.5s and switches to **Executive Risk Overview** (Inherent Exposure ₹967.23M, Net Risk Reduced ₹491.78M / -50.8%).

2. **CLICK 2: Inspect Tail Risk & Loss Exceedance Curve**
   - Click **Quantitative Risk** in sidebar.
   - *Result:* Demonstrates 100,000 Monte Carlo trial distributions, dual-area Exceedance Probability curves (amber baseline vs. emerald residual), and VaR95 reference line.

3. **CLICK 3: Optimize Budget & Remediation Package**
   - Click **Investment Optimization** in sidebar ➔ Click **Full Scope (₹300k)** preset chip.
   - *Result:* Triggers real-time PuLP 0/1 Knapsack optimization selecting all 5 CVEs (Cost ₹188k), displaying **Residual Modeled Exposure: ₹0.00** with explicit scope framing: *"₹0 modeled residual exposure across ingested findings — this does not represent zero organizational cyber risk."*

---

## 4. FAIL-SOFT DEMO STEP (1 CLICK)

- Click **Scan & Ingestion** in sidebar ➔ Click **⚠️ Malformed Scan (Fail-Soft Test)**.
- *Result:* Displays a clean red `INGESTION_FAILED` alert banner explaining XML syntax error handling without crashing the React UI or exposing stack traces.
