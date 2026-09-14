# Test Report

## Scope

The test suite uses Python’s standard `unittest` framework and covers five realistic scenarios across three test modules. It requires no external network access, package installation, credentials, or real-company data.

| Scenario | Test location | Expected result |
| --- | --- | --- |
| Clean company input | `test_validation.py::test_clean_company_input` | Structured company data is accepted |
| Malformed source file | `test_validation.py::test_malformed_json_is_rejected` | Malformed JSON is rejected rather than silently repaired |
| Contradictory company | `test_evidence.py::test_contradictory_company_detected` | 500 versus 1,200 employee claims produce a contradiction |
| Missing evidence and prompt injection | `test_evidence.py::test_missing_evidence_and_injection_are_bounded` | Material gaps remain visible; embedded instruction language is detected as untrusted content only |
| Acquisition screening | `test_report_quality.py::test_acquisition_screening_full_report` | Full Markdown/HTML output passes deterministic quality gates |

## Run command

```bash
python3 -m unittest discover -s tests -v
```

## Latest validation result

The full suite was executed on **August 11, 2026** after the final evidence-classification update. **All five tests passed.** The full sample validation sequence also passed: structured-input validation, evidence tracking, Markdown/HTML report generation, deterministic quality checks, Python syntax compilation, source-integrity review, and the Skill-format validator.

Re-run the suite after any changes to the schema, evidence logic, required sections, risk language, or output controls.

