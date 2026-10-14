"""Drive a running shinobido2.exe from boot to the field of the first mission on the mission board,
from a save at the hub in slot 1 (e.g. the hub-day1 save). Each step presses a button, then waits
until the screen shows what the next step expects (a reference crop matched against a screenshot),
so menu timing doesn't matter.

usage: python -I to-mission.py <folder with shinobido2.exe> [screenshot dir]
         (the game must already be started: v3kdrive.py <folder> start)
       python -I to-mission.py --capture <screen name> <screenshot>   (set a reference)
"""
import os
import subprocess
import sys
import time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DRIVE = os.path.join(HERE, '..', 'third_party', 'recomp', 'tools', 'v3kdrive.py')

# screens, recognised by regions (960x544 coordinates) of a reference screenshot: the mean absolute
# pixel difference must stay under a limit. The references are screenshots of the game, so they
# live in the game project's ignored build/ folder (tools/to-mission.py --capture <name> saves one).
REF_DIR = os.path.join('build', 'screens')
SCREENS = {
    'title': [(380, 478, 580, 502)],         # the "Press START button" bar
    'menu': [(100, 160, 340, 280)],          # "New Game" / "Continue"
    'load_list': [(0, 30, 960, 190)],        # the Load dialog's title and first row
    'load_confirm': [(130, 230, 830, 470)],  # "Do you want to load...?" and No / Yes
    'load_done': [(130, 230, 830, 470)],     # "Loading complete." and OK
    # the menu, the message bar and the button help (the banner shows the background, which changes)
    'hub': [(60, 100, 330, 450), (0, 475, 700, 505), (0, 505, 960, 544)],
    'field': [(0, 410, 230, 544)],           # the HUD's tool diamond bottom left
}
LIMIT = 18.0


def drive(folder, *args):
    return subprocess.run([sys.executable, '-I', DRIVE, folder, '--exe', 'shinobido2.exe', *args],
                          capture_output=True, text=True)


def screen(folder, path):
    drive(folder, 'run', f'shot:{path}', os.devnull)
    for _ in range(20):
        if os.path.exists(path):
            break
        time.sleep(0.2)
    return Image.open(path).convert('RGB').resize((960, 544))


def matches(img, name):
    ref_path = os.path.join(REF_DIR, name + '.png')
    if not os.path.exists(ref_path):
        sys.exit(f'to-mission: no reference {ref_path} (capture it with --capture {name})')
    ref = Image.open(ref_path).convert('RGB').resize((960, 544))
    for box in SCREENS[name]:
        a, b = img.crop(box).tobytes(), ref.crop(box).tobytes()
        if sum(abs(x - y) for x, y in zip(a, b)) / len(a) > LIMIT:
            return False
    return True


def wait_for(folder, shots, name, timeout, press=None, every=6.0):
    """until the screen is `name`: take screenshots; if `press` is given, press it every `every`
    seconds meanwhile (for screens that need a nudge)"""
    start = time.time()
    last_press = 0.0
    n = 0
    while time.time() - start < timeout:
        path = os.path.join(shots, f'wait-{name}-{n}.png')
        n += 1
        img = screen(folder, path)
        if matches(img, name):
            os.replace(path, os.path.join(shots, f'{name}.png'))
            return True
        os.remove(path)
        if press and time.time() - last_press > every:
            drive(folder, 'run', press, os.devnull)
            last_press = time.time()
        time.sleep(1)
    print(f'to-mission: no "{name}" screen within {timeout} s (see {shots})', file=sys.stderr)
    img.save(os.path.join(shots, f'timeout-{name}.png'))
    return False


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == '--capture':
        # --capture <name> <screenshot>: make <screenshot> the reference for <name>
        os.makedirs(REF_DIR, exist_ok=True)
        Image.open(sys.argv[3]).convert('RGB').resize((960, 544)).save(os.path.join(REF_DIR, sys.argv[2] + '.png'))
        return
    folder = sys.argv[1]
    shots = sys.argv[2] if len(sys.argv) > 2 else os.path.join('build', 'drive')
    os.makedirs(shots, exist_ok=True)
    # Start during the logos skips nothing; on the title it opens the menu; during the attract
    # movie the title shows if nothing is pressed for a while, and Start returns to it
    if not wait_for(folder, shots, 'menu', 180, 'start', every=5.0):
        sys.exit(1)
    steps = [
        ('load_list', 20, 'cross'),          # Continue -> the Load dialog
        ('load_confirm', 15, 'cross'),       # slot 1 -> "load this saved data?"
        ('load_done', 30, 'hold:right:250,wait 800,cross'),  # Yes (on the right) -> "Loading complete."
        ('hub', 40, 'cross'),                # OK -> the hub
    ]
    for name, timeout, press in steps:
        if press:
            drive(folder, 'run', press, os.devnull)
        if not wait_for(folder, shots, name, timeout):
            sys.exit(1)
    # Missions -> first mission -> details -> start, then the field
    drive(folder, 'run', 'cross,wait 3500,cross,wait 3500,cross,wait 3000,cross', os.devnull)
    if not wait_for(folder, shots, 'field', 60):
        sys.exit(1)
    print('to-mission: in the field')


if __name__ == '__main__':
    main()
