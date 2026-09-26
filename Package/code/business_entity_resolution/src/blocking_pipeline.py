"""
Purpose: Performs lowercase string normalization, clears local duplicate row
tracking records, dynamically fits the unsupervised TF-IDF vocabulary natively
on the unseen test set tokens, and isolates high-recall candidates.

<── Called by main.py

"""

# Clears duplicate streams & fits token vocabularies