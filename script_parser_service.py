import sys
import json
import re
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

# Define standard fallback defaults if the cast JSON is empty or missing a character block
default_profile = {"voice_filename": "male_04.wav", "exaggeration": 0.60, "cfg_weight": 0.50, "speed_factor": 1.0}

def load_voice_cast(cast_json_path):
    """Load the decoupled voice cast profiles from disk."""
    cast_json_path = Path(cast_json_path)
    if cast_json_path.exists():
        with open(cast_json_path, 'r') as f:
            return json.load(f)
    return {}

def build_row(line_counter, character, text, voice_cast):
    """Map a single parsed line to its voice parameters and output filename."""
    char_profile = voice_cast.get(character, voice_cast.get("default", default_profile))

    # Safe parsing if the voice cast json still has a legacy raw string instead of a dictionary
    if isinstance(char_profile, str):
        voice_file = char_profile
        exaggeration = default_profile["exaggeration"]
        cfg_weight = default_profile["cfg_weight"]
        speed_factor = default_profile["speed_factor"]
    else:
        voice_file = char_profile.get("voice_filename", default_profile["voice_filename"])
        exaggeration = char_profile.get("exaggeration", default_profile["exaggeration"])
        cfg_weight = char_profile.get("cfg_weight", default_profile["cfg_weight"])
        speed_factor = char_profile.get("speed_factor", default_profile["speed_factor"])

    return {
        "line_number": line_counter,
        "character": character,
        "text": text,
        "voice_filename": voice_file,
        "exaggeration": exaggeration,
        "cfg_weight": cfg_weight,
        "speed_factor": speed_factor,
        "output_filename": f"line_{str(line_counter).zfill(3)}.wav"
    }

def parse_lines(lines, voice_cast):
    """Core parsing logic — accepts a list of raw text lines."""
    formatted_rows = []
    line_counter = 1

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(r"^(?:\s*)?([A-Z0-9_\-\s]+):\s*(.*)$", line, re.IGNORECASE)
        if match:
            character = match.group(1).strip().lower()
            text = match.group(2).strip()
            formatted_rows.append(build_row(line_counter, character, text, voice_cast))
            line_counter += 1

    return formatted_rows

def parse_radio_script(script_path, cast_json_path):
    """Parse a script from a file path on disk."""
    voice_cast = load_voice_cast(cast_json_path)
    with open(script_path, 'r') as f:
        lines = f.readlines()
    return parse_lines(lines, voice_cast)

def parse_radio_script_from_text(script_text, cast_json_path):
    """Parse a script from a raw text string (e.g. passed in via n8n form)."""
    voice_cast = load_voice_cast(cast_json_path)
    lines = script_text.splitlines()
    return parse_lines(lines, voice_cast)


class PipelineParserHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/parse':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                payload = json.loads(post_data.decode('utf-8'))
                script_path = payload.get("script_path")
                script_text = payload.get("script_text")
                voice_cast_path = payload.get("voice_cast_path")

                if not voice_cast_path:
                    raise ValueError("voice_cast_path is required.")

                # Prefer raw text if provided (n8n form mode), fall back to file path (CLI/test mode)
                if script_text:
                    result_data = parse_radio_script_from_text(script_text, voice_cast_path)
                elif script_path:
                    result_data = parse_radio_script(script_path, voice_cast_path)
                else:
                    raise ValueError("Must provide either script_path or script_text in the request payload.")

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

    def log_message(self, format, *args):
        # Suppress default per-request console noise; swap for logging if needed
        pass


def run_server(host='0.0.0.0', port=5000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, PipelineParserHandler)
    print(f"Parser API engine online on {host}:{port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    # CLI mode: python script_parser_service.py <script_path> <voice_cast_path>
    if len(sys.argv) > 2:
        results = parse_radio_script(sys.argv[1], sys.argv[2])
        print(json.dumps(results, indent=2))
    else:
        # Server mode: read config and start listener
        default_host = "0.0.0.0"
        default_port = 5000

        script_dir = Path(__file__).resolve().parent
        config_path = script_dir / "parser_config.json"

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config_data = json.load(f)
                    server_settings = config_data.get("server", {})
                    default_host = server_settings.get("host", default_host)
                    default_port = server_settings.get("port", default_port)
            except Exception as e:
                print(f"Warning: Failed to read parser_config.json ({e}). Using fallbacks.", file=sys.stderr)

        run_server(host=default_host, port=default_port)