import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

## Generates a bar plot for a given mutation percentage column (Total by default) and saves it to a specified filename.
def plot_data(data, title, filename, value_column='Total'):
    """
    Plot mutation data as a bar graph for a specific column and save the plot.

    Parameters:
    - data (DataFrame): Data containing mutation frequencies indexed by position.
    - title (str): Title for the plot.
    - filename (str): Path to save the generated plot image.
    - value_column (str): The column in 'data' to plot (default is 'Total').

    Produces a bar plot showing mutation percentages by position.
    """
    plt.figure(figsize=(12, 6))
    plt.bar(data.index, data[value_column], width=1.0)
    plt.xlabel('Position')
    plt.ylabel(f'{value_column} Mutation Percentage (%)')
    plt.title(title)
    plt.grid(axis='y', linestyle='--', linewidth=0.5)
    plt.xticks(range(0, max(data.index) + 75, 75), rotation=45)
    plt.xlim(left=0)
    plt.tight_layout()
    save_plot(filename)

## Saves the current plot to a file and closes it to release memory.
def save_plot(filename):
    """
    Save the plot to a specified file.

    Parameters:
    - filename (str): Path to save the plot.

    Finalizes the plot by saving and closing it to free memory.
    """
    plt.savefig(filename)
    plt.close()
    print(f"Plot saved as {filename}")

## Loads a dataset and generates plots for overall mutation frequencies and each nucleotide base if present.
def process_csv_and_plot(dataset_path, dataset_name):
    """
    Process a CSV dataset and generate plots for mutation frequencies.

    Parameters:
    - dataset_path (str): Path to the CSV file with mutation data.
    - dataset_name (str): Descriptive name for the dataset (used in titles).

    Loads data from 'dataset_path' and creates mutation frequency plots for overall and each base.
    """
    if os.path.exists(dataset_path):
        data = pd.read_csv(dataset_path, index_col='Position')
        plot_data(data, f'Mutation Frequencies - {dataset_name}', dataset_path.replace('.csv', '_total.png'))
        plot_each_base(data, dataset_name, dataset_path)
    else:
        print(f"File {dataset_path} not found.")

## Plots mutation frequencies for each base (A, T, C, G) if available in the dataset.
def plot_each_base(data, dataset_name, dataset_path):
    """
    Generate and save plots for mutation frequencies of each nucleotide base.

    Parameters:
    - data (DataFrame): Data containing mutation frequencies.
    - dataset_name (str): Name of the dataset (for plot titles).
    - dataset_path (str): Original CSV path to derive plot filenames.

    Loops through each base ('A', 'T', 'C', 'G') and creates a plot if column exists in 'data'.
    """
    for base in ['A', 'T', 'C', 'G']:
        if base in data.columns:
            plot_data(data, f'{base} Mutation Frequencies - {dataset_name}', dataset_path.replace('.csv', f'_{base}.png'), base)

## Parses command-line arguments and initiates plotting for each dataset provided.
def main():
    """
    Main function to parse arguments and initiate plotting for each dataset.

    This function uses argparse to gather command-line arguments for dataset paths,
    loads each dataset, and generates mutation frequency plots.
    """
    parser = argparse.ArgumentParser(description="Plot mutation frequencies from CSV files")
    parser.add_argument("--dataset1", required=True, help="Path to the first dataset CSV file")
    parser.add_argument("--dataset2", required=True, help="Path to the second dataset CSV file")
    parser.add_argument("--enrichment", required=True, help="Path to the enrichment CSV file")
    args = parser.parse_args()

    for dataset_path, name in [(args.dataset1, 'Dataset 1'), (args.dataset2, 'Dataset 2'), (args.enrichment, 'Enrichment')]:
        process_csv_and_plot(dataset_path, name)

if __name__ == "__main__":
    main()
