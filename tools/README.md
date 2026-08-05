# Outils démos vocales AlexIA

- `dialogues.json` - source de vérité des 12 scénarios (6 métiers × nouveau/reconnu)
- `gen_tts.py` - génère les répliques via ElevenLabs v3 (`export XI_KEY=...` requis)
- `assemble12.py` - assemble les MP3 (EQ téléphone, pauses, loudnorm) + times.json
- `patch_variants.py` - injecte scénarios/timings dans les 6 pages demo-*.html
- `times.json` - timings de synchronisation des bulles (état actuel)

État : médical + avocats ont leur audio (4 fichiers assets/vo/*-{nouveau,connu}.mp3).
Restent à générer (crédits) : immobilier, construction, horeca, automobile
→ relancer gen_tts.py (reprise auto) puis assemble12.py puis patch_variants.py.
