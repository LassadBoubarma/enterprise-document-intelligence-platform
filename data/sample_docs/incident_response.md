# Production Incident Response Guide — Synthetic Demo

Document ID: INC-001

## Severity 1 definition
A Severity 1 (Sev-1) incident is an event causing major customer impact, loss of a critical service, confirmed compromise of a production system, or a material risk of data exposure.

## First actions
The first engineer or analyst who confirms a Sev-1 incident must create an incident record immediately, page the on-call incident commander and preserve relevant logs. The responder must not delete or overwrite evidence.

For a suspected security compromise, the Security team must be added to the incident bridge as soon as the incident is declared. Customer-facing communications are coordinated by the incident commander and the designated communications owner.

## Containment and recovery
Containment actions should reduce harm while preserving evidence. Emergency production changes must be documented in the incident record. After recovery, the team must complete a post-incident review within five business days.

## Post-incident review
The review records timeline, impact, root cause, contributing factors, corrective actions and owners. Corrective actions require target dates.
