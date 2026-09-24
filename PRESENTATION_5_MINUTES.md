# Kịch bản trình bày C1 trong 5 phút

## Mục tiêu của phần trình bày

Người nghe cần hiểu một câu: **“Chỉ kiểm tra lại 100/2.000 ảnh thì xếp ảnh có nhãn đáng nghi lên đầu giúp tìm nhiều lỗi thật hơn chọn ngẫu nhiên cùng ngân sách.”**

Kết quả chính phải đọc đúng: **78 lỗi trong top 100 của nhóm, tức Error Recall@5% = 39%**. Random trên cùng 2.000 ảnh và cùng 100 lượt review tìm trung bình **9,64 lỗi**, tức **4,82% recall**, qua 100 seed đã khóa. Đây là kết quả trên **lỗi mô phỏng**, không phải phép đo trên vendor thật.

Mở sẵn [slide PDF](artifacts/C1_Peer_Showcase_5min.pdf) hoặc [PowerPoint](artifacts/C1_Peer_Showcase_5min.pptx). Nếu dùng demo, mở sẵn [demo đổi kịch bản](artifacts/demo_scenarios.html) trên máy trình bày và tải lại trang để nó ở kịch bản chính seed `677`. Demo là file offline. Đặt tab slide và tab demo cạnh nhau để chuyển ngay, không tìm file trước lớp.

## Phân bổ thời gian

| Đồng hồ | Nội dung | Mục tiêu |
| --- | --- | --- |
| **0:00–0:45** | Slide 1 — Pain | Nói ai bị ảnh hưởng, ngân sách 5%, giả thuyết. |
| **0:45–1:35** | Slide 2 — Baseline | Giải thích random cùng 100 ảnh, 100 seed, công thức recall. |
| **1:35–2:45** | Slide 3 — Solution và demo | Giải thích 15 hàng xóm; demo **tối đa 25 giây**. |
| **2:45–3:55** | Slide 4 — Evidence | Nêu 78 so với 9,64, failure 6/80 và stress test. |
| **3:55–4:45** | Slide 5 — Decision | Chọn Rework, giới hạn và bước tiếp. |
| **4:45–5:00** | Dự phòng | Kết thúc trước chuông; không mở thêm demo. |

**Quy tắc hard stop:** Khi đồng hồ tới 5:00, dừng. Nếu thao tác demo chậm, bỏ qua demo và đi thẳng slide 4: bằng chứng metric đã có trên slide. Không dùng ảnh đẹp hoặc giao diện để thay bảng kết quả.

## Lời thoại theo từng slide

### Slide 1 — Pain, 0:00–0:45

> “Đội gán nhãn vừa giao một lô ảnh sản phẩm. Nhãn sai có thể làm mô hình học và đánh giá sai. Chỉ đủ thời gian kiểm tra lại 5%, nhóm phải chọn **100 trong 2.000 ảnh** để tìm nhiều lỗi nhất. Giả thuyết là ảnh có nhãn lệch với các ảnh gần giống đáng review hơn. Bài thử dùng Fashion-MNIST và **200 lỗi** tạo có kiểm soát: rải rác, nhầm lớp và sai theo lô.”

**Chỉ tay vào:** 2.000 ảnh → 200 lỗi mô phỏng → 100 lượt review. Đừng nói 10% là tỷ lệ lỗi thực tế của vendor; đó là cấu hình bài thử.

### Slide 2 — Baseline, 0:45–1:35

> “Baseline bắt buộc là chọn ngẫu nhiên đúng 100 ảnh trên **cùng tập evaluation 2.000 ảnh**. Để một lần may rủi không quyết định kết luận, chúng tôi khóa trước 100 seed random và báo cáo trung bình: **9,64 lỗi trong 100 ảnh**, tương ứng **Error Recall@5% = 9,64 chia 200 = 4,82%**. Từng lượt random tìm từ 4 đến 17 lỗi. Con số 9,64 là trung bình của 100 lượt, không phải một lượt bốc được một phần của ảnh. Cách này là mốc tối thiểu để xem giải pháp của nhóm có thật sự giúp chọn ảnh tốt hơn không.”

**Chỉ tay vào:** 9,64 và 4,82%. Nói “trung bình 100 seed” một lần rõ ràng. Không chọn seed random xấu để demo như thể đó là baseline chính.

### Slide 3 — Solution và demo, 1:35–2:45

> “Phương pháp của nhóm lấy **8.000 ảnh development**, thu mỗi ảnh về 14×14 pixel rồi tìm **15 ảnh gần giống nhất** cho từng ảnh cần kiểm tra. Các ảnh gần giống bỏ phiếu có trọng số. Nếu nhãn hiện tại nhận ít ủng hộ, điểm đáng nghi cao và ảnh được đưa lên đầu. Hệ thống xếp hạng tất cả ảnh rồi giao **top 100** cho người review. Đáp án của evaluation chỉ được dùng **sau khi thứ hạng đã cố định** để chấm kết quả.”

**Demo 20–25 giây, đúng ba thao tác:**

1. Chuyển sang [demo_scenarios.html](artifacts/demo_scenarios.html): chỉ vào kết quả chính **78/200 lỗi**.
2. Bấm **Tạo kịch bản khác** một lần: seed lỗi `2000`, hàng chờ của nhóm tìm **72/200 lỗi**.
3. Bấm **Random cùng kịch bản**: lần bốc này tìm **10/200 lỗi**; hai cách đang xét **cùng bản lỗi mới**. Quay lại slide 4 ngay.

**Câu chốt demo:** “Cùng dữ liệu và seed thì kết quả lặp lại được; đổi bản lỗi mô phỏng thì chúng tôi tính lại thứ hạng, nên số của nhóm cũng đổi. Kịch bản mới chỉ để minh họa, không thay kết quả chính trên slide.”

Nếu demo không mở được, chỉ vào hình và công thức trên slide 3 rồi chuyển tiếp. Không dành quá 25 giây để khắc phục trước lớp.

### Slide 4 — Evidence, 2:45–3:55

> “Trên tập evaluation chính, trong 100 ảnh được đưa lên đầu có **78 lỗi thật**. Vì toàn tập có 200 lỗi, Error Recall@5% của nhóm là **39%**; precision là **78%**. So với random **4,82%**, recall cao khoảng **8,1 lần** trên benchmark này. Nhưng kết quả không đều theo loại lỗi: nhóm tìm **49/80 lỗi rải rác**, **23/40 lỗi theo lô**, và chỉ **6/80 lỗi Shirt bị ghi thành T-shirt/top**. Đây là failure case quan trọng. Khi đổi tỷ lệ lỗi trong stress test, recall là **52% ở mức lỗi 5%** và **22,5% ở mức 20%**; mẫu số khác nhau, nên không đọc đó là cùng một phép so sánh.”

**Chỉ tay vào:** 39% vs 4,82%, rồi cột “Nhầm 2 lớp” và 6/80. Đừng chỉ đọc con số 8,1× rồi bỏ qua failure. Nếu bị hỏi 30 kịch bản mới, nói đó là **minh họa bổ sung trên cùng ảnh**, không phải tập evaluation độc lập.

### Slide 5 — Decision, 3:55–4:45

> “Quyết định của nhóm là **Rework**, chưa triển khai thật. Hàng chờ có ích trên lỗi mô phỏng, nhưng bỏ sót **74/80** lỗi nhầm giữa hai loại áo. Nhãn gốc Fashion-MNIST chưa được nhóm kiểm toán toàn bộ, và chúng tôi chưa đo thời gian người thật review hay chất lượng mô hình sau khi sửa nhãn. Bước tiếp theo là thêm tín hiệu theo người gán hoặc theo lô, rồi thử trên một tập mới có nhãn được hai người xem độc lập và phân xử. Khi đó sẽ đo thêm số lỗi tìm được trên mỗi phút review, rồi mới quyết định pilot.”

**Dừng tại đây.** Nếu còn thời gian, chỉ nhắc “Code và cách reproduce nằm trong README”; không mở thêm trang.

## Vì sao cấu trúc này hợp rubric 100 điểm?

| Tiêu chí | Điểm tối đa | Bằng chứng người chấm nhìn thấy |
| --- | ---: | --- |
| Pain point & framing | 10 | Slide 1: ai bị ảnh hưởng, ngân sách 5%, giả thuyết. |
| Metric validity | 15 | Slide 2 và 4: cùng tập, cùng 100 review, công thức Recall@5%. |
| Technical solution | 20 | Slide 3: pipeline 15 hàng xóm và demo chạy offline. |
| Experiment & evidence | 25 | Slide 2 và 4: random 100 seed, 78 vs 9,64, split development/evaluation. |
| Robustness & failure | 10 | Slide 4: 6/80 lỗi nhầm lớp và stress test. |
| Production feasibility | 10 | Slide 5: human review, giới hạn, bước pilot. |
| Presentation & Q&A | 10 | Nói đúng 5 phút; phần trả lời bên dưới bám metric và giới hạn. |

**Bonus innovation:** Đừng tự nhận điểm bonus chỉ vì có demo hoặc 15-NN. Muốn nhận bonus, nhóm phải chứng minh kỹ thuật ngoài slide hoặc một cải tiến/đánh giá có giá trị theo đúng điều kiện của lớp. Bằng chứng chính phải hợp lệ trước.

## Chuẩn bị trước khi lên lượt

- Máy mở offline được PDF và HTML; tăng zoom để cả lớp đọc rõ số **78**, **9,64**, **6/80**.
- Để demo ở kịch bản chính bằng cách **tải lại trang** ngay trước khi lên.
- Người trình bày bấm slide; nếu có người thứ hai, người đó chỉ phụ trách chuyển sang tab demo rồi quay lại slide 4. Tập dượt điểm chuyển màn hình.
- Không chạy `python3 run_demo.py` trên sân khấu: bộ kết quả và demo đã được tạo sẵn. Lệnh đó dùng để reproduce sau buổi học và sẽ ra cùng số vì seed đã khóa.
- Tập dượt với đồng hồ ít nhất hai lần; cắt phần demo trước nếu tổng vượt 4:45.
- Gói nộp gồm [README](README.md), [hướng dẫn demo](DEMO_GUIDE.md), [mã nguồn](run_demo.py), [kết quả chính](artifacts/results.json), slide PDF/PPTX và ghi chú giới hạn.

## Trả lời Q&A trong 10 phút

Trả lời theo nhịp **kết luận → số liệu/cách đo → giới hạn**. Nếu nhóm chưa đo điều gì, nói rõ “chưa đo” rồi nêu thí nghiệm cần làm; đừng suy từ demo.

| Câu hỏi có thể gặp | Trả lời ngắn có evidence |
| --- | --- |
| **Tại sao chạy lại vẫn đúng 78?** | Tập ảnh, nhãn mô phỏng seed `677`, 15 hàng xóm và ngân sách 100 đều cố định nên top 100 tái lập. Demo đổi kịch bản seed `2000` tính lại và cho 72 lỗi. Kịch bản bổ sung không thay bài đánh giá chính. |
| **Baseline random có quá yếu không?** | Random là baseline bắt buộc và cùng ngân sách. Nó tìm trung bình 9,64 lỗi qua 100 seed. Nhóm **chưa** chứng minh hơn các detector mạnh hơn như classifier/Cleanlab; đó là phép so sánh cần làm tiếp. |
| **Ground truth có bias không?** | Nhóm biết chính xác lỗi **đã tiêm** vào; nhãn gốc Fashion-MNIST chỉ là nhãn tham chiếu và có thể có ảnh mơ hồ. Cần tập nhỏ được người thật phân xử để đánh giá ngoài mô phỏng. |
| **Có data leakage không?** | Chia 8.000 development và 2.000 evaluation; detector nhìn ảnh và nhãn hiện tại, không nhận danh sách lỗi của evaluation. Chỉ sau khi khóa top 100 mới dùng đáp án để chấm. Kiểm tra trực tiếp trong `run_demo.py`. |
| **30 kịch bản mới có phải 30 test độc lập không?** | Không. Chúng dùng lại 2.000 ảnh evaluation với các bản lỗi mô phỏng khác. Toàn bộ seed và kết quả có trong `scenario_results.json`; không dùng để chọn kết quả báo cáo cuối. |
| **Precision 78% nghĩa là gì?** | Trong 100 ảnh giao người review, 78 ảnh có lỗi đã tiêm; 22 ảnh là cảnh báo sai theo ground truth mô phỏng. Người review vẫn cần xác nhận. |
| **Nếu bỏ sót 122 lỗi thì sao gọi là tốt?** | Với ngân sách chỉ 100 lượt, nhóm tìm 78/200 lỗi, cao hơn random trung bình 9,64. Nhưng còn 122 lỗi ngoài hàng chờ, nên quyết định là Rework thay vì Deploy. |
| **Vì sao lỗi Shirt → T-shirt/top khó?** | Hai lớp trông giống nhau trong ảnh 28×28; các hàng xóm có thể vẫn ủng hộ nhãn sai. Nhóm chỉ tìm 6/80 lỗi loại này, thấp hơn rõ so với các loại khác. |
| **Ca hai người đảo nhãn 0/1 có được giải chưa?** | Chưa có thí nghiệm chuyên biệt. Demo hiện dùng 10 lớp và lỗi theo lô dạng ánh xạ khác. Cần dữ liệu có `annotator_id` và mô phỏng đảo 0↔1 để đo riêng trước khi khẳng định. |
| **Scale 10 lần thì sao?** | Prototype so mỗi ảnh evaluation với 8.000 ảnh development theo pixel; thời gian tính score cho 2.000 ảnh trong lần đo là khoảng 0,15 giây trên máy thử, chưa gồm thời gian review người. Chưa benchmark 10×; nếu cần mở rộng, thử chỉ mục nearest-neighbor và đo lại recall/runtime. |
| **Tại sao không Deploy?** | Bỏ sót 74/80 lỗi nhầm lớp, chỉ đo lỗi mô phỏng, chưa có defects/minute hoặc kiểm chứng trên nhãn thật. Cần sửa và pilot có người duyệt. |

## Sau phần Q&A và peer voting

Sau 5 phút trình bày, lớp có 10 phút hỏi đáp và 5 phút chấm chéo. Nhóm chỉ trả lời câu hỏi bằng bằng chứng hoặc thừa nhận giới hạn; không cần thêm slide. Điểm nhóm là median các phiếu rubric nhận được; Best Solution Vote là phiếu riêng. Kết quả bonus và winner phụ thuộc quy tắc lớp, không nên đưa dự đoán điểm lên slide.
