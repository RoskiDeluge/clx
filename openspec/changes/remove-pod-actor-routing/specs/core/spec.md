## REMOVED Requirements
### Requirement: Pod/actor routing
The system SHALL build a `/pods/{pod}/actors/{actor}/run` backend path when pod/actor identifiers are provided.

#### Scenario: Pod/actor path resolution
- **WHEN** the user provides `pod_name` and `actor_id` (or related env vars)
- **THEN** the client uses `/pods/{pod}/actors/{actor}/run` instead of `/v1/query`

**Reason**: This route is specific to Paseo and conflicts with a strictly backend-agnostic contract.
**Migration**: Use a backend that implements `/v1/query` and configure `CLX_BACKEND_URL`.
