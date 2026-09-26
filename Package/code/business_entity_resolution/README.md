<!--
How to reproduce-
end-to-end (data → blocking → matching → output)
-->

<<<<<<< Updated upstream
<!-- exact run instructions. -->
=======
<!-- exact run instructions. -->

# Business Entity Resolution Pipeline (Offline Execution Environment)

This pipeline runs entirely offline in an isolated sandboxed workspace, resolving multi-source business entities via high-recall dynamic text blocking and a precision-heavy downstream LightGBM classifier.

## Step 1: Offline Environment Initialization
Before executing the pipeline, install the pinned, pre-compiled stable dependencies from the local binary wheel storage directory:
```bash
pip install --no-index --find-links=./src/wheels -r requirements.txt
```

## Step 2: Running Execution Sequence
Execute the end-to-end serialized pipeline by calling the main entry control module:
```bash
python3 src/main.py
```
This automated wrapper script handles text normalization, fits the token vocabulary natively on the test corpus, builds the similarity store matrices, and exports the final validated outputs to the `output/` directory.
>>>>>>> Stashed changes
