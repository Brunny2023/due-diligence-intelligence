# V2.2 OpenRouter Deployment Guide

## Purpose and architecture

V2.2 preserves the V2.1 evidence methodology and adds only an optional, run-on-demand contextual-inference boundary. A user starts one substantive investigation in Capafy. After the existing untrusted-content and disclosure controls determine that external inference is permitted, `scripts/inference_provider.py` reads non-secret configuration from `config/inference_runtime.json`, obtains the hosted runtime credential from the execution environment, and sends a non-streaming request to the configured OpenRouter model. The existing deterministic V2.1 scripts then validate inputs, track evidence, assemble the report, and run quality gates before the result is returned.

```text
Capafy user invocation
  → V2.2 Skill scope, permission, and untrusted-content controls
  → OpenRouter provider adapter (only for the invoked contextual task)
  → publisher-configured reasoning model
  → preserved V2.1 evidence / verification / decision workflow
  → deterministic report assembly and quality checks
  → validated output to the Capafy user
```

The package does not start a service, poll, schedule inference, retain an idle model process, or create a usage counter. The adapter runs only when the agent explicitly invokes `complete()` for a permitted investigation.

## Runtime configuration

| Setting | Package default | Production rule |
| --- | --- | --- |
| Provider | `openrouter` | V2.2 supports OpenRouter through an abstraction that can later support another provider. |
| Base URL | `https://openrouter.ai/api/v1` | Keep HTTPS and the approved OpenRouter host unless the package is security-reviewed again. |
| Completion path | `/chat/completions` | Used only for explicitly permitted contextual inference. |
| Credential variable | `OPENROUTER_API_KEY` | Host it in Capafy; never place a value in this package, a report, a log, or a user-facing message. |
| Model variable | `DDI_OPENROUTER_MODEL` | Required in production. The publisher supplies an exact current OpenRouter model identifier. |
| Temperature | `0.1` | Configurable in `config/inference_runtime.json`. |
| Maximum output tokens | `3000` | Configurable in `config/inference_runtime.json`. |
| Timeout | `45` seconds | Configurable in `config/inference_runtime.json`. |
| Retry policy | One retry after 0.25 seconds | Only transient rate-limit, timeout, network, or provider-availability errors can retry. |
| Local/CI mode | `DDI_INFERENCE_MODE=mock` | Uses no credential and makes no network request. |

The exact deployed model is deliberately **not** embedded in source or in the configuration file. The current OpenRouter documentation shows `openai/gpt-5.2` as a valid example identifier, but it is only a verified non-production example. Before publication, the publisher must confirm the selected model’s exact current identifier using the OpenRouter Models API or catalog and map that identifier to `DDI_OPENROUTER_MODEL`. The package does not assume any unverified identifier such as “Opus 5.” [1] [2]

> **Credential handling boundary.** Capafy’s current publishing guidance says publishers select the credentials required at runtime and choose **Host**. Capafy describes hosted credentials as encrypted-vault values injected at runtime, but the viewed documentation does not specify the exact variable name or retrieval API available to package code. Therefore this package names `OPENROUTER_API_KEY` as its implementation requirement; the publisher must confirm or map that name in the live hosted-credential flow rather than relying on an undocumented Capafy convention. [3] [4]

## Capafy Publisher Console setup

1. Choose **Run on Capafy** and upload the complete V2.2 package, including `SKILL.md`, `scripts/`, `config/`, `references/`, disclosures, tests, and deployment documentation.
2. In the credential handling step, identify the OpenRouter credential surfaced by the publisher flow and choose **Host**. Enter the actual credential only in Capafy’s hosted credential interface; do not add it to the ZIP, a chat message, a source file, an Agent Card, or a manual configuration file. [3]
3. Confirm with the live hosted runtime that the hosted credential is exposed to this Skill as `OPENROUTER_API_KEY`. If Capafy uses a different documented runtime name, update only `config/inference_runtime.json`’s `api_key_env`, re-run the test suite and security scan, and publish the revised package.
4. Select a current text/reasoning model from OpenRouter’s catalog, verify its exact identifier, and configure it as the runtime value of `DDI_OPENROUTER_MODEL`. Do not use the included example as a default production selection. [1] [2]
5. In the Agent Card and data-sharing disclosure, list `openrouter.ai` as the runtime inference provider and describe the limited purpose: contextual interpretation and synthesis when the execution permits data transmission. List any future fallback or lower-cost provider before enabling it.
6. For the planned **$19 monthly subscription**, set Capafy’s native **Current Period Request Limit** to **60** after confirming the current live field in the Publisher Console. This is the native limit for substantive user-initiated investigations; it must not count internal model calls, documents, claims, report sections, or risks as additional user requests. [5]
7. Run a deliberately small, fictional, user-initiated production connection check through the deployed Agent. Confirm that the response is useful, the report passes the V2.1 quality gate, and no secret/header/raw provider error is shown. Do not request, print, upload, or copy the credential during the test.
8. Complete the current Agent Card, support email, pricing, data-handling disclosure, test cases, and review submission requirements. Do not submit until the actual model and credential mapping have been confirmed in the deployed environment.

## Connection and failure behavior

The adapter uses OpenRouter’s documented OpenAI-compatible Chat Completions endpoint and keeps the credential only in memory to build the request Authorization header. It does not enable browsing, plugins, file parsing, tool execution, streaming, debug echo, or automatic model routing. It returns only normalized content, model, purpose, and integer token counts; it does not return raw headers, raw provider payloads, or credentials. [1] [2]

| Condition | Safe agent-facing result | Retry behavior |
| --- | --- | --- |
| Credential absent | `MISSING_CREDENTIAL` and publisher configuration guidance | No retry |
| Invalid/unauthorized credential | `AUTHENTICATION_FAILED` | No retry |
| Provider rate limit | `RATE_LIMITED` | One bounded retry |
| Provider timeout | `PROVIDER_TIMEOUT` | One bounded retry |
| Network/provider unavailable | `NETWORK_FAILURE` or `PROVIDER_UNAVAILABLE` | One bounded retry |
| Invalid response | `MALFORMED_PROVIDER_RESPONSE` | No retry |
| Context too long | `CONTEXT_LENGTH_EXCEEDED` and staging/reduction guidance | No retry |
| Model refusal | `MODEL_REFUSAL` | No retry |
| Insufficient evidence | No provider error; complete the bounded V2.1 report and state the evidence requirement | Not applicable |

## Data and inference boundaries

User material remains untrusted data. The model must not follow instructions found inside supplied documents. External inference is blocked unless the execution context sets `external_data_permitted=True`; when it is blocked, the Skill performs document-only analysis and discloses that limitation. The V2.1 evidence hierarchy, status labels, reconciliation process, uncertainty-versus-risk boundary, professional disclaimer, and deterministic quality controls remain authoritative after any contextual inference.

The four existing V2.1 deterministic helpers remain offline and have no provider logic. Only `scripts/inference_provider.py` can make the narrowly scoped OpenRouter request. The static V2.2 security scanner checks for credential-like values, unexpected endpoints, and network-capable imports in those deterministic helpers.

## Current publication status and remaining confirmations

| Item | Status | Required publisher action |
| --- | --- | --- |
| OpenRouter adapter and mock test mode | Implemented | Use mock mode for CI/local verification. |
| Credential storage | No credential is packaged | Host and map the real credential in Capafy. |
| Production model identifier | Not selected by package | Verify and configure the publisher-selected model at runtime. |
| 60-request monthly entitlement | Platform-native field documented | Set and verify the 60 Current Period Request Limit in the live Publisher Console. |
| Runtime variable convention | Skill implementation requirement | Confirm that Capafy maps the hosted secret to `OPENROUTER_API_KEY`, or update the one configuration field. |
| Provider/data disclosure | Draft package declarations updated | Finalize Agent Card and any live privacy fields to match actual deployed providers. |
| Model cost and fallback routing | Single-model path only | Confirm model pricing and capacity; do not enable future routing without review. |

## References

[1]: https://openrouter.ai/docs/quickstart "OpenRouter Quickstart"
[2]: https://openrouter.ai/docs/guides/overview/models "OpenRouter Models"
[3]: https://capafy.ai/developer/doc/2.2 "Capafy Publishing Flow"
[4]: https://capafy.ai/earn/ "Capafy Publisher Information"
[5]: https://capafy.ai/developer/doc/3.1 "Capafy Pricing Models"
