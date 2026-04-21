# Architecture

## Runtime map
- `src/zpe_smell/codec.py`: odorant model, corpus construction, smell bundle encode/decode path.
- `src/zpe_smell/stream.py`: minimal stream routing used to verify nuisance-prefix handling.
- `src/zpe_smell/evaluation.py`: fixed benchmark evaluation and public proof artifact assembly.
- `src/zpe_smell/reproduce.py`: CLI entry point that regenerates the public JSON artifact.

## Data shape
- The committed corpus contains 35 smell episodes.
- Every episode is converted into a bundle of extension words with a smell preamble and checksum.
- Evaluation compares decoded bundles against the fixed reference geometry on the same surface.

## Public proof flow
1. Build the default surrogate receptor-response model.
2. Generate the fixed 35-episode corpus.
3. Encode and decode the corpus.
4. Score the decoded result against the reference surface.
5. Write the public artifact JSON and compare it to the committed reference.
