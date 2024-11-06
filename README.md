# Mutation Analysis

This project is a mutation analysis tool that processes BAM files, aligns them with a reference genome, and calculates mutation frequencies for each nucleotide position. It outputs mutation statistics and visualizations.

## Project Structure
```bash
mutation_analysis/
├── inputs/                 # Input files, such as BAM files and reference FASTA
├── results/                # Output files, including processed FASTA, SAM files, and analysis results
├── minimap2/               # Minimap2 tool installation
├── scripts/                # Project scripts and configuration
│   ├── config.env          # Configuration file for paths and environment variables
│   ├── MutationAnalyzer.py # Python script for mutation analysis
│   ├── plot_results.py     # Python script for plotting mutation data
│   ├── requirements.txt    # Required Python packages
│   ├── run_analysis.sh     # Main script to run the entire analysis
│   └── setup.sh            # Script to set up dependencies and environment
```
## Setup Instructions
1. Clone the Repository
```bash
git clone https://github.com/genepearl/mutation_analysis.git
cd mutation_analysis
```
2. Configure Environment Variables

In the scripts folder, you will find a config.env file. Adjust the paths in this file according to your setup. For example:
```bash
# Base directory for the project
export BASE_DIR="/path/to/your/mutation_analysis"
export INPUT_DIR="$BASE_DIR/inputs"
export RESULTS_DIR="$BASE_DIR/results"
export MINIMAP_DIR="$BASE_DIR/minimap2"
export SCRIPTS_DIR="$BASE_DIR/scripts"
export VENV_DIR="$BASE_DIR/env"

# Specify paths to reference and BAM files
export REFERENCE_FILE="$INPUT_DIR/template.fasta"
export BAM_FILE_1="$INPUT_DIR/dataset1.bam"  # Update with actual filename
export BAM_FILE_2="$INPUT_DIR/dataset2.bam"  # Update with actual filename
```

3. Run the Setup Script

The setup script:

  - creates a virtual environment
  - installs dependencies (`requirements.txt`)
  - installs Minimap2 if it is not already installed
    
```bash
bash scripts/setup.sh
```
## Running the Analysis
After setting up the environment, you can run the main analysis script, run_analysis.sh, which performs the following steps:

1. Convert BAM to FASTA using `samtools`.
2. Align sequences using Minimap2.
3. Run the mutation analysis with `MutationAnalyzer.py`.
4. Generate plots for mutation frequencies and enrichment using `plot_results.py`.
```bash
bash scripts/run_analysis.sh
```
This script will automatically activate the virtual environment, run the analysis, and deactivate the environment upon completion.

## Outputs
1. Mutation Frequencies for Dataset 1 (`mutation_frequencies_dataset1.csv`):

   - **Template Base**: Reference base at each position.
   - **Total Mutation Percentage**: Overall mutation percentage at each position.
   - **Mutation Percentages per Base (A, T, C, G)**: Mutation percentages for each nucleotide compared to the template base.

2. Mutation Frequencies for Dataset 2 (`mutation_frequencies_dataset2.csv`):

   - Same structure as Dataset 1.

3. Enrichment Analysis (`mutation_enrichment.csv`):

   - Enrichment is calculated as the difference in mutation percentages between Dataset 1 and Dataset 2 for each position.
     
### Visualizations
The analysis includes 15 plots in total to visualize mutation frequencies and enrichment values:

#### Dataset 1 Plots
1. **Total Mutation Frequency**: Mutation percentage across all positions.
2. **A Mutation Frequency**: Mutation percentage at positions where `A` differs from the template.
3. **T Mutation Frequency**: Mutation percentage at positions where `T` differs from the template.
4. **C Mutation Frequency**: Mutation percentage at positions where `C` differs from the template.
5. **G Mutation Frequency**: Mutation percentage at positions where `G` differs from the template.

#### Dataset 2 Plots
1. **Total Mutation Frequency**: Mutation percentage across all positions.
2. **A Mutation Frequency**: Mutation percentage at positions where `A` differs from the template.
3. **T Mutation Frequency**: Mutation percentage at positions where `T` differs from the template.
4. **C Mutation Frequency**: Mutation percentage at positions where `C` differs from the template.
5. **G Mutation Frequency**: Mutation percentage at positions where `G` differs from the template.

#### Enrichment Plots
1. **Total Enrichment**: Difference in total mutation percentages between Dataset 1 and Dataset 2.
2. **A Enrichment**: Difference in mutation percentages for `A` mutations between Dataset 1 and Dataset 2.
3. **T Enrichment**: Difference in mutation percentages for `T` mutations between Dataset 1 and Dataset 2.
4. **C Enrichment**: Difference in mutation percentages for `C` mutations between Dataset 1 and Dataset 2.
5. **G Enrichment**: Difference in mutation percentages for `G` mutations between Dataset 1 and Dataset 2.
