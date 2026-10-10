# AWS factory pilot

A personal, public pilot proving reusable pinned AWS developer tools in Codex
Cloud. It produces a fictional AWS inventory with compliance findings and planned
remediations, without credentials, AWS APIs, resources, deployment or spending.

```sh
python3 scripts/inventory.py --format markdown
python3 scripts/inventory.py --format json
python3 -m unittest discover -s tests
```

The standard-library demo reads only [fictional data](data/inventory.json).
Every report labels data fictional and remediations planned; this is not a live
account assessment or an executed remediation. Account 333438771545 and
ap-southeast-1 are examples only.

## Start here

- [M7 owning Issue](https://github.com/kcloud1/aws-factory-pilot/issues/1)
- [Accepted intent](intent/0001-project-bootstrap/intent.md) and [SPEC](SPEC.md)
- [Core tooling setup/recovery](docs/ENV_PROFILE.md) and [cloud proof](docs/evidence/M7_CLOUD.md)
- [M8 repository-owned startup/readiness](docs/CLOUD_SETUP.md) ([Issue #3](https://github.com/kcloud1/aws-factory-pilot/issues/3))
- [Four-answer future app intake](docs/APP_INTAKE.md)

Agents start at AGENTS.md; conditional contracts remain SPEC, ENV, CONTEXT,
CHATGPT and the proportional AI_NATIVE_SDLC. INIT is one-time bootstrap.
Universal governance and optional starter references are retained from
[repo-starter](https://github.com/amitkarpe/repo-starter). No hosting profile or
Cloudflare release is selected for M7. New hosting/authentication/provider work
requires its own bounded intent and authority.
