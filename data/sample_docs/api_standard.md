# Internal API Engineering Standard — Synthetic Demo

Document ID: API-001

## Authentication
All non-public APIs require authenticated callers. Service-to-service APIs use short-lived workload credentials. Privileged operations must require OAuth 2.0 access tokens with an explicitly approved privileged scope.

API keys alone are not sufficient for privileged operations. Long-lived shared credentials are prohibited.

## Authorisation
Authorisation must be enforced server-side for every privileged operation. A successful authentication does not imply authorisation.

## Transport security
Production API traffic must use TLS. Plain-text HTTP is not permitted for production service communication.

## Logging
Privileged write operations must produce an audit event containing the caller identity, operation, target resource, result and timestamp. Secrets and access tokens must not be written to application logs.

## Rate controls
Externally reachable APIs must define rate limits appropriate to the service risk and expected load.
