"""
gbext CLI main entry point.
Exposes interfaces for running all experimental suites.
"""

from pathlib import Path

import typer

from gbext.experiments import benchmark_matrix, correctness_matrix, frontier_gate
from gbext.frontier.analysis import analyze_frontier

app = typer.Typer(help="GB-style extension-field arithmetic experimental CLI")


@app.command("run-correctness")
def run_correctness(
    config: Path = typer.Option(..., "--config", help="Path to config YAML file"),
    instances: Path = typer.Option("data/catalog/instances.csv", "--instances", help="Path to instances catalog"),
    output: Path = typer.Option("results/correctness_summary.csv", "--output", help="Path to output CSV"),
) -> None:
    print(f"Loading config {config}...")
    correctness_matrix.run_correctness(instances, output)


@app.command("run-benchmark")
def run_benchmark(
    config: Path = typer.Option(..., "--config", help="Path to config YAML file"),
    instances: Path = typer.Option("data/catalog/instances.csv", "--instances", help="Path to instances catalog"),
    output: Path = typer.Option("results/benchmark_summary.csv", "--output", help="Path to output CSV"),
) -> None:
    print(f"Loading config {config}...")
    benchmark_matrix.run_benchmark(instances, output)


@app.command("run-frontier-gate")
def run_frontier_gate(
    config: Path = typer.Option(
        "configs/frontier_gate.yaml",
        "--config",
        help="Preregistered exact-operation frontier configuration",
    ),
) -> None:
    """Run the no-timing SEP/FUS exact-operation sweep."""
    parquet_path, _ = frontier_gate.run_frontier_gate(config)
    decision_path = analyze_frontier(config, parquet_path)
    print(f"Frontier data: {parquet_path}")
    print(f"Decision: {decision_path}")


@app.command("analyze-frontier")
def analyze_frontier_command(
    config: Path = typer.Option("configs/frontier_gate.yaml", "--config"),
    parquet: Path | None = typer.Option(None, "--parquet"),
) -> None:
    """Recompute the preregistered discovery/holdout decision."""
    decision_path = analyze_frontier(config, parquet)
    print(f"Decision: {decision_path}")


@app.command("run-sparse-study")
def run_sparse_study(
    config: Path = typer.Option(..., "--config", help="Path to config YAML file"),
) -> None:
    print("Legacy timing-oriented sparse study is not a Q1 evidence path.")
    raise typer.Exit(code=2)


@app.command("run-break-even")
def run_break_even(
    config: Path = typer.Option(..., "--config", help="Path to config YAML file"),
) -> None:
    print("Deprecated. Use 'gbext run-frontier-gate'.")
    raise typer.Exit(code=2)


@app.command("run-ct-proxy")
def run_ct_proxy(
    config: Path = typer.Option(..., "--config", help="Path to config YAML file"),
) -> None:
    print("Constant-time proxy metrics are outside the frontier experiment.")
    raise typer.Exit(code=2)


@app.command("make-report")
def make_report(
    input_dir: Path = typer.Option("results/", "--input", help="Directory with CSV results"),
    output_dir: Path = typer.Option("results/summaries/", "--output", help="Output directory for reports and figures"),
) -> None:
    import matplotlib.pyplot as plt
    import pandas as pd

    input_path = input_dir / "benchmark_summary.csv"
    if not input_path.exists():
        print(f"Error: {input_path} not found.")
        raise typer.Exit(code=1)

    df = pd.read_csv(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    sample_instance = df["instance_id"].iloc[0]
    subdf = df[df["instance_id"] == sample_instance]

    plt.figure(figsize=(10, 6))
    plt.bar(subdf["method"], subdf["mean_time"])
    plt.title(f"Performance for {sample_instance}")
    plt.ylabel("Mean Time (s)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plot_path = output_dir / "sample_benchmark_plot.png"
    plt.savefig(plot_path)
    print(f"Generated plot: {plot_path}")


if __name__ == "__main__":
    app()
