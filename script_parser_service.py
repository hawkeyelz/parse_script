import sys
import json
import re
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

def parse_radio_script(script_path, cast_json_path):
    script_path = Path(script_path)
    cast_json_path = Path(cast_json_path)
    
    # 1. Load the decoupled voice cast profiles
    if cast_json_path.exists():
        with open(cast_json_path, 'r') as f:
            voice_cast = json.load(f)
    else:
        voice_cast = {}

    # Define standard fallback defaults if the cast JSON is empty or missing a character block
    default_profile = {"voice_filename": "male_04.wav", "exaggeration": 0.60, "cfg_weight": 0.50}

    # 2. Read the script file
    with open(script_path, 'r') as f:
        lines = f.readlines()

    formatted_rows = []
    line_counter = 1

    # 3. Parse characters and map to voice parameters
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = re.match(r"^([A-Z0-9_\-\s]+):\s*(.*)$", line, re.IGNORECASE)
        if match:
            character = match.group(1).strip().lower()
            text = match.group(2).strip()
            
            # Fetch the character profile block, look for 'default', or use fallback dictionary
            char_profile = voice_cast.get(character, voice_cast.get("default", default_profile))
            
            # Safe parsing if the voice cast json still has a legacy raw string instead of a dictionary
            if isinstance(char_profile, str):
                voice_file = char_profile
                exaggeration = default_profile["exaggeration"]
                cfg_weight = default_profile["cfg_weight"]
            else:
                voice_file = char_profile.get("voice_filename", default_profile["voice_filename"])
                exaggeration = char_profile.get("exaggeration", default_profile["exaggeration"])
                cfg_weight = char_profile.get("cfg_weight", default_profile["cfg_weight"])
            
            formatted_rows.append({
                "line_number": line_counter,
                "character": character,
                "text": text,
                "voice_filename": voice_file,
                "exaggeration": exaggeration,
                "cfg_weight": cfg_weight,
                "output_filename": f"line_{str(line_counter).zfill(3)}.wav"
            })
            line_counter += 1

    return formatted_rows
class PipelineParserHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/parse':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
                script_path = payload.get("script_path")
                voice_cast_path = payload.get("voice_cast_path")
                
                # Execute the parsing logic
                result_data = parse_radio_script(script_path, voice_cast_path)
                
                # Send successful response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result_data).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=5000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, PipelineParserHandler)
    print(f"Parser API engine online on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    # If arguments are passed, run as CLI tool like before
    if len(sys.argv) > 2:
        results = parse_radio_script(sys.argv[1], sys.argv[2])
        print(json.dumps(results, indent=2))
    else:
        # Otherwise, default to starting up the network listener on port 5000
        run_server(port=5000)