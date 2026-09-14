# Capafy Compliance Checklist — Rebased Final

## Package controls

| Control | Rebased package status | Publisher action |
| --- | --- | --- |
| Human-readable, standard-library-first code | Implemented | Keep source readable in the submitted package. |
| Deterministic-helper network isolation | Implemented | Preserve the rule that no packaged deterministic helper makes a network request. |
| Provider, model, endpoint, and credential logic | Removed from package | Configure and disclose any host-runtime arrangement through the live platform only. |
| Hosted credential | Not required by package | Do not add a credential to package source, configuration, tests, reports, or documentation. |
| Prompt-injection handling | Implemented as an untrusted-content control | Preserve the control in prompts, documentation, and future package changes. |
| Secret-pattern / network scan | Implemented in `scripts/security_scan.py` | Run after every code, configuration, or documentation change; do not include credentials in tests. |
| Data sharing | Package makes no external network call | Complete live host-runtime data-sharing declarations as required by the platform. |
| Professional boundaries | Implemented | Do not market the Skill as legal, investment, tax, accounting, regulatory, or transaction-execution advice. |
| Run-on-Demand execution | Implemented | Do not add background workers, polling, scheduled jobs, idle processes, or a persistent backend. |
| Subscription / request entitlement | Not implemented by package | If using US$19/month and 60 substantive investigations, configure any available native platform control; do not add an app-level counter. |
| Test cases | Local suite included | Enter and run final Publisher-interface test cases. |

## Required live-interface confirmation

Confirm current categories/tags from presets, support email, delivery model, pricing, any native request-limit setting, actual host-provided model/provider/data-processing disclosure, third-party data services, platform test cases, welcome message, version number, release note, and review submission. The package does not invent or manage these live values.

## Rebased accuracy statement

The Agent Card claims only implemented behavior: V2.1 evidence-aware verification, reconciliation-aware discrepancy review, Diligence Decision Map, risk and opportunity registers, evidence requests, linked management questions, scenario controls, objective-specific impact analysis, evidence-calibrated conclusions, deterministic validation, static credential/network-boundary scanning, and Run-on-Demand compatibility. It does not claim platform approval, professional certification, a particular model or provider, a configured credential, autonomous external research, subscription enforcement, payment processing, or outcomes not supported by evidence.

## Publisher review gate

Do not submit until the package test suite, security scan, report quality gate, Skill-format validation, archive-integrity check, and fictional platform test case all pass. If live platform settings differ from the published Agent Card and data-sharing declaration, update those documents before review; do not introduce model/provider/credential logic into the Skill package.
