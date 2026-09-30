---
name: fraud-detection
description: |Detects fraudulent transactions and logs audit trails 
  A short description of what this skill does.
metadata:
  Author: Rahul Uday Thampi
  version: "1.0"
---

## Instructions

1.Train a Random Forest model on transaction data to classify transactions as fraudulent or non-fraudulent.
2.Highlight suspected frauds with probability > 0.8.
3.Log suspicious transactions into 'audit_trail.db'.
4.Export results into 'suspected_frauds.csv' for reporting.