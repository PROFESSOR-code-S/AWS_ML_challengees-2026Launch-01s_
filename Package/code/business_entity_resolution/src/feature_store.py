import os
import pandas as pd
import rapidfuzz
import jellyfish

def generate_similarity_matrices(input_dir, candidate_pairs_path):
    print("-> Ingesting candidate pairs file from disk...")
    df_candidates = pd.read_csv(candidate_pairs_path, sep="\t").fillna("")
    
    s1 = pd.read_csv(os.path.join(input_dir, "test_source1.tsv"), sep="\t").set_index("entity_id")
    s2 = pd.read_csv(os.path.join(input_dir, "test_source2.tsv"), sep="\t").set_index("entity_id")
    s3 = pd.read_csv(os.path.join(input_dir, "test_source3.tsv"), sep="\t").set_index("entity_id")
    
    db_lookup = pd.concat([s2, s3])
    feature_rows = []
    
    for _, row in df_candidates.iterrows():
        s1_id = row["source1_entity_id"]
        candidate_list = str(row["candidate_entity_ids"]).split(",") if row["candidate_entity_ids"] else []
        
        if not candidate_list:
            continue
            
        s1_row = s1.loc[s1_id]
        s1_name = str(s1_row["business_name"]).lower()
        s1_addr = str(s1_row["business_address"]).lower()
        
        for cand_id in candidate_list:
            if cand_id not in db_lookup.index:
                continue
                
            cand_row = db_lookup.loc[cand_id]
            cand_name = str(cand_row["business_name"]).lower()
            cand_addr = str(cand_row["business_address"]).lower()
            
            # Algorithmic metric evaluation
            name_jw = rapidfuzz.distance.JaroWinkler.similarity(s1_name, cand_name)
            name_tsr = rapidfuzz.process.extractOne(s1_name, [cand_name], scorer=rapidfuzz.fuzz.token_sort_ratio)[1] / 100.0
            addr_lev = rapidfuzz.distance.Levenshtein.normalized_similarity(s1_addr, cand_addr)
            phonetic_match = 1.0 if jellyfish.soundex(s1_name[:8]) == jellyfish.soundex(cand_name[:8]) else 0.0
            
            # ======================================================================
            # HERE IS THE INJECTED CROSS-COUNTRY DOMAIN SHIFT SAFETY LINE:
            # ======================================================================
            country_match = 1.0 if str(s1_row["country"]).strip().lower() == str(cand_row["country"]).strip().lower() else 0.0
            
            feature_rows.append({
                "source1_entity_id": s1_id,
                "candidate_entity_id": cand_id,
                "feat_name_jw": name_jw,
                "feat_name_tsr": name_tsr,
                "feat_addr_lev": addr_lev,
                "feat_phonetic": phonetic_match,
                "feat_country": country_match  # <── Added to feature store profile array
            })
            
    feature_matrix = pd.DataFrame(feature_rows)
    del s1, s2, s3, db_lookup
    return feature_matrix
