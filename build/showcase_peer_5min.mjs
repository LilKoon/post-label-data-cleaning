import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "/Users/lilkoon/Documents/ChatGPT/Post-label Data Cleaning";
const skillDir = "/Users/lilkoon/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
const pythonExecutable = "/Users/lilkoon/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";
const finalPath = path.join(workspaceDir, "artifacts", "C1_Peer_Showcase_5min.pptx");
const buildDir = path.join(workspaceDir, "build");
const revision = process.env.DECK_REVISION ?? "peer-v1";
const { finalizePresentation, applyPresentationChartFont } = await import(
  pathToFileURL(path.join(skillDir, "container_tools", "artifact_tool_utils.mjs")).href
);

const data = JSON.parse(await fs.readFile(path.join(workspaceDir, "artifacts", "results.json"), "utf8"));
const model = data.model;
const base = data.random_baseline;
const pct = x => (100 * x).toFixed(2).replace(/\.00$/, "").replace(".", ",") + "%";
const C = {
  navy: "#173A63", blue: "#1E65A5", cyan: "#3D8CC4", pale: "#E8F1FA",
  paper: "#FAFCFE", ink: "#183153", muted: "#516B84", line: "#B8D0E5",
  red: "#B83336", warm: "#FFF4EC", green: "#2F7955", white: "#FFFFFF",
};
const font = "Arial";
const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });

function addText(slide, text, x, y, w, h, size=24, color=C.ink, bold=false, align="left") {
  const shape = slide.shapes.add({
    geometry: "textbox", position: {left:x,top:y,width:w,height:h}, fill:"none",
    line:{fill:"none",width:0},
  });
  shape.text = text;
  shape.text.style = {
    typeface:font, fontSize:size, bold, color, alignment:align,
    verticalAlignment:"middle", autoFit:"none", wrap:"square",
    insets:{left:0,right:0,top:0,bottom:0},
  };
  return shape;
}
function rule(slide,x,y,w,color=C.line,h=2){
  slide.shapes.add({geometry:"rect",position:{left:x,top:y,width:w,height:h},fill:color,line:{fill:"none",width:0}});
}
function baseSlide(number,title){
  const slide=deck.slides.add();slide.background.fill=C.paper;
  addText(slide,`C1  /  ${["PAIN","BASELINE","SOLUTION","EVIDENCE","DECISION"][number-1]}`,70,30,470,28,16,C.blue,true);
  addText(slide,title,70,72,1130,76,42,C.navy,true);
  rule(slide,70,160,1140,C.line,2);
  addText(slide,String(number).padStart(2,"0")+" / 05",1110,667,100,24,16,C.muted,false,"right");
  return slide;
}
async function dataImage(slide,filename,x,y,w,h,alt){
  slide.images.add({blob:new Uint8Array(await fs.readFile(path.join(buildDir,filename))),contentType:"image/png",alt,fit:"contain",position:{left:x,top:y,width:w,height:h}});
}

// 1 — Pain
{
  const slide=baseSlide(1,"Chỉ đủ thời gian xem lại 5% ảnh");
  addText(slide,"Lô ảnh sản phẩm đã được gán nhãn; lỗi nhãn có thể làm mô hình học sai.",70,192,1060,72,29,C.ink);
  addText(slide,"Câu hỏi production",70,292,400,34,18,C.blue,true);
  addText(slide,"Nên đưa 100 ảnh nào cho người kiểm tra để tìm nhiều nhãn sai nhất?",70,336,880,104,34,C.navy,true);
  rule(slide,70,500,1130,C.line,2);
  addText(slide,"2.000 ảnh",70,530,260,72,37,C.navy,true);
  addText(slide,"200 lỗi mô phỏng",392,530,360,72,37,C.red,true);
  addText(slide,"100 lượt review",825,530,380,72,37,C.blue,true);
  addText(slide,"Fashion-MNIST · giả thuyết: nhãn lệch với ảnh gần giống dễ sai",70,614,1110,31,18,C.muted);
  slide.speakerNotes.textFrame.setText("0:00–0:45. Pain point: đội gán nhãn xong một lô ảnh, nhưng chỉ đủ ngân sách kiểm tra 5%. Cần chọn 100/2.000 ảnh để phát hiện nhiều lỗi nhãn thật nhất. Lỗi ảnh hưởng đội huấn luyện và đánh giá mô hình. Benchmark dùng Fashion-MNIST với 200 lỗi tiêm có kiểm soát, không phải tỷ lệ lỗi vendor thật. Giả thuyết: ảnh có nhãn lệch với các ảnh gần giống sẽ đáng kiểm tra hơn. Nguồn dữ liệu: https://github.com/zalandoresearch/fashion-mnist");
}

// 2 — Baseline
{
  const slide=baseSlide(2,"Baseline: chọn 100 ảnh ngẫu nhiên");
  addText(slide,"Cùng 5% ngân sách, chọn ngẫu nhiên là cách dễ nhất để kiểm tra lại dữ liệu.",70,193,1080,67,28,C.ink);
  addText(slide,base.mean_errors_found.toFixed(2).replace(".",","),70,286,440,148,104,C.navy,true);
  addText(slide,"lỗi thật / 100 ảnh",72,421,510,49,31,C.ink);
  rule(slide,653,282,2,C.line,180);
  addText(slide,pct(base.mean_error_recall),704,300,460,125,76,C.blue,true);
  addText(slide,"Error Recall@5%",707,422,450,47,29,C.ink);
  rule(slide,70,530,1130,C.line,2);
  addText(slide,"100 random seed (1000–1099)",70,554,460,42,23,C.muted);
  addText(slide,`Dao động: ${base.min_errors_found}–${base.max_errors_found} lỗi`,567,554,600,42,23,C.muted);
  addText(slide,"Cùng 2.000 ảnh evaluation và 100 lượt review; không chọn một seed đẹp.",70,612,1080,35,20,C.muted);
  slide.speakerNotes.textFrame.setText("0:45–1:35. Baseline bắt buộc là random sampling. Cả random và phương pháp nhóm đều chỉ được chọn 100 ảnh trên đúng 2.000 ảnh evaluation. Random chạy 100 seed chốt trước, từ 1000 đến 1099: trung bình 9,64 lỗi; Error Recall@5% = 9,64/200 = 4,82%. Từng lượt dao động 4–17 lỗi. 9,64 là trung bình, không phải số của một lượt. Cách so sánh này tránh chọn seed xấu để làm baseline.");
}

// 3 — Solution
{
  const slide=baseSlide(3,"Solution: ảnh nào có nhãn đáng nghi?");
  addText(slide,"8.000 ảnh development",70,198,340,36,24,C.navy,true);
  addText(slide,"→",423,196,50,44,31,C.blue,true);
  addText(slide,"15 ảnh giống nhất",484,198,334,36,24,C.navy,true);
  addText(slide,"→",830,196,50,44,31,C.blue,true);
  addText(slide,"Xếp hạng top 100",890,198,320,36,24,C.navy,true);
  rule(slide,70,252,1130,C.line,2);
  addText(slide,"Mỗi ảnh được thu nhỏ thành 14×14 pixel. Các ảnh gần giống bỏ phiếu cho nhãn có khả năng đúng.",70,274,1090,69,27,C.ink);
  addText(slide,"Điểm đáng nghi = 1 − P(nhãn hiện tại | 15 ảnh gần nhất)",70,363,1120,62,30,C.blue,true);
  await dataImage(slide,"found_a.png",72,460,135,135,"Ví dụ ảnh Shirt bị gán T-shirt/top");
  addText(slide,"Ảnh #33007",232,469,225,32,20,C.muted,true);
  addText(slide,"Nhãn hiện tại: T-shirt/top",232,509,470,37,24,C.red,true);
  addText(slide,"Nhãn tham chiếu: Shirt",232,554,470,37,24,C.green,true);
  addText(slide,"Đáp án evaluation chỉ được mở sau khi top 100 đã được xếp xong.",72,622,1080,31,19,C.muted);
  slide.speakerNotes.textFrame.setText("1:35–2:45, gồm demo tối đa 25 giây. Nhóm dùng 8.000 ảnh development, thu ảnh 28×28 xuống 14×14, tìm 15 hàng xóm gần nhất và bỏ phiếu có trọng số. Với mỗi ảnh evaluation, điểm đáng nghi bằng 1 trừ mức ủng hộ nhãn hiện tại; sắp giảm dần và lấy top 100. Detector chỉ nhận ảnh và nhãn hiện tại, không nhận đáp án evaluation. Demo: mở artifacts/demo_scenarios.html, chỉ mốc chính 78 lỗi, bấm Tạo kịch bản khác một lần thấy seed 2000 và 72 lỗi; chọn Random cùng kịch bản thấy 10 lỗi. Đây là kịch bản mô phỏng bổ sung, không thay số đánh giá chính. Nguồn ảnh: https://github.com/zalandoresearch/fashion-mnist");
}

// 4 — Evidence
{
  const slide=baseSlide(4,"Evidence: 78 lỗi trong 100 ảnh được chọn");
  addText(slide,"39,0%",70,193,320,105,73,C.blue,true);
  addText(slide,"Recall@5% của nhóm",70,292,420,38,23,C.ink);
  addText(slide,"4,82%",503,193,333,105,73,C.muted,true);
  addText(slide,"Recall@5% random",503,292,380,38,23,C.ink);
  addText(slide,"8,1×",971,210,229,83,53,C.navy,true,"right");
  addText(slide,"recall",1015,292,186,34,20,C.muted,false,"right");
  rule(slide,70,349,1130,C.line,2);
  addText(slide,"Recall theo loại lỗi (%)",70,371,640,38,24,C.navy,true);
  const totals=model.total_by_type, found=model.found_by_type, random=base.mean_found_by_type;
  const categories=["Rải rác","Nhầm 2 lớp","Theo lô"];
  const keys=["random","systematic","batch"];
  const chart=slide.charts.add("bar",{
    position:{left:63,top:413,width:777,height:222},categories,
    series:[
      {name:"Random",values:keys.map(k=>100*random[k]/totals[k]),fill:C.line},
      {name:"Nhóm",values:keys.map(k=>100*found[k]/totals[k]),fill:C.blue},
    ],
    hasLegend:true,legend:{position:"bottom",textStyle:{typeface:font,fontSize:16}},
    barOptions:{direction:"bar",grouping:"clustered",gapWidth:70},
    xAxis:{min:0,max:70,majorUnit:20,textStyle:{typeface:font,fontSize:15}},
    yAxis:{textStyle:{typeface:font,fontSize:17}},
    chartFill:C.paper,plotAreaFill:C.paper,
  });
  applyPresentationChartFont(chart,{fontFamily:font});
  addText(slide,"Failure case",877,401,300,36,20,C.red,true);
  addText(slide,"Chỉ 6/80 lỗi Shirt → T-shirt/top được tìm thấy.",877,445,306,105,23,C.ink,true);
  addText(slide,"Stress: recall 52% khi lỗi 5%; 22,5% khi lỗi 20%.",877,562,306,82,18,C.muted);
  slide.speakerNotes.textFrame.setText("2:45–3:55. Sau khi khóa ranking, đối chiếu đáp án lỗi đã tiêm. Trong top 100 nhóm có 78 ảnh lỗi: Error Recall@5% = 78/200 = 39%, Precision@5% = 78/100 = 78%. Random 100 seed có recall trung bình 4,82%; nhóm cao khoảng 8,1 lần trên benchmark này. Theo loại: 49/80 rải rác, 6/80 Shirt→T-shirt/top, 23/40 theo lô. Kết quả 6/80 là failure case quan trọng. Stress test với 5% lỗi đạt recall 52%, với 20% đạt 22,5%; mẫu số khác nên không so tỷ lệ này như cùng một bài kiểm tra. 30 kịch bản demo thêm dùng lại ảnh evaluation, chỉ để minh họa, không phải test độc lập.");
}

// 5 — Decision
{
  const slide=baseSlide(5,"Decision: Rework trước khi triển khai thật");
  addText(slide,"REWORK",70,194,510,91,65,C.red,true);
  addText(slide,"Ranking vượt random, nhưng chưa đủ tin cậy cho lỗi có hệ thống.",70,289,1090,70,29,C.ink);
  rule(slide,70,386,1130,C.line,2);
  addText(slide,"Điểm mạnh",70,411,250,36,21,C.blue,true);
  addText(slide,"Hàng chờ top 100 chạy offline; tìm 78 lỗi trên bài thử.",70,457,500,76,24,C.ink);
  addText(slide,"Giới hạn",651,411,250,36,21,C.red,true);
  addText(slide,"Chỉ 6/80 lỗi nhầm lớp; dữ liệu là lỗi mô phỏng, chưa đo phút review.",651,457,535,104,24,C.ink);
  rule(slide,70,572,1130,C.line,2);
  addText(slide,"Bước tiếp: tín hiệu theo lô, nhãn thật được phân xử độc lập và phút review.",70,593,1130,64,24,C.navy,true);
  slide.speakerNotes.textFrame.setText("3:55–4:45. Quyết định: Rework. Hàng chờ của nhóm tốt hơn random trên mô phỏng, nhưng bỏ sót 74/80 lỗi nhầm Shirt→T-shirt/top. Ground truth dựa trên nhãn gốc Fashion-MNIST và lỗi tiêm; chưa đo thời gian người review, lỗi tự nhiên hay mô hình sau khi sửa nhãn. Bước tiếp: thêm tín hiệu theo người gán/lô, thử trên development mới, sau đó đánh giá trên một tập thật được hai người xem độc lập và phân xử; đo defects/minute. Không deploy tự động và không đổi ngưỡng sau khi xem đáp án. Dừng trước 5:00, để 15 giây dự phòng.");
}

for(let i=0;i<5;i++){
  const slide=deck.slides.getItem(i);
  const preview=await deck.export({slide,format:"png",scale:1});
  await fs.writeFile(path.join(buildDir,`slide-${revision}-${i+1}.png`),new Uint8Array(await preview.arrayBuffer()));
}
const stagingDir=path.join(workspaceDir,".codex-finalizer");
await fs.mkdir(stagingDir,{recursive:true});
const candidatePath=path.join(stagingDir,`candidate-${revision}.pptx`);
await (await PresentationFile.exportPptx(deck)).save(candidatePath);
const validation=await finalizePresentation({
  workspaceDir,candidatePath,finalPath,
  pythonExecutable,
  integrityValidatorPath:path.join(skillDir,"container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath:path.join(skillDir,"container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs:["--expected-slide-size-emu","12192000,6858000","--validate-bullet-geometry","--validate-heading-fit"],
  explicitTotalSlideCount:5,
  requiredNativeTableOwnerSlides:[],
  requiredNativeChartOwnerSlides:[4],
  materializeLiteralChartWorkbooks:true,
  fontPolicy:{basis:"design",families:[font]},
  verifyArtifactToolImport:true,
  receiptPath:path.join(stagingDir,"C1_Peer_Showcase_5min.validation.json"),
});
console.log(JSON.stringify({finalPath,validation},null,2));
