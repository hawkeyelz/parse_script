 # Chatterbox Turbo Voice Profile Documentation

This guide outlines how to configure character performance weights inside the `voice_cast.json` profile map. By adjusting these parameters, you can alter the emotional delivery, energy, and stability of a single voice file across multiple character variants.

## Parameter Reference

### 1. Exaggeration (`exaggeration`)
Controls the intensity, pitch variance, and dramatic emphasis of the delivery.
* **Low Values (0.30 - 0.50):** Flat, muted, conversational, or deadpan. Useful for a tired detective, a subtle whisper, or natural under-the-breath dialogue.
* **Standard Value (0.60):** The baseline narrative tone. Natural cadence and human inflection.
* **High Values (0.80 - 1.00):** Highly theatrical, expressive, or booming. Essential for energetic radio announcers, shouting, panicking characters, or dramatic narrative hooks.

### 2. CFG Weight (`cfg_weight`)
*Classifier-Free Guidance.* Controls how strictly the model adheres to the text prompt versus allowing its neural weights to inject loose, chaotic, or human-like variation.

$$\text{Final Output} = \text{Unconditioned} + \text{CFG Weight} \times (\text{Conditioned} - \text{Unconditioned})$$

* **Low Values (0.30 - 0.45):** Loosens the model's focus. The voice becomes unpredictable, erratic, and raw. This introduces natural human imperfections, breathing patterns, or a slightly creepy, unstable theatrical drawl.
* **Standard Value (0.50):** Optimal balance. Clear pronunciation with enough micro-variation to sound fluid and non-robotic.
* **High Values (0.70 - 1.00+):** Forces intense focus on clean dictation. The voice sounds crisp, highly stylized, sharp, and authoritative. Excellent for punchy, fast-paced announcer delivery.

> **VRAM Note:** Setting CFG too high on a 4GB VRAM limit can occasionally cause audio clipping or metallic saturation as the math over-constrains the generation loop.

---

## Performance Recipe Matrix

Use these baseline configurations when building your character variants:

| Performance Style | Exaggeration | CFG Weight | Best Used For |
| :--- | :--- | :--- | :--- |
| **Standard Narrator** | `0.60` | `0.50` | Default reading, documentation, flat storytelling. |
| **Old-Time Announcer** | `0.95` | `0.85` | Booming intros, commercial breaks, high-energy hooks. |
| **Excited / Shouting** | `0.90` | `0.75` | Action sequences, punchy delivery, elevated energy. |
| **Suspenseful / Creepy** | `0.80` | `0.40` | Low stability, dramatic pauses, unstable villain dialogue. |
| **Subdued / Whisper** | `0.40` | `0.35` | Intimate dialogue, quiet scenes, tired or defeated characters. |
