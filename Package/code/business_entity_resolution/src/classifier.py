submission_rows = []
for s1_id, match_list in final_predictions.items():
    # The dictionary keys (s1_id) retain their original host string casing exactly!
    matched_str = ",".join(sorted(list(set(match_list))))
    submission_rows.append({
        "source1_entity_id": s1_id,
        "matched_entity_ids": matched_str
    })

'''
This way code will apply lowercase modifications strictly to evaluate string data relationships while preserving the absolute structure of tracking IDs, protecting us on dashboard scoring.

'''