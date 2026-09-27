# Amazon ML Challenge 2026: Business Entity Resolution

Team: 'Mythos'

Members: SAMRIDDHA MODANWAL,
AGRAJ SINGH, SIDDHI CHATURVEDI, ADITYA SINGH

## Problem Scenario-

In large-scale commercial platforms, business identity data arrives from multiple independent sources — each contributing partial, noisy fragments of information about the same real-world entities. These fragments share no common identifiers, and the challenge of determining which records refer to the same business is known as Entity Resolution (ER).

### The challenge-

Challenge is to build an ML solution that, given business records from 3 independent data sources with noisy and inconsistent fields, determines which records across sources refer to the same real-world business entity. Source 1 is the deduplicated reference source

### Extract-

Blocking strategy is very crucial major consideration in solution to the problem given.

## Problem Statement-

Task is to find all matching records from Source 2 and Source 3 for each Source 1 entity. A Source 1 entity may match zero, one, or many records from Source 2 and Source 3.

## Evaluated on-

    Submissions are evaluated using F_β Score (β = 0.5) — a precision-heavy metric that
    penalizes false merges (matching two different businesses) more than missed matches.

## Dataset-

    <>

## Data Description-

Each source file (*_source1.tsv, *_source2.tsv, *_source3.tsv) has the following columns:

    1. entity_id: Unique identifier for the record. The prefix indicates the source — S1-, S2-, or S3-.
    2. business_name: Name of the business entity (may contain abbreviations, legal suffixes, typos, transliterations)
    3. business_address: Address of the business (may contain partial addresses, format variations, missing components, landmark-based references)
    4. country: Country label for the record. The training data covers US and India. The test set additionally contains a third country, France, that does not appear in the training data.

   Treat country as an open set of string labels:

### Care taken around not to-

hard-code,

filter,

or one-hot
our pipeline to only {US, India}, since every test entity — France included — must appear in submission.

NOTE: There is no separate source column — a record's source is given by its entity_id prefix (S1-/S2-/S3-) and by which file it appears in.

### Data File Descriptions-

#### Training files-

    1. dataset/train/train_source1.tsv: Source 1 training records (the deduplicated reference source)
    2. dataset/train/train_source2.tsv: Source 2 training records
    3. dataset/train/train_source3.tsv: Source 3 training records
    4. dataset/train/train_ground_truth.tsv: Ground truth matching labels for the training set

#### Test files-

    1. dataset/test/test_source1.tsv: Source 1 test records. Generate matches for every entity in this file.
    2. dataset/test/test_source2.tsv: Source 2 test records
    3. dataset/test/test_source3.tsv: Source 3 test records

#### An attention point and a suggestion given to us-

No 'ground_truth' is provided for the test set.
To measure your own performance, hold out a validation split from the training data and score it yourself using the F_0.5 formula (given in challenge).

#### &Task- 1.1

##### Output Format of 'output/candidate_pairs.tsv'-

This is the exact set of records we will feed into our matching model for inference.
If pipeline has several blocking/filtering stages 'output/candidate_pairs.tsv' is the last one.

Every ID in 'output/matching_results.tsv' should therefore appear here.

It is not scored on the leaderboard; we use it to analyse blocking quality (recall ceiling, reduction ratio) and to verify your pipeline

#### &Task- 1.2

##### Output Format of 'output/matching_results.tsv' -

Final entity matches:
Column Description
source1_entity_id The entity_id of a Source 1 record
matched_entity_ids :     Comma-separated list of matching entity_ids from Source 2 and/or Source 3

Example (columns separated by a single tab, ID lists separated by commas with no quoting):

    source1_entity_id       matched_entity_ids
    S1-00001            S2-00047,S2-00193,S3-00812
    S1-00002            S3-00004
    S1-00003

Important:

    ● Every Source 1 entity in the test set must have exactly one row
    ● Leave matched_entity_ids empty for entities with no matches (singletons)
    ● No duplicate entity IDs within a single ID list
    ● ID lists must only contain Source 2 or Source 3 IDs that exist in the test set

### Dataset Pre-Processing -

<>

## Challenge constrained us to -

1. 'matched_entity_ids' must only reference entities from Source 2 or Source 3. Self-matches to Source 1, and IDs that do not exist in the test set, will be rejected.
2. Every Source 1 entity must appear in your submission. Missing entities will cause
rejection.
3. Duplicate entity IDs in any ID list
  
   will cause rejection, as will duplicate
'source1_entity_id' rows.
4. Final model can have up to 8 Billion parameters only.

## Submission 'package' Structure-

    'package' => Mythos_submission.zip
    ├── output/
    │ ├── matching_results.tsv # final matches (same file you upload to the leaderboard)
    │ └── candidate_pairs.tsv # your blocking candidate set
    ├── code/
    │ └── business_entity_resolution/
    │ ├── src/ # all your source code
    │ ├── README.md # how to reproduce end-to-end (data → blocking → matching
    → output)
    │ └── requirements.txt # pinned dependencies / environment
    ├── util.py (Add-on on top of asked submission structure)
    └── Documentation_template.md # your methodology write-up (this filled-in template)

## P.S. (Post script)-

Reffer to README.md present at-

    Package\code\business_entity_resolution\README.md

for  guide on 'how to reproduce'- end-to-end (data → blocking → matching → output)
