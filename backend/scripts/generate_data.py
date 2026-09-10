import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.synthetic_data import generate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic synthetic RailOpt AI data.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/synthetic/synthetic_dataset.json"))
    args = parser.parse_args()

    dataset = generate_dataset(args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generated synthetic dataset with seed {args.seed}: {args.output}")
    for name in ("assets", "maintenance_tasks", "trains", "block_windows", "goods_forecasts", "resources"):
        print(f"  {name}: {len(dataset[name])}")


if __name__ == "__main__":
    main()
