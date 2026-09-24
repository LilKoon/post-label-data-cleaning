import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "/Users/lilkoon/Documents/ChatGPT/Post-label Data Cleaning";
const skillDir = "/Users/lilkoon/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
const pythonExecutable = "/Users/lilkoon/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";
const finalPath = path.join(workspaceDir, "artifacts", "C1_Showcase.pptx");
const buildDir = path.join(workspaceDir, "build");
const revision = process.env.DECK_REVISION ?? "v3";
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
  addText(slide,"Benchmark Fashion-MNIST · 10% nhãn bị đổi có kiểm soát",70,614,1050,31,18,C.muted);
  slide.speakerNotes.textFrame.setText("Khoảng 50 giây. Pain point: vendor vừa gán nhãn một lô ảnh; chỉ đủ ngân sách kiểm tra 5%. Bài thử dùng 2.000 ảnh Fashion-MNIST, tiêm đúng 200 lỗi có kiểm soát. Người chịu hậu quả là đội ML dùng nhãn này để huấn luyện và đánh giá mô hình. 200 lỗi là setup benchmark, không phải tỷ lệ lỗi vendor thật. Nguồn: https://github.com/zalandoresearch/fashion-mnist");
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
  addText(slide,"Random không biết ảnh nào đáng nghi, nên phần lớn lượt xem lại không gặp lỗi.",70,612,1060,35,20,C.muted);
  slide.speakerNotes.textFrame.setText("Khoảng 50 giây. Baseline bắt buộc là random sampling cùng 100 ảnh trên đúng evaluation set. Chạy 100 seed cố định. Trung bình 9,64 lỗi, recall 4,82%; một lần chạy có thể dao động từ 4 đến 17. Nêu rõ đây là trung bình nhiều lần, không chọn seed đẹp.");
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
  addText(slide,"Demo offline: đổi giữa hàng chờ của nhóm và random, rồi hiện đáp án.",72,622,1080,31,19,C.muted);
  slide.speakerNotes.textFrame.setText("Khoảng 60 giây. Đây là prototype 15-nearest-neighbor: thu ảnh 28x28 thành 14x14, dùng các ảnh development có nhãn lỗi mô phỏng để bỏ phiếu. Ảnh evaluation hoàn toàn không tham gia huấn luyện. Score = 1 trừ xác suất của nhãn hiện tại. Sắp xếp giảm dần, chọn 100 ảnh. Cho demo HTML offline nếu có thời gian: chuyển giữa random và model, bật hiện đáp án. Nhãn tham chiếu chỉ xuất hiện sau khi thứ tự đã khóa. Nguồn ảnh: Fashion-MNIST, https://github.com/zalandoresearch/fashion-mnist");
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
  slide.speakerNotes.textFrame.setText("Khoảng 65 giây. Chỉ sau khi khóa ranking mới đối chiếu đáp án. 78/200 lỗi thật trong top 100, recall 39%, precision 78%. Random 100 seed trung bình 9,64/200, recall 4,82%; tỷ lệ khoảng 8,1 lần. Theo loại: 49/80 rải rác, 6/80 nhầm Shirt và T-shirt/top, 23/40 theo lô. Đây là failure case quan trọng. Stress test giữ cố định mô hình và ngân sách: 5% lỗi recall 52%, 20% lỗi recall 22,5%. Stress khác prevalence nên recall không so trực tiếp với kịch bản chính.");
}

// 5 — Decision
{
  const slide=baseSlide(5,"Decision: Rework trước khi triển khai thật");
  addText(slide,"REWORK",70,194,510,91,65,C.red,true);
  addText(slide,"Ranking vượt random, nhưng chưa đủ tin cậy cho lỗi có hệ thống.",70,289,1090,70,29,C.ink);
  rule(slide,70,386,1130,C.line,2);
  addText(slide,"Điểm mạnh",70,411,250,36,21,C.blue,true);
  addText(slide,"78 lỗi / 100 lượt review; random trung bình 9,64.",70,457,500,76,24,C.ink);
  addText(slide,"Giới hạn",651,411,250,36,21,C.red,true);
  addText(slide,"Chỉ 6/80 lỗi nhầm lớp; dữ liệu là lỗi mô phỏng, chưa đo phút review.",651,457,535,104,24,C.ink);
  rule(slide,70,572,1130,C.line,2);
  addText(slide,"Bước tiếp: thêm tín hiệu theo lớp/lô, rồi kiểm chứng trên một tập nhãn thật được phân xử độc lập.",70,593,1130,64,24,C.navy,true);
  slide.speakerNotes.textFrame.setText("Khoảng 55 giây. Quyết định là Rework. Tổng recall cao nhưng loại nhầm Shirt thành T-shirt chỉ được 6/80; đây là loại lỗi thực tế quan trọng. Ground truth trong benchmark dựa trên nhãn gốc Fashion-MNIST và lỗi tạo có kiểm soát. Chưa đo human review time, chưa thử lỗi tự nhiên hoặc downstream recovery. Bước tiếp là thêm tín hiệu class-aware hoặc batch metadata, kiểm tra trên development mới, sau đó đánh giá với tập thật được phân xử độc lập. Không đổi kết quả evaluation hiện tại.");
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
  receiptPath:path.join(stagingDir,"C1_Showcase.validation.json"),
});
console.log(JSON.stringify({finalPath,validation},null,2));
