"""SFX soak test (Phase 5): the sound-effects dropout came at about the 6th mission load of a
session. This starts the game with its audio recorded, goes to the first mission
(tools/to-mission.py), then repeats a cycle: ~20 s of swings, dashes and jumps, measured, then
pause → Restart Mission. It prints the loudness of each cycle's combat.

usage: python -I sfx-soak.py <folder with shinobido2.exe> <cycles> [out dir]
  Needs: build/proccap/proccap.exe (third_party/recomp/tools/proccap), [audio] volume > 0 and the
  game's Music Volume 0 (the hub-day1 save has it), a hub save in slot 1, no game running.
  Writes <out>/run.wav, <out>/cycles.csv and screenshots.
"""
import csv
import os
import subprocess
import sys
import time
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DRIVE = os.path.join(ROOT, 'third_party', 'recomp', 'tools', 'v3kdrive.py')
PROCCAP = os.path.join(ROOT, 'build', 'proccap', 'proccap.exe')
COMBAT = ','.join(['square,wait 300,square,wait 300,square,wait 800,hold:ls_left+circle:1000,cross,wait 900,'
                   'square,wait 300,square,wait 300,square,wait 800,hold:ls_right+circle:1000,cross,wait 900'] * 3)
RESTART = 'start,wait 2500,cross,wait 2000,hold:up:250,wait 800,cross,wait 22000'


def drive(folder, *args):
    return subprocess.run([sys.executable, '-I', DRIVE, folder, '--exe', 'shinobido2.exe', *args],
                          capture_output=True, text=True)


def seconds(wav):
    """seconds recorded so far (the header is written at the end; count the data)"""
    return max(0, os.path.getsize(wav) - 44) / (48000 * 4)


def loudness(wav, start, end):
    with open(wav, 'rb') as f:
        f.seek(44 + int(start * 48000) * 4)
        raw = f.read(int((end - start) * 48000) * 4)
    pcm = np.frombuffer(raw[:len(raw) // 4 * 4], dtype='<i2').astype(np.float32).reshape(-1, 2).mean(axis=1) / 32768
    if len(pcm) == 0:
        return -100.0, -100.0
    rms = 10 * np.log10(np.mean(pcm ** 2) + 1e-10)
    peak = 20 * np.log10(np.max(np.abs(pcm)) + 1e-10)
    return rms, peak


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    folder, cycles = sys.argv[1], int(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'build', 'soak')
    os.makedirs(out, exist_ok=True)
    wav = os.path.join(out, 'run.wav')
    for f in (wav, wav + '.stop'):
        if os.path.exists(f):
            os.remove(f)

    r = drive(folder, 'start')
    print(r.stdout.strip())
    pid = subprocess.run(['powershell', '-NoProfile', '-Command', '(Get-Process shinobido2).Id'],
                         capture_output=True, text=True).stdout.split()[0]
    cap = subprocess.Popen([PROCCAP, pid, wav, '--quiet'], stderr=subprocess.DEVNULL)
    time.sleep(1)
    if subprocess.run([sys.executable, '-I', os.path.join(HERE, 'to-mission.py'), folder, os.path.join(out, 'drive')]).returncode:
        sys.exit('could not reach the mission')

    rows = []
    for n in range(1, cycles + 1):
        a = seconds(wav)
        drive(folder, 'run', COMBAT + f',shot:{os.path.join(out, f"c{n:02}.png")}', os.devnull)
        b = seconds(wav)
        rms, peak = loudness(wav, a, b)
        rows.append((n, round(a, 1), round(b, 1), round(rms, 1), round(peak, 1)))
        print(f'cycle {n:2}: {a:7.1f}-{b:7.1f} s  rms {rms:6.1f} dB  peak {peak:6.1f} dB', flush=True)
        drive(folder, 'run', RESTART, os.devnull)

    open(wav + '.stop', 'w').close()
    cap.wait(timeout=30)
    drive(folder, 'close')
    with open(os.path.join(out, 'cycles.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cycle', 'start_s', 'end_s', 'rms_db', 'peak_db'])
        w.writerows(rows)


if __name__ == '__main__':
    main()
