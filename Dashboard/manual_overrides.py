"""
Manual overrides for trial data to address false positives or specific data corrections.
"""

# Dictionary mapping NCT IDs to their correct gene list.
# format: 'NCT_ID': ['Gene1', 'Gene2'] or 'NCT_ID': [] for sporadic/none
# How to add future fixes: Simply edit Dashboard/manual_overrides.py and add the NCT ID and the desired gene list (e.g., ['C9orf72'] or []). The system will automatically pick this up on the next data refresh.
GENE_OVERRIDES = {
    'NCT07294144': [],  # False positive for SOD1, should be sporadic
}
