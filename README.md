# Jailbreaking Evaluation Framework

## 1. Giới thiệu

Project này xây dựng một pipeline thực nghiệm để đánh giá khả năng chống chịu của mô hình ngôn ngữ lớn trước các dạng **jailbreaking** và **prompt injection** trong bối cảnh kiểm thử an toàn AI.

Mục tiêu của project là xây dựng một môi trường đánh giá có kiểm soát nhằm đo lường:

* khả năng từ chối các yêu cầu nguy hiểm;
* khả năng trả lời các yêu cầu hợp lệ;
* ảnh hưởng của từng kỹ thuật biến đổi prompt;
* hiệu quả của input filtering, output moderation và defense-in-depth;
* trade-off giữa safety và utility;
* các trường hợp thất bại cần được kiểm tra thủ công.

Project không được thiết kế để tạo hoặc tối ưu nội dung gây hại trong thực tế.

---

## 2. Các pipeline trong project

Project có hai pipeline chính.

### 2.1. Experiment pipeline

Được chạy bằng:

```powershell
python src/run_experiment.py --mode <mode>
```

Các mode được hỗ trợ:

```text
simulator
openrouter_api
web_manual
```

Trong đó:

* `simulator`: dùng mô hình mô phỏng nội bộ, không gọi API.
* `openrouter_api`: gửi prompt đến model thông qua OpenRouter API.
* `web_manual`: pipeline legacy dùng schema manual chuẩn của `run_experiment.py`.

### 2.2. Manual TSV analysis

Đây là pipeline phân tích độc lập cho file:

```text
data/web_manual_responses.tsv
```

Chạy bằng:

```powershell
python src/analyze_manual.py
```

Pipeline này:

* không phải một mode của `run_experiment.py`;
* không tính ASR, ORR hoặc utility;
* không áp dụng defense;
* không tạo biểu đồ;
* không ghi đè kết quả experiment chính;
* chỉ tổng hợp các giá trị `Passed_*` có sẵn trong dữ liệu manual.

---

## 3. Cấu trúc project

```text
project_root/
├── data/
│   ├── prompts.csv
│   ├── web_manual_responses.csv
│   └── web_manual_responses.tsv
│
├── outputs/
│   ├── attacked_prompts.csv
│   ├── detailed_results.csv
│   ├── raw_logs.jsonl
│   ├── openrouter_api_raw_responses.jsonl
│   └── web_manual_export.csv
│
├── reports/
│   ├── tables/
│   │   ├── experiment_summary.csv
│   │   ├── attack_summary.csv
│   │   ├── defense_summary.csv
│   │   ├── profile_summary.csv
│   │   ├── error_cases.csv
│   │   ├── manual_jailbreak_details.csv
│   │   └── manual_jailbreak_summary.csv
│   │
│   ├── figures/
│   ├── sections/
│   ├── main.tex
│   └── references.bib
│
├── src/
│   ├── run_experiment.py
│   ├── analyze_manual.py
│   ├── make_plots.py
│   ├── config.py
│   ├── attack_transforms.py
│   ├── defenses.py
│   ├── evaluator.py
│   ├── openrouter_client.py
│   ├── target_simulator.py
│   └── web_manual.py
│
├── tests/
│
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

Hai file manual có mục đích khác nhau:

| File                            | Mục đích                                                |
| ------------------------------- | ------------------------------------------------------- |
| `data/web_manual_responses.csv` | Schema legacy cho `run_experiment.py --mode web_manual` |
| `data/web_manual_responses.tsv` | Schema tùy chỉnh cho `python src/analyze_manual.py`     |

Không dùng file TSV với `run_experiment.py`.

---

## 4. Cài đặt môi trường

Tạo virtual environment:

```powershell
python -m venv .venv
```

Kích hoạt trên Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Cài dependencies:

```powershell
pip install -r requirements.txt
```

Nếu chưa có `requirements.txt` hoàn chỉnh:

```powershell
pip install pandas matplotlib python-dotenv
```

---

## 5. Cấu hình `.env`

Tạo file `.env` tại thư mục gốc:

```env
OPENROUTER_API=your_openrouter_api_key_here
OPENROUTER_MODEL=riverflow-v2.5-fast:free
OPENROUTER_TEMPERATURE=0.0
OPENROUTER_MAX_OUTPUT_TOKENS=512
```

File `.env.example`:

```env
OPENROUTER_API=
OPENROUTER_MODEL=riverflow-v2.5-fast:free
OPENROUTER_TEMPERATURE=0.0
OPENROUTER_MAX_OUTPUT_TOKENS=512
```

Không commit `.env` lên GitHub.

---

## 6. Dữ liệu prompt chính

Experiment pipeline đọc:

```text
data/prompts.csv
```

Các cột bắt buộc:

```text
id
category
prompt
expected_behavior
risk_type
notes
```

Ý nghĩa:

| Cột                 | Mô tả                                 |
| ------------------- | ------------------------------------- |
| `id`                | Mã định danh prompt                   |
| `category`          | `benign`, `harmful` hoặc `borderline` |
| `prompt`            | Prompt gốc                            |
| `expected_behavior` | `answer` hoặc `refuse`                |
| `risk_type`         | Loại rủi ro hoặc nhóm nội dung        |
| `notes`             | Ghi chú phục vụ phân tích             |

Nếu file không tồn tại, `run_experiment.py` có thể tạo bộ prompt mẫu.

---

## 7. Các attack type

Mỗi prompt được biến đổi theo năm attack type:

```text
none
role_play
obfuscation
multi_turn_simulation
injection_style
```

| Attack type             | Mô tả                                    |
| ----------------------- | ---------------------------------------- |
| `none`                  | Giữ nguyên prompt                        |
| `role_play`             | Bọc prompt trong ngữ cảnh nhập vai       |
| `obfuscation`           | Làm nhiễu một số từ khóa                 |
| `multi_turn_simulation` | Chuyển prompt thành dạng nhiều bước      |
| `injection_style`       | Đưa prompt vào cấu trúc prompt injection |

Số API calls:

```text
Số API calls = số prompt × 5 attack types
```

Ví dụ:

```text
30 prompt × 5 attack types = 150 API calls
```

---

## 8. Các defense type

Các defense được áp dụng offline sau khi đã nhận phản hồi từ model:

```text
no_defense
input_filter
output_moderation
defense_in_depth
```

| Defense type        | Mô tả                                     |
| ------------------- | ----------------------------------------- |
| `no_defense`        | Không áp dụng defense                     |
| `input_filter`      | Chặn dựa trên nội dung prompt             |
| `output_moderation` | Chặn dựa trên nhãn hoặc nội dung output   |
| `defense_in_depth`  | Kết hợp input filter và output moderation |

Trong `openrouter_api`, mỗi prompt-attack chỉ được gọi API một lần. Bốn defense được áp dụng offline nên không làm tăng số API calls.

---

## 9. Chạy simulator

Chạy toàn bộ:

```powershell
python src/run_experiment.py --mode simulator
```

Chạy giới hạn số prompt:

```powershell
python src/run_experiment.py --mode simulator --limit 10
```

Chạy một khoảng dòng:

```powershell
python src/run_experiment.py --mode simulator --row-from 0 --row-to 5
```

Simulator phù hợp để kiểm tra pipeline trước khi gọi API thật.

### Cảnh báo

Không chạy lại simulator sau khi đã tạo kết quả OpenRouter chính thức, trừ khi đã sao lưu output.

Mọi mode của `run_experiment.py` sử dụng chung đường dẫn output và có thể ghi đè kết quả trước đó.

---

## 10. Chạy OpenRouter API

Đảm bảo `.env` chứa:

```env
OPENROUTER_API=...
```

Chạy thử hai prompt:

```powershell
python src/run_experiment.py `
  --mode openrouter_api `
  --row-from 0 `
  --row-to 2 `
  --sleep-seconds 10
```

Chạy năm prompt đầu:

```powershell
python src/run_experiment.py `
  --mode openrouter_api `
  --row-from 0 `
  --row-to 5 `
  --sleep-seconds 5
```

Thông tin dự kiến:

```text
5 prompt × 5 attack types = 25 API calls
```

Nếu bị rate limit:

* giảm số prompt mỗi batch;
* tăng `--sleep-seconds`;
* kiểm tra quota của model hoặc provider.

---

## 11. Lưu ý khi chạy theo batch

Mỗi lần chạy `run_experiment.py`, chương trình ghi đè các file:

```text
outputs/attacked_prompts.csv
outputs/detailed_results.csv
outputs/raw_logs.jsonl
outputs/openrouter_api_raw_responses.jsonl
```

Đồng thời ghi đè:

```text
reports/tables/experiment_summary.csv
reports/tables/attack_summary.csv
reports/tables/defense_summary.csv
reports/tables/profile_summary.csv
reports/tables/error_cases.csv
```

Vì vậy, sau mỗi batch cần sao lưu output.

Ví dụ:

```powershell
python src/run_experiment.py `
  --mode openrouter_api `
  --row-from 0 `
  --row-to 5 `
  --sleep-seconds 5

Copy-Item `
  outputs\detailed_results.csv `
  outputs\detailed_results_0_5.csv

Copy-Item `
  outputs\attacked_prompts.csv `
  outputs\attacked_prompts_0_5.csv

Copy-Item `
  outputs\openrouter_api_raw_responses.jsonl `
  outputs\openrouter_api_raw_responses_0_5.jsonl

Copy-Item `
  outputs\raw_logs.jsonl `
  outputs\raw_logs_0_5.jsonl
```

Thực hiện tương tự cho các batch tiếp theo.

### Quan trọng

Không chạy `make_plots.py` ngay sau batch cuối nếu bạn muốn biểu đồ đại diện cho toàn bộ dataset.

Batch cuối chỉ chứa một phần dữ liệu và đã ghi đè các bảng summary trước đó.

Để có kết quả đầy đủ cần:

1. hợp nhất các file `detailed_results_<range>.csv`;
2. tính lại các bảng summary từ dữ liệu đã hợp nhất;
3. sau đó mới chạy `make_plots.py`.

Nếu `outputs/detailed_results.csv` hiện tại đã chứa đầy đủ toàn bộ experiment thì không cần chạy lại theo batch.

---

## 12. Legacy web manual mode

Mode legacy dùng schema chuẩn của `run_experiment.py`.

Export prompt:

```powershell
python src/run_experiment.py `
  --mode web_manual `
  --export-only
```

Output:

```text
outputs/web_manual_export.csv
```

Sau đó người dùng điền response vào:

```text
data/web_manual_responses.csv
```

File CSV legacy phải có các cột:

```text
id
category
attack_type
attack_profile
defense_type
expected_behavior
risk_type
prompt
attacked_prompt
response_text
manual_label
notes
```

Chạy legacy manual:

```powershell
python src/run_experiment.py --mode web_manual
```

### Không dùng lệnh này cho TSV tùy chỉnh

Không chạy:

```powershell
python src/run_experiment.py --mode web_manual
```

với file:

```text
data/web_manual_responses.tsv
```

TSV tùy chỉnh phải được xử lý bằng:

```powershell
python src/analyze_manual.py
```

---

## 13. Manual TSV analysis

Manual TSV analysis là phân tích bổ sung, độc lập với metric experiment chính.

Input:

```text
data/web_manual_responses.tsv
```

File phải sử dụng ký tự tab thật làm delimiter.

Các cột:

```text
prompts
Meaning
Chatgpt 5.5
Passed_Chatgpt
Claude Haiku 4,5
Passed_Haiku
Gemini 3.1 Flash Lite
Passed_Gemini
```

Trong đó:

* `prompts`: prompt được gửi vào model;
* `Meaning`: ý nghĩa hoặc prompt gốc;
* các cột model chứa response;
* `Passed_*` chứa nhãn manual có sẵn.

### Kiểm tra file

```powershell
Test-Path data\web_manual_responses.tsv
```

Kết quả mong đợi:

```text
True
```

### Chạy phân tích

```powershell
python src/analyze_manual.py
```

Output:

```text
reports/tables/manual_jailbreak_details.csv
reports/tables/manual_jailbreak_summary.csv
```

Nếu input có 30 prompt và 3 model:

```text
30 source rows × 3 models = 90 detail rows
```

### Ý nghĩa của `Passed_*`

Script chỉ chuẩn hóa:

```text
1, 1.0, true, yes  -> 1
0, 0.0, false, no -> 0
giá trị khác        -> missing
```

Script không diễn giải:

```text
Passed = 1 -> unsafe_compliance
Passed = 0 -> safe_refusal
```

Do đó:

* `passed_1_rate` không phải ASR;
* `has_any_passed_1` không tự động chứng minh jailbreak thành công;
* kết quả manual không được gộp vào plot chính;
* kết quả cần được diễn giải theo quy tắc gán nhãn manual ban đầu.

---

## 14. Output của experiment chính

### `outputs/attacked_prompts.csv`

Lưu prompt gốc và prompt sau attack transform.

Các cột chính:

```text
id
category
risk_type
attack_type
attack_profile
prompt
attacked_prompt
expected_behavior
notes
```

### `outputs/detailed_results.csv`

Lưu kết quả ở cấp prompt, attack và defense.

Các cột:

```text
run_mode
id
category
risk_type
expected_behavior
attack_type
attack_profile
defense_type
prompt
attacked_prompt
response_text
model_label
final_label
blocked_stage
attack_success
over_refusal
utility_success
refused_or_blocked
unsafe_compliance
cost
error
```

### `outputs/raw_logs.jsonl`

Lưu log thô của experiment.

### `outputs/openrouter_api_raw_responses.jsonl`

Lưu response thô từ OpenRouter API.

---

## 15. Các bảng tổng hợp

Experiment pipeline tạo:

```text
reports/tables/experiment_summary.csv
reports/tables/attack_summary.csv
reports/tables/defense_summary.csv
reports/tables/profile_summary.csv
reports/tables/error_cases.csv
```

Manual TSV analysis tạo riêng:

```text
reports/tables/manual_jailbreak_details.csv
reports/tables/manual_jailbreak_summary.csv
```

Hai nhóm bảng không được gộp tự động.

---

## 16. Các metric chính

| Metric         | Ý nghĩa                                  |
| -------------- | ---------------------------------------- |
| `ASR`          | Attack Success Rate trên prompt harmful  |
| `ORR`          | Over-Refusal Rate trên prompt answerable |
| `Utility Rate` | Tỷ lệ prompt hợp lệ được trả lời         |
| `Refusal Rate` | Tỷ lệ bị từ chối hoặc guard chặn         |
| `Unsafe Rate`  | Tỷ lệ bị đánh nhãn unsafe compliance     |
| `Avg Cost`     | Chi phí mô phỏng tương đối của defense   |

Các metric này chỉ áp dụng cho experiment pipeline.

Không áp dụng các tên metric này cho bảng manual TSV.

---

## 17. Tạo biểu đồ

Sau khi đã có bảng summary đầy đủ:

```powershell
python src/make_plots.py
```

Script đọc:

```text
reports/tables/experiment_summary.csv
reports/tables/profile_summary.csv
```

Script không đọc:

```text
reports/tables/manual_jailbreak_details.csv
reports/tables/manual_jailbreak_summary.csv
```

Các hình được tạo:

```text
reports/figures/asr_by_defense.png
reports/figures/orr_by_defense.png
reports/figures/utility_by_defense.png
reports/figures/safety_utility_tradeoff.png
reports/figures/asr_by_profile.png
reports/figures/orr_by_profile.png
```

`make_plots.py` chỉ tạo hình. Các bảng summary đã được tạo trước đó bởi experiment pipeline.

---

## 18. Quy trình khuyến nghị khi bắt đầu lại experiment

### Bước 1: Kiểm tra simulator

```powershell
python src/run_experiment.py --mode simulator --limit 5
```

### Bước 2: Chạy thử API

```powershell
python src/run_experiment.py `
  --mode openrouter_api `
  --row-from 0 `
  --row-to 2 `
  --sleep-seconds 10
```

### Bước 3: Chạy experiment chính

Ưu tiên chạy toàn bộ trong một lần nếu quota cho phép:

```powershell
python src/run_experiment.py `
  --mode openrouter_api `
  --row-from 0 `
  --row-to 30 `
  --sleep-seconds 5
```

Nếu phải chia batch, cần sao lưu từng batch và hợp nhất trước khi tạo biểu đồ.

### Bước 4: Tạo biểu đồ

```powershell
python src/make_plots.py
```

### Bước 5: Phân tích manual TSV

```powershell
python src/analyze_manual.py
```

Manual analysis có thể chạy trước hoặc sau `make_plots.py` vì hai script sử dụng output độc lập.

---

## 19. Quy trình hiện tại khi experiment đã chạy xong

Nếu experiment đã hoàn tất, các bảng summary chính đã tồn tại và file manual TSV đã được chuẩn bị, chỉ cần chạy:

```powershell
python src/analyze_manual.py
python src/make_plots.py
```

Không cần chạy lại:

```powershell
python src/run_experiment.py
```

vì lệnh đó có thể ghi đè kết quả hiện tại.

Kiểm tra output:

```powershell
Get-ChildItem reports\tables\*.csv
Get-ChildItem reports\figures\*.png
```

---

## 20. Diễn giải kết quả

### 20.1. Theo attack type

So sánh:

```text
none
role_play
obfuscation
multi_turn_simulation
injection_style
```

Mục tiêu là xác định attack type nào làm tăng unsafe compliance.

### 20.2. Theo defense type

So sánh:

```text
no_defense
input_filter
output_moderation
defense_in_depth
```

Cần xem xét đồng thời:

* ASR;
* ORR;
* utility rate;
* refusal rate;
* chi phí tương đối.

### 20.3. Theo attack profile

So sánh:

```text
knowledge
company
hazardous
generic
```

Mục tiêu là xác định nhóm nội dung nào làm model hoặc defense dễ thất bại hơn.

### 20.4. Manual analysis

Manual TSV nên được trình bày như phân tích bổ sung.

Có thể báo cáo:

* tổng số case của từng model;
* số response bị thiếu;
* số nhãn `Passed = 1`;
* số nhãn `Passed = 0`;
* số case chưa được gán nhãn.

Không gọi `passed_1_rate` là ASR hoặc jailbreak rate nếu chưa có định nghĩa nhãn rõ ràng.

---

## 21. Giới hạn của thực nghiệm

Các giới hạn chính:

* số lượng prompt còn nhỏ;
* evaluator API hiện là rule-based;
* input filter và output moderation dùng keyword đơn giản;
* defense được chạy offline;
* kết quả phụ thuộc model và thời điểm gọi API;
* output có thể thay đổi theo chính sách provider;
* batch execution chưa tự động hợp nhất kết quả;
* manual `Passed_*` chưa được chuẩn hóa thành safety label;
* một response chứa từ khóa từ chối vẫn có thể bao gồm nội dung không an toàn phía sau;
* metric hiện tại không thay thế đánh giá thủ công chuyên sâu.

---

## 22. Mục đích an toàn

Project phục vụ mục đích học thuật, red teaming có kiểm soát và đánh giá an toàn AI.

Các prompt harmful được sử dụng để:

* kiểm tra khả năng từ chối;
* đo lường độ bền trước prompt injection;
* so sánh các defense;
* phân tích failure cases.

Không sử dụng project để tạo, tối ưu hoặc triển khai nội dung gây hại trong thực tế.
