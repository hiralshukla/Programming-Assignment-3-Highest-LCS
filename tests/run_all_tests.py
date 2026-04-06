from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import time


def test_index(path: Path) -> int:
    return int(path.stem.replace("test", ""))


def should_generate_graph(argv: list[str]) -> bool:
    return "--graph" in argv


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "data"
    solver = repo_root / "src" / "hvlcs.py"
    graph_script = repo_root / "tests" / "graph.py"
    generate_graph = should_generate_graph(argv)

    test_inputs = sorted(data_dir.glob("test*.in"), key=test_index)
    if not test_inputs:
        print("No test*.in files found in data/.")
        return 1

    print(f"Running {len(test_inputs)} test files...\n")

    failures = 0
    for test_input in test_inputs:
        out_name = f"{test_input.stem}.out"

        start = time.perf_counter()
        result = subprocess.run(
            [sys.executable, str(solver), test_input.name, out_name],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        if result.returncode != 0:
            failures += 1
            print(f"{test_input.name}: FAIL ({elapsed_ms:.2f} ms)")
            if result.stdout.strip():
                print(result.stdout.strip())
            if result.stderr.strip():
                print(result.stderr.strip())
            continue

        out_path = data_dir / out_name
        first_line = ""
        if out_path.exists():
            with out_path.open("r", encoding="utf-8") as f:
                first_line = f.readline().strip()

        print(f"{test_input.name}: OK ({elapsed_ms:.2f} ms) score={first_line}")

    print()
    if failures:
        print(f"Completed with {failures} failure(s).")
        return 1

    print("All tests completed successfully.")

    if generate_graph:
        print("\nGenerating runtime graph...")
        graph_result = subprocess.run(
            [sys.executable, str(graph_script)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if graph_result.returncode != 0:
            print("Graph generation failed.")
            if graph_result.stdout.strip():
                print(graph_result.stdout.strip())
            if graph_result.stderr.strip():
                print(graph_result.stderr.strip())
            return 1

        print("Graph generation completed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))