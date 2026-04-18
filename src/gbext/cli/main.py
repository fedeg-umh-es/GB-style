"""
gbext CLI main entry point.
Exposes interfaces for running all experimental suites.
"""

import typer
from pathlib import Path
from gbext.experiments import correctness_matrix, benchmark_matrix

app = typer.Typer(help="GB-style redundant convolution arithmetic experimental CLI")

@app.command("run-correctness")
def run_correctness(
    config: Path = typer.Option(..., "--config", help="Path to config YAML file"),
    instances: Path = typer.Option("data/catalog/instances.csv", "--instances", help="Path to instances catalog"),
    output: Path = typer.Option("results/correctness_summary.csv", "--output", help="Path to output CSV")
):
    print(f"Loading config {config}...") # Placeholder, would parse config
    print("Running correctness matrix...")
    correctness_matrix.run_correctness(instances, output)

@app.command("run-benchmark")
def run_benchmark(
    config: Path = typer.Option(..., "--config", help="Path to config YAML file"),
    instances: Path = typer.Option("data/catalog/instances.csv", "--instances", help="Path to instances catalog"),
    output: Path = typer.Option("results/benchmark_summary.csv", "--output", help="Path to output CSV")
):
    print(f"Loading config {config}...")
    print("Running benchmark matrix...")
    benchmark_matrix.run_benchmark(instances, output)

@app.command("run-sparse-study")
def run_sparse_study(
    config: Path = typer.Option(..., "--config", help="Path to config YAML file")
):
    print("Running sparse modulus study... (placeholder)")

@app.command("run-break-even")
def run_break_even(
    config: Path = typer.Option(..., "--config", help="Path to config YAML file")
):
    print("Running break-even study... (placeholder)")

@app.command("run-ct-proxy")
def run_ct_proxy(
    config: Path = typer.Option(..., "--config", help="Path to config YAML file")
):
    print("Running constant-time proxy study... (placeholder)")
    print("WARNING: constant-time proxy != side-channel proof")

@app.command("make-report")
def make_report(
    input_dir: Path = typer.Option("results/", "--input", help="Directory with CSV results"),
    output_dir: Path = typer.Option("results/summaries/", "--output", help="Output directory for reports and figures")
):
    import pandas as pd
    import matplotlib.pyplot as plt
    
    input_path = input_dir / "benchmark_summary.csv"
    if not input_path.exists():
        print(f"Error: {input_path} not found.")
        raise typer.Exit(code=1)
        
    df = pd.read_csv(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate simple comparative bar plot for a single instance
    sample_instance = df['instance_id'].iloc[0]
    subdf = df[df['instance_id'] == sample_instance]
    
    plt.figure(figsize=(10, 6))
    plt.bar(subdf['method'], subdf['mean_time'])
    plt.title(f"Performance for {sample_instance}")
    plt.ylabel("Mean Time (s)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plot_path = output_dir / "sample_benchmark_plot.png"
    plt.savefig(plot_path)
    print(f"Generated plot: {plot_path}")

if __name__ == "__main__":
    app()
