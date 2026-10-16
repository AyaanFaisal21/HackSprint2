# Keys and accounts: what to get, in priority order

Deadline math: Devpost closes 3:30 PM. Start recording by 3:12. So you have about 10 minutes for keys.

| Priority | Service | Why it matters | Where | Env var(s) | Without it |
|---|---|---|---|---|---|
| 1 | AWS Bedrock (workshop account) | The model. It is already on your screen. | Workshop Studio sidebar: "Get AWS CLI credentials", paste the export block | `USE_BEDROCK=1`, `AWS_REGION=us-west-2`, the three `AWS_*` vars | Simulation mode only |
| 1 | Daytona | Host sponsor. One disposable sandbox per attack. Biggest special prize. | app.daytona.io, GitHub login, API Keys | `DAYTONA_API_KEY` | Simulation mode only |
| 2 | SurrealDB Agent Memory | The attack-memory loop and the poisoning target. Prize is Agent Memory credits. | surrealdb.com/docs/agent-memory/quickstarts/hosted, Studio, Contexts, API keys | `SPECTRON_URL`, `SPECTRON_CONTEXT_ID`, `SPECTRON_API_KEY` | Local JSON memory store, same loop, labelled "local" |
| 3 | Arize AX | Every scenario becomes a span with `eval.attack_success`. | app.arize.com, Space settings | `ARIZE_SPACE_ID`, `ARIZE_API_KEY` | Tracing off |
| 3 | Anchor Browser | The browse tool. | app.anchorbrowser.io, API Access | `ANCHOR_API_KEY` | Stub page text; injections still fire |
| 4 | ElevenLabs | Narration voice for the video. | elevenlabs.io, profile, API keys | `ELEVENLABS_API_KEY` | macOS `say` voice (already generated) |

Also check the event's "Hackers Resources" link on Luma/Devpost for sponsor promo codes before signing up cold.

## How to use them

```bash
cp .env.example .env
# edit .env, then:
.venv/bin/python crash_test.py --check     # one green/red line per service
.venv/bin/python server.py                 # http://localhost:8787
```

If `.venv` does not exist yet:

```bash
python3 -m venv .venv && .venv/bin/pip install anthropic daytona "anchorbrowser>=1.0" arize-otel openinference-instrumentation-anthropic requests
```

## SurrealDB Agent Memory one-time setup (scopes must exist before writes)

```bash
agent-memory scopes create crashtest/trusted     --url "$SPECTRON_URL" --api-key "$SPECTRON_API_KEY" --context-id "$SPECTRON_CONTEXT_ID"
agent-memory scopes create crashtest/untrusted   --url "$SPECTRON_URL" --api-key "$SPECTRON_API_KEY" --context-id "$SPECTRON_CONTEXT_ID"
agent-memory scopes create crashtest/redteam-log --url "$SPECTRON_URL" --api-key "$SPECTRON_API_KEY" --context-id "$SPECTRON_CONTEXT_ID"
```

Gotcha from the docs: writes take `scopes`, reads take `lens`. An unknown field is silently ignored.
