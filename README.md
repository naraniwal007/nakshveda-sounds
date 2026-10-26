# NakshVeda — Aarti / Shankh Sound Packs (packs-v1)

Background audio for the NakshVeda app's **Aarti mode**. Every mix is built only from CC0 sources (see [SOURCES.md](SOURCES.md)) plus self-synthesized layers. **There are no vocals or crowd sounds.**

## What's new in v5 — ढोल अब साफ़ सुनाई देता है / dhol-dominant
- **हिन्दी:** 3 शंख के तुरंत बाद ढोल अब सबसे प्रमुख ताल है — phone speaker पर भी साफ़। ढोल की अपनी lane: ज़्यादा volume, 1.5–3 kHz की "थाप", low-end saturation; ढोल की हर थाप पर घंटा/झालर थोड़े दब जाते हैं (side-chain)। नगाड़ा अब भी मज़बूत। लगातार keherwa groove। नया `mandir_preview_10s.mp3`।
- **English:** The dhol now has its own bus:
  - +6–10 dB relative to v4;
  - a 1.5–3 kHz attack boost;
  - asymmetric low-end saturation, so the bass shows up as harmonics on small speakers;
  - bells, jhalar and the bed duck 2–3.5 dB under each dhol hit.
  - The groove is a steady keherwa with 16th-note ghost strokes.
  - Two more CC0 dholak recordings were added.
  - New: `assets/previews/mandir_preview_10s.mp3`.
- **Phone-speaker check** (200 Hz high-pass simulation, groove section): the dhol sits at −0.9 to −2.0 dB of the full mix, 7–10 dB above the bells and 4–8 dB above the nagada. In v4 it was −4.4 to −8 dB.

## हिन्दी
- **हर preview सीधे शंख से शुरू होता है।** पहले 3 बार शंखनाद, फिर तुरंत नगाड़ा, ढोल, घंटा, मंजीरा, कर्ताल और झालर की आरती groove। शुरुआत में पहले वाला ambience अब नहीं है।
- **8 mixes:** मंदिर (सामान्य), शिव (डमरू), गणेश, दुर्गा, हनुमान, लक्ष्मी, जगदीश, मृदंग (आदि ताल)।
- `assets/loops/`: हर mix का seamless loop। Android/web के लिए `.ogg` और iOS के लिए `.m4a` (AAC)। दोनों sample-exact हैं, इसलिए loop बिना झटके के चलता है।
- `assets/clips/`: `shankh_intro` (3 शंख), `shankh_naad` (1 शंख), और हर mix का `<name>_ending` (तिहाई और घंटी की गूँज)।
- `assets/previews/`: हर mix का 20 सेकंड का MP3 preview।
- Loudness: −14 LUFS, true peak ≤ −1 dBTP।
- **App में चलाने का क्रम:** `shankh_intro` → `<deity>_loop` (बार-बार) → बंद करते समय `<deity>_ending`।

## English
- **Every preview starts directly with the shankh.** Three blows lead straight into the groove: nagada and dhol prominent, with ghanta, manjira, kartal and jhalar. The old pre-shankh ambience has been removed.
- **8 mixes:** mandir (generic), shiv (damru), ganesh, durga, hanuman, lakshmi, jagdish, mridang (adi talam, tishra nadai).
- `assets/loops/<name>_loop.ogg|m4a`: seamless loops of about 27–34 s, each a whole number of bars or tala cycles.
  - `.ogg` (Vorbis 128k) is for Android and web. `.m4a` (AAC-LC 160k) is for iOS.
  - Both decode sample-exact. Each m4a is resampled to a multiple of 1024 samples, so AAC frame padding never adds a gap; this changes its length by less than 6 ms.
- `assets/clips/`:
  - `shankh_intro` (3 blows, 6.9 s)
  - `shankh_naad` (single blow, 5.6 s)
  - `<name>_ending` (tihai plus bell tail, about 6 s)
- `assets/previews/<name>_preview_20s.mp3`: 20 s previews (MP3 192k), plus `mandir_preview_10s.mp3`.
- `manifest_app.json`: the same data with flat `file` names and a `url` for each GitHub release asset (packs-v1).
- Mastered to −14 LUFS integrated, true peak ≤ −1 dBTP.
- `manifest.json` gives name, file, bytes, sha256, duration and sample count for every asset.

### Suggested playback (Flutter / just_audio)
1. Play `shankh_intro` once.
2. Loop `<deity>_loop` (use `LoopMode.one`, or a gapless `ConcatenatingAudioSource`). Use `.m4a` on iOS and `.ogg` elsewhere.
3. On stop, fade the loop for about 0.3 s and play `<deity>_ending`.

### Rebuilding
`scripts/` contains the numpy/scipy mixer and the ffmpeg mastering chain. To rebuild:
1. Download the CC0 sources from SOURCES.md into `scripts/wav/<freesound-id>.wav` (44.1 kHz stereo 16-bit).
2. Run, in order:
   - `python3 arrange.py`
   - `python3 make_assets.py`
   - `python3 loops_v4.py`
   - `python3 m4a_fix.py`
   - `python3 m4a_fix2.py`
   - `python3 manifest.py ..`

Licence: see [LICENSE.md](LICENSE.md). The sources are CC0. The mixes are © AXIORA GLOBAL SYSTEMS PVT LTD.
