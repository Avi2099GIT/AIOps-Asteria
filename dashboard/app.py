
import os
import requests
import streamlit as st

API_BASE = os.environ.get("ASTERIA_API_BASE", "http://localhost:8000/v1")

st.set_page_config(page_title="Asteria AIOps Dashboard", layout="wide")

st.title("Asteria AIOps – Anomaly Dashboard (Phase 6)")

st.sidebar.header("Controls")
tenant_id = st.sidebar.text_input("Tenant ID", value="demo-tenant")
service = st.sidebar.text_input("Service", value="checkout-service")
environment = st.sidebar.text_input("Environment", value="prod")

st.markdown("### 1. Run Live Anomaly Check")

log_message = st.text_area("Log / message to score", height=120, value="Error: timeout talking to payment provider")

if st.button("Score anomaly"):
    payload = {
        "tenant_id": tenant_id,
        "service": service,
        "environment": environment,
        "message": log_message,
        "tags": {},
    }
    try:
        resp = requests.post(f"{API_BASE}/predict/anomaly", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        st.success(f"Anomaly score: {data['anomaly_score']:.3f} ({data['severity']}, confidence={data['confidence']:.2f})")
        with st.expander("Raw response"):
            st.json(data)
    except Exception as e:
        st.error(f"Failed to score anomaly: {e}")

st.markdown("### 2. Recent Anomalies")

if st.button("Refresh anomalies"):
    try:
        resp = requests.get(f"{API_BASE}/anomalies/recent?limit=50", timeout=10)
        resp.raise_for_status()
        items = resp.json()
        if not items:
            st.info("No anomalies logged yet.")
        else:
            st.dataframe(items)
    except Exception as e:
        st.error(f"Failed to load anomalies: {e}")
