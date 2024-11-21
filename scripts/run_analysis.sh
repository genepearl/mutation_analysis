#!/bin/bash

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
source "$SCRIPT_DIR/config.env"

# Step 1: Convert BAM to FASTA using samtools
echo "Converting BAM files to FASTA..."

convert_bam_to_fasta() {
    local bam_file=$1
    local fasta_file=$2

    if "$SAMTOOLS" fasta "$bam_file" > "$fasta_file"; then
        echo "Converted $bam_file to $fasta_file"
    else
        echo "Error converting $bam_file to FASTA."
        exit 1
    fi
}

convert_bam_to_fasta "$BAM_FILE_1" "$FASTA_FILE_1"
convert_bam_to_fasta "$BAM_FILE_2" "$FASTA_FILE_2"

# Step 2: Run Minimap2 on the processed FASTA files
echo "Running Minimap2..."

run_minimap() {
    local reference=$1
    local input_file=$2
    local output_file=$3

    if "$MINIMAP_DIR/minimap2" -a "$reference" "$input_file" > "$output_file"; then
        echo "Minimap2 alignment complete for $input_file."
    else
        echo "Error running Minimap2 on $input_file."
        exit 1
    fi
}

# Use the reference file directly from the inputs directory
run_minimap "$REFERENCE_FILE" "$FASTA_FILE_1" "$SAM_FILE_1"
run_minimap "$REFERENCE_FILE" "$FASTA_FILE_2" "$SAM_FILE_2"

# Step 3: Run MutationAnalyzer in the virtual environment with RESULTS_DIR
echo "Running MutationAnalyzer..."

source "$VENV_DIR/bin/activate"

# Define CSV output paths
MUTATION_FREQ_DATASET1="$RESULTS_DIR/mutation_frequencies_dataset1.csv"
MUTATION_FREQ_DATASET2="$RESULTS_DIR/mutation_frequencies_dataset2.csv"
MUTATION_ENRICHMENT="$RESULTS_DIR/mutation_enrichment.csv"

python3 "$SCRIPTS_DIR/MutationAnalyzer.py" --reference "$REFERENCE_FILE" --sam1 "$SAM_FILE_1" --sam2 "$SAM_FILE_2" --results_dir "$RESULTS_DIR"

# Step 4: Run Plotting Script with specific files
echo "Running Plotting Script..."

python3 "$SCRIPTS_DIR/plot_results.py" --dataset1 "$MUTATION_FREQ_DATASET1" --dataset2 "$MUTATION_FREQ_DATASET2" --enrichment "$MUTATION_ENRICHMENT"

# Deactivate the virtual environment
deactivate

echo "Process completed successfully."
