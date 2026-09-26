# The Single Entry Controller ──>

import os
import sys

# Ensure local source directory paths take namespace import priority
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blocking import run_unsupervised_blocking
from feature_store import generate_similarity_matrices
from classifier import run_precision_inference

def main():
    print("=== Initializing Automated Offline Pipeline ===")
    
    # Establish canonical submission directory targets
    input_dir = os.path.abspath("../../../../../dataset/test")
    output_dir = os.path.abspath("../../../../../output")
    
    candidate_pairs_path = os.path.join(output_dir, "candidate_pairs.tsv")
    matching_results_path = os.path.join(output_dir, "matching_results.tsv")
    
    # Phase 1: High-Recall Space Reduction
    run_unsupervised_blocking(input_dir, candidate_pairs_path)
    
    # Phase 2: Feature Matrix Extraction
    feature_matrix = generate_similarity_matrices(input_dir, candidate_pairs_path)
    
    # Phase 3: Precision-Heavy Matching & Singleton Preservation
    run_precision_inference(feature_matrix, matching_results_path)
    
    print("=== Execution Complete: Output Files Populated ===")

if __name__ == "__main__":
    main()