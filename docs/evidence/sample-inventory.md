# Fictional AWS inventory

Example data only. No AWS calls or executed remediations.

Account example: 333438771545 · Region: ap-southeast-1 · Deployment: NONE

Resources: 3 · Findings: 3 · Resources without findings: 1

| Resource | Service | Example findings |
| --- | --- | --- |
| demo-assets | s3 | owner-tag, public-access |
| demo-database | rds | None in this mock |
| demo-web | ec2 | encryption |

## Planned remediations

- demo-assets / owner-tag (low, PLANNED): Plan an Owner tag after separate authorization.
- demo-assets / public-access (high, PLANNED): Review access requirements and plan private access after separate authorization.
- demo-web / encryption (medium, PLANNED): Plan an encrypted replacement after separate authorization.
