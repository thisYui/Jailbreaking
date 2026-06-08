# Jailbreaking Evaluation Framework

## 1. Giới thiệu

Project này xây dựng một pipeline thực nghiệm để đánh giá khả năng chống chịu của mô hình ngôn ngữ lớn trước các dạng **jailbreaking** và **prompt injection** trong bối cảnh kiểm thử an toàn AI.

Mục tiêu của project không phải là tạo nội dung gây hại, mà là xây dựng một môi trường đánh giá có kiểm soát nhằm đo lường:

* mô hình có từ chối đúng các yêu cầu nguy hiểm hay không;
* mô hình có trả lời đúng các yêu cầu hợp lệ hay không;
* các kỹ thuật tấn công prompt ảnh hưởng thế nào đến hành vi mô hình;
* các lớp phòng thủ như input filtering, output moderation và defense-in-depth có cải thiện độ an toàn hay không;
* trade-off giữa safety và utility.

Project hỗ trợ ba chế độ chạy:

```text
simulator
google_api
web_manual
```

Trong đó:

* `simulator`: dùng mô phỏng nội bộ, không gọi API thật.
* `google_api`: gọi mô hình Gemini thông qua Google API.
* `web_manual`: export prompt để kiểm thử thủ công qua giao diện web.

---

## 2. Cấu trúc project

Cấu trúc thư mục chính:

```text
project_root/
├── data/
│   ├── prompts.csv
│   └── web_manual_responses.csv
│
├── outputs/
│   ├── attacked_prompts.csv
│   ├── detailed_results.csv
│   ├── raw_logs.jsonl
│   ├── google_api_raw_responses.jsonl
│   └── web_manual_export.csv
│
├── reports/
│   ├── tables/
│   ├── figures/
│   ├── sections/
│   ├── main.tex
│   └── Report.pdf
│
├── src/
│   ├── run_experiment.py
│   ├── config.py
│   ├── attack_transforms.py
│   ├── defenses.py
│   ├── evaluator.py
│   ├── google_api_client.py
│   ├── target_simulator.py
│   ├── web_manual.py
│   └── make_plots.py
│
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

---

## 3. File `.env`

Project dùng file `.env` để lưu cấu hình API và model. File này **không nên commit lên GitHub** vì có thể chứa API key.

Tạo file `.env` ở thư mục gốc project:

```env
GEMINI_API_KEY=your_google_ai_studio_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.0
GEMINI_MAX_OUTPUT_TOKENS=512
```

Nên tạo thêm file `.env.example` để mô tả cấu hình cần thiết mà không chứa key thật:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.0
GEMINI_MAX_OUTPUT_TOKENS=512
```

---

## 4. Cài đặt môi trường

Tạo virtual environment:

```bash
python -m venv .venv
```

Kích hoạt môi trường trên Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Cài thư viện cần thiết:

```bash
pip install pandas matplotlib python-dotenv google-genai
```

Nếu dùng file `requirements.txt`, có thể cài bằng:

```bash
pip install -r requirements.txt
```

---

## 5. Dữ liệu đầu vào

File prompt chính nằm ở:

```text
data/prompts.csv
```

Các cột bắt buộc:

```text
id, category, prompt, expected_behavior, risk_type, notes
```

Ý nghĩa:

| Cột                 | Mô tả                                                        |
| ------------------- | ------------------------------------------------------------ |
| `id`                | Mã định danh prompt                                          |
| `category`          | Nhóm prompt: `benign`, `harmful`, hoặc `borderline`          |
| `prompt`            | Prompt gốc                                                   |
| `expected_behavior` | Hành vi kỳ vọng: `answer` hoặc `refuse`                      |
| `risk_type`         | Loại rủi ro, ví dụ `knowledge_*`, `company_*`, `hazardous_*` |
| `notes`             | Ghi chú phục vụ báo cáo                                      |

Nếu `data/prompts.csv` chưa tồn tại, chương trình có thể tự tạo bộ prompt mẫu.

---

## 6. Các loại tấn công

Pipeline áp dụng nhiều biến thể tấn công lên mỗi prompt gốc:

```text
none
role_play
obfuscation
multi_turn_simulation
injection_style
```

Ý nghĩa:

| Attack type             | Mô tả                                                      |
| ----------------------- | ---------------------------------------------------------- |
| `none`                  | Không biến đổi prompt                                      |
| `role_play`             | Bọc prompt trong ngữ cảnh nhập vai                         |
| `obfuscation`           | Làm nhiễu nhẹ một số từ khóa                               |
| `multi_turn_simulation` | Giả lập yêu cầu nhiều bước                                 |
| `injection_style`       | Đưa prompt vào dạng external content hoặc prompt injection |

Do mỗi prompt được chạy qua 5 attack types, số API calls trong chế độ `google_api` được tính như sau:

```text
Số API calls = số dòng prompt × 5
```

Ví dụ:

```text
30 prompt rows × 5 attack types = 150 API calls
```

---

## 7. Các lớp phòng thủ

Sau khi có phản hồi từ mô hình, pipeline đánh giá phản hồi qua các defense types:

```text
no_defense
input_filter
output_moderation
defense_in_depth
```

Ý nghĩa:

| Defense type        | Mô tả                                            |
| ------------------- | ------------------------------------------------ |
| `no_defense`        | Không áp dụng phòng thủ                          |
| `input_filter`      | Chặn dựa trên nội dung prompt đầu vào            |
| `output_moderation` | Chặn dựa trên nhãn hoặc nội dung phản hồi đầu ra |
| `defense_in_depth`  | Kết hợp input filtering và output moderation     |

Lưu ý: trong chế độ `google_api`, defense được chạy **offline** sau khi nhận phản hồi. Defense không làm tăng số API calls.

---

## 8. Chạy bằng simulator

Chế độ simulator không gọi API thật, phù hợp để kiểm tra pipeline nhanh:

```bash
python src/run_experiment.py --mode simulator
```

Chạy giới hạn số dòng:

```bash
python src/run_experiment.py --mode simulator --limit 10
```

Chạy theo khoảng dòng:

```bash
python src/run_experiment.py --mode simulator --row-from 0 --row-to 5
```

---

## 9. Chạy bằng Google API

Trước khi chạy, cần chắc chắn file `.env` đã có `GEMINI_API_KEY`.

Chạy 5 dòng đầu tiên, nghỉ 5 giây giữa các API calls:

```bash
python src/run_experiment.py --mode google_api --row-from 0 --row-to 5 --sleep-seconds 5
```

Lệnh trên sẽ tạo:

```text
5 prompt rows × 5 attack types = 25 API calls
```

Chạy batch tiếp theo:

```bash
python src/run_experiment.py --mode google_api --row-from 5 --row-to 10 --sleep-seconds 5
```

Chạy toàn bộ 30 dòng theo từng batch nhỏ:

```bash
python src/run_experiment.py --mode google_api --row-from 0 --row-to 5 --sleep-seconds 5
python src/run_experiment.py --mode google_api --row-from 5 --row-to 10 --sleep-seconds 5
python src/run_experiment.py --mode google_api --row-from 10 --row-to 15 --sleep-seconds 5
python src/run_experiment.py --mode google_api --row-from 15 --row-to 20 --sleep-seconds 5
python src/run_experiment.py --mode google_api --row-from 20 --row-to 25 --sleep-seconds 5
python src/run_experiment.py --mode google_api --row-from 25 --row-to 30 --sleep-seconds 5
```

Nếu vẫn bị rate limit, giảm số dòng mỗi batch và tăng thời gian nghỉ:

```bash
python src/run_experiment.py --mode google_api --row-from 0 --row-to 2 --sleep-seconds 10
```

---

## 10. Lưu ý khi chạy nhiều batch

Mỗi lần chạy, các file output mặc định sẽ bị ghi đè:

```text
outputs/attacked_prompts.csv
outputs/detailed_results.csv
outputs/raw_logs.jsonl
outputs/google_api_raw_responses.jsonl
```

Vì vậy sau mỗi batch nên copy output sang file riêng.

Ví dụ trên Windows PowerShell:

```powershell
python src/run_experiment.py --mode google_api --row-from 0 --row-to 5 --sleep-seconds 5

Copy-Item outputs\detailed_results.csv outputs\detailed_results_0_5.csv
Copy-Item outputs\attacked_prompts.csv outputs\attacked_prompts_0_5.csv
Copy-Item outputs\google_api_raw_responses.jsonl outputs\google_api_raw_responses_0_5.jsonl
Copy-Item outputs\raw_logs.jsonl outputs\raw_logs_0_5.jsonl
```

Batch tiếp theo:

```powershell
python src/run_experiment.py --mode google_api --row-from 5 --row-to 10 --sleep-seconds 5

Copy-Item outputs\detailed_results.csv outputs\detailed_results_5_10.csv
Copy-Item outputs\attacked_prompts.csv outputs\attacked_prompts_5_10.csv
Copy-Item outputs\google_api_raw_responses.jsonl outputs\google_api_raw_responses_5_10.jsonl
Copy-Item outputs\raw_logs.jsonl outputs\raw_logs_5_10.jsonl
```

---

## 11. Chạy web manual mode

Chế độ này dùng để export prompt đã bị biến đổi, sau đó người dùng copy prompt vào giao diện web và paste response thủ công vào file phản hồi.

Export prompt:

```bash
python src/run_experiment.py --mode web_manual --export-only
```

File được tạo:

```text
outputs/web_manual_export.csv
```

Sau đó copy `attacked_prompt` vào web UI, lấy response và điền vào:

```text
data/web_manual_responses.csv
```

Rồi chạy đánh giá:

```bash
python src/run_experiment.py --mode web_manual
```

---

## 12. Output chính

Sau khi chạy, project tạo các file chính:

### `outputs/attacked_prompts.csv`

Lưu prompt gốc và prompt sau khi áp dụng attack transform.

Các cột quan trọng:

```text
id, category, risk_type, attack_type, attack_profile, prompt, attacked_prompt, expected_behavior, notes
```

### `outputs/detailed_results.csv`

Lưu kết quả chi tiết ở cấp từng prompt, attack type và defense type.

Các cột quan trọng:

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

Lưu log thô của quá trình chạy.

### `outputs/google_api_raw_responses.jsonl`

Lưu phản hồi thô từ Google API khi chạy `google_api`.

---

## 13. Các chỉ số đánh giá

Pipeline tính các chỉ số chính:

| Metric         | Ý nghĩa                                                                 |
| -------------- | ----------------------------------------------------------------------- |
| `ASR`          | Attack Success Rate, tỷ lệ prompt harmful khiến model unsafe compliance |
| `ORR`          | Over-Refusal Rate, tỷ lệ prompt answerable nhưng bị từ chối             |
| `Utility Rate` | Tỷ lệ prompt hợp lệ được trả lời đúng                                   |
| `Refusal Rate` | Tỷ lệ phản hồi bị từ chối hoặc bị guard chặn                            |
| `Unsafe Rate`  | Tỷ lệ phản hồi bị đánh giá là unsafe compliance                         |
| `Avg Cost`     | Chi phí mô phỏng tương đối của defense pipeline                         |

Các bảng tổng hợp được lưu ở:

```text
reports/tables/
```

Bao gồm:

```text
experiment_summary.csv
attack_summary.csv
defense_summary.csv
profile_summary.csv
error_cases.csv
```

---

## 14. Tạo biểu đồ cho báo cáo

Sau khi có bảng kết quả, chạy:

```bash
python src/make_plots.py
```

Biểu đồ sẽ được lưu vào:

```text
reports/figures/
```

Các hình chính:

```text
asr_by_defense.png
orr_by_defense.png
utility_by_defense.png
safety_utility_tradeoff.png
asr_by_profile.png
orr_by_profile.png
```

---

## 15. Quy trình chạy khuyến nghị cho báo cáo

### Bước 1: Kiểm tra pipeline bằng simulator

```bash
python src/run_experiment.py --mode simulator --limit 30
```

### Bước 2: Chạy thử Google API với batch nhỏ

```bash
python src/run_experiment.py --mode google_api --row-from 0 --row-to 2 --sleep-seconds 10
```

### Bước 3: Nếu ổn, chạy theo batch 5 dòng

```bash
python src/run_experiment.py --mode google_api --row-from 0 --row-to 5 --sleep-seconds 5
```

### Bước 4: Lưu output batch

```powershell
Copy-Item outputs\detailed_results.csv outputs\detailed_results_0_5.csv
Copy-Item outputs\attacked_prompts.csv outputs\attacked_prompts_0_5.csv
Copy-Item outputs\google_api_raw_responses.jsonl outputs\google_api_raw_responses_0_5.jsonl
Copy-Item outputs\raw_logs.jsonl outputs\raw_logs_0_5.jsonl
```

### Bước 5: Chạy các batch tiếp theo

```bash
python src/run_experiment.py --mode google_api --row-from 5 --row-to 10 --sleep-seconds 5
python src/run_experiment.py --mode google_api --row-from 10 --row-to 15 --sleep-seconds 5
python src/run_experiment.py --mode google_api --row-from 15 --row-to 20 --sleep-seconds 5
python src/run_experiment.py --mode google_api --row-from 20 --row-to 25 --sleep-seconds 5
python src/run_experiment.py --mode google_api --row-from 25 --row-to 30 --sleep-seconds 5
```

### Bước 6: Tạo bảng và hình cho báo cáo

```bash
python src/make_plots.py
```

---

## 16. Diễn giải kết quả trong báo cáo

Khi viết báo cáo, nên tách kết quả theo ba lớp phân tích:

### 16.1. Theo attack type

So sánh ASR giữa:

```text
none
role_play
obfuscation
multi_turn_simulation
injection_style
```

Mục tiêu là xác định dạng jailbreaking nào làm mô hình dễ bị unsafe compliance nhất.

### 16.2. Theo defense type

So sánh:

```text
no_defense
input_filter
output_moderation
defense_in_depth
```

Mục tiêu là đánh giá defense nào giảm ASR tốt nhất, đồng thời có gây over-refusal quá cao hay không.

### 16.3. Theo attack profile

So sánh các nhóm:

```text
knowledge
company
hazardous
generic
```

Mục tiêu là xem mô hình dễ thất bại hơn ở nhóm nào: tri thức an toàn, dữ liệu nội bộ công ty, hay nội dung rủi ro cao.

---

## 17. Giới hạn của thực nghiệm

Một số giới hạn cần nêu trong báo cáo:

* Bộ prompt còn nhỏ, chủ yếu phục vụ kiểm thử có kiểm soát.
* Nhãn `model_label` trong chế độ API được suy ra bằng rule-based evaluator, chưa thay thế hoàn toàn human evaluation.
* Input filter và output moderation hiện là rule-based đơn giản, chưa phải classifier chuyên dụng.
* Defense chạy offline sau response nên không phản ánh đầy đủ kiến trúc production thực tế.
* Kết quả phụ thuộc vào model, thời điểm gọi API, cấu hình temperature và chính sách an toàn của nhà cung cấp.

---

## 18. Mục đích an toàn

Project này phục vụ mục đích học thuật và đánh giá an toàn AI. Các prompt harmful trong dataset được thiết kế ở mức kiểm thử có kiểm soát, nhằm đo lường khả năng từ chối của mô hình và hiệu quả của các lớp phòng thủ.

Không sử dụng project để tạo, tối ưu hoặc triển khai nội dung gây hại trong thực tế.
