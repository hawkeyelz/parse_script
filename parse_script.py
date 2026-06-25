import sys
import json
import re
from pathlib import Path

def parse_radio_script(script_path, cast_json_path):
    script_path = Path(script_path)
    cast_json_path = Path(cast_json_path)
    
    # 1. Load the decoupled voice cast
    if cast_json_path.exists():
        with open(cast_json_path, 'r') as f:
            voice_cast = json.load(f)
    else:
        voice_cast = {"default": "male_04.wav"}

    # 2. Read the script file
    with open(script_path, 'r') as f:
        lines = f.readlines()

    formatted_rows = []
    line_counter = 1

    # 3. Parse characters and map to voice files
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = re.match(r"^([A-Z0-9_\s]+):\s*(.*)$", line, re.IGNORECASE)
        if match:
            character = match.group(1).strip().lower()
            text = match.group(2).strip()
            
            voice_file = voice_cast.get(character, voice_cast.get("default", "male_04.wav"))
            
            formatted_rows.append({
                "line_number": line_counter,
                "character": character,
                "text": text,
                "voice_filename": voice_file,
                "output_filename": f"line_{str(line_counter).zfill(3)}.wav"
            })
            line_counter += 1

    # 4. Print clean JSON to stdout for n8n to catch
    print(json.dumps(formatted_rows, indent=2))

if __name__ == "__main__":
    # Expects arguments: python parse_script.py [script.txt] [voice_cast.json]
    if len(sys.argv) > 2:
        parse_radio_script(sys.argv[1], sys.argv[2])