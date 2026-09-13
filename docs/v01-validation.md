# v0.1 Validation Slice

The v0.1 integration slice is the executable proof path:

`work_id -> gate -> receipt -> ledger -> propose -> run -> verify -> continuity`

`needs_confirm` is a hard stop. Confirmation does not arrive by timeout; without confirmation, execution does not run and the work remains open.

Verification must write back against the same `work_id` before continuity closes the work.

The stub provider is the first implementation. The failure catalog lives in the integration test. Ollama is the next provider only after this slice is green in CI.

PI-090 and PI-091 remain architectural maps. No new PI-09x boundary is introduced here.
