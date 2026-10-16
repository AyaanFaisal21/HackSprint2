# Record and submit (12 minutes, start no later than 3:12)

## 0. Before recording (2 min)
1. The server is already running on port 8787 (started by Claude). Do not start a second one. If http://localhost:8787 does not load, run `cd ~/Documents/CrashTest && .venv/bin/python server.py` in a terminal.
2. Chrome: open http://localhost:8787 full screen (Ctrl+Cmd+F). Hide the bookmarks bar (Cmd+Shift+B).
3. Click through the four tabs once so fonts and the 3D hero are warm. Reload. Leave the "dry run" box unchecked so the run is live.
4. Open `media/narration.m4a` in QuickTime but do not press play yet.

## 1. Record (3 min) - one-take method, no editing
1. Cmd+Shift+5, choose "Record Selected Window" or the full screen, Options: Microphone = built-in mic (this captures the narration playing from your speakers), turn volume to about 70%.
2. Click Record, press play on narration.m4a, and alt-tab back to Chrome within one second.
3. Follow the bracketed screen directions in SCRIPT.md. Click "Launch crash test" when the narration says "Let's launch."
4. Stop with the stop icon in the menu bar. The .mov lands on the Desktop.

If you have an extra 4 minutes, the clean method: record with Microphone = none, then in iMovie drag the .mov to the timeline, drag narration.m4a under it, Share > File > 1080p.

## 2. Upload (3 min)
YouTube Studio > Create > Upload, visibility Unlisted, title "Crash Test - Daytona HackSprint NYC". Copy the link as soon as it appears; processing can finish after you submit.

## 3. Devpost (3 min)
Paste from DEVPOST.md: name, tagline, the story sections, built-with tags. Video link. Add 2 screenshots (Run tab mid-run and the final scoreboard). Repo link if pushed. Submit, then confirm the submission page shows "Submitted".

## Repo push (only if time remains after submitting)
```bash
cd ~/Documents/CrashTest && git init -q && git add -A && git commit -qm "Crash Test: red-team harness with attack memory" && gh repo create crash-test --public --source=. --push
```
`.gitignore` already excludes `.env`, the venv, logs and generated media.

## Decision at 3:12
- Live run finished (dashboard badge says LIVE, scoreboard filled): record the live run. Run `media/make_voice.sh` first so the narration carries the real numbers.
- Live run still going or broken: record in simulation. Start the server, open http://localhost:8787/?demo=1 (badge says REPLAY) or launch with the dry-run option, and insert "in simulation" after "Let's launch" when the narration reaches that line. Say so plainly in the Devpost text under Challenges; the judges respect it more than a hidden stub.
