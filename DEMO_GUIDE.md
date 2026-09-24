# Hướng dẫn demo C1 — Tìm nhãn sai trong 5% ảnh được review

## Mục đích và một câu giải thích

Một lô ảnh sản phẩm đã được gán nhãn, nhưng người kiểm tra chỉ có thể xem lại 5%. Demo này xếp những ảnh **có nhãn đáng nghi** lên đầu và đo xem trong 100 ảnh được chọn tìm được bao nhiêu nhãn sai thật, so với chọn ngẫu nhiên 100 ảnh.

Đây là **prototype chạy được trên dữ liệu mô phỏng**. Nó không tự sửa nhãn và chưa chứng minh hiệu quả trên một lô vendor thật.

## Demo đổi kịch bản để thấy kết quả của nhóm thay đổi

Mở [`artifacts/demo_scenarios.html`](artifacts/demo_scenarios.html) và bấm **Tạo kịch bản khác**. Trang vẫn dùng đúng 2.000 ảnh evaluation và phương pháp 15 hàng xóm, nhưng tạo một bản **nhãn đang dùng có 200 lỗi mô phỏng mới**. Sau đó nó tính lại điểm đáng nghi, top 100 của nhóm và top 100 random **trên cùng bản nhãn mới**. Bấm **Xếp hạng của nhóm** hoặc **Random cùng kịch bản** để xem hai hàng chờ; bấm **Hiện đáp án** để đối chiếu lỗi thật.

Trang bắt đầu bằng kịch bản chính seed `677`: nhóm tìm **78 lỗi**. Lượt bấm đầu chuyển sang seed `2000`: nhóm tìm **72 lỗi**. Có 30 kịch bản bổ sung với seed lỗi `2000–2029`, random seed `5000–5029`, theo thứ tự cố định và **giữ toàn bộ kết quả** trong [`artifacts/scenario_results.json`](artifacts/scenario_results.json). Hai kịch bản có thể tình cờ tìm cùng số lỗi dù nhãn sai và hàng chờ khác nhau. Hết 30 kịch bản, nút quay về kịch bản chính.

Khi trình bày, chỉ cần **tải lại trang** để quay ngay về kịch bản chính 78 lỗi.

Đây là **minh họa độ nhạy của phương pháp khi lỗi thay đổi**, không phải 30 evaluation set độc lập: ảnh evaluation được dùng lại, và các seed bổ sung được tạo sau thí nghiệm chính. Vì vậy số báo cáo trên slide vẫn là **78 so với random trung bình 9,64**. Không chọn một kịch bản bổ sung đẹp nhất để thay số chính. Nếu bị hỏi “sao chạy lại vẫn 78?”, hãy giải thích: chạy lại cùng seed chính thì tái lập 78; bấm kịch bản mới là một thử nghiệm mô phỏng khác.

## Demo bốc random mới sau mỗi lần bấm

Mở [`artifacts/demo_live.html`](artifacts/demo_live.html). Trang mặc định hiện hàng chờ cố định của phương pháp nhóm. Mỗi lần bấm **Bốc random mới**, trang chọn một nhóm **100 ảnh khác** trong 2.000 ảnh evaluation và tính lại số lỗi tìm được, Recall@5% và Precision@5%. Bấm **Hiện đáp án** để xem từng ảnh trong lượt bốc đó; bấm **Xếp hạng của nhóm** để quay về danh sách và kết quả cố định **78 lỗi**.

Hai lần bốc có thể tình cờ tìm **cùng số lỗi** dù 100 ảnh được chọn khác nhau. Dòng “Lượt bốc #…” và ID ảnh cho biết danh sách đã thay đổi. Các lượt bốc trực tiếp này chỉ giúp hiểu tính ngẫu nhiên; baseline chính trên slide vẫn là trung bình của 100 seed đã khóa.

## Các file nên mở khi trình bày

| File | Nội dung |
| --- | --- |
| [`artifacts/C1_Peer_Showcase_5min.pdf`](artifacts/C1_Peer_Showcase_5min.pdf) | **Bản trình bày mới theo rubric 5 slide / 5 phút.** |
| [`PRESENTATION_5_MINUTES.md`](PRESENTATION_5_MINUTES.md) | Lời thoại theo đồng hồ, thao tác demo, câu hỏi Q&A. |
| [`artifacts/demo_scenarios.html`](artifacts/demo_scenarios.html) | **Bản nên dùng khi trình bày:** đổi kịch bản lỗi và tính lại cả hai hàng chờ. |
| [`artifacts/demo_live.html`](artifacts/demo_live.html) | Bản minh họa biến thiên của riêng random baseline. |
| [`artifacts/demo.html`](artifacts/demo.html) | Demo offline: chuyển giữa hàng chờ của nhóm và random; bật **Hiện đáp án** để xem từng ảnh có sai nhãn không. |
| [`artifacts/C1_Showcase.pdf`](artifacts/C1_Showcase.pdf) | Bản chiếu 5 slide, phù hợp khi trình bày ở máy không có PowerPoint. |
| [`artifacts/C1_Showcase.pptx`](artifacts/C1_Showcase.pptx) | Bản PowerPoint có thể chỉnh sửa, gồm chart và speaker notes. |
| [`artifacts/results.json`](artifacts/results.json) | Số đo, seed, chia tập và hash file dữ liệu nguồn. |
| [`artifacts/review_queue.csv`](artifacts/review_queue.csv) | Top 100 ảnh do phương pháp chọn. File này **không chứa nhãn đúng**. |

`demo.html` là một file tự chứa ảnh, CSS và JavaScript, nên có thể mở trực tiếp bằng trình duyệt mà không cần Internet. Bốn file Fashion-MNIST nén trong `data/raw/` đã được tải để có thể chạy lại thí nghiệm offline.

## Cách demo trong khoảng 45 giây

1. Mở `artifacts/demo.html` trên máy trình bày. Trang mặc định cho thấy hàng chờ **Xếp hạng của nhóm** và ba metric.
2. Chỉ vào ảnh đầu danh sách: mỗi ảnh có nhãn hiện tại; người review sẽ xem những ảnh ở đầu trước.
3. Bấm **Hiện đáp án**. Viền đỏ là ảnh đã bị đổi nhãn; viền xanh là ảnh không bị đổi nhãn. Đáp án chỉ hiện ở bước trình diễn sau khi thứ tự đã cố định.
4. Bấm **Random · seed 1000** để xem một danh sách chọn ngẫu nhiên cùng 100 ảnh. Con số trên slide Baseline là **trung bình của 100 seed**, không phải riêng seed 1000 hiển thị trong demo.

Nếu không mở được HTML lúc trình bày, dùng slide 3–4 cùng [`artifacts/review_queue.csv`](artifacts/review_queue.csv) và [`artifacts/results.json`](artifacts/results.json) để giải thích cách chọn ảnh và metric.

## Dữ liệu và cách tạo ground truth

- Nguồn: [Fashion-MNIST của Zalando Research](https://github.com/zalandoresearch/fashion-mnist), ảnh xám 28×28 của 10 loại sản phẩm. Nguồn công bố giấy phép MIT.
- Chia từ phần train gốc: **8.000 ảnh development** và **2.000 ảnh evaluation**, cân bằng 800/200 ảnh mỗi lớp; seed chia tập `20260924`.
- Dành riêng **2.000 ảnh** từ test gốc cho phép đo downstream về sau; prototype hiện chưa đo downstream recovery.
- Trên evaluation, bản nhãn mô phỏng có **200 lỗi thật**, gồm 80 lỗi đổi nhãn rải rác, 80 ảnh `Shirt → T-shirt/top`, và 40 ảnh từ lô dùng sai ánh xạ nhãn. Development cũng nhận 10% lỗi theo tỷ lệ tương ứng nhưng dùng seed khác.
- Nhãn gốc được dùng làm **nhãn tham chiếu cho lỗi đã tiêm**. Cách này cho phép tính recall chính xác đối với lỗi mô phỏng. Nhãn gốc có thể có ca mơ hồ hoặc lỗi tự nhiên chưa được audit; không tuyên bố đây là ground truth hoàn hảo của mọi ảnh.
- Kiểm tra hash ảnh trùng hệt giữa ba phần đã chọn cho kết quả **0 cặp trùng**.

Các hàm xếp hạng chỉ nhận ảnh, nhãn hiện tại và dữ liệu development. Danh sách lỗi đã tạo chỉ được dùng khi tính metric sau khi ranking đã cố định. Evaluation không được dùng để chọn `k=15`, ngưỡng review hay seed đẹp.

## Phương pháp đang chạy

1. Thu ảnh 28×28 thành vector 14×14 bằng trung bình mỗi ô 2×2.
2. Với ảnh evaluation, tìm **15 ảnh gần nhất** trong 8.000 ảnh development theo khoảng cách pixel; mỗi ảnh gần nhất bỏ phiếu có trọng số cho lớp của nó.
3. Tính `điểm đáng nghi = 1 − P(nhãn hiện tại | 15 ảnh gần nhất)`.
4. Xếp giảm dần theo điểm, lấy đúng **100 ảnh đầu**. Trường hợp đồng điểm giữ thứ tự ID ổn định.

`run_demo.py` tính ranking và metric. `make_demo_page.py` dùng kết quả đó để tạo HTML tương tác. Không cần Cleanlab hay mô hình deep learning để chạy prototype này.

## Kết quả đã đo

Với **2.000 ảnh evaluation, 200 nhãn sai, 100 lượt review**:

| Phương pháp | Lỗi thật trong 100 ảnh | Error Recall@5% | Precision@5% |
| --- | ---: | ---: | ---: |
| Random, trung bình 100 seed | 9,64 | 4,82% | 9,64% |
| Xếp hạng của nhóm | 78 | **39,0%** | **78,0%** |

Đây là cải thiện khoảng **8,1 lần về Error Recall@5%** trên benchmark mô phỏng này. Không làm tròn 9,64 thành một “lần random” cụ thể: đó là trung bình nhiều lần chọn ngẫu nhiên.

| Loại lỗi | Tìm được / tổng lỗi | Recall theo loại |
| --- | ---: | ---: |
| Rải rác | 49/80 | 61,25% |
| `Shirt → T-shirt/top` | **6/80** | **7,5%** |
| Theo lô | 23/40 | 57,5% |

**Failure case chính:** hai loại áo giống nhau về hình dạng, nên nhiều ảnh `Shirt` bị gán `T-shirt/top` vẫn có các hàng xóm bỏ phiếu cho nhãn đang dùng. Phương pháp chỉ tìm được 6/80 lỗi loại này. Đây là lý do slide cuối chọn **Rework**.

Stress test giữ nguyên cách xếp hạng và ngân sách 100 ảnh: khi tiêm 5% lỗi, recall là **52%**; khi tiêm 20% lỗi, recall là **22,5%**. Tỷ lệ lỗi thật khác nhau làm mẫu số của recall khác nhau, nên dùng stress test để xem độ bền, không dùng để thay kết quả chính.

## Chạy lại thí nghiệm

Cần Python 3.10+ với NumPy và Pillow. Trên máy hiện tại, dùng Python đi kèm workspace runtime hoặc Python đã cài các gói trong `requirements.txt`.

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 run_demo.py --output-dir artifacts/lan-chay-cua-ban
python3 make_demo_page.py --output-dir artifacts/lan-chay-cua-ban
python3 make_live_demo.py --output-dir artifacts/lan-chay-cua-ban
python3 make_scenario_demo.py --output-dir artifacts/lan-chay-cua-ban
```

Mỗi lần chạy hãy chọn **một thư mục output mới**. Script dừng nếu file kết quả đã tồn tại, để không ghi đè kết quả cũ. Sau khi chạy, mở `artifacts/lan-chay-cua-ban/demo.html` và đối chiếu `results.json`; các **số đếm/metric** phải giống bảng trên. Thời gian chạy có thể khác theo máy. `data/raw/` chứa bốn file IDX gzip nguồn; nếu tách riêng code khỏi thư mục này, tải chúng từ repository Fashion-MNIST và ghi lại hash mới.

Trong thư mục vừa chạy cũng có `demo_live.html`: bấm nút random ở đó để bốc lại ngay trên giao diện mà không cần chạy Python thêm lần nào.

### Vì sao chạy lại vẫn ra đúng các số cũ?

Đây là **chạy lại để kiểm tra khả năng tái lập**, không phải bốc thăm một thí nghiệm mới. Mã cố định seed chia tập `20260924`, seed tạo lỗi development `311`, seed tạo lỗi evaluation `677`, và 100 seed random baseline `1000–1099`. Vì vậy mỗi lần chạy đều lấy đúng những ảnh ấy, tạo đúng những lỗi ấy và xếp hạng theo cùng quy tắc. Số lỗi, recall và danh sách top 100 **phải giống nhau**; thời gian xử lý có thể thay đổi. Chẳng hạn, 100 lần random trong *một lần chạy* tìm từ **4 đến 17 lỗi**, nhưng chạy lại vẫn tính trên đúng 100 seed đó nên trung bình luôn là **9,64**.

Nếu muốn xem phương pháp có bền với tình huống khác, hãy xem mục `stress_tests` trong `results.json`: mã đã thử trước các mức lỗi **5%, 10%, 20%**. Một thí nghiệm với seed hoặc dữ liệu mới phải được ghi là **kịch bản bổ sung**, lưu ở thư mục riêng và báo cáo đầy đủ theo quy tắc đã chốt. Không thay bộ evaluation chính bằng lần chạy cho kết quả đẹp hơn.

Để **bốc 100 lượt random mới mỗi lần gọi lệnh**, dùng:

```bash
python3 explore_random.py --runs 100
```

Lệnh này lấy một seed mới từ hệ thống, in seed đã dùng, số lỗi của 10 lượt đầu và kết quả trung bình. Chạy lại lệnh sẽ nhận một bộ 100 lượt khác. Nếu muốn kiểm tra lại đúng một bộ vừa thấy, truyền `--seed` bằng `first_seed` được in ra, ví dụ `python3 explore_random.py --runs 100 --seed 12345`. Đây là **thử nghiệm khám phá**; nó không ghi đè `artifacts/results.json` và không thay con số baseline chính trên slide.

## Lời thoại gợi ý cho đúng 5 phút

| Slide | Thời gian | Câu cần nói |
| --- | ---: | --- |
| 1 — Pain | 45–50 giây | “Chỉ review 5%, chọn ảnh nào để tìm nhiều lỗi nhãn thật nhất?” Dữ liệu là mô phỏng từ Fashion-MNIST. |
| 2 — Baseline | 45–50 giây | Random 100 seed: trung bình 9,64 lỗi/100 ảnh, recall 4,82%. |
| 3 — Solution + demo | 60 giây | Nêu 15 hàng xóm, điểm đáng nghi, mở HTML và bật đáp án. |
| 4 — Evidence | 65–70 giây | 78 lỗi, recall 39%; nhấn mạnh chỉ 6/80 lỗi nhầm lớp được tìm thấy. |
| 5 — Decision | 45–50 giây | Rework, chưa deploy thật; kế tiếp thêm tín hiệu theo lớp/lô và đánh giá trên nhãn thật được phân xử độc lập. |

Để có thời gian trả lời câu hỏi, nên tập dượt kết thúc phần nói trong khoảng **4 phút 20 giây**. Khi đủ 5 phút, dừng demo ngay; kết quả chính đã nằm trên slide 4.

## Rủi ro và bước tiếp theo

Prototype chỉ đánh giá **lỗi tạo có kiểm soát**, chưa đo người review thực sự mất bao nhiêu phút hoặc mô hình downstream cải thiện ra sao sau khi sửa nhãn. Bước tiếp theo là kiểm chứng trên một tập nhỏ có nhãn thật được hai người xem độc lập và phân xử, đồng thời đo `defects/minute`. Chỉ sau đó mới cân nhắc pilot trong quy trình gán nhãn thực tế.
