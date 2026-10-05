# ROBIN

**ROBIN — Responsive Orchestrated Brain & Interactive Navigator**

A privacy-first, cross-device AI assistant for Windows, laptop, and Android, with a lightweight interactive 2D character interface.

## Project principles

- **User authority first:** sensitive actions require explicit policy approval.
- **Dormant when idle:** ambient character behavior must remain lightweight.
- **Sleep means sleep:** when ROBIN is put to sleep, normal interaction is disabled until the user presses `ESC` on the host runtime.
- **Local-first:** runtime state and sensitive data stay local unless a feature explicitly requires a remote service.
- **Portable:** the USB is an encrypted master/backup and recovery package, not the machine doing all computation.
- **Safe self-improvement:** ROBIN may learn and prepare upgrades, but activation of code changes requires user approval.
- **Verified actions:** computer actions follow intent → policy → execution → verification.

## Initial architecture

```text
ROBIN
├── core/          brain, intents, memory, tasks, lifecycle
├── security/      policy, permissions, approvals
├── runtime/       host/device runtime contracts
├── skills/        user-approved capabilities and learned skills
├── knowledge/     knowledge acquisition and storage contracts
├── character/     animation/state contracts
├── storage/       local/USB portability contracts
├── config/        configuration
└── tests/         automated tests
```

## Milestone 1 — foundation

The repository now contains the deterministic foundation and its automated tests. It does **not** claim that Windows automation, Android control, voice, vision, payments, gallery access, calling, or production self-upgrading are implemented yet.

Implemented foundation:

- typed application configuration
- structured logging
- lifecycle state machine
- sleep state with `ESC` wake contract
- deterministic command and intent boundaries
- provider-neutral brain shell
- safe action/policy gateway
- approval token abstraction
- persistent local memory interface
- skill/upgrade proposal boundary
- local-runtime + portable-master-backup storage contract
- health/status reporting
- automated tests
- CI workflow for Python 3.11–3.13

## Development

Python 3.11+ is the initial development target.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m robin
```

## Security boundary

ROBIN's language/AI layer must never directly execute privileged system operations. Actions are represented as typed requests and passed through the policy engine. Payment execution, unrestricted gallery access, credential extraction, and autonomous code activation are intentionally outside the initial trust boundary.
