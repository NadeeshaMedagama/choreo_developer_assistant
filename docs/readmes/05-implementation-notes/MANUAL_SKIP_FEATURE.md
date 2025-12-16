# Manual Skip Feature - Usage Guide

## Overview
The ingestion system now includes a **manual skip feature** that allows you to monitor system RAM usage and manually skip files that are causing high memory consumption.

## How It Works

### 1. **Automatic Startup**
When you run any ingestion script, the keyboard monitor automatically starts in the background:
- `python backend/run_ingestion.py`
- `python backend/scripts/ingest/ingest_wso2_choreo_repos.py`

### 2. **Monitoring RAM**
You should monitor your system RAM using tools like:
- **htop** (Linux/Mac)
- **Task Manager** (Windows)
- **System Monitor** (Ubuntu/Linux GUI)

### 3. **Manual Skip**
When you see RAM usage getting too high:

1. Press **`q`** on your keyboard
2. Press **`Enter`**
3. The program will skip the current file and continue with the next one

### 4. **What Happens**
```
Processing README: docs/long-file.md [Memory: 1234.5MB (85.2%)]
⌨️  You press 'q' + Enter
🔴 MANUAL SKIP REQUESTED by user - Will skip current file after current operation...
⏭️  The program will continue with the next file
⏭️  MANUAL SKIP: User requested to skip long-file.md
✓ Continuing with next repository/file...
```

## Key Features

✅ **Non-blocking**: Keyboard monitoring runs in a background thread
✅ **Safe**: Won't crash the program if there are input errors
✅ **Multiple checkpoints**: Checks for skip at multiple points during processing:
   - Before chunking
   - During chunking
   - During embedding generation (per batch)
✅ **Continues processing**: Skips only the problematic file, continues with others
✅ **Memory cleanup**: Forces garbage collection after skipping

## When to Use This Feature

Use the manual skip feature when:
- 🔴 RAM usage exceeds 85-90%
- 🔴 System becomes slow/laggy during processing
- 🔴 A specific file is taking too long to process
- 🔴 You see swap memory being used heavily

## Example Workflow

```bash
# Terminal 1: Run ingestion
python backend/scripts/ingest/ingest_wso2_choreo_repos.py --max-repos 10

# Terminal 2: Monitor RAM
watch -n 1 free -h

# When RAM gets too high:
# Switch to Terminal 1
# Press: q + Enter
# The current file will be skipped
```

## Technical Details

### Skip Points
The feature checks for manual skip at these points:
1. **Before chunking** - Before breaking file into chunks
2. **During chunking** - If chunking takes too long
3. **During embedding batches** - At the start of each embedding batch

### Thread Safety
- Uses thread-safe locks to prevent race conditions
- The skip flag is cleared automatically after each file
- Multiple repositories continue processing even if one file is skipped

### Logging
You'll see these messages:
- ⌨️ = Keyboard monitor started
- 💡 = Usage tip
- 🔴 = Manual skip requested
- ⏭️ = File being skipped
- ✓ = Continuing with next item

## Troubleshooting

**Q: I pressed 'q' but nothing happened?**
- Make sure to press **Enter** after 'q'
- The skip happens after the current operation completes (a few seconds)

**Q: Can I skip multiple files?**
- Yes! Press 'q' + Enter for each file you want to skip

**Q: Will it skip entire repositories?**
- No, it only skips the current file, then continues with other files in the same repo

**Q: What if the program is completely frozen?**
- Use Ctrl+C to stop the entire program
- The manual skip feature works best before complete freezes

## Benefits

1. **No need to restart**: Skip problematic files without restarting the entire ingestion
2. **Flexible control**: You decide when to skip based on real-time RAM monitoring
3. **Preserves progress**: Already processed files remain in the database
4. **Continues automatically**: No manual intervention needed after skip
5. **Safe and reliable**: Won't corrupt data or crash the program

## Success Message

When the feature starts, you'll see:
```
🎛️  Starting manual skip feature...
⌨️  Keyboard monitor started - Press 'q' + Enter to skip current file
💡 TIP: Press 'q' + Enter anytime to skip the current file if RAM is too high
✓ Manual skip feature enabled - Press 'q' + Enter anytime to skip problematic files
```

---

**Note**: This feature is especially useful when ingesting large repositories or when your system has limited RAM. It gives you manual control to prevent system freezes while still completing as much ingestion as possible.

