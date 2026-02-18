import os
from pathlib import Path
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
import re


def get_folder_size_mb(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total / (1024 * 1024)


def convert_single_wav(wav_path):
    filename_lower = wav_path.name.lower()

    if any(skip_pattern in filename_lower for skip_pattern in ['YOUR_FILE_PATTERN']):
        return f'Skipping : {wav_path.name}'

    mp3_path = wav_path.with_suffix('.mp3')
    if mp3_path.exists():
        return f'Skipping (exists): {wav_path.name}'

    try:
        cmd = [
            'ffmpeg', '-i', str(wav_path),
            '-codec:a', 'mp3', '-b:a', '192k',
            '-y', str(mp3_path)
        ]
        start_time = time.perf_counter()
        subprocess.run(cmd, check=True, capture_output=True)
        elapsed = time.perf_counter() - start_time
        wav_path.unlink()
        return f'Done: {wav_path.name} → {mp3_path.name} ({elapsed:.1f}s)'
    except Exception as e:
        return f'ERROR {wav_path.name}: {e}'


def fast_convert_wav_to_mp3(root_folder, max_workers=8):
    root_path = Path(root_folder)
    start_total = time.perf_counter()

    initial_size_mb = get_folder_size_mb(root_folder)
    print(f'📁 Initial folder size: {initial_size_mb:.1f} MB')

    wav_files = list(root_path.rglob('*.wav'))
    if not wav_files:
        print('❌ No WAV files found!')
        return

    print(f'Found {len(wav_files)} WAV files. Using {max_workers} workers...')

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(convert_single_wav, wav_files))

    total_time = time.perf_counter() - start_total
    final_size_mb = get_folder_size_mb(root_folder)
    savings_mb = initial_size_mb - final_size_mb
    done_count = len([r for r in results if "Done:" in r])

    print(f'\n🚀 SUMMARY:')
    print(f'✅ {done_count}/{len(wav_files)} files converted')
    print(f'⏱️  Total time: {total_time:.1f}s')
    if len(wav_files) > 0:
        print(f'   ({total_time/len(wav_files):.2f}s/file avg)')
    print(
        f'💾 Before: {initial_size_mb:.1f} MB → After: {final_size_mb:.1f} MB')
    print(
        f'📉 Saved: {savings_mb:.1f} MB ({savings_mb/initial_size_mb*100:.1f}% smaller!)')

    for result in results:
        print(result)


# Usage
fast_convert_wav_to_mp3(
    'YOUR_FILE_PATH}', max_workers=8)
