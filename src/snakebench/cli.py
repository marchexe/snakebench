"""Command-line interface for Snakebench Advisor."""

import argparse
from pathlib import Path

from tabulate import tabulate

from .load import load_parquet_files
from .summarize import summarize_by_tool
from .advise import suggest_resources, suggest_resources_stratified
from .report import build_markdown_report
from .readiness import build_readiness_markdown, inspect_dataset


def cmd_summarize(args):
    """Handle 'snakebench summarize' command."""
    try:
        df = load_parquet_files(args.path)
        summary = summarize_by_tool(df)

        print("\n=== Tool Summary ===\n")
        print(
            tabulate(
                summary,
                headers="keys",
                tablefmt="grid",
                showindex=False,
                floatfmt=".2f",
            )
        )
        print(f"\nSummary generated from {len(df)} observations.\n")

    except Exception as e:
        print(f"Error: {e}", flush=True)
        exit(1)


def cmd_advise(args):
    """Handle 'snakebench advise' command."""
    try:
        df = load_parquet_files(args.path)

        # Check if stratification is requested
        if args.stratify:
            # Parse stratification strategy
            stratify_by = args.stratify.split(",")
            stratify_by = [s.strip() for s in stratify_by]

            # Map CLI names to actual column names
            stratify_cols = ["tool"]  # Always include tool
            if "input-size" in stratify_by or "input_size" in stratify_by:
                stratify_cols.append("input_size_bin")
            if "threads" in stratify_by:
                stratify_cols.append("threads")

            print(f"\n=== Resource Suggestions (stratified by {', '.join(stratify_by)}) ===\n")
            
            try:
                suggestions = suggest_resources_stratified(df, by=stratify_cols)
                print(
                    tabulate(
                        suggestions,
                        headers="keys",
                        tablefmt="grid",
                        showindex=False,
                        floatfmt=".2f",
                    )
                )
                print(f"\nStratified suggestions based on {len(df)} observations.\n")
            except Exception as e:
                print(f"Warning: Could not generate stratified suggestions: {e}")
                print("Falling back to tool-level suggestions.\n")
                summary = summarize_by_tool(df)
                suggestions = suggest_resources(summary)
                print(
                    tabulate(
                        suggestions,
                        headers="keys",
                        tablefmt="grid",
                        showindex=False,
                        floatfmt=".2f",
                    )
                )
                print(f"\nSuggestions based on {len(df)} observations.\n")
        else:
            # v0.1 behavior: tool-level only
            summary = summarize_by_tool(df)
            suggestions = suggest_resources(summary)

            print("\n=== Resource Suggestions ===\n")
            print(
                tabulate(
                    suggestions,
                    headers="keys",
                    tablefmt="grid",
                    showindex=False,
                    floatfmt=".2f",
                )
            )
            print(f"\nSuggestions based on {len(df)} observations.\n")

    except Exception as e:
        print(f"Error: {e}", flush=True)
        exit(1)


def cmd_report(args):
    """Handle 'snakebench report' command."""
    try:
        df = load_parquet_files(args.path)
        summary = summarize_by_tool(df)
        suggestions = suggest_resources(summary)

        # Try to generate stratified suggestions for v0.2
        try:
            stratified_suggestions = suggest_resources_stratified(df)
        except Exception:
            stratified_suggestions = None

        report = build_markdown_report(
            summary,
            suggestions,
            len(df),
            stratified_suggestions_df=stratified_suggestions,
            psb_report=inspect_dataset(df),
        )

        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"Report written to {output_path}")

    except Exception as e:
        print(f"Error: {e}", flush=True)
        exit(1)


def cmd_readiness(args):
    """Handle 'snakebench dry' and 'snakebench readiness' commands."""
    try:
        df = load_parquet_files(args.path)
        report = build_readiness_markdown(df)
        print(report)

        if args.out:
            output_path = Path(args.out)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"Readiness report written to {output_path}")

    except Exception as e:
        print(f"Error: {e}", flush=True)
        exit(1)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="snakebench",
        description="Telemetry-driven Snakemake resource advisor",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # summarize command
    summarize_parser = subparsers.add_parser(
        "summarize",
        help="Summarize telemetry by tool",
    )
    summarize_parser.add_argument(
        "path",
        help="Path to parquet file or directory",
    )
    summarize_parser.set_defaults(func=cmd_summarize)

    # advise command
    advise_parser = subparsers.add_parser(
        "advise",
        help="Generate resource suggestions",
    )
    advise_parser.add_argument(
        "path",
        help="Path to parquet file or directory",
    )
    advise_parser.add_argument(
        "--stratify",
        default=None,
        help="Stratify suggestions by: input-size, or input-size,threads (default: none, tool-level only)",
    )
    advise_parser.set_defaults(func=cmd_advise)

    # report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate markdown report",
    )
    report_parser.add_argument(
        "path",
        help="Path to parquet file or directory",
    )
    report_parser.add_argument(
        "--out",
        default="reports/example_report.md",
        help="Output file path (default: reports/example_report.md)",
    )
    report_parser.set_defaults(func=cmd_report)

    # dry/readiness commands
    for command in ["dry", "readiness"]:
        readiness_parser = subparsers.add_parser(
            command,
            help="Check dataset readiness without running workflows",
        )
        readiness_parser.add_argument(
            "path",
            help="Path to parquet file or directory",
        )
        readiness_parser.add_argument(
            "--out",
            default=None,
            help="Optional output markdown file path",
        )
        readiness_parser.set_defaults(func=cmd_readiness)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
