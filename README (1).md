# Zero Trust 6G - Federated Anomaly Detection

A real-time visualization dashboard for Zero Trust Framework with 6G Edge Networks, featuring ML-based anomaly detection using Isolation Forest and Autoencoder models.

## Features

- **Live Backend Connection**: Real-time connection status indicator
- **Federated Simulation**: Simulate 3-10 edge nodes with ML training
- **Trust Score Calculation**: Hybrid trust metric combining Autoencoder MSE and Isolation Forest scores
- **Access Control Decisions**: GRANT, RESTRICT, or DENY based on trust scores
- **Interactive Visualizations**: 
  - MSE distribution histogram
  - Trust evolution line charts
  - Per-sample decision tables
  - Live trust evaluator with sliders
- **System Terminal**: Real-time event logging

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install fastapi uvicorn scikit-learn tensorflow pandas numpy
```

### 2. Start the Backend Server

```bash
uvicorn app:app --reload --port 8000
```

The server will start at `http://localhost:8000`

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. Open the Frontend

Open `index.html` in your web browser. You can either:

**Option A: Double-click the file**
- Simply double-click `index.html` to open it in your default browser

**Option B: Use a simple HTTP server (recommended)**
```bash
# Using Python
python -m http.server 8080

# Using Node.js
npx serve

# Using PHP
php -S localhost:8080
```

Then navigate to `http://localhost:8080/index.html`

## How to Use

1. **Check Connection**: The dashboard shows connection status in the top-right corner
   - Green "Backend Online" = Ready to go
   - Yellow "Backend Offline" = Start the backend server

2. **Run Simulation**:
   - Select number of edge nodes (3, 5, 7, or 10)
   - Click "▶ Run Simulation"
   - Watch real-time logs in the terminal

3. **View Results**:
   - **KPI Cards**: Total samples, anomalies, average trust score
   - **Node Results**: Per-node training statistics
   - **Access Decisions**: Color-coded decision table with trust bars
   - **MSE Distribution**: Histogram showing normal vs anomalous patterns
   - **Trust Evolution**: Line chart tracking trust scores per node

4. **Live Evaluator**:
   - Adjust Autoencoder MSE slider (0 - 0.5)
   - Adjust Isolation Forest score slider (-0.5 - 0.5)
   - Watch trust score and decision update in real-time

## Trust Score Formula

```python
# Trust components
ae_trust = exp(-mse * 10)
if_trust = clip(if_score + 0.5, 0, 1)

# Hybrid trust score
trust_score = 0.5 * ae_trust + 0.5 * if_trust
```

## Access Control Logic

- **GRANT** (trust > 0.80): Full access
- **RESTRICT** (0.50 < trust ≤ 0.80): Limited access
- **DENY** (trust ≤ 0.50): Access denied

## API Endpoints

### GET /api/simulate
Runs federated simulation across multiple edge nodes.

**Parameters**:
- `num_nodes` (int, default=3): Number of edge nodes

**Response**:
```json
{
  "num_nodes": 3,
  "total_samples": 600,
  "total_anomalies": 30,
  "avg_trust_score": 0.7234,
  "nodes": [...],
  "mse_distribution": {...}
}
```

### GET /api/trust_eval
Evaluates trust score for given metrics.

**Parameters**:
- `ae_mse` (float, default=0.05): Autoencoder MSE
- `if_score` (float, default=0.1): Isolation Forest score

**Response**:
```json
{
  "ae_mse": 0.05,
  "if_score": 0.1,
  "trust_score": 0.7865,
  "decision": "GRANT",
  "ae_trust_component": 0.6065,
  "if_trust_component": 0.6
}
```

### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "ok"
}
```

## Troubleshooting

### Backend won't start
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use
- Try a different port: `uvicorn app:app --reload --port 8001`

### Frontend shows "Backend Offline"
- Ensure the backend is running on port 8000
- Check browser console for CORS errors
- Try accessing `http://localhost:8000/health` directly

### No data showing
- Click "▶ Run Simulation" to generate data
- Check the terminal log for errors
- Verify backend connection status

## Architecture

```
Edge Devices → Zero Trust Layer → ML Model (IF+AE) → Decision Engine → Access Control
```

The system uses:
- **Isolation Forest**: Detects anomalies in network behavior
- **Autoencoder**: Measures reconstruction error for trust calculation
- **Hybrid Trust**: Combines both metrics for robust decision-making
- **Federated Learning**: Distributes training across edge nodes

## File Structure

```
.
├── app.py          # FastAPI backend server
├── index.html      # Frontend dashboard
└── README.md       # This file
```

## Tech Stack

**Backend**:
- FastAPI
- scikit-learn
- NumPy
- Python 3.8+

**Frontend**:
- Vanilla JavaScript
- Chart.js
- Modern CSS (CSS Grid, Flexbox)
- No framework dependencies

## License

This is a research/educational project demonstrating Zero Trust security principles in 6G networks.
