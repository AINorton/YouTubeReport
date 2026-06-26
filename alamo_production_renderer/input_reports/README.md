# Input Reports

Create a unique folder for every report request/run.

Do **not** reuse `current_run`.
Do **not** mix CSVs from different users, clients, campaigns, or dates.

Recommended helper command:

```bash
python scripts/make_run_folders.py --client "Client Name"
```

This creates folders like:

```text
input_reports/client_name_20260626_1542/
output/client_name_20260626_1542/
```

Place only the current report run's CSV exports in the new input folder.

Expected CSV types:

```text
Campaign report*.csv
Automatic placements report*.csv
Matched locations report*.csv
Devices*.csv
Demographics(Gender*.csv
Demographics(Age*.csv
Day_&_hour*.csv
```

Run the renderer with the matching output folder:

```bash
python render_report.py \
  --input-dir input_reports/client_name_YYYYMMDD_HHMM \
  --client "Client Name" \
  --template "templates/Alamo Intelligence Snapshot Base True (1).png" \
  --geo-dir geo \
  --output-dir output/client_name_YYYYMMDD_HHMM
```

If a folder already contains CSV files, do not add new report files to it. Create a new run folder instead.
