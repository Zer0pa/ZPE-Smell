# ZPE-Smell Novelty Card

**Product:** ZPE-Smell
**Domain:** Olfactory receptor-panel encoding — surrogate competitive-binding receptor-response panel
**What we sell:** Reproducible bounded smell codec over a fixed 35-episode surrogate receptor-response benchmark surface; useful now for audit and replication on that declared surface, and improving continuously

**Status:** Research in Progress — bounded to the declared surrogate receptor-response scope; not yet admitted to the broader Zer0pa cross-lane certified graph

## Novel contributions

1. **Receptor-panel-identity transport for odour mixtures** — The codec carries odour mixtures as a fully structured bundle over competitive-binding receptor states. Each sniff encodes the 3D latent base point, the complete 8-channel receptor-panel fiber weights, per-channel adaptation state, and pairwise residual correction, rather than collapsing the mixture to a sparse sketch. The preservation of full receptor-panel identity through the encode/decode path — on the declared surrogate receptor-response scope — is the candidate novel contribution. Code: [`src/zpe_smell/codec.py:386-429`](../../../src/zpe_smell/codec.py) (encode) and [`src/zpe_smell/codec.py:432-540`](../../../src/zpe_smell/codec.py) (decode). The competitive-binding state that drives encoding is computed at [`src/zpe_smell/codec.py:319-338`](../../../src/zpe_smell/codec.py). Nearest prior art: receptor-space smell descriptors and Euclidean projections from molecular structure; none known to package the full receptor-panel vector with explicit adaptation and residual channels in a self-verifying bundle with committed proof artifacts. What is genuinely new here: the specific combination of base-point + fiber + adaptation + residual in a single verifiable word-stream bundle on a declared surrogate surface.

2. **Competitive-binding adaptation model with pairwise residual correction** — The codec computes receptor activation via a competitive-binding function (Ehlert / occupancy-theory form) then applies a sniff-history adaptation state and mixture-pair residual corrections before encoding. This gives the stream explicit history sensitivity and pairwise interaction fidelity within the bundle. Code: [`src/zpe_smell/codec.py:319-338`](../../../src/zpe_smell/codec.py) (`_competitive_binding`); residual-pair definitions at [`src/zpe_smell/codec.py:258-272`](../../../src/zpe_smell/codec.py). What is genuinely new here: the specific integration of the adaptation track and residual track into the bundle word stream on the surrogate scope.

3. **Image-prefixed nuisance-routing gate in the smell stream** — The stream router (`src/zpe_smell/stream.py`) keeps image-prefixed words correctly routed even when prepended to a smell bundle, and the evaluation surface tests this property at zero attack-success rate. Code: [`src/zpe_smell/stream.py:18-54`](../../../src/zpe_smell/stream.py) (`iter_stream`); gate exercised at [`src/zpe_smell/evaluation.py:200-213`](../../../src/zpe_smell/evaluation.py).

## Standard techniques used (explicit, not novel)

- Occupancy / competitive-binding receptor models (standard pharmacology)
- Linear projection from receptor space to 3D latent (pseudoinverse, `numpy.linalg.pinv`)
- Fixed-point uniform quantisation for unit and signed-unit values
- Scalar product checksum over packed payload words
- Spearman rank correlation as a retrieval fidelity metric
- Nearest-neighbour recall at 1 as a retrieval metric
- NumPy / SciPy numerics throughout

## Compass-8 / 8-primitive architecture

NO — ZPE-Smell does not implement the Compass-8 directional encoding pattern. The codec uses a smell bundle over competitive-binding receptor states with full receptor-panel identity transport, adaptation, and residual channels. There is no directional token alphabet, no Freeman-chain-code-derived encoding, and no 3-bit directional primitive in the word stream. Confirmed by inspection of [`src/zpe_smell/codec.py`](../../../src/zpe_smell/codec.py) and [`src/zpe_smell/stream.py`](../../../src/zpe_smell/stream.py) — no Compass-8 implementation present. This is consistent with LICENSE §7.14 and the ground-truth declaration of NO for this repo.

## Open novelty questions for the license agent

- The competitive-binding model and adaptation track are the genuine differentiators from a pure receptor-vector sketch; the license agent should confirm whether these warrant independent schedule entries or sit under the single receptor-panel-identity transport claim.
- The "research-in-progress" label is accurately applied here: the outstanding item for admission to the certified subset is an inter-lane admission witness, not lane-local validity. The lane-local benchmark clears cleanly on the committed surrogate scope.
