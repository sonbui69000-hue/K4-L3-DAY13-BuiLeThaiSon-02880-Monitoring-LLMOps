from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

LOG_PATH = Path("data/logs.jsonl")
REFRESH_SECONDS = 30
WINDOW_MINUTES = 60

st.set_page_config(page_title="Day 13 Monitoring & LLMOps", layout="wide")
st.title("K4-L3B Day 13 Monitoring & LLMOps")
st.caption("Nguồn: data/logs.jsonl · Time range: 60 phút · Refresh: 30 giây")


def load_logs() -> pd.DataFrame:
    if not LOG_PATH.exists():
        return pd.DataFrame()
    records = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if not records:
        return pd.DataFrame()
    frame = pd.DataFrame(records)
    frame["ts"] = pd.to_datetime(frame["ts"], utc=True, errors="coerce")
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=WINDOW_MINUTES)
    return frame[frame["ts"] >= cutoff].copy()


def percentile(values: pd.Series, p: int) -> float:
    values = pd.to_numeric(values, errors="coerce").dropna()
    return float(values.quantile(p / 100)) if not values.empty else 0.0


def threshold_chart(series: pd.Series, threshold: float, title: str, unit: str) -> None:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        st.info("Chưa có dữ liệu trong 60 phút gần nhất.")
        return
    chart = pd.DataFrame({"value": values.to_numpy()})
    fig, ax = plt.subplots(figsize=(8, 2.4))
    ax.plot(chart.index, chart["value"], marker="o", linewidth=1)
    ax.axhline(threshold, color="red", linestyle="--", label=f"Threshold {threshold} {unit}")
    ax.set_title(title)
    ax.set_ylabel(unit)
    ax.legend(loc="upper right")
    st.pyplot(fig, clear_figure=True)


logs = load_logs()
if logs.empty:
    st.warning("Chưa có structured log trong khoảng 60 phút gần nhất.")
    st.stop()

responses = logs[logs["event"] == "response_sent"]
requests = logs[logs["event"] == "request_received"]
fails = logs[logs["event"] == "request_failed"]
tool_events = logs[logs["tool_success"].notna()] if "tool_success" in logs else pd.DataFrame()

latency_p50 = percentile(responses.get("latency_ms", pd.Series(dtype=float)), 50)
latency_p95 = percentile(responses.get("latency_ms", pd.Series(dtype=float)), 95)
latency_p99 = percentile(responses.get("latency_ms", pd.Series(dtype=float)), 99)
ttft_p95 = percentile(responses.get("ttft_ms", pd.Series(dtype=float)), 95)

latency_panel, traffic_panel = st.columns(2)
with latency_panel:
    st.subheader("Latency")
    a, b, c, d = st.columns(4)
    a.metric("P50", f"{latency_p50:.0f} ms")
    b.metric("P95", f"{latency_p95:.0f} ms")
    c.metric("P99", f"{latency_p99:.0f} ms")
    d.metric("TTFT P95", f"{ttft_p95:.0f} ms")
    threshold_chart(responses.get("latency_ms", pd.Series(dtype=float)), 3000, "Latency with SLO threshold", "ms")
with traffic_panel:
    st.subheader("Traffic")
    st.metric("Requests", len(requests))
    traffic = requests.set_index("ts").resample("1min").size().rename("requests_per_minute")
    st.line_chart(traffic)
    threshold_chart(traffic, 1, "Traffic with minimum threshold", "requests/minute")
    st.caption("Unit: requests/minute · threshold: 1")

errors_panel, cost_panel = st.columns(2)
with errors_panel:
    st.subheader("Errors")
    error_rate = (len(fails) / len(requests) * 100) if len(requests) else 0.0
    retrieval_success = (tool_events["tool_success"].astype(bool).mean() * 100) if not tool_events.empty else 0.0
    a, b = st.columns(2)
    a.metric("Error rate", f"{error_rate:.2f}%")
    b.metric("Retrieval success", f"{retrieval_success:.2f}%")
    error_series = fails.set_index("ts").resample("1min").size() / requests.set_index("ts").resample("1min").size().replace(0, pd.NA) * 100
    threshold_chart(error_series.fillna(0), 2, "Error rate with threshold", "%")
    if not fails.empty:
        st.bar_chart(fails["error_type"].fillna("unknown").value_counts())
    else:
        st.success("Không có request lỗi trong cửa sổ hiện tại.")
with cost_panel:
    st.subheader("Cost")
    costs = pd.to_numeric(responses.get("cost_usd", pd.Series(dtype=float)), errors="coerce").fillna(0)
    st.metric("Total", f"${costs.sum():.6f}")
    by_minute = responses.assign(cost=costs).set_index("ts")["cost"].resample("1min").sum()
    threshold_chart(by_minute, 2.5, "Cost with total threshold", "USD")
    st.caption("Unit: USD · threshold: $2.50")

tokens_panel, quality_panel = st.columns(2)
with tokens_panel:
    st.subheader("Tokens")
    token_frame = responses[[c for c in ("tokens_in", "tokens_out") if c in responses]].apply(pd.to_numeric, errors="coerce").fillna(0)
    st.metric("Input", f"{token_frame.get('tokens_in', pd.Series(dtype=float)).sum():.0f}")
    st.metric("Output", f"{token_frame.get('tokens_out', pd.Series(dtype=float)).sum():.0f}")
    token_total = token_frame.sum(axis=1) if not token_frame.empty else pd.Series(dtype=float)
    threshold_chart(token_total, 50000, "Tokens with threshold", "tokens")
    st.caption("Unit: tokens · threshold: 50,000")
with quality_panel:
    st.subheader("Quality")
    quality = pd.to_numeric(responses.get("quality_score", pd.Series(dtype=float)), errors="coerce").dropna()
    st.metric("Average", f"{quality.mean():.2f}" if not quality.empty else "0.00")
    threshold_chart(quality, 0.75, "Quality proxy with SLO threshold", "score")

st.sidebar.info("Reload trang để cập nhật dữ liệu; refresh contract: 30 giây.")
