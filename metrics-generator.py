import time
import random
import os
from flask import Flask, jsonify, Response, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY

app = Flask(__name__)

# --- Standard Health Check Metrics ---
# Counter to track the total number of health check requests
health_check_requests_total = Counter(
    "health_check_requests_total",
    "Total number of health check requests"
)
# Histogram to measure the latency of health check requests
health_check_latency_seconds = Histogram(
    "health_check_latency_seconds",
    "Latency of health check requests"
)

# --- High Cardinality Metrics ---
# This Gauge metric will be used to generate a large number of unique time series.
# Each series will be differentiated by 'series_id', 'dimension_alpha', and 'dimension_beta' labels.
high_cardinality_gauge = Gauge(
    "high_cardinality_gauge",
    "A gauge metric with extremely high cardinality for testing monitoring stack limits",
    ["series_id", "dimension_alpha", "dimension_beta"]
)

# This Counter metric will also contribute to high cardinality, similar to the gauge.
high_cardinality_counter = Counter(
    "high_cardinality_counter",
    "A counter metric with extremely high cardinality for testing monitoring stack limits",
    ["series_id", "dimension_alpha", "dimension_beta"]
)

# --- Helper data for label values ---
# These lists provide a small number of distinct values for the additional dimensions.
# The real cardinality explosion comes from the 'series_id'.
DIM_ALPHA_VALUES = ["group_A", "group_B", "group_C", "group_D", "group_E", "group_F", "group_G"]
DIM_BETA_VALUES = ["type_X", "type_Y", "type_Z", "type_W"]

def generate_label_values(index):
    """
    Generates deterministic label values for a given index.
    This ensures that each 'series_id' maps consistently to 'dimension_alpha'
    and 'dimension_beta' values, while the 'series_id' itself remains unique.
    """
    series_id = f"unique_series_{index}"
    # Cycle through the predefined dimension values
    alpha_val = DIM_ALPHA_VALUES[index % len(DIM_ALPHA_VALUES)]
    beta_val = DIM_BETA_VALUES[index % len(DIM_BETA_VALUES)]
    return series_id, alpha_val, beta_val

# --- Flask Endpoints ---

@app.route("/health")
def health_check():
    """
    Standard health check endpoint.
    Increments a counter and records latency for basic monitoring.
    """
    start_time = time.time()
    health_check_requests_total.inc()
    response = jsonify({"status": "healthy"}), 200
    latency = time.time() - start_time
    health_check_latency_seconds.observe(latency)
    return response

@app.route("/metrics")
def metrics():
    """
    Exposes Prometheus metrics by calling generate_latest() from prometheus_client.
    This endpoint will return a large amount of data after high-cardinality
    metrics have been generated.
    """
    return Response(generate_latest(), mimetype="text/plain")

@app.route("/generate_high_cardinality_metrics")
def generate_metrics():
    """
    Endpoint to trigger the generation of high-cardinality metrics.
    
    Query Parameters:
    - series_count (int, default: 10000):
      The number of unique time series to generate. Each unique series_id will
      have both a gauge and a counter metric associated with it.
      Be cautious when setting this to very high numbers (e.g., millions) as
      it will consume significant memory in the Flask application.
      
    - value_range (int, default: 1000):
      The maximum random value for the gauge metrics.
    """
    series_count = int(request.args.get("series_count", 10000))
    value_range = int(request.args.get("value_range", 1000))

    generated_count = 0
    start_time = time.time()

    app.logger.info(f"Starting generation of {series_count} high-cardinality metrics...")

    # Loop to create and update unique metric series
    for i in range(series_count):
        series_id, dim_a, dim_b = generate_label_values(i)

        # Set a random value for the high-cardinality gauge metric
        high_cardinality_gauge.labels(
            series_id=series_id,
            dimension_alpha=dim_a,
            dimension_beta=dim_b
        ).set(random.uniform(0, value_range))

        # Increment the high-cardinality counter metric
        high_cardinality_counter.labels(
            series_id=series_id,
            dimension_alpha=dim_a,
            dimension_beta=dim_b
        ).inc()

        generated_count += 1
        # Log progress for long-running generations
        if generated_count % 10000 == 0:
            app.logger.info(f"Generated {generated_count} series...")

    duration = time.time() - start_time
    app.logger.info(f"Finished generating {generated_count} series in {duration:.2f} seconds.")

    return jsonify({
        "status": "success",
        "generated_series_count": generated_count,
        "generation_duration_seconds": round(duration, 2),
        "message": (
            "Metrics generated successfully. "
            "Access the /metrics endpoint to view the output. "
            "Subsequent calls to this endpoint will add more unique series."
        )
    }), 200

# --- Application Startup ---
if __name__ == "__main__":
    # Configure basic logging to see generation progress in the console
    import logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    
    # Run the Flask application
    app.run(host="0.0.0.0", port=8080)
