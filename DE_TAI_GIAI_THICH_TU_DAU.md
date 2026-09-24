# C1 từ đầu đến cuối: Vì sao hàng chờ của nhóm cố định?

> **Tóm tắt:** Có 2.000 ảnh đã gán nhãn nhưng chỉ đủ thời gian xem lại 100 ảnh (5%). Nhóm viết chương trình đưa ảnh có nhãn đáng nghi lên đầu hàng chờ để người kiểm tra xem trước. Kết quả trên dữ liệu mô phỏng: hàng chờ của nhóm tìm 78/200 lỗi; chọn ngẫu nhiên tìm trung bình 9,64/200 lỗi qua 100 lượt đã định trước.

## 1. Vấn đề của đề tài

Một đội gán nhãn vừa hoàn thành một lô ảnh sản phẩm. Một số ảnh bị gán nhầm loại. Nếu đưa dữ liệu đó vào huấn luyện hoặc đánh giá, mô hình có thể học sai và kết quả đánh giá thiếu tin cậy. Đội dữ liệu và đội xây mô hình chịu ảnh hưởng trực tiếp.

**Câu hỏi C1:** Với cùng một ngân sách review 5%, chọn ảnh nào để tìm được nhiều nhãn sai thật nhất?

Hệ thống của nhóm chỉ **ưu tiên ảnh để người xem lại**. Nó không tự tuyên bố nhãn nào là đúng và không tự sửa toàn bộ dataset.

### Ví dụ hai người gán nhãn 0/1 ngược nhau có liên quan không?

Có. Nếu người A dùng `0 = vật A, 1 = vật B` còn người B dùng `0 = vật B, 1 = vật A`, khi gộp dữ liệu sẽ có một **lô nhãn sai theo quy tắc**. Đó là một dạng lỗi C1 cần phát hiện.

Prototype hiện tại dùng 10 loại quần áo và tạo ba kiểu lỗi, trong đó có lỗi **sai theo lô**. Nó chưa mô phỏng đúng riêng ca hai annotator đảo 0↔1. Muốn khẳng định xử lý tốt ca đó, nhóm cần làm thêm thí nghiệm với `annotator_id` hoặc `batch_id` và phép đảo 0↔1, rồi đo riêng kết quả.

## 2. Dữ liệu và “đáp án”

Nhóm dùng [Fashion-MNIST của Zalando Research](https://github.com/zalandoresearch/fashion-mnist): ảnh quần áo xám 28×28, 10 lớp, giấy phép MIT. Dữ liệu chia thành 8.000 ảnh **development** để phát triển phương pháp, 2.000 ảnh **evaluation** để báo cáo kết quả và 2.000 ảnh **downstream test** để dành cho nghiên cứu sau.

Nhóm sao chép nhãn gốc, rồi cố ý đổi một số nhãn trong bản sao. Trên evaluation có đúng **200 nhãn bị đổi**:

| Kiểu lỗi | Số lỗi | Ví dụ |
| --- | ---: | --- |
| Rải rác | 80 | Một ảnh giày bị ghi thành lớp khác. |
| Nhầm có hệ thống | 80 | `Shirt` bị ghi thành `T-shirt/top`. |
| Theo lô | 40 | Cả một lô dùng sai ánh xạ nhãn. |

Vì biết ảnh nào đã bị đổi, nhóm có thể đếm lỗi thật khi chấm điểm. **Nhãn gốc là nhãn tham chiếu cho lỗi đã tiêm**, không có nghĩa mọi nhãn gốc của Fashion-MNIST đã được kiểm toán là hoàn hảo. Đây là dữ liệu mô phỏng, chưa phải lô vendor thật.

## 3. Thuật toán được nhìn thấy gì?

Trước khi chọn 100 ảnh, thuật toán chỉ nhận **ảnh**, **nhãn hiện tại** của chúng và dữ liệu development. Nó không được đọc nhãn tham chiếu của evaluation hoặc danh sách 200 ảnh đã bị đổi nhãn.

Sau khi tạo xong thứ hạng, chương trình mới đối chiếu với đáp án để tính metric. Trong demo, nút **Hiện đáp án** giúp người xem nhìn bước đối chiếu này. File [review_queue.csv](artifacts/review_queue.csv) lưu top 100 của nhóm và điểm đáng nghi, **không chứa nhãn đúng**.

## 4. “Xếp hạng của nhóm” thực sự làm gì?

Với từng ảnh evaluation, code làm bốn bước:

1. Thu ảnh 28×28 xuống 14×14 để so sánh pixel.
2. Tìm **15 ảnh gần giống nhất** trong 8.000 ảnh development.
3. Cho 15 ảnh đó bỏ phiếu có trọng số theo độ gần để ước lượng mức ủng hộ từng lớp.
4. Tính **điểm đáng nghi = 1 − mức ủng hộ nhãn hiện tại**. Điểm càng cao, ảnh càng được xem sớm. Lấy đúng 100 ảnh đầu.

Ví dụ: một ảnh mang nhãn `Sneaker`, nhưng những ảnh rất giống nó thường mang nhãn `Sandal`. Điểm đáng nghi của ảnh đó sẽ cao. Tuy nhiên, **đáng nghi không đồng nghĩa chắc chắn sai**: ảnh mơ hồ hoặc cách đo khoảng cách pixel kém cũng có thể gây báo động nhầm.

Phiếu được tính theo trọng số, nên không đơn giản là số phiếu chia 15. Nếu hai ảnh bằng điểm, code dùng thứ tự hàng trong evaluation để phá hòa ổn định. Phương pháp đang chạy là **15-nearest-neighbor**; chưa dùng Cleanlab hay một mô hình lớn. Xem các hàm `image_features`, `neighbor_probabilities`, `rank_suspicion` trong [experiment.py](experiment.py), và bước chọn top 100 trong [run_demo.py](run_demo.py).

## 5. Vì sao hàng chờ của nhóm cố định?

**Cố định nghĩa là: cùng ảnh + cùng nhãn hiện tại + cùng dữ liệu development + cùng quy tắc thì ra cùng thứ hạng.** Nó không có nghĩa nhóm tự tay chọn sẵn 100 ảnh đẹp.

Ví dụ chỉ có 5 ảnh và được review 2 ảnh:

| Ảnh | Điểm đáng nghi do thuật toán tính | Thứ tự |
| --- | ---: | ---: |
| A | 0,90 | 1 |
| B | 0,75 | 2 |
| C | 0,40 | 3 |
| D | 0,20 | 4 |
| E | 0,10 | 5 |

Hàng chờ sẽ là **A rồi B**. Bấm nút thêm lần nữa vẫn là A rồi B, vì không có gì trong bài toán đã thay đổi. Tương tự, trên 2.000 ảnh thật của thí nghiệm, thuật toán tính điểm rồi chọn top 100; chạy lại với cùng cấu hình sẽ ra cùng 100 ID và cùng **78 lỗi**.

Nếu nút **Xếp hạng của nhóm** tự bốc một top 100 khác mỗi lần, người xem sẽ không biết nhóm đang đánh giá quy tắc nào. Một lượt may mắn có thể trông đẹp hơn lượt khác. Chỉ chọn lượt đẹp nhất để báo cáo là **cherry-pick**. Vì vậy kết quả chính phải tái lập được.

Danh sách của nhóm **được tính bởi code**, rồi lưu trong `review_queue.csv` và hiển thị trong demo. Nó không được tạo bằng cách đọc đáp án. Thứ hạng có thể thay đổi hợp lệ nếu đưa vào lô ảnh mới, nếu nhãn hiện tại được người review sửa, hoặc nếu nhóm công khai đổi phương pháp và làm **thí nghiệm mới**. Nếu tương lai thuật toán có yếu tố ngẫu nhiên, nên khóa seed cho kết quả chính và báo cáo thêm độ dao động qua các seed định trước.

## 6. Vì sao Random thay đổi khi bấm?

**Random baseline** là cách đơn giản để so sánh: chọn ngẫu nhiên đúng 100 trong 2.000 ảnh. Nó có nhiều danh sách hợp lệ; mỗi lượt bốc có thể chọn ID khác và tìm được số lỗi khác.

Trong [demo_live.html](artifacts/demo_live.html):

| Nút | Tác dụng |
| --- | --- |
| **Xếp hạng của nhóm** | Hiện top 100 đã tính theo 15 hàng xóm; luôn là kết quả 78 lỗi trên tập này. |
| **Bốc random mới** | Bốc 100 ảnh khác để thấy việc chọn ngẫu nhiên dao động ra sao. |

Hai lượt random có thể tình cờ **trùng số lỗi dù danh sách ảnh khác nhau**. Nút này phục vụ trình diễn; nó không thay đổi bảng kết quả chính.

Để có mốc so sánh ổn định, nhóm đã khóa trước **100 seed random từ 1000 đến 1099**. Mỗi seed chọn 100 ảnh trên **chính 2.000 ảnh evaluation đó**. Trung bình là **9,64 lỗi**; chạy lại đúng 100 seed sẽ luôn ra 9,64. Lệnh `python3 explore_random.py --runs 100` bốc 100 lượt *khám phá mới*, có thể cho trung bình khác, nhưng không ghi đè kết quả chính.

Vậy **cả hai cách đều có quy trình đánh giá chính cố định**: cách của nhóm tạo một thứ hạng xác định; cách random được báo cáo bằng 100 lượt có seed đã chốt. Chỉ nút random trong demo là động để dễ hiểu độ dao động.

## 7. Nhóm đo kết quả như thế nào?

Ngân sách review là **100/2.000 ảnh = 5%**. Tập evaluation có **200 lỗi thật đã tạo**.

```text
Error Recall@5% = số lỗi thật trong 100 ảnh được chọn / 200 lỗi thật
Precision@5%    = số lỗi thật trong 100 ảnh được chọn / 100 ảnh đã review
```

`Error Recall@5%` là metric chính: với cùng ngân sách, tìm được bao nhiêu phần của toàn bộ lỗi? `Precision@5%` cho biết trong các ảnh phải xem, tỷ lệ ảnh thực sự bị sai là bao nhiêu.

| Cách chọn | Lỗi trong 100 ảnh | Error Recall@5% | Precision@5% |
| --- | ---: | ---: | ---: |
| Random, trung bình 100 seed cố định | 9,64 | 4,82% | 9,64% |
| Xếp hạng của nhóm | 78 | **39%** | **78%** |

Ví dụ, `78 / 200 = 39%` recall và `78 / 100 = 78%` precision. Số 9,64 là **trung bình của 100 lượt**, không phải một lượt chọn được “9,64 ảnh”. Trong bộ 100 seed chính, từng lượt random tìm từ 4 đến 17 lỗi. Nếu chọn ngẫu nhiên 100 ảnh từ tập có 10% lỗi thì kỳ vọng khoảng 10 lỗi; 9,64 là trung bình thực tế của 100 lượt đã khóa.

Theo từng kiểu lỗi, nhóm tìm được **49/80 lỗi rải rác**, **6/80 lỗi `Shirt → T-shirt/top`**, **23/40 lỗi theo lô**. Kết quả tổng thể tốt hơn random nhưng rất yếu với hai loại áo dễ nhầm. Đây là failure case quan trọng hơn một vài ảnh demo đẹp. Số liệu gốc nằm trong [results.json](artifacts/results.json).

## 8. Vì sao tách development và evaluation?

Nếu nhìn đáp án evaluation rồi sửa thuật toán để đẩy đúng các ảnh sai lên đầu, nhóm sẽ “học thuộc đề thi”. Metric khi ấy không chứng minh phương pháp tìm lỗi trên dữ liệu chưa biết.

- **Development:** được dùng để thử, chọn cách tính và sửa phương pháp.
- **Evaluation:** dùng đo kết quả cuối sau khi phương pháp đã chốt; đáp án chỉ dùng để chấm và phân tích lỗi.
- **Downstream test:** đang để dành, chưa có kết quả về mô hình sau khi sửa nhãn.

Thí nghiệm khóa seed chia tập `20260924`, seed tạo lỗi development `311`, seed tạo lỗi evaluation `677`. Khóa seed giúp người khác **chạy lại đúng thí nghiệm**, không tự chứng minh phương pháp tốt trên mọi lô/seed. Muốn thử độ bền thì phải báo cáo thêm các kịch bản theo quy tắc định trước, không chọn lượt đẹp nhất.

## 9. Hiện đã làm được gì và quyết định gì?

**Đã làm:** code chạy offline; tạo ba kiểu lỗi mô phỏng; xếp hạng ảnh; random baseline cùng ngân sách; bảng metric; stress test với mức lỗi 5% và 20%; demo tương tác; 5 slide.

**Chưa chứng minh:** hiệu quả trên lô vendor thật; khả năng giải chuyên biệt ca hai annotator đảo 0/1; thời gian người thật review; chất lượng mô hình downstream sau khi sửa nhãn. Phương pháp dựa vào độ giống pixel nên dễ bỏ sót lỗi mà nhãn sai vẫn trông hợp lý.

**Quyết định hiện tại: Rework.** Kết quả mô phỏng hứa hẹn nhưng chưa đủ để triển khai thật. Bước tiếp theo là thêm tín hiệu theo người gán/lô, làm thí nghiệm riêng về đảo 0↔1, kiểm tra một tập nhãn thật bằng người độc lập và đo thời gian review.

## 10. Xem demo theo thứ tự nào?

1. Mở [demo_live.html](artifacts/demo_live.html). Trang đầu là **Xếp hạng của nhóm**.
2. Bấm **Hiện đáp án** để thấy ảnh nào trong top 100 đã bị đổi nhãn.
3. Bấm **Bốc random mới** vài lần; xem ID ảnh và số lỗi có thể thay đổi.
4. Bấm lại **Xếp hạng của nhóm**; kết quả trở lại **78 lỗi** vì dữ liệu và quy tắc không đổi.
5. Đối chiếu với [results.json](artifacts/results.json) và [5 slide showcase](artifacts/C1_Showcase.pdf).

Muốn chạy lại toàn bộ, xem [DEMO_GUIDE.md](DEMO_GUIDE.md). Chạy lại ra cùng số là **thí nghiệm tái lập được**, không phải demo bị hỏng.

## 11. Câu trả lời ngắn khi thuyết trình

> **“Vì sao của nhóm luôn 78 còn random thì nhảy?”** Vì của nhóm là một quy tắc sắp xếp xác định trên cùng 2.000 ảnh. Random mỗi lần bốc một danh sách mới. Để so sánh công bằng, nhóm dùng **trung bình 100 lượt random đã khóa seed**, không chọn một lượt random xấu để đối đầu với 78. Kết quả 78 chỉ chứng minh hiệu quả trên dữ liệu mô phỏng này; nhóm vẫn bỏ sót nhiều lỗi `Shirt → T-shirt/top` nên quyết định **Rework**.
