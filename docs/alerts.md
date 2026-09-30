# Template Alert và Runbook

Mỗi alert dựa trên triệu chứng người dùng hoặc SLO. Quy trình chung là Metrics → Logs → Traces.

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: P95 `response_sent.latency_ms` ≤ 3000ms
- Điều kiện: P95 latency > 3000ms trong 5 phút.
- Ảnh hưởng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời.
- Ba bước kiểm tra:
  1. Mở dashboard Latency, xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có latency cao.
  3. Mở trace cùng `correlation_id`, so sánh retrieval và generation để tìm span chậm.
- Mitigation: rollback prompt nếu regression được xác nhận, tắt practice incident hoặc giảm tải; sau đó theo dõi P95.
- Owner: `student-02880`

## Alert 2

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: tỷ lệ request thành công.
- Điều kiện: error rate > 2% trong 5 phút.
- Ảnh hưởng: một phần request không trả được câu trả lời.
- Ba bước kiểm tra:
  1. Mở dashboard Errors, xem error rate, error type và retrieval success.
  2. Lọc các event `request_failed`, lấy `correlation_id` và `error_type`.
  3. Mở trace tương ứng, xác định span retrieval hoặc generation bị lỗi.
- Mitigation: khôi phục dependency/configuration lỗi, tắt incident practice hoặc rollback thay đổi gần nhất; xác nhận error rate giảm.
- Owner: `student-02880`

## Alert 3

- Tên: `LowRetrievalSuccess`
- Severity: `warning`
- Duration: `10m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: retrieval success rate ≥ 90%.
- Điều kiện: retrieval success rate < 90% trong 10 phút.
- Ảnh hưởng: câu trả lời có thể thiếu context hoặc rơi vào fallback.
- Ba bước kiểm tra:
  1. Mở dashboard Errors, xác nhận tỷ lệ `tool_success == true` trên mọi event có field này.
  2. Lọc log theo `tool_name`, `tool_success` và `correlation_id` để chọn request thất bại.
  3. Mở trace cùng correlation ID, kiểm tra thời gian và trạng thái observation retrieval.
- Mitigation: khôi phục vector store/configuration, giảm tải hoặc chuyển sang fallback an toàn; chạy lại workload và kiểm tra quality proxy.
- Owner: `student-02880`
