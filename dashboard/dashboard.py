import streamlit as st
import redis
import json
import time

# Connect to Redis
redis_host = st.secrets.get("REDIS_HOST", "localhost")
redis_port = st.secrets.get("REDIS_PORT", 6379)
redis_key = st.secrets.get("REDIS_OUTPUT_KEY", "some-output-key")

redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

st.set_page_config(page_title="Resource Monitoring Dashboard", layout="wide")

st.title("Resource Monitoring Dashboard")

# Create placeholders for metrics
st.header("Network Metrics")
percent_network_egress = st.metric("Percent Network Egress", "0%")

st.header("Memory Metrics")
percent_memory_cached = st.metric("Percent Memory Cached", "0%")

st.header("CPU Metrics")
cpu_metrics = st.empty()

# Fetch and display metrics
def update_dashboard():
    try:
        data = redis_client.get(redis_key)
        if not data:
            st.warning("No data found in Redis.")
            return

        metrics = json.loads(data)

        # Update network metrics
        percent_network_egress.metric("Percent Network Egress", f"{metrics.get('percent-network-egress', 0):.2f}%")

        # Update memory metrics
        percent_memory_cached.metric("Percent Memory Cached", f"{metrics.get('percent-memory-cached', 0):.2f}%")

        # Update CPU metrics
        with cpu_metrics.container():
            st.write("### CPU Utilization")
            for key, value in metrics.items():
                if key.startswith("avg-util-"):
                    st.metric(key, f"{value:.2f}%")

    except Exception as e:
        st.error(f"Error fetching data: {e}")

# Periodically refresh the dashboard
while True:
    update_dashboard()
    time.sleep(5)
