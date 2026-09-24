"""Create a self-contained, offline HTML review-queue demo from measured results."""

from __future__ import annotations

import argparse
import base64
import csv
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image

from experiment import CLASS_NAMES, ERROR_NAMES, evaluate_top_k, inject_noise, read_idx, split_train_indices


ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"


def thumbnail_data(image: np.ndarray) -> str:
    thumb = Image.fromarray(image, mode="L").resize((112, 112), Image.Resampling.NEAREST)
    stream = io.BytesIO()
    thumb.save(stream, format="PNG")
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode("ascii")


def build(output_dir: Path = ARTIFACTS) -> Path:
    output = output_dir / "demo.html"
    if output.exists():
        raise FileExistsError(f"Choose a new --output-dir; {output} already exists")
    result = json.loads((output_dir / "results.json").read_text(encoding="utf-8"))
    train_images = read_idx(ROOT / "data" / "raw" / "train-images-idx3-ubyte.gz")
    train_labels = read_idx(ROOT / "data" / "raw" / "train-labels-idx1-ubyte.gz")
    _, eval_ids = split_train_indices(train_labels, result["protocol"]["split_seed"])
    noisy, error_type, _ = inject_noise(train_labels[eval_ids], result["protocol"]["evaluation_noise_seed"])
    budget = result["protocol"]["review_budget_count"]
    with (output_dir / "review_queue.csv").open(newline="", encoding="utf-8") as handle:
        model_source_ids = [int(row["source_image_id"]) for row in csv.DictReader(handle)]
    source_to_row = {int(source_id): row for row, source_id in enumerate(eval_ids)}
    model_rows = np.asarray([source_to_row[source_id] for source_id in model_source_ids])
    random_rows = np.random.default_rng(1000).permutation(len(eval_ids))[:budget]
    random_result = evaluate_top_k(random_rows, error_type, budget)

    def records(rows: np.ndarray) -> list[dict]:
        return [
            {
                "rank": rank,
                "image_id": int(eval_ids[row]),
                "image": thumbnail_data(train_images[eval_ids[row]]),
                "current": CLASS_NAMES[int(noisy[row])],
                "reference": CLASS_NAMES[int(train_labels[eval_ids[row]])],
                "error_type": ERROR_NAMES.get(int(error_type[row]), "none"),
            }
            for rank, row in enumerate(rows, start=1)
        ]

    payload = {
        "model": {"name": "Xếp hạng của nhóm", "metrics": result["model"], "records": records(model_rows)},
        "random": {"name": "Random · seed 1000", "metrics": random_result, "records": records(random_rows)},
        "random_mean": result["random_baseline"]["mean_errors_found"],
        "total_errors": result["model"]["total_errors"],
        "budget": budget,
    }
    html = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>C1 · Hàng chờ review nhãn</title>
<style>
  :root{font-family:Arial,Helvetica,sans-serif;color:#183153;background:#f4f7fb}
  *{box-sizing:border-box} body{margin:0} header{background:#13355c;color:white;padding:30px max(24px,calc((100vw - 1180px)/2))}
  header h1{font-size:33px;margin:0 0 7px} header p{font-size:17px;line-height:1.5;max-width:850px;margin:0;color:#d8e8f8}
  main{max-width:1180px;margin:0 auto;padding:28px 24px 50px} .lead{font-size:19px;margin:0 0 20px;line-height:1.45}
  .controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:22px}
  button{font:inherit;cursor:pointer;border:2px solid #1d5f9e;border-radius:8px;padding:10px 15px;background:white;color:#174675;font-weight:700}
  button.active,button:hover{background:#1d5f9e;color:white} .spacer{flex:1} .check{display:flex;align-items:center;gap:7px;font-weight:700}
  .stats{display:flex;gap:28px;flex-wrap:wrap;border-top:2px solid #c6d7e9;border-bottom:2px solid #c6d7e9;padding:18px 0;margin-bottom:19px}
  .stat strong{display:block;font-size:32px;color:#123d6a}.stat span{display:block;font-size:14px;color:#45617e}
  .note{font-size:14px;color:#45617e;margin:0 0 20px;line-height:1.4}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(165px,1fr));gap:13px}
  .card{background:white;border:1px solid #cddbed;border-radius:10px;padding:13px;min-height:252px}
  .card.error{border-color:#b83b35;background:#fff9f7}.card.clean{border-color:#4c8a6c}
  .rank{font-size:13px;font-weight:700;color:#54708e;margin-bottom:5px}.card img{width:112px;height:112px;display:block;margin:0 auto 10px;image-rendering:pixelated}
  .card p{font-size:13px;line-height:1.35;margin:4px 0;overflow-wrap:anywhere}.truth{padding-top:6px;border-top:1px solid #dde6f0;margin-top:7px!important}
  .type{font-weight:700;color:#a32925}.clean .type{color:#286f48}
  footer{margin-top:30px;font-size:13px;color:#5b7089;line-height:1.45}
  @media(max-width:600px){header h1{font-size:26px}.stats{gap:16px}.stat strong{font-size:27px}}
</style>
</head>
<body>
<header><h1>C1 · Chọn 5% ảnh để review</h1><p>Demo offline từ Fashion-MNIST: so sánh danh sách do mô hình xếp hạng với một lần chọn ngẫu nhiên. Nhấn “Hiện đáp án” để xem lỗi thật sau khi đã chốt thứ tự.</p></header>
<main>
  <p class="lead">Cùng ngân sách <strong>100 / 2.000 ảnh</strong>. Danh sách nào đưa được nhiều nhãn sai thật đến người review hơn?</p>
  <div class="controls"><button id="modelBtn" class="active">Xếp hạng của nhóm</button><button id="randomBtn">Random · seed 1000</button><span class="spacer"></span><label class="check"><input id="reveal" type="checkbox"> Hiện đáp án</label></div>
  <div class="stats"><div class="stat"><strong id="found">–</strong><span>lỗi thật trong 100 ảnh</span></div><div class="stat"><strong id="recall">–</strong><span>Error Recall@5%</span></div><div class="stat"><strong id="precision">–</strong><span>Precision@5%</span></div></div>
  <p class="note" id="note"></p><div class="grid" id="grid"></div>
  <footer>Đáp án là nhãn gốc của Fashion-MNIST và danh sách lỗi được tiêm có kiểm soát. Đây là kết quả của bài thử mô phỏng; chưa đo thời gian human review hoặc hiệu quả trên nhãn sai tự nhiên.</footer>
</main>
<script>
const DATA=__PAYLOAD__;
let selected='model';
function render(){
 const method=DATA[selected], show=document.getElementById('reveal').checked, metrics=method.metrics;
 document.getElementById('found').textContent=metrics.errors_found+' / '+DATA.total_errors;
 document.getElementById('recall').textContent=(100*metrics.error_recall).toFixed(1)+'%';
 document.getElementById('precision').textContent=(100*metrics.precision).toFixed(1)+'%';
 document.getElementById('note').textContent=selected==='model'
  ? 'Danh sách đã khóa trước khi đối chiếu đáp án. Random 100 seed tìm trung bình '+DATA.random_mean.toFixed(2)+' lỗi / 100 ảnh.'
  : 'Đây là một seed ngẫu nhiên để xem danh sách ảnh; bảng báo cáo dùng trung bình của 100 seed.';
 document.getElementById('modelBtn').classList.toggle('active',selected==='model');
 document.getElementById('randomBtn').classList.toggle('active',selected==='random');
 const grid=document.getElementById('grid');grid.replaceChildren();
 for(const item of method.records){
  const card=document.createElement('article');card.className='card'+(show?(item.error_type==='none'?' clean':' error'):'');
  const heading=document.createElement('div');heading.className='rank';heading.textContent='#'+item.rank+' · ảnh '+item.image_id;
  const image=document.createElement('img');image.src=item.image;image.alt='Ảnh sản phẩm '+item.image_id;
  const current=document.createElement('p');current.textContent='Nhãn hiện tại: '+item.current;
  card.append(heading,image,current);
  if(show){const truth=document.createElement('p');truth.className='truth';truth.textContent='Nhãn tham chiếu: '+item.reference;
   const type=document.createElement('p');type.className='type';type.textContent=item.error_type==='none'?'Nhãn đúng':'Lỗi: '+item.error_type;
   card.append(truth,type)}
  grid.append(card)
 }
}
document.getElementById('modelBtn').onclick=()=>{selected='model';render()};
document.getElementById('randomBtn').onclick=()=>{selected='random';render()};
document.getElementById('reveal').onchange=render;
render();
</script></body></html>"""
    output.write_text(html.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False)), encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ARTIFACTS, help="Directory with results.json and review_queue.csv")
    print(build(parser.parse_args().output_dir))
