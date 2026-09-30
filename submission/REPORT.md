# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

## 1. Thông tin học viên

- **Họ và tên:** Bui Le Thai Son
- **MSSV:** 02880
- **Lớp:** K4-L3B
- **Repository URL:**
- **Commit SHA cuối:**
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-02880`

## 2. Evidence index

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Kết quả | Ghi chú |
|---|---:|---|
| `validate_logs.py` | 100/100 | 36 records, 20 correlation IDs, 0 PII leak |
| `validate_dashboard.py` | 6/6 panel | Contract hợp lệ |
| `pytest` | 24 passed | `.venv` |
| Số traces hợp lệ | 15 | 10 baseline + 5 challenge |
| Baseline latency P95 | 861 ms | 10 requests |
| Challenge latency P95 | 2,653 ms | 5 requests |
| Retrieval success | 100% | Challenge vẫn trả response thành công |

## 4. Logging và PII

- **Correlation ID:** nhận header hợp lệ hoặc sinh `req-` + 8 ký tự hex.
- **Metadata:** user hash, session, feature, model và environment.
- **PII:** scrub đệ quy trước khi ghi JSONL.
- **Kết quả:** 0 PII leak; log validator đạt 100/100.

## 5. Tracing và prompt versioning

- **Trace tree:** `day13-agent-request` → `lab-agent-run` → `retrieval` + `generation`.
- **Generation:** có model, usage và cost; không capture raw input/output.
- **Nối log-trace:** dùng `correlation_id`.
- **Challenge trace đại diện:** correlation ID `req-b4bd2913`; trace ID `1a39fa5296301cf1b552dd30d6cd15fa`.
- **Prompt name:** `day13-chat`.
- **Prompt version/rollback:** Trace b33d3171ca9e9558c18529a243af6596 to Trace 8dd34fbdfcbf9c2a0655525815d7e437 rollback

## 6. Dashboard, SLO và alerts

- **Dashboard:** `dashboard/streamlit_app.py`, gồm Latency, Traffic, Errors, Cost, Tokens, Quality.
- **Contract:** `validate_dashboard.py` đạt 6/6 panel.
- **SLO:** 99.5% request thành công và latency không quá 3000ms trong 28 ngày.
- **Error budget:** 0.5%; 10.000 request tương ứng tối đa 50 request không đạt.
- **Alerts:** HighLatencyP95, HighErrorRate, LowRetrievalSuccess; có duration, severity, Slack channel và runbook.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`.
- **Khoảng thời gian:** `2026-09-30 04:33:52–04:34:06 UTC`.
- **Triệu chứng metrics:** latency P95 tăng từ 861ms lên 2,653ms; baseline có request nhanh khoảng 152–154ms, challenge ổn định khoảng 2,651–2,653ms.
- **Log line/correlation ID:** `request_received` của `req-b4bd2913`, session `k4-l3b-challenge-s01`.
- **Trace:** `1a39fa5296301cf1b552dd30d6cd15fa`; retrieval span khoảng 2.5 giây, generation khoảng 151ms.
- **Root cause:** practice incident `rag_slow` làm retrieval chậm 2.5 giây.
- **Fix action:** tắt `rag_slow`; `/health` xác nhận mọi incident `false`.
- **Preventive measure:** cảnh báo P95 latency, cảnh báo retrieval success, và runbook Metrics → Logs → Traces.

## 8. Giải thích và tự đánh giá

- **Quyết định kỹ thuật:** scrub trước khi serialize để tránh ghi PII thô.
- **Luồng điều tra:** metrics khoanh vùng, logs chọn correlation ID, traces xác định retrieval chậm.
- **Prompt version:** label trỏ tới version và hỗ trợ promote/rollback.
- **Kết quả:** CP1, tracing, dashboard contract và CP3 runtime đã kiểm chứng.

## 9. Checklist trước khi nộp

- [x] Bổ sung ảnh evidence.
- [x] Log validator đạt 100/100.
- [x] Dashboard validator đạt 6/6.
- [x] Full pytest đạt 24 passed.
- [x] Challenge evidence nối metric → log → trace.
- [x] Không commit secret, PII thô hoặc `config/challenge.json`.
