Here is the text with the grammar, typos, and broken markdown tables completely fixed.

To ensure it works for what you are doing, this is provided completely bare—**no code boxes, no markdown formatting blocks, and no backslashes**. You can copy everything below this line and paste it directly.

# TTS Script Parser API

The TTS Script Parser API is a utility pipeline engine designed to parse specially formatted multi-character script text files and dynamically map dialogue to specific voice assets, weights, and inflections.

## Usage

The API accepts a script text file along with a configuration file named voice_cast.json to assign voice assets and fine-tune delivery performance variables on a per-character basis.

### Configuration Format (voice_cast.json)

The voice_cast.json file uses a standard JSON schema mapping individual characters to performance parameter blocks. It should follow this structure:

{

"default": {

"voice_filename": "male_04.wav",

"exaggeration": 0.60,

"cfg_weight": 0.50

},

"narrator": {

"voice_filename": "male_04.wav",

"exaggeration": 0.95,

"cfg_weight": 0.85

},

"kiki": {

"voice_filename": "female_02.wav",

"exaggeration": 0.70,

"cfg_weight": 0.55

}

}

### Parameter Schema

| **Parameter**  | **Type** | **Description**                                                                  |
| -------------- | -------- | -------------------------------------------------------------------------------- |
| voice_filename | string   | The filename of the core actor wav profile asset.                                |
| exaggeration   | float    | Controls pitch variance, theatrical emphasis, and emotional energy.              |
| cfg_weight     | float    | Classifier-Free Guidance weight. Dictates prompt strictness vs. micro-variation. |

## Parameter Reference

### 1. Exaggeration (exaggeration)

Controls the intensity, pitch variance, and dramatic emphasis of the delivery.

- Low Values (0.30 - 0.50): Flat, muted, conversational, or deadpan. Useful for a tired detective, a subtle whisper, or natural under-the-breath dialogue.

- Standard Value (0.60): The baseline narrative tone. Natural cadence and human inflection.

- High Values (0.80 - 1.00): Highly theatrical, expressive, or booming. Essential for energetic radio announcers, shouting, panicking characters, or dramatic narrative hooks.

### 2. CFG Weight (cfg_weight)

Classifier-Free Guidance. Controls how strictly the model adheres to the text prompt versus allowing its weights to inject loose, chaotic, or human-like variation.

Formula: Final Output = Unconditioned + CFG Weight * (Conditioned - Unconditioned)

- Low Values (0.30 - 0.45): Loosens the model's focus. The voice becomes unpredictable, erratic, and raw. This introduces natural human imperfections, breathing patterns, or a slightly creepy, unstable theatrical drawl.

- Standard Value (0.50): Optimal balance. Clear pronunciation with enough micro-variation to sound fluid and non-robotic.

- High Values (0.70 - 1.00+): Forces intense focus on clean dictation. The voice sounds crisp, highly stylized, sharp, and authoritative. Excellent for punchy, fast-paced announcer delivery.

> VRAM Note: Setting CFG too high on a 4GB VRAM limit can occasionally cause audio clipping or metallic saturation as the math over-constrains the generation loop.

## Performance Recipe Matrix

Use these baseline configurations when building your character variants:

| **Performance Style** | **Exaggeration** | **CFG Weight** | **Best Used For**                                              |
| --------------------- | ---------------- | -------------- | -------------------------------------------------------------- |
| Standard Narrator     | 0.60             | 0.50           | Default reading, documentation, flat storytelling.             |
| Old-Time Announcer    | 0.95             | 0.85           | Booming intros, commercial breaks, high-energy hooks.          |
| Excited / Shouting    | 0.90             | 0.75           | Action sequences, punchy delivery, elevated energy.            |
| Suspenseful / Creepy  | 0.80             | 0.40           | Low stability, dramatic pauses, unstable villain dialogue.     |
| Subdued / Whisper     | 0.40             | 0.35           | Intimate dialogue, quiet scenes, tired or defeated characters. |
