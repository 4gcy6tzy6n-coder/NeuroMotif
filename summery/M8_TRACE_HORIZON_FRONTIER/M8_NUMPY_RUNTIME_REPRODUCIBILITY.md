# M8 numerical runtime reproducibility check

**Task code:** `M8_NUMPY_RUNTIME_REPRODUCIBILITY_CHECK`

The canonical 1,350-row M8 task grid was rerun with the same code, seeds and contract under Python 3.12.13 / NumPy 2.4.4. This runtime emitted no `RuntimeWarning` during the run. The original run used Python 3.9.6 / NumPy 2.0.2; the environment's NumPy reports Apple Accelerate as its BLAS, and the run emitted 9 matrix-multiplication warnings.

The two CSVs have the same 1,350 condition keys and all **1,350 accuracy values match exactly** (maximum absolute difference 0). The primary effect and bootstrap interval are also identical. This supports classifying the warning as specific to the older tested runtime/library combination, with no effect on these measured outputs. It does not prove all NumPy 2.0.2 / Accelerate operations are harmless; the old warnings are preserved in the provenance record.

The comparison runtime's complete run manifest and output SHA-256 values are recorded in `M8_NUMPY_RUNTIME_REPRODUCIBILITY.json`.
