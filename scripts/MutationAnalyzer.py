import pysam
import pandas as pd
import logging
import os
import argparse
from Bio import SeqIO
from multiprocessing import Pool, cpu_count

# Configure logging to track progress and issues
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MutationAnalyzer:
    """
    Analyzes mutation frequencies from SAM files by comparing against a reference FASTA sequence.

    This class processes sequencing data to identify mismatches with a reference genome, calculating
    mutation percentages for each base (A, T, C, G) at each position in the reference sequence.
    """

    def __init__(self, fasta_file_path, sam_file_path, batch_size=1000):
        """
        Initialize MutationAnalyzer with reference, SAM file paths, and batch processing size.

        Parameters:
        - fasta_file_path (str): Path to the reference FASTA file.
        - sam_file_path (str): Path to the SAM file with sequence alignments.
        - batch_size (int): Number of reads to process in each batch (default is 1000).
        """
        self.reference_sequence = self.load_reference_sequence(fasta_file_path)
        self.sam_file_path = sam_file_path
        self.batch_size = batch_size
        self.position_coverage = {}  # Track the total reads covering each position
        self.mutation_counts = {}  # Track mutations at each position
        self.base_mutation_counts = {}  # Track base-specific mutation counts at each position

    def load_reference_sequence(self, fasta_file_path):
        """
        Load the reference DNA sequence from a FASTA file.

        Parameters:
        - fasta_file_path (str): Path to the reference FASTA file.

        Returns:
        - str: The DNA sequence from the FASTA file.
        """
        logging.info(f"Loading reference sequence from {fasta_file_path}")
        with open(fasta_file_path, "r") as fasta_file:
            record = next(SeqIO.parse(fasta_file, "fasta"))
            return str(record.seq)

    @staticmethod
    def parse_cigar(cigar_tuple):
        """
        Translate CIGAR tuples to a human-readable list of operations.

        Parameters:
        - cigar_tuple (list of tuples): CIGAR tuples from a SAM alignment.

        Returns:
        - list of tuples: Human-readable CIGAR operations.
        """
        cigar_ops = {0: "M", 1: "I", 2: "D", 4: "S", 5: "H"}
        return [(cigar_ops[op], length) for op, length in cigar_tuple]

    def process_read_data(self, read_data):
        """
        Process individual read data to update coverage and mutation information.

        Parameters:
        - read_data (tuple): A tuple containing the read's query sequence, start position,
          CIGAR operations, and query name.

        Returns:
        - tuple: Coverage, mutation counts, and base mutation counts dictionaries for the read.
        """
        query_sequence, ref_start, cigar_tuples, _ = read_data
        if query_sequence is None or cigar_tuples is None:
            return {}, {}, {}

        local_position_coverage = {}
        local_mutation_counts = {}
        local_base_mutation_counts = {}
        ref_pos, query_pos = ref_start, 0
        cigar = self.parse_cigar(cigar_tuples)

        for operation, length in cigar:
            query_pos, ref_pos = self.handle_cigar_operation(
                operation, length, ref_pos, query_pos, query_sequence,
                local_position_coverage, local_mutation_counts, local_base_mutation_counts
            )

        return local_position_coverage, local_mutation_counts, local_base_mutation_counts

    def handle_cigar_operation(self, operation, length, ref_pos, query_pos, query_sequence,
                               local_position_coverage, local_mutation_counts, local_base_mutation_counts):
        """
        Handle individual CIGAR operation to update position and mutation counts.

        Parameters:
        - operation (str): The CIGAR operation (e.g., "M" for match/mismatch).
        - length (int): Length of the operation.
        - ref_pos (int): Current reference position.
        - query_pos (int): Current query position.
        - query_sequence (str): The sequence of the read.
        - local_position_coverage (dict): Coverage dictionary for the current read batch.
        - local_mutation_counts (dict): Mutation count dictionary for the current read batch.
        - local_base_mutation_counts (dict): Base-specific mutation count dictionary for the current read batch.

        Returns:
        - tuple: Updated query and reference positions.
        """
        if operation == "M":
            for _ in range(length):
                if ref_pos < len(self.reference_sequence) and query_pos < len(query_sequence):
                    self.update_mutation_data(
                        ref_pos, query_sequence[query_pos], local_position_coverage,
                        local_mutation_counts, local_base_mutation_counts
                    )
                query_pos += 1
                ref_pos += 1
        elif operation in ["I", "S", "H"]:
            query_pos += length
        elif operation == "D":
            ref_pos += length
        return query_pos, ref_pos

    def update_mutation_data(self, ref_pos, query_base, local_position_coverage,
                             local_mutation_counts, local_base_mutation_counts):
        """
        Update coverage and mutation data for a specific base at a given position.

        Parameters:
        - ref_pos (int): The reference position being updated.
        - query_base (str): The base in the query sequence at ref_pos.
        - local_position_coverage (dict): Coverage dictionary for the current read batch.
        - local_mutation_counts (dict): Mutation count dictionary for the current read batch.
        - local_base_mutation_counts (dict): Base-specific mutation count dictionary for the current read batch.
        """
        local_position_coverage[ref_pos + 1] = local_position_coverage.get(ref_pos + 1, 0) + 1
        if query_base != self.reference_sequence[ref_pos]:
            self.increment_mutation_counts(ref_pos, query_base, local_mutation_counts, local_base_mutation_counts)

    def increment_mutation_counts(self, ref_pos, query_base, local_mutation_counts, local_base_mutation_counts):
        """
        Increment mutation counts and base-specific mutation counts for a given position.

        Parameters:
        - ref_pos (int): The reference position being updated.
        - query_base (str): The base in the query sequence at ref_pos.
        - local_mutation_counts (dict): Mutation count dictionary for the current read batch.
        - local_base_mutation_counts (dict): Base-specific mutation count dictionary for the current read batch.
        """
        position = ref_pos + 1
        local_mutation_counts[position] = local_mutation_counts.get(position, 0) + 1
        local_base_mutation_counts.setdefault(position, {'A': 0, 'T': 0, 'C': 0, 'G': 0})
        local_base_mutation_counts[position][query_base] += 1

    def merge_results(self, batch_results):
        """
        Accumulate batch results into overall coverage and mutation counts.

        Parameters:
        - batch_results (tuple): Tuple of dictionaries from process_read_data.
        """
        for pos, count in batch_results[0].items():
            self.position_coverage[pos] = self.position_coverage.get(pos, 0) + count
        for pos, count in batch_results[1].items():
            self.mutation_counts[pos] = self.mutation_counts.get(pos, 0) + count
        for pos, base_counts in batch_results[2].items():
            if pos not in self.base_mutation_counts:
                self.base_mutation_counts[pos] = {'A': 0, 'T': 0, 'C': 0, 'G': 0}
            for base, base_count in base_counts.items():
                self.base_mutation_counts[pos][base] += base_count

    def process_large_dataset(self):
        """
        Process the entire SAM file in batches for mutation analysis.

        Uses multiprocessing to process read data in parallel.
        """
        logging.info(f"Processing SAM file in batches of {self.batch_size}")
        batch_number, reads_data = 1, []
        with pysam.AlignmentFile(self.sam_file_path, "r") as samfile, Pool(cpu_count()) as pool:
            for read in samfile:
                reads_data.append((read.query_sequence, read.reference_start, read.cigartuples, read.query_name))
                if len(reads_data) >= self.batch_size:
                    self.process_batch(pool, reads_data, batch_number)
                    reads_data = []
                    batch_number += 1
            if reads_data:
                self.process_batch(pool, reads_data, batch_number)
        logging.info("Finished processing all batches")

    def process_batch(self, pool, reads_data, batch_number):
        """
        Process a single batch of reads and merge the results.

        Parameters:
        - pool (Pool): Multiprocessing pool for parallel processing.
        - reads_data (list): List of read data for the batch.
        - batch_number (int): The current batch number.
        """
        logging.info(f"Processing batch {batch_number} with {len(reads_data)} reads")
        results = pool.map(self.process_read_data, reads_data)
        for batch_results in results:
            self.merge_results(batch_results)

    def calculate_mutation_frequencies(self):
        """
        Calculate mutation frequencies as percentages for each position.

        Returns:
        - dict: A dictionary where each position maps to a dictionary of total and base-specific percentages.
        """
        logging.info("Calculating mutation frequencies")
        mutation_frequencies = {}
        for pos in range(1, len(self.reference_sequence) + 1):
            mutation_frequencies[pos] = self.get_base_mutation_percentages(pos)
        return mutation_frequencies

    def get_base_mutation_percentages(self, pos):
        """
        Calculate mutation percentage for each base at a given position.

        Parameters:
        - pos (int): Position in the reference sequence.

        Returns:
        - dict: A dictionary with the template base, total mutation percentage, and percentages for each base.
        """
        total_reads = self.position_coverage.get(pos, 0)
        mutations = self.mutation_counts.get(pos, 0)
        overall_percentage = (mutations / total_reads) * 100 if total_reads > 0 else 0
        base_percentages = {base: (self.base_mutation_counts.get(pos, {}).get(base, 0) / total_reads) * 100
                            if total_reads > 0 else 0 for base in ['A', 'T', 'C', 'G']}
        template_base = self.reference_sequence[pos - 1]  # Retrieve template base
        return {'Template_Base': template_base, 'Total': overall_percentage, **base_percentages}

    @staticmethod
    def save_to_csv(data, filename):
        """
        Save mutation data to a CSV file.

        Parameters:
        - data (dict): Mutation data with mutation percentages for each position.
        - filename (str): Path to save the CSV file.
        """
        logging.info(f"Saving data to {filename}")
        df = pd.DataFrame(data).T
        df.index.name = 'Position'
        df.to_csv(filename)
        logging.info("Data saved successfully")

    @staticmethod
    def calculate_enrichment(frequencies1, frequencies2):
        """
        Calculate enrichment by subtracting mutation percentages between two datasets.

        Parameters:
        - frequencies1 (dict): Mutation frequencies for dataset 1.
        - frequencies2 (dict): Mutation frequencies for dataset 2.

        Returns:
        - dict: Enrichment values for each position.
        """
        enrichment = {}
        for pos in frequencies1:
            enrichment[pos] = {key: frequencies1[pos].get(key, 0) - frequencies2[pos].get(key, 0)
                               for key in frequencies1[pos] if key != 'Template_Base'}
            enrichment[pos]['Template_Base'] = frequencies1[pos].get('Template_Base', '')
        return enrichment

def setup_analyzer(reference, sam_file, batch_size):
    """
    Set up and execute the mutation analysis for a given reference and SAM file.

    Parameters:
    - reference (str): Path to the reference FASTA file.
    - sam_file (str): Path to the SAM file.
    - batch_size (int): Size of read batches to process.

    Returns:
    - dict: Mutation frequencies calculated by the analyzer.
    """
    analyzer = MutationAnalyzer(reference, sam_file, batch_size)
    analyzer.process_large_dataset()
    return analyzer.calculate_mutation_frequencies()

def save_frequencies(data, results_dir, filename):
    """
    Save mutation frequencies to a CSV file in the specified directory.

    Parameters:
    - data (dict): Mutation frequencies to save.
    - results_dir (str): Directory to save the CSV file.
    - filename (str): Name of the CSV file.
    """
    MutationAnalyzer.save_to_csv(data, os.path.join(results_dir, filename))

def run_analysis(reference, sam1, sam2, results_dir, batch_size=1000):
    """
    Run the complete mutation analysis workflow.

    Parameters:
    - reference (str): Path to the reference FASTA file.
    - sam1 (str): Path to the first SAM file.
    - sam2 (str): Path to the second SAM file.
    - results_dir (str): Directory to save output files.
    - batch_size (int): Size of read batches to process.
    """
    analyzer1 = setup_analyzer(reference, sam1, batch_size)
    save_frequencies(analyzer1, results_dir, 'mutation_frequencies_dataset1.csv')

    analyzer2 = setup_analyzer(reference, sam2, batch_size)
    save_frequencies(analyzer2, results_dir, 'mutation_frequencies_dataset2.csv')

    enrichment = MutationAnalyzer.calculate_enrichment(analyzer1, analyzer2)
    save_frequencies(enrichment, results_dir, 'mutation_enrichment.csv')

def main():
    """
    Parse arguments and initiate the mutation analysis.
    """
    parser = argparse.ArgumentParser(description="Run MutationAnalyzer on SAM files")
    parser.add_argument("--reference", required=True, help="Path to the reference FASTA file")
    parser.add_argument("--sam1", required=True, help="Path to the first SAM file")
    parser.add_argument("--sam2", required=True, help="Path to the second SAM file")
    parser.add_argument("--results_dir", required=True, help="Directory to save output files")

    args = parser.parse_args()
    os.makedirs(args.results_dir, exist_ok=True)
    run_analysis(args.reference, args.sam1, args.sam2, args.results_dir)

if __name__ == "__main__":
    main()
