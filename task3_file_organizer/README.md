# Task 3 - Automated File Organizer & Cleanup Utility

Sorts a cluttered folder into `Documents/ Images/ Videos/ Audio/ Archives/ Code/ Others/`.

## Run
```bash
python organizer.py --dry-run              # preview Downloads folder
python organizer.py ~/Downloads            # organize for real
python organizer.py /some/folder
```

## Details
- Extension -> category dictionary, `os.scandir()` to inspect files, `shutil.move()` to relocate.
- Name collisions become `report (1).pdf`, `report (2).pdf` - nothing is overwritten.
- `PermissionError` / `FileExistsError` / `OSError` are caught per file and logged.
- Logging goes to the console and `organizer.log`; a summary table is printed at the end.
