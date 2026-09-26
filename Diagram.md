## Notice point -

Unsupervised Representation (what the Blocker does) and Supervised Learning (what the downstream Matcher does)

The Blocker doesn't look at labels:

The TF-IDF vectorizer only maps which strings exist in the test corpus to establish a search space. It calculates token frequencies, not true matches. It doesn't know—and doesn't care—if record S1-100 actually matches record S2-500.

The Matcher remains blind:

Your actual classification model (LightGBM/XGBoost) is frozen before the test data is introduced. It only looks at relative similarity scores (e.g., "Jaro-Winkler = 0.85"). Because it evaluates raw mathematical distances rather than specific vocabulary words, it cannot memorize "Rue" or "Gare." It treats a French string mutation exactly like an Indian string mutation.Therefore, building a dynamic token index on the test set is completely valid under the rules, scales efficiently, and will not artificially inflate our score through model memorization.

## How to structure the pipeline architecture efficiently

    [S3 Input Bucket] 
           │ (Fast streaming via SageMaker Pipe Mode / Fast File Mode)
           ▼
     ┌───────────────┐
     │ SageMaker     │ ──► Phase 1: Preprocessing & Tokenization
     │ Processing    │ ──► Phase 2: Scale Blocking (Outputs candidate_pairs.tsv to S3)
     └───────────────┘
           │
           ▼
     ┌───────────────┐
     │ SageMaker     │ ──► Phase 3: Feature Extraction (RapidFuzz, Similarity Indexes)
     │ Training/Inf  │ ──► Phase 4: Downstream Classifier (LightGBM/8B Model inference)
     └───────────────┘
          │
          ▼
    [S3 Output Bucket] ──► Final Leaderboard TSVs

## Cloud Development Phase

    [Raw TSV Files] ──► [S3 Table Bucket (Apache Iceberg)] ──► [Fast Athena/SQL Queries] ──► Preprocessed Tokens
                                                                                                      │
     [Downstream LightGBM Model] ◄── [Dynamic Key Similarity Matrices] ◄── [RapidFuzz Multi-Threading] ┘

## Architecture & Storage Placement Blueprint

    ────────────────────────────────────────────────────────────────────────┐
    │                      AWS FREE TIER STORAGE LAYER                       │
    └────────────────────────────────────────────────────────────────────────┘
           │                                                           ▲
           │ (Fast File Mode Streaming)                                │ (Upload Final)
           ▼                                                           │
    ┌────────────────────────────────────────────────────────────────────────┐
    │ SAGE MAKER STUDIO NOTEBOOK / PROCESSING JOB RUNTIME (Up to 50 GB Free) │
    ├────────────────────────────────────────────────────────────────────────┤
    │                                                                        │
    │  [Volatile Shared Host Volume: /tmp/pipeline_buffer (RAM / NVMe)]      │
    │                                                                        │
    │  ┌────────────────────────┐  Shared  ┌────────────────────────┐        │
    │  │ CONTAINER 1:           │  Pipe    │ CONTAINER 2:           │        │
    │  │ Blocker & Sanitizer    │ ────────►│ Feature Engineer       │        │
    │  └────────────────────────┘  Buffer  └────────────────────────┘        │
    │               │                                  │                     │
    │               │ (Self-Destruct                    │ (Self-Destruct      │
    │               ▼  Wipe /tmp/c1)                   ▼  Wipe /tmp/c2)      │
    │        [Wipe Trigger]                     [Wipe Trigger]               │
    │                                                  │                     │
    │                                                  ▼ Matrix Stream       │
    │                                      ┌────────────────────────┐        │
    │                                      │ CONTAINER 3:           │────────┘
    │                                      │ Precision Classifier   │
    │                                      └────────────────────────┘
    └────────────────────────────────────────────────────────────────────────┘

Container does not imply docker container in this case, as repository was made based on submission requirements and not actual live project ready for deployment.

### Expanded Architectural Pipeline Diagram -

    ====================================================================================================
                                    PHASE 1: PREPROCESSOR & BLOCKER
    ====================================================================================================
     [Mounted Host Filesystem] 
                │
                ▼ (FastFile Mode / Tab-Separated Stream Chunk Ingestion)
     ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
     │ 1. TEXT SANITATION ENGINE                                                                      │
     │    ├─► Lowercasing, structural whitespace stripping, legal suffix normalization mappings.      │
     │    └─► DEDUPLICATION CHECK: Drop duplicate tracking items per row block to prevent loop drift.  │
     └────────────────────────────────────────────────────────────────────────────────────────────────┘
                │
                ▼ (Clean Data Stream)
     ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
     │ 2. DYNAMIC SPARSE INDEX GENERATOR                                                              │
     │    ├─► Reads test files directly to extract raw character n-gram tokens dynamically.           │
     │    └─► Fits an unsupervised TF-IDF vocabulary natively on the test data matrix.                 │
     └────────────────────────────────────────────────────────────────────────────────────────────────┘
                │
                ▼ (Populated Term-Document Matrices)
     ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
     │ 3. HIGH-RECALL CANDIDATE FILTER (LET GOOD NUMBER DATA PASS)                                    │
     │    ├─► Computes fast cosine matrix approximations across rows.                                 │
     │    └─► Retains a broad candidate group per entity to maintain an optimal recall ceiling.│
     └────────────────────────────────────────────────────────────────────────────────────────────────┘
                │
                ▼
     [Shared Volatile Storage: /opt/ml/processing/output/candidate_pairs.tsv]
                │
                │ (Trigger Next Stage)
                ▼
    ====================================================================================================
                                      PHASE 2: FEATURE ENGINEER
    ====================================================================================================
     [Shared Volatile Storage: Read candidate_pairs.tsv]
                │
                ▼
     ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
     │ 4. STRUCTURAL METRIC CALCULATION                                                               │
     │    ├─► Direct key access to target records across the cross-column boundary.                   │
     │    ├─► RapidFuzz Execution: Jaro-Winkler, Token Sort Ratio, Levenshtein edit distance metrics. │
     │    └─► Phonetic Mapping: Run jellyfish algorithms to capture variable word pronunciations.     │
     └────────────────────────────────────────────────────────────────────────────────────────────────┘
                │
                ▼
     ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
     │ 5. DENSE COMPARISON MATRIX GENERATOR                                                           │
     │    ├─► Assembles purely numerical similarity tracking arrays (Values normalized from 0.0-1.0). │
     │    └─► SELF-DESTRUCT CLEANSE: Wipes text buffers from memory instantly post-matrix assembly.   │
     └────────────────────────────────────────────────────────────────────────────────────────────────┘
                │
            ▼
     [Numerical Vector Matrix Stream] ──► Pushed to Downstream Classifier (Phase 3 Engine)
    ====================================================================================================
                     PHASE 3: MATCHING DESIGN (DON'T PENALIZE SINGLETONS)
    ====================================================================================================
     ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
     │ 6. CONSERVATIVE PROBABILITY MATCHING                                                           │
     │    ├─► Pushes similarity feature profiles through a pre-compiled LightGBM classifier.          │
     │    ├─► Apply Conservative Thresholds: Lower confidence matches are pushed to an empty state.   │
     │    └─► PROTECT SINGLETON VALUATION: Confirms "no match" predictions to secure 1.0 scores.│
     └────────────────────────────────────────────────────────────────────────────────────────────────┘
                │
                ▼ (Output File Verification via local validation execution script)
     [Mounted Host Filesystem: /output/matching_results.tsv]

## FOLDER code/business_entity_resolution -

    src/                     # All source python pipelines offline models, & dictionaries
    ├── models/
    │   └── final_lightgbm_matcher.txt
    ├── utils/
    └── normalization_map.json

### The Serialized Execution Flow

     [Host Machine Trigger] ──► run_pipeline.sh
                                 │
                                 ▼
     ┌─────────────────────────────────────────────────────────┐
    │ STEP 1: ACTIVATE CONTAINER 1 (Blocker & Sanitizer)      │
    │  ├─► Mounts: host inputs & /tmp/pipeline_buffer         │
    │  ├─► Execution: Streams data, drops duplicates, LSH.    │
    │  └─► STOP & WIPE: Writes candidate_pairs.tsv ──► EXITS  │  ◄── Memory Cleared 🫧
     └─────────────────────────────────────────────────────────┘
                                 │
                                 ▼
     ┌─────────────────────────────────────────────────────────┐
    │ STEP 2: ACTIVATE CONTAINER 2 (Feature Engineer)         │
    │  ├─► Mounts: /tmp/pipeline_buffer                       │
    │  ├─► Execution: RapidFuzz matrix generation.            │
    │  └─► STOP & WIPE: Writes dense similarity rows ──► EXITS│  ◄── Memory Cleared 🫧
     └─────────────────────────────────────────────────────────┘
                                 │
                                 ▼
     ┌─────────────────────────────────────────────────────────┐
    │ STEP 3: ACTIVATE CONTAINER 3 (Precision Matcher)        │
    │  ├─► Mounts: /tmp/pipeline_buffer & host outputs        │
    │  ├─► Execution: Static inference via 8B/LightGBM model. │
    │  └─► STOP & WIPE: Writes matching_results.tsv ──► EXITS │  ◄── Memory Cleared 🫧
     └─────────────────────────────────────────────────────────┘
                                 │
                                 ▼
     [Final Validation Check] ──► run utils/validate_submission.py ──► PASS ✅
