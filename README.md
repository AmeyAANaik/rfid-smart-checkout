# RFID Smart Checkout Simulator

Software-only, reproducible virtual checkout experiment. **Not an electromagnetic / UHF antenna simulation.**

## Run
Requires Python 3.10+ with no third-party dependencies.

```bash
python -m unittest discover -s tests -v
python simulator.py
```

## Models
- 20 inside-tag EPCs, one outside-tag EPC
- independently sampled tag read probability, repeated scan cycles
- EPC deduplication, missed items, false inclusions and invoice calculation
- configurable probabilities and reproducible random seeds

These probabilities are illustrative, **not** estimates of any particular reader's performance.

## Next steps
Build a Java reader adapter and billing state machine, model realistic anti-collision scheduling, investigate antenna coverage with openEMS, and validate assumptions against an actual certified reader.
