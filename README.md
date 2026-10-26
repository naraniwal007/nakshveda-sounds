# NakshVeda — Aarti / Shankh Sound Packs (packs-v1)

Background audio for the NakshVeda app's **Aarti mode**. Every mix is built only from CC0 sources (see [SOURCES.md](SOURCES.md)) plus self-synthesized layers. **There are no vocals or crowd sounds.**

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
- `assets/previews/<name>_preview_20s.mp3`: 20 s previews (MP3 192k).
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
