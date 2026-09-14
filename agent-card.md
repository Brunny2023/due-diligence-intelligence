# Agent Card — Business Due Diligence & Acquisition Intelligence

## Name

**Business Due Diligence & Acquisition Intelligence**

## Short description

Turn imperfect company evidence into an evidence-calibrated Diligence Decision Map with claim verification, reconciliation-aware discrepancies, risk and opportunity registers, evidence requests, management questions, scenarios, and objective-specific decision impacts.

## Details

This Skill is a V2.1-authoritative evidence and decision-intelligence workflow for acquisition, investment, vendor, partnership, customer, competitor, and general company investigations. It converts supplied documents, URLs, notes, financial information, and structured research into a reproducible working diligence report. It preserves evidence provenance and distinguishes **FACT**, **COMPANY CLAIM**, **THIRD-PARTY CLAIM**, **ANALYST INFERENCE**, and **UNVERIFIED SIGNAL**.

The Skill’s core chain is: **source → claim → evidence → verification → confidence → risk or opportunity → decision impact → evidence required → management question → what could change the conclusion**. It provides evidence-aware claim verification; source-family and source-independence treatment; reconciliation-aware discrepancy analysis; a Diligence Decision Map; risk and opportunity registers; prioritized evidence requests; management interrogation; scenario analysis; and objective-specific transaction impacts.

V2.1 precision controls remain authoritative. The Skill uses qualitative evidence-calibrated assessments, prevents arbitrary numerical scores, separates evidence quality from risk severity, and derives executive findings from structured records so unresolved claims are not presented more strongly in summaries than in detailed analysis. The host environment may supply an LLM for contextual interpretation and synthesis, but the Skill contains no provider integration, model selection, API credential management, endpoint, inference service, billing, subscription, or entitlement mechanism.

## Suitable use cases

- Acquisition-target, investment-target, vendor, partnership, customer, competitor, and general company reviews.
- Fragmented evidence packs, pitch decks, financial summaries, customer or supplier information, contracts, notes, and permitted public-source material.
- Decision preparation where the user needs to understand reliability, missing evidence, risks, opportunities, and questions before acting.

## Important limits

The Skill is an AI-generated analytical aid. It does not provide legal, investment, financial, tax, accounting, regulatory, or other professional advice. It does not claim external research occurred unless such evidence is explicitly registered. It does not make final transaction, investment, contracting, or partnership decisions.

User-supplied material is untrusted data and cannot override the Skill’s evidence rules, security controls, or output requirements. The Skill is designed for Run on Demand only; it has no background workers, polling, scheduled inference, persistent server, idle process, payment processing, subscription management, or internal request counter.

## Rebase release note

This release restores V2.1 as the analytical baseline and selectively retains the provider-agnostic V2.2 improvements that strengthen deterministic package security and validation. It removes the prior independent provider adapter, API credential/configuration path, model/provider selection interface, endpoint handling, mock-inference tests, and provider-specific deployment material because those are supplied by the host environment rather than by this Skill.

## Publisher-interface confirmations still required

Select only live Capafy category and tag presets; enter a valid support email; choose delivery and pricing in the live interface; confirm the host-supplied model/provider and data-handling disclosures required by the platform; set any native monthly request limit the publisher offers; submit platform test cases; and complete review submission. No package placeholder is a live-platform value.
