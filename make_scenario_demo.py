"""Build an offline demo that compares both queues on fresh simulated scenarios."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from experiment import CLASS_NAMES, image_features, neighbor_probabilities, read_idx, split_train_indices
from experiment import evaluate_top_k, inject_noise, rank_suspicion
from make_demo_page import thumbnail_data


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "artifacts"


def scenario_record(
    reference_labels: np.ndarray,
    probabilities: np.ndarray,
    noise_seed: int,
    random_seed: int,
    budget_fraction: float = 0.05,
) -> dict:
    """Re-rank after changing only the simulated current labels."""
    reference_labels = np.asarray(reference_labels)
    probabilities = np.asarray(probabilities)
    if probabilities.shape != (len(reference_labels), 10):
        raise ValueError("Expected one 10-class probability row per evaluation image")
    noisy, error_type, _ = inject_noise(reference_labels, noise_seed)
    budget = int(np.ceil(len(noisy) * budget_fraction))
    scores = 1 - probabilities[np.arange(len(noisy)), noisy]
    model_rows = rank_suspicion(scores)[:budget]
    random_rows = np.random.default_rng(random_seed).permutation(len(noisy))[:budget]
    return {
        "noise_seed": noise_seed,
        "random_seed": random_seed,
        "current_labels": noisy.tolist(),
        "error_types": error_type.tolist(),
        "model_rows": model_rows.tolist(),
        "random_rows": random_rows.tolist(),
        "model_metrics": evaluate_top_k(model_rows, error_type, budget),
        "random_metrics": evaluate_top_k(random_rows, error_type, budget),
    }


def replace_required(source: str, old: str, new: str) -> str:
    if old not in source:
        raise ValueError(f"Demo template is missing: {old[:70]}")
    return source.replace(old, new, 1)


def build(output_dir: Path = DEFAULT_OUTPUT, extra_scenarios: int = 30) -> Path:
    """Create a standalone HTML demo with 1 official and 30 fixed-seed explorations."""
    if extra_scenarios < 1:
        raise ValueError("extra_scenarios must be positive")
    target = output_dir / "demo_scenarios.html"
    summary_target = output_dir / "scenario_results.json"
    if target.exists():
        raise FileExistsError(f"Scenario demo already exists: {target}")
    if summary_target.exists():
        raise FileExistsError(f"Scenario result summary already exists: {summary_target}")
    results = json.loads((output_dir / "results.json").read_text(encoding="utf-8"))
    protocol = results["protocol"]
    train_images = read_idx(ROOT / "data/raw/train-images-idx3-ubyte.gz")
    train_labels = read_idx(ROOT / "data/raw/train-labels-idx1-ubyte.gz")
    dev_ids, eval_ids = split_train_indices(train_labels, protocol["split_seed"])
    reference = train_labels[eval_ids]
    noisy_dev, _, _ = inject_noise(train_labels[dev_ids], protocol["development_noise_seed"])
    probabilities = neighbor_probabilities(
        image_features(train_images[dev_ids]), noisy_dev, image_features(train_images[eval_ids])
    )
    if not np.all(np.isfinite(probabilities)):
        raise ValueError("Neighbor probabilities contain a non-finite value")
    official = scenario_record(reference, probabilities, protocol["evaluation_noise_seed"], 1000)
    if official["model_metrics"]["errors_found"] != results["model"]["errors_found"]:
        raise ValueError("Official scenario no longer matches results.json")
    with (output_dir / "review_queue.csv").open(newline="", encoding="utf-8") as handle:
        official_queue = [int(row["source_image_id"]) for row in csv.DictReader(handle)]
    if [int(eval_ids[row]) for row in official["model_rows"]] != official_queue:
        raise ValueError("Official scenario no longer matches review_queue.csv")

    scenarios = [official] + [
        scenario_record(reference, probabilities, noise_seed=2000 + offset, random_seed=5000 + offset)
        for offset in range(extra_scenarios)
    ]
    payload = {
        "pool": [
            {"image_id": int(source_id), "image": thumbnail_data(train_images[source_id]), "reference": int(reference[row])}
            for row, source_id in enumerate(eval_ids)
        ],
        "class_names": CLASS_NAMES,
        "scenarios": scenarios,
        "official_random_mean": results["random_baseline"]["mean_errors_found"],
        "budget": protocol["review_budget_count"],
    }

    template = (output_dir / "demo.html").read_text(encoding="utf-8")
    prefix, open_script, remainder = template.partition("<script>")
    _, close_script, suffix = remainder.partition("</script>")
    if not open_script or not close_script:
        raise ValueError("Expected one inline script in the existing demo")
    prefix = replace_required(
        prefix,
        "so sánh danh sách do mô hình xếp hạng với một lần chọn ngẫu nhiên. Nhấn “Hiện đáp án” để xem lỗi thật sau khi đã chốt thứ tự.",
        "mỗi kịch bản tạo lại lỗi mô phỏng và tính lại cả hàng chờ của nhóm lẫn random. Kịch bản gốc vẫn là kết quả báo cáo chính.",
    )
    prefix = replace_required(
        prefix,
        '<div class="controls"><button id="modelBtn" class="active">Xếp hạng của nhóm</button><button id="randomBtn">Random · seed 1000</button>',
        '<div class="scenario-bar"><button id="nextBtn">Tạo kịch bản khác</button><strong id="scenarioLabel" aria-live="polite"></strong></div><div class="controls"><button id="modelBtn" class="active" aria-pressed="true">Xếp hạng của nhóm</button><button id="randomBtn" aria-pressed="false">Random cùng kịch bản</button>',
    )
    prefix = replace_required(
        prefix,
        '<p class="note" id="note"></p><div class="grid" id="grid"></div>',
        '<p class="comparison" id="comparison" aria-live="polite"></p><p class="note" id="note"></p><div class="grid" id="grid"></div>',
    )
    prefix = replace_required(
        prefix,
        "</style>",
        ".scenario-bar{display:flex;align-items:center;flex-wrap:wrap;gap:14px;margin:0 0 18px;padding:15px;background:#e9f2fb;border:1px solid #c6d7e9;border-radius:9px}.scenario-bar strong{font-size:15px}.comparison{font-weight:700;color:#123d6a;margin:0 0 12px}.note{max-width:900px}</style>",
    )
    script = r"""
const DATA=__PAYLOAD__;
let scenarioIndex=0;
let selected='model';
const names={0:'Nhãn đúng',1:'Lỗi rải rác',2:'Lỗi nhầm lớp',3:'Lỗi theo lô'};

function render(){
  const scenario=DATA.scenarios[scenarioIndex];
  const rows=selected==='model'?scenario.model_rows:scenario.random_rows;
  const metrics=selected==='model'?scenario.model_metrics:scenario.random_metrics;
  const show=document.getElementById('reveal').checked;
  document.getElementById('scenarioLabel').textContent=scenarioIndex===0
    ? 'Kịch bản chính · seed lỗi '+scenario.noise_seed
    : 'Kịch bản thử '+scenarioIndex+'/'+(DATA.scenarios.length-1)+' · seed lỗi '+scenario.noise_seed;
  document.getElementById('found').textContent=metrics.errors_found+' / '+metrics.total_errors;
  document.getElementById('recall').textContent=(100*metrics.error_recall).toFixed(1)+'%';
  document.getElementById('precision').textContent=(100*metrics.precision).toFixed(1)+'%';
  document.getElementById('comparison').textContent='Cùng 100 lượt review: nhóm '+scenario.model_metrics.errors_found
    +' lỗi · random '+scenario.random_metrics.errors_found+' lỗi.';
  document.getElementById('note').textContent=scenarioIndex===0
    ? 'Mốc báo cáo chính: nhóm 78 lỗi; random trung bình '+DATA.official_random_mean.toFixed(2)
      +' lỗi qua 100 seed. Random đang hiển thị chỉ là seed '+scenario.random_seed+'.'
    : 'Kịch bản minh họa bổ sung: giữ nguyên 2.000 ảnh và thuật toán, tạo 200 lỗi mô phỏng khác. '
      +'Seed random '+scenario.random_seed+'. Báo cáo đầy đủ mọi kịch bản, không chọn lượt đẹp để thay số chính.';
  for(const id of ['modelBtn','randomBtn']){
    const active=(id==='modelBtn')===(selected==='model');
    const button=document.getElementById(id);
    button.classList.toggle('active',active);
    button.setAttribute('aria-pressed',String(active));
  }
  const grid=document.getElementById('grid');grid.replaceChildren();
  rows.forEach((row,index)=>{
    const item=DATA.pool[row],kind=scenario.error_types[row];
    const card=document.createElement('article');
    card.className='card'+(show?(kind===0?' clean':' error'):'');
    const heading=document.createElement('div');heading.className='rank';
    heading.textContent='#'+(index+1)+' · ảnh '+item.image_id;
    const image=document.createElement('img');image.src=item.image;image.alt='Ảnh sản phẩm '+item.image_id;
    const current=document.createElement('p');
    current.textContent='Nhãn hiện tại: '+DATA.class_names[scenario.current_labels[row]];
    card.append(heading,image,current);
    if(show){
      const truth=document.createElement('p');truth.className='truth';
      truth.textContent='Nhãn tham chiếu: '+DATA.class_names[item.reference];
      const type=document.createElement('p');type.className='type';type.textContent=names[kind];
      card.append(truth,type);
    }
    grid.append(card);
  });
}
document.getElementById('nextBtn').onclick=()=>{
  scenarioIndex=(scenarioIndex+1)%DATA.scenarios.length;
  selected='model';render();
};
document.getElementById('modelBtn').onclick=()=>{selected='model';render()};
document.getElementById('randomBtn').onclick=()=>{selected='random';render()};
document.getElementById('reveal').onchange=render;
render();
"""
    target.write_text(
        prefix + "<script>" + script.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        + "</script>" + suffix,
        encoding="utf-8",
    )
    summary_target.write_text(json.dumps({
        "purpose": "Exploratory offline demo only; official reported metrics remain in results.json.",
        "evaluation_images_reused": len(eval_ids),
        "model_unchanged": "15-nearest-neighbor label disagreement (14x14 pixels)",
        "scenarios": [
            {
                "kind": "official" if index == 0 else "exploratory",
                "noise_seed": item["noise_seed"],
                "random_seed": item["random_seed"],
                "model": item["model_metrics"],
                "random": item["random_metrics"],
            }
            for index, item in enumerate(scenarios)
        ],
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--extra-scenarios", type=int, default=30)
    args = parser.parse_args()
    print(build(args.output_dir, args.extra_scenarios))
