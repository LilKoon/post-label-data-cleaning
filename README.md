# C1 — Post-label Data Cleaning

> **Bộ trình bày 5 phút:** [Slide PDF](artifacts/C1_Peer_Showcase_5min.pdf) · [PowerPoint có ghi chú](artifacts/C1_Peer_Showcase_5min.pptx) · [Lời thoại và Q&A](PRESENTATION_5_MINUTES.md).

> **Muốn thấy kết quả nhóm thay đổi theo dữ liệu lỗi mới:** Mở [demo_scenarios.html](artifacts/demo_scenarios.html), bấm **Tạo kịch bản khác**, rồi so sánh hai hàng chờ trên cùng kịch bản. Xem [giải thích trong hướng dẫn](DEMO_GUIDE.md).

> **Demo random tương tác:** Mở [demo_live.html](artifacts/demo_live.html) và bấm **Bốc random mới** để xem một danh sách 100 ảnh khác cùng metric mới. Xem [hướng dẫn thao tác](DEMO_GUIDE.md).

> **Cập nhật demo (24/09/2026):** Prototype đã chạy trên Fashion-MNIST. Xem [hướng dẫn demo](DEMO_GUIDE.md), [demo offline](artifacts/demo.html), [5 slide PDF](artifacts/C1_Showcase.pdf), [PowerPoint](artifacts/C1_Showcase.pptx) và [kết quả đo](artifacts/results.json). Dòng “Trạng thái: Kế hoạch thí nghiệm” ở phần cũ bên dưới ghi lại trạng thái trước khi prototype được thực hiện.

## Đọc trước: nhóm mình đang làm gì?

**Tên đề tài dễ hiểu:** Tìm ảnh quần áo bị gán sai nhãn khi chỉ đủ thời gian kiểm tra lại 5% dữ liệu.

Hãy tưởng tượng có 2.000 ảnh sản phẩm vừa được gán nhãn `áo`, `quần`, `giày`… Một số ảnh có nhãn sai. Người kiểm tra chỉ xem được **100 ảnh**. Câu hỏi của nhóm là: **nên đưa 100 ảnh nào cho họ xem để tìm được nhiều lỗi nhất?** Mô hình phân loại trong bài này là công cụ giúp sắp thứ tự ảnh cần kiểm tra.

### Mục đích

Tạo một danh sách ảnh **đáng nghi nhất** để người kiểm tra xem trước. Nếu danh sách đó tìm được nhiều lỗi thật hơn 100 ảnh chọn ngẫu nhiên, cách làm của nhóm có ích. Nhóm cần đo điều đó bằng số, không chỉ trình chiếu vài ảnh ví dụ.

### Nhóm phải làm những gì?

1. **Lấy dữ liệu:** dùng ảnh quần áo từ [Fashion-MNIST](https://github.com/zalandoresearch/fashion-mnist). Mỗi ảnh có một nhãn gốc thuộc 10 loại. Nhóm dùng nhãn gốc làm nhãn tham chiếu cho thí nghiệm mô phỏng.
2. **Tạo tình huống có lỗi:** sao chép nhãn gốc rồi cố ý đổi một số nhãn trong bản sao. Tạo ít nhất ba kiểu: đổi nhầm rải rác; hay nhầm hai loại áo giống nhau; cả một lô ảnh dùng sai quy tắc gán nhãn. Chương trình phải ghi lại chính xác ảnh nào đã bị đổi.
3. **Giấu đáp án:** chia dữ liệu thành phần để thử và chỉnh cách làm (*development*) và phần chỉ dùng báo cáo cuối (*evaluation*). Chương trình tìm lỗi chỉ được thấy **ảnh và nhãn đang dùng**, không được đọc danh sách ảnh đã cố ý đổi nhãn trong evaluation.
4. **Chạy cách đơn giản nhất:** chọn ngẫu nhiên 5% ảnh để kiểm tra. Đây là **baseline** bắt buộc.
5. **Chạy cách của nhóm:** huấn luyện mô hình nhìn ảnh và tính xem nhãn hiện tại có đáng nghi không; xếp ảnh đáng nghi lên đầu. Có thể thử Cleanlab hoặc tín hiệu theo lô, nhưng chỉ chọn cách cuối bằng kết quả trên development.
6. **So sánh công bằng:** trên **cùng tập evaluation**, cho random và cách của nhóm mỗi bên chọn đúng 5% ảnh. Mở đáp án đã giấu để đếm mỗi bên tìm được bao nhiêu nhãn sai thật.
7. **Giải thích kết quả:** nêu loại lỗi nào tìm tốt, loại nào bỏ sót, thời gian/chi phí, rồi quyết định nên thử áp dụng, sửa tiếp hay không dùng phương pháp này.

### Con số nào quyết định kết quả?

Giả sử evaluation có **2.000 ảnh**, trong đó **200 nhãn sai**, và được kiểm tra **100 ảnh**:

| Cách chọn 100 ảnh | Số lỗi thật tìm được | Error Recall@5% = lỗi tìm được / 200 |
| --- | ---: | ---: |
| Chọn ngẫu nhiên | Ví dụ 10 | Ví dụ 5% |
| Cách của nhóm | Ví dụ 40 | Ví dụ 20% |

**Các số 10 và 40 chỉ để giải thích cách tính, chưa phải kết quả thí nghiệm.** Khi làm bài, nhóm phải chạy code và thay bằng số đo thật. Ngoài tổng số lỗi, cần báo cáo riêng kết quả của **từng kiểu lỗi**. Nếu cách của nhóm bỏ sót lỗi theo lô, hãy trình bày đó là một failure case.

### Vì sao phải chia development và evaluation?

Nếu nhóm xem trước ảnh nào bị đổi nhãn trong evaluation rồi chỉnh thuật toán để tìm đúng chúng, kết quả sẽ không còn công bằng. Vì thế, nhóm được thử nhiều cách trên development; sau khi chốt cách làm, mới chạy evaluation để báo cáo cuối. Kết quả xấu cũng phải báo cáo. Đây là ý nghĩa của luật **không cherry-pick**.

### Cuối cùng nhóm cần nộp gì?

Code hoặc notebook chạy được; README hướng dẫn chạy lại; nguồn và giấy phép dataset; cách chia dữ liệu và tạo ground truth; bảng **random so với cách của nhóm**; ít nhất một lỗi bị bỏ sót hoặc hạn chế; và **5 slide** tóm tắt pain point, cách làm, metric, failure case, quyết định production. Phần bên dưới là kế hoạch kỹ thuật chi tiết để triển khai các việc này.

> **Trạng thái:** Kế hoạch thí nghiệm. Repository hiện chưa có dữ liệu, mã nguồn hoặc kết quả đo. Các ngưỡng và số lượng bên dưới là cấu hình đề xuất; nhóm cần chốt chúng **trước khi mở đáp án evaluation**.

## 1. Bài toán trong một câu

Sau khi một lô ảnh sản phẩm đã được gán nhãn, nhóm chỉ đủ nguồn lực kiểm tra lại **5% số ảnh**. Cần xếp hạng ảnh cần human review sao cho tìm được nhiều **nhãn sai thật** hơn chọn ngẫu nhiên cùng ngân sách.

Nhãn sai có thể khiến mô hình phân loại học nhầm, làm metric đánh giá thiếu tin cậy và ảnh hưởng đến đội vận hành danh mục sản phẩm cùng người dùng cuối. Hệ thống chỉ **ưu tiên mẫu cần xem lại**; người review xác nhận và sửa nhãn. Dataset công khai bên dưới là mô phỏng cho tình huống này, không phải dữ liệu vendor thật.

## 2. Quyết định MVP

| Mục | Cấu hình đề xuất | Vì sao |
| --- | --- | --- |
| Dataset | [Fashion-MNIST của Zalando Research](https://github.com/zalandoresearch/fashion-mnist) | Có ảnh để review trực quan, 10 lớp, đủ lớn để chia tập và tạo nhiều loại lỗi. Nguồn công bố giấy phép MIT. |
| Đơn vị xếp hạng | Một ảnh và nhãn hiện tại của ảnh đó | Khớp với một lượt human review. |
| Review budget | `B = 5%` của tập evaluation | Đúng primary metric của đề C1. |
| Baseline bắt buộc | Chọn ngẫu nhiên đúng `K = ceil(0.05 × N_eval)` ảnh | Mốc so sánh cùng ngân sách. |
| Solution đầu tiên | Xếp hạng theo mức không khớp giữa xác suất dự đoán và nhãn hiện tại | Có thể chạy và kiểm chứng trước khi thêm thành phần phức tạp. |
| Research technique để thử | [Cleanlab / Confident Learning](https://research.google/pubs/confident-learning-estimating-uncertainty-in-dataset-labels/) | Kỹ thuật chuyên tìm lỗi nhãn; chỉ giữ lại nếu thắng phương pháp đơn giản trên development. |

Không cần cloud deployment, frontend hoàn chỉnh hoặc mô hình lớn để hoàn thành MVP. Ưu tiên thí nghiệm tái lập được và evidence có metric.

## 3. Dữ liệu, ground truth và ba loại lỗi

### Chia tập

- Lấy khoảng **8.000 ảnh development** và **2.000 ảnh evaluation** từ phần train gốc của Fashion-MNIST, chia theo lớp với seed cố định.
- Lấy **2.000 ảnh downstream test sạch** từ phần test gốc. Tập này chỉ dùng để kiểm tra tác động sau khi sửa nhãn, không dùng để chọn phương pháp phát hiện lỗi.
- Gán ID cố định cho từng ảnh. Kiểm tra ảnh trùng hệt trước khi chia; các bản trùng phải ở cùng một phần để tránh rò rỉ.
- Lưu danh sách ID và seed của từng phần. Mọi bước tiền xử lý cần học từ dữ liệu, chẳng hạn chuẩn hóa, chỉ được fit trên phần dùng để huấn luyện ở bước đó.

### Tạo lỗi có kiểm soát

Tạo một bản `noisy_label` từ nhãn gốc. Đề xuất tỷ lệ lỗi **10%** trong development và evaluation, với ba cơ chế không chồng lên cùng một ảnh:

1. **Lỗi rải rác:** đổi nhãn của ảnh được chọn sang một lớp khác nhãn gốc.
2. **Nhầm có hệ thống giữa lớp gần nhau:** ví dụ một phần ảnh `Shirt` bị gán thành `T-shirt/top`. Chốt cặp lớp trước khi chạy evaluation.
3. **Lỗi theo lô:** tạo ID lô gán nhãn cho toàn bộ dữ liệu trước, rồi áp dụng sai ánh xạ nhãn cho một lô đã chọn. Cách chọn lô, kích thước lô và ánh xạ phải được ghi lại từ trước.

Script tạo lỗi lưu riêng `image_id`, `original_label`, `noisy_label` và `error_type`. **Đây là đáp án evaluation**, không được đưa vào file đầu vào của thuật toán xếp hạng hoặc dùng để sửa trọng số sau khi đã chạy evaluation. Nhóm đo được chính xác các lỗi *đã tạo*; nhãn gốc của public dataset vẫn có thể chứa lỗi hoặc trường hợp mơ hồ. Ghi giới hạn này trong báo cáo và kiểm tra thủ công một số trường hợp bất đồng nếu có thời gian.

## 4. Tách development và evaluation: luật chống cherry-pick

| Phần | Được dùng để làm gì? | Không được dùng để làm gì? |
| --- | --- | --- |
| Development | Chọn mô hình, tín hiệu xếp hạng, tham số, cách xử lý hòa điểm; thử và sửa code. | Không báo cáo nó như kết quả evaluation cuối. |
| Evaluation khóa kín | Tính metric cuối cho random và phương pháp đã chốt, trên cùng ID và review budget. | Không nhìn đáp án để chọn phương pháp, đổi ngưỡng, đổi seed hay bỏ ca khó. |
| Downstream test sạch | Đo chất lượng mô hình phân loại trước/sau sửa nhãn. | Không dùng để tune detector hoặc chọn lần chạy đẹp nhất. |

Trước khi chạy evaluation, lưu lại cấu hình cuối: dataset version/source, danh sách ID, seed, mã nguồn hoặc commit, mô hình, tham số, công thức xếp hạng, `B = 5%`, metric, stress test và quy tắc ra quyết định. Nếu sửa lỗi code sau đó, ghi rõ lỗi, thay đổi và chạy lại **toàn bộ phương pháp** theo một quy tắc nhất quán; không sửa riêng các case nhìn thấy đáp án.

## 5. Baseline và solution

### Random baseline

Với `N_eval = 2.000`, mỗi lần chọn ngẫu nhiên đúng `K = 100` ảnh. Chạy nhiều seed đã định trước, báo cáo trung bình, khoảng dao động và kết quả từng seed. Mọi phương pháp dùng cùng tập evaluation và cùng `K`.

### Phương pháp đơn giản

Huấn luyện mô hình phân loại trên development. Với mỗi ảnh evaluation, tính xác suất của nhãn hiện tại `p(noisy_label | image)`. Xếp ảnh có xác suất này **thấp nhất** lên đầu danh sách review. Mô hình không được học nhãn đúng hoặc cơ chế tạo lỗi của evaluation.

### Phương pháp nghiên cứu

Thử Cleanlab/Confident Learning trên development và so sánh với score đơn giản. Khi chấm điểm chính dữ liệu mà mô hình đã học, dùng dự đoán **ngoài mẫu** qua các fold; dự đoán trên mẫu đã dùng để huấn luyện có thể quá lạc quan. [Hướng dẫn chính thức của Cleanlab](https://docs.cleanlab.ai/stable/tutorials/datalab/datalab_quickstart.html).

Nếu muốn cải tiến, có thể thử thêm bất đồng với ảnh gần giống hoặc tín hiệu bất thường theo lô. Phải đo **ablation** trên development: score đơn giản; Cleanlab; thành phần bổ sung; tổ hợp cuối. Chỉ đưa tổ hợp sang evaluation sau khi đã chốt.

## 6. Metric và bảng evidence

Đặt `K = ceil(B × N_eval)`. Với mỗi phương pháp, lấy đúng `K` ảnh đầu danh sách:

```text
Error Recall@5% = số lỗi thật trong top K / tổng số lỗi thật của evaluation
Precision@5%    = số lỗi thật trong top K / K
Recall theo loại = số lỗi loại đó trong top K / tổng số lỗi của loại đó
```

**Error Recall@5% là primary metric.** Báo cáo thêm số lỗi tìm được, Precision@5%, recall của từng loại lỗi và kết quả random qua nhiều seed. Nếu thực sự cho người review xem ảnh và đo thời gian, thêm `defects/minute = lỗi được người review xác nhận / số phút review`. Nếu chỉ đối chiếu ID với file đáp án, gọi đó là **khả năng tìm lỗi của ranking với giả định reviewer nhận ra lỗi**, không gọi là năng suất human review đã đo.

| Phương pháp | Lỗi trong top K | Error Recall@5% | Precision@5% | Lỗi rải rác | Nhầm lớp | Lỗi theo lô |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Random, nhiều seed | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |
| Score đơn giản | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |
| Solution cuối | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |

Để đo tác động sau sửa nhãn, huấn luyện cùng một mô hình phân loại theo cùng cấu hình trên: (a) dữ liệu nhãn lỗi chưa sửa, (b) dữ liệu đã sửa các ảnh được random chọn, (c) dữ liệu đã sửa các ảnh do solution chọn. So sánh macro-F1 hoặc accuracy trên **cùng downstream test sạch**. Đây là secondary evidence; không thay cho Error Recall@5%.

## 7. Robustness, failure case và quyết định production

- **Stress test:** giữ nguyên phương pháp đã khóa và thử các mức lỗi 5%, 10%, 20% trên các bản dữ liệu/seed định trước. Không chọn kết quả tốt nhất để thay evaluation chính.
- **Failure analysis:** ghi ít nhất một lỗi thật bị bỏ sót và một cảnh báo sai; giải thích bằng ảnh, nhãn và score. Kiểm tra xem phương pháp có yếu riêng ở lỗi theo lô hoặc ở các lớp dễ nhầm không.
- **Runtime/cost:** ghi thời gian tạo score, thời gian review nếu đo được, và số lỗi thật trên mỗi 100 lượt review.
- **Rủi ro:** ảnh 28×28 có thể mơ hồ; ground truth chủ yếu là lỗi mô phỏng; hiệu quả trên lô gán nhãn thật cần được kiểm tra thêm.

**Quy tắc quyết định cần được chốt trước evaluation.** Một ngưỡng đề xuất để nhóm thảo luận: chỉ `Deploy` ở mức **pilot có người duyệt** nếu Error Recall@5% ít nhất gấp 3 lần kỳ vọng random, Precision@5% đạt ít nhất 30% trong kịch bản 10% nhãn lỗi, và cả ba loại lỗi đều có mẫu được phát hiện. `Rework` nếu chỉ thắng ở một số loại lỗi hoặc chi phí review chưa hợp lý; `Reject` nếu không hơn random một cách đáng tin. Đây là ngưỡng đề xuất, **chưa phải kết quả**. Nhóm có thể đổi ngưỡng trước khi mở đáp án evaluation và phải giải thích bằng use case.

## 8. Công việc theo thứ tự

- [ ] Viết và khóa `experiment contract`: pain point, dữ liệu, split, ba loại lỗi, seed, metric, ngân sách, quy tắc quyết định.
- [ ] Tạo script tải dữ liệu, chia tập, tạo lỗi và lưu đáp án evaluation tách khỏi đầu vào detector.
- [ ] Kiểm tra số mẫu, số lỗi mỗi loại, ID trùng và khả năng tái lập cùng seed.
- [ ] Chạy random baseline, lưu kết quả từng seed.
- [ ] Chạy score đơn giản; thử Cleanlab và các cải tiến **chỉ trên development**.
- [ ] Khóa phương pháp, sau đó chạy evaluation và điền bảng evidence.
- [ ] Chạy ít nhất một stress test/ablation, viết failure case và giới hạn.
- [ ] Viết README phần **Cách chạy lại** bằng lệnh thực tế sau khi đã có code; ghi phiên bản môi trường và thời gian chạy.
- [ ] Chuẩn bị notebook/code chạy được, bảng kết quả, 5-slide PDF/PPTX và demo dùng dữ liệu có sẵn khi offline.

## 9. Bố cục 5 slide / 5 phút

1. **Pain point:** ai bị ảnh hưởng và câu hỏi “xem 5% thì tìm được bao nhiêu lỗi?”.
2. **Protocol:** dataset, ba loại lỗi, ground truth và cách khóa evaluation.
3. **Solution:** pipeline xếp hạng, kỹ thuật nghiên cứu và lý do chọn.
4. **Evidence:** bảng random so với solution, kết quả theo loại lỗi và một phát hiện không hiển nhiên.
5. **Failure & decision:** lỗi bỏ sót, chi phí, giới hạn, quyết định Deploy/Rework/Reject.

## 10. Tài liệu tham khảo

- [Fashion-MNIST — nguồn dữ liệu và giấy phép](https://github.com/zalandoresearch/fashion-mnist/blob/master/README.md)
- [Confident Learning: Estimating Uncertainty in Dataset Labels](https://research.google/pubs/confident-learning-estimating-uncertainty-in-dataset-labels/)
- [Cleanlab Datalab: dự đoán ngoài mẫu để tìm vấn đề trong nhãn](https://docs.cleanlab.ai/stable/tutorials/datalab/datalab_quickstart.html)
