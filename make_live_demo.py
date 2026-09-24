"""Add a fresh-random-draw button to a self-contained C1 offline demo."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from experiment import CLASS_NAMES, ERROR_NAMES, inject_noise, read_idx, split_train_indices
from make_demo_page import thumbnail_data


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "artifacts"


def build(output_dir: Path = DEFAULT_OUTPUT) -> Path:
    source = output_dir / "demo.html"
    target = output_dir / "demo_live.html"
    if target.exists():
        raise FileExistsError(f"Interactive demo already exists: {target}")
    result = json.loads((output_dir / "results.json").read_text(encoding="utf-8"))
    html = source.read_text(encoding="utf-8")
    prefix, separator, remainder = html.partition("<script>")
    _, closing, suffix = remainder.partition("</script>")
    if not separator or not closing:
        raise ValueError("The source demo does not contain the expected script block")

    train_images = read_idx(ROOT / "data" / "raw" / "train-images-idx3-ubyte.gz")
    train_labels = read_idx(ROOT / "data" / "raw" / "train-labels-idx1-ubyte.gz")
    _, eval_ids = split_train_indices(train_labels, result["protocol"]["split_seed"])
    noisy, error_type, _ = inject_noise(train_labels[eval_ids], result["protocol"]["evaluation_noise_seed"])
    source_to_row = {int(source_id): row for row, source_id in enumerate(eval_ids)}
    with (output_dir / "review_queue.csv").open(newline="", encoding="utf-8") as handle:
        model_rows = [source_to_row[int(record["source_image_id"])] for record in csv.DictReader(handle)]
    budget = result["protocol"]["review_budget_count"]
    if len(model_rows) != budget or len(set(model_rows)) != budget:
        raise ValueError("Review queue does not contain exactly the budgeted unique items")

    pool = [
        {
            "image_id": int(source_id),
            "image": thumbnail_data(train_images[source_id]),
            "current": CLASS_NAMES[int(noisy[row])],
            "reference": CLASS_NAMES[int(train_labels[source_id])],
            "error_type": ERROR_NAMES.get(int(error_type[row]), "none"),
        }
        for row, source_id in enumerate(eval_ids)
    ]
    if sum(item["error_type"] != "none" for item in pool) != result["model"]["total_errors"]:
        raise ValueError("Demo ground truth does not match measured result")
    payload = {
        "pool": pool,
        "model_rows": model_rows,
        "model_metrics": result["model"],
        "random_mean": result["random_baseline"]["mean_errors_found"],
        "budget": budget,
        "total_errors": result["model"]["total_errors"],
    }
    prefix = prefix.replace("Random · seed 1000</button>", "Bốc random mới</button>")
    prefix = prefix.replace(
        "Bấm “Hiện đáp án” để xem lỗi thật sau khi đã chốt thứ tự.",
        "Bấm “Bốc random mới” để thử một danh sách khác; số liệu baseline trên slide vẫn giữ cố định.",
    )
    script = r"""
const DATA=__PAYLOAD__;
let selected='model';
let randomRows=[];
let drawNumber=0;
let previousSignature='';

function drawRandom(){
  const n=DATA.pool.length;
  let selectedRows=[];
  let signature='';
  // Prevent an identical queue on consecutive clicks. This never checks the answer.
  do {
    const rows=Array.from({length:n},(_,i)=>i);
    for(let i=0;i<DATA.budget;i++){
      const j=i+Math.floor(Math.random()*(n-i));
      [rows[i],rows[j]]=[rows[j],rows[i]];
    }
    selectedRows=rows.slice(0,DATA.budget);
    signature=selectedRows.join(',');
  } while(signature===previousSignature);
  previousSignature=signature;
  randomRows=selectedRows;
  drawNumber++;
}

function currentRows(){return selected==='model'?DATA.model_rows:randomRows}

function render(){
  const rows=currentRows();
  const show=document.getElementById('reveal').checked;
  const found=selected==='model' ? DATA.model_metrics.errors_found
    : rows.reduce((count,row)=>count+(DATA.pool[row].error_type!=='none'),0);
  document.getElementById('found').textContent=found+' / '+DATA.total_errors;
  document.getElementById('recall').textContent=(100*found/DATA.total_errors).toFixed(1)+'%';
  document.getElementById('precision').textContent=(100*found/DATA.budget).toFixed(1)+'%';
  document.getElementById('note').textContent=selected==='model'
    ? 'Danh sách của nhóm giữ cố định. Random baseline chính: trung bình '+DATA.random_mean.toFixed(2)+' lỗi qua 100 seed.'
    : 'Lượt bốc #'+drawNumber+' · 100 ảnh được chọn mới. Hai lượt có thể trùng số lỗi dù ảnh khác nhau. Baseline trên slide vẫn là trung bình 100 seed cố định.';
  document.getElementById('modelBtn').classList.toggle('active',selected==='model');
  document.getElementById('randomBtn').classList.toggle('active',selected==='random');
  const grid=document.getElementById('grid');grid.replaceChildren();
  rows.forEach((row,index)=>{
    const item=DATA.pool[row];
    const card=document.createElement('article');
    card.className='card'+(show?(item.error_type==='none'?' clean':' error'):'');
    const heading=document.createElement('div');heading.className='rank';
    heading.textContent='#'+(index+1)+' · ảnh '+item.image_id;
    const image=document.createElement('img');image.src=item.image;image.alt='Ảnh sản phẩm '+item.image_id;
    const current=document.createElement('p');current.textContent='Nhãn hiện tại: '+item.current;
    card.append(heading,image,current);
    if(show){
      const truth=document.createElement('p');truth.className='truth';truth.textContent='Nhãn tham chiếu: '+item.reference;
      const type=document.createElement('p');type.className='type';
      type.textContent=item.error_type==='none'?'Nhãn đúng':'Lỗi: '+item.error_type;
      card.append(truth,type);
    }
    grid.append(card);
  });
}

document.getElementById('modelBtn').onclick=()=>{selected='model';render()};
document.getElementById('randomBtn').onclick=()=>{drawRandom();selected='random';render()};
document.getElementById('reveal').onchange=render;
render();
"""
    target.write_text(prefix + "<script>" + script.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False)) + "</script>" + suffix, encoding="utf-8")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    print(build(parser.parse_args().output_dir))
