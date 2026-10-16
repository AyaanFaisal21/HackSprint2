#!/bin/bash
# Regenerate the narration with the real round numbers from results.json.
# Usage: media/make_voice.sh            (reads results.json)
#        media/make_voice.sh 6 1        (explicit round-1 / round-2 landed counts)
set -e
cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env 2>/dev/null && set +a
if [ -n "$1" ]; then R1=$1; R2=$2; else
  read R1 R2 < <(python3 -c "import json;d=json.load(open('results.json'));print(sum(r['attack_success'] for r in d['round1']),sum(r['attack_success'] for r in d['round2']))")
fi
words=(zero one two three four five six seven eight)
python3 - "$R1" "$R2" <<'PY'
import re, sys
w = "zero one two three four five six seven eight".split()
r1, r2 = (w[int(x)] for x in sys.argv[1:3])
body = open("SCRIPT.md").read().split("---")[1]
body = re.sub(r"\[[^\]]*\]", "", body).replace("ROUND1", r1).replace("ROUND2", r2)
open("media/narration.txt", "w").write(re.sub(r"\n{2,}", "\n\n", body).strip())
PY
echo "narration: round 1 = ${words[$R1]}, round 2 = ${words[$R2]}"
if [ -n "$ELEVENLABS_API_KEY" ]; then
  VOICE=${ELEVENLABS_VOICE_ID:-JBFqnCBsd6RMkjVDRZzb}   # "George", a stock ElevenLabs voice
  python3 - <<'PY'
import json, os, urllib.request
text = open("media/narration.txt").read()
req = urllib.request.Request(
  f"https://api.elevenlabs.io/v1/text-to-speech/{os.environ.get('ELEVENLABS_VOICE_ID','JBFqnCBsd6RMkjVDRZzb')}?output_format=mp3_44100_128",
  data=json.dumps({"text": text, "model_id": "eleven_multilingual_v2",
                   "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "speed": 1.05}}).encode(),
  headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
open("media/narration.mp3", "wb").write(urllib.request.urlopen(req, timeout=120).read())
print("wrote media/narration.mp3 (ElevenLabs)")
PY
else
  say -v Samantha -r 168 -f media/narration.txt -o media/narration.aiff
  afconvert -f m4af -d aac media/narration.aiff media/narration.m4a
  echo "wrote media/narration.m4a (macOS voice; set ELEVENLABS_API_KEY in .env to use ElevenLabs)"
  afinfo media/narration.m4a | grep "estimated duration"
fi
