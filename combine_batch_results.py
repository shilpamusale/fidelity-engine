#!/usr/bin/env python3
import pandas as pd
import glob
import os
from datetime import datetime

# List of all agents
AGENTS = ["baseline_agent", "COT_agent", "RAG_agent", "nli_filtered_agent"]


def combine_csv_files(prompt_type):
    """Combine all CSV files for a given prompt type across all agents."""
    all_dataframes = []
    file_count = 0

    print(f"\nProcessing {prompt_type} files:")
    print("-" * 50)

    for agent in AGENTS:
        # Find all CSV files for this agent and prompt type
        pattern = os.path.join(agent, f"{agent}_{prompt_type}_batch_*.csv")
        csv_files = glob.glob(pattern)

        # Get the most recent file if multiple exist
        if csv_files:
            # Sort by modification time and get the most recent
            latest_file = max(csv_files, key=os.path.getmtime)
            print(f"  {agent}: {os.path.basename(latest_file)}")

            try:
                # Read the CSV file
                df = pd.read_csv(latest_file)
                # Ensure the agent column is set correctly
                df["agent"] = agent
                all_dataframes.append(df)
                file_count += 1
            except Exception as e:
                print(f"    Error reading {latest_file}: {e}")
        else:
            print(f"  {agent}: No {prompt_type} CSV files found")

    if all_dataframes:
        # Combine all dataframes
        combined_df = pd.concat(all_dataframes, ignore_index=True)

        # Generate output filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_filename = f"combined_{prompt_type}_all_agents_{timestamp}.csv"

        # Save combined CSV
        combined_df.to_csv(output_filename, index=False)

        print(f"\nCombined {file_count} files into: {output_filename}")
        print(f"Total rows: {len(combined_df)}")

        # Show summary statistics
        if "elapsed" in combined_df.columns:
            print("\nTiming Summary by Agent:")
            print("-" * 50)
            timing_summary = combined_df.groupby("agent")["elapsed"].agg(
                ["count", "mean", "std", "min", "max"]
            )
            print(timing_summary.round(3))

        return output_filename
    else:
        print(f"\nNo {prompt_type} CSV files found to combine")
        return None


def main():
    """Main function to combine all batch test results."""
    print("=" * 80)
    print("COMBINING BATCH TEST RESULTS")
    print("=" * 80)

    # Check if we have any CSV files
    all_csv_files = glob.glob("*/*_batch_*.csv")
    if not all_csv_files:
        print("No batch test CSV files found. Please run batch tests first.")
        return

    # Combine prompts.csv results
    prompts_file = combine_csv_files("prompts")

    # Combine modified_prompts.csv results
    modified_prompts_file = combine_csv_files("modified_prompts")

    # Summary
    print("\n" + "=" * 80)
    print("COMBINATION COMPLETE")
    print("=" * 80)

    if prompts_file:
        print(f"✓ Prompts results: {prompts_file}")
    else:
        print("✗ No prompts results found")

    if modified_prompts_file:
        print(f"✓ Modified prompts results: {modified_prompts_file}")
    else:
        print("✗ No modified prompts results found")

    print("\nYou can now analyze and compare results across all agents!")


if __name__ == "__main__":
    main()
