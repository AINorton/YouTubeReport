# Output

Use a unique output folder for every report request/run.

Recommended helper command:

```bash
python scripts/make_run_folders.py --client "Client Name"
```

This creates a matching output folder like:

```text
output/client_name_20260626_1542/
```

Expected outputs:

```text
Alamo_YouTube_Snapshot_deterministic.pdf
Alamo_YouTube_Snapshot_deterministic.png
Alamo_YouTube_Snapshot_deterministic.validation.txt
generated_map.png
```

Do not reuse old output folders as proof of a new run. Always check the validation report in the matching output folder for the current run.
