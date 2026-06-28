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
            
        match = re.match(r"^(?:\\s*)?([A-Z0-9_\-\s]+):\s*(.*)$", line, re.IGNORECASE)
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


def run_server(host='0.0.0.0', port=5000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, PipelineParserHandler)
    print(f"Parser API engine online on {host}:{port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    # If arguments are passed, run as CLI tool like before
    if len(sys.argv) > 2:
        results = parse_radio_script(sys.argv[1], sys.argv[2])
        print(json.dumps(results, indent=2))
    else:
        # Default network listener settings
        default_host = "0.0.0.0"
        default_port = 5000
        
        # Dynamically locate parser_config.json right next to this service file
        script_dir = Path(__file__).resolve().parent
        config_path = script_dir / "parser_config.json"
        
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config_data = json.load(f)
                    # Extract server settings safely from the json config layout
                    server_settings = config_data.get("server", {})
                    default_host = server_settings.get("host", default_host)
                    default_port = server_settings.get("port", default_port)
            except Exception as e:
                print(f"Warning: Failed to read parser_config.json ({e}). Using fallbacks.", file=sys.stderr)
        
        # Start the network listener using both configured host and port
        run_server(host=default_host, port=default_port)
