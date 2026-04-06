from __future__ import annotations

import argparse
import csv
from pathlib import Path
import statistics
import sys
import time


def test_index(path: Path) -> int:
	return int(path.stem.replace("test", ""))


def parse_test_input(test_input: Path) -> tuple[dict[str, int], str, str]:
	with test_input.open("r", encoding="utf-8") as f:
		alphabet_size = int(f.readline().strip())
		alphabet: dict[str, int] = {}
		for _ in range(alphabet_size):
			letter, value = f.readline().split()
			alphabet[letter] = int(value)

		a = f.readline().rstrip("\n")
		b = f.readline().rstrip("\n")

	return alphabet, a, b


def compute_hvlcs_score(alphabet: dict[str, int], a: str, b: str) -> int:
	n = len(a)
	m = len(b)

	# DP table that mirrors the recurrence used in src/hvlcs.py.
	dp = [[0] * (m + 1) for _ in range(n + 1)]

	for i in range(1, n + 1):
		ai = a[i - 1]
		for j in range(1, m + 1):
			if ai == b[j - 1]:
				dp[i][j] = alphabet[ai] + dp[i - 1][j - 1]
			else:
				dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

	return dp[n][m]


def parse_lengths(test_input: Path) -> tuple[int, int]:
	_, a, b = parse_test_input(test_input)
	return len(a), len(b)


def run_solver_once_inprocess(test_input: Path) -> float:
	alphabet, a, b = parse_test_input(test_input)
	start = time.perf_counter()
	_ = compute_hvlcs_score(alphabet, a, b)
	elapsed_ms = (time.perf_counter() - start) * 1000

	return elapsed_ms


def run_tests(repo_root: Path, repeats: int) -> list[dict[str, float | int | str]]:
	data_dir = repo_root / "data"
	test_inputs = sorted(data_dir.glob("test*.in"), key=test_index)

	if not test_inputs:
		raise FileNotFoundError("No test*.in files found in data/.")
	if repeats < 1:
		raise ValueError("repeats must be at least 1")

	results: list[dict[str, float | int | str]] = []

	for test_input in test_inputs:
		len_a, len_b = parse_lengths(test_input)
		cell_count = len_a * len_b

		# Warmup run to reduce one-time effects (imports/cache) before timed samples.
		run_solver_once_inprocess(test_input)

		samples: list[float] = []
		for _ in range(repeats):
			samples.append(run_solver_once_inprocess(test_input))

		mean_ms = statistics.fmean(samples)
		std_ms = statistics.stdev(samples) if repeats > 1 else 0.0
		results.append(
			{
				"test": test_input.stem,
				"len_a": len_a,
				"len_b": len_b,
				"cell_count": cell_count,
				"runs": repeats,
				"mean_ms": mean_ms,
				"std_ms": std_ms,
				"min_ms": min(samples),
				"max_ms": max(samples),
			}
		)

	return results


def write_csv(results: list[dict[str, float | int | str]], output_csv: Path) -> None:
	with output_csv.open("w", newline="", encoding="utf-8") as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(
			[
				"test",
				"len_a",
				"len_b",
				"cell_count",
				"runs",
				"mean_ms",
				"std_ms",
				"min_ms",
				"max_ms",
			]
		)
		for row in results:
			writer.writerow(
				[
					row["test"],
					row["len_a"],
					row["len_b"],
					row["cell_count"],
					row["runs"],
					f"{float(row['mean_ms']):.4f}",
					f"{float(row['std_ms']):.4f}",
					f"{float(row['min_ms']):.4f}",
					f"{float(row['max_ms']):.4f}",
				]
			)


def linear_fit(x_vals: list[float], y_vals: list[float]) -> tuple[float, float]:
	if len(x_vals) != len(y_vals) or not x_vals:
		raise ValueError("x and y must be non-empty and same length")

	x_mean = statistics.fmean(x_vals)
	y_mean = statistics.fmean(y_vals)

	numerator = 0.0
	denominator = 0.0
	for x_val, y_val in zip(x_vals, y_vals):
		numerator += (x_val - x_mean) * (y_val - y_mean)
		denominator += (x_val - x_mean) ** 2

	if denominator == 0:
		return 0.0, y_mean

	slope = numerator / denominator
	intercept = y_mean - slope * x_mean
	return slope, intercept


def plot_results(
	results: list[dict[str, float | int | str]],
	output_by_test_png: Path,
	output_by_size_png: Path,
) -> None:
	try:
		import matplotlib.pyplot as plt
	except ImportError as exc:
		raise ImportError(
			"matplotlib is required to generate the graph. Install with: pip install matplotlib"
		) from exc

	test_names = [str(row["test"]) for row in results]
	means = [float(row["mean_ms"]) for row in results]
	stds = [float(row["std_ms"]) for row in results]
	sizes = [float(row["cell_count"]) for row in results]

	plt.figure(figsize=(10, 5.5))
	plt.errorbar(test_names, means, yerr=stds, marker="o", linewidth=2, capsize=4)
	plt.title("HVLCS Runtime by Test File (Mean +/- Std Dev)")
	plt.xlabel("Test File")
	plt.ylabel("Runtime (ms)")
	plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
	plt.tight_layout()
	plt.savefig(output_by_test_png, dpi=200)
	plt.close()

	slope, intercept = linear_fit(sizes, means)
	fit_x = sorted(sizes)
	fit_y = [slope * x_val + intercept for x_val in fit_x]

	plt.figure(figsize=(10, 5.5))
	plt.scatter(sizes, means, s=55, label="Measured mean runtime")
	plt.plot(fit_x, fit_y, linewidth=2, label="Linear fit")
	plt.title("HVLCS Runtime vs |A| x |B|")
	plt.xlabel("DP table cells (|A| x |B|)")
	plt.ylabel("Runtime (ms)")
	plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
	plt.legend()
	plt.tight_layout()
	plt.savefig(output_by_size_png, dpi=200)
	plt.close()


def parse_args(argv: list[str]) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Generate HVLCS runtime graphs.")
	parser.add_argument(
		"--repeats",
		type=int,
		default=10,
		help="Number of timed runs per test file (default: 10).",
	)
	return parser.parse_args(argv)


def main(argv: list[str]) -> int:
	args = parse_args(argv)
	repo_root = Path(__file__).resolve().parents[1]
	tests_dir = Path(__file__).resolve().parent
	output_csv = tests_dir / "runtime_results.csv"
	output_by_test_png = tests_dir / "runtime_graph.png"
	output_by_size_png = tests_dir / "runtime_vs_size.png"

	try:
		results = run_tests(repo_root, repeats=args.repeats)
		write_csv(results, output_csv)
		plot_results(results, output_by_test_png, output_by_size_png)
	except Exception as exc:
		print(f"Error: {exc}")
		return 1

	print("Runtime graphs generated.")
	print(f"CSV: {output_csv}")
	print(f"By test PNG: {output_by_test_png}")
	print(f"By size PNG: {output_by_size_png}")
	for row in results:
		print(
			f"{row['test']}: mean={float(row['mean_ms']):.2f} ms "
			f"std={float(row['std_ms']):.2f} ms "
			f"cells={row['cell_count']}"
		)

	return 0


if __name__ == "__main__":
	raise SystemExit(main(sys.argv[1:]))
