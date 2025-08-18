from pathlib import Path
import re

filename = "patient_4322-2025-06-13 14;39&494.0-depth_data.npy"
pattern = r"patient_(\d+)-(\d{4}-\d{2}-\d{2} \d{2};\d{2})&([\d\.]+)-([\w_]+)(\.[A-Za-z0-9]+)"

print(bool(re.match(pattern, filename)))
