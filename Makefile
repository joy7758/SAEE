.PHONY: check check-in-place generate check-generated check-provider-evidence check-experimental check-codex-context codex-context-check check-external-ai-test check-external-ai-manual-run check-external-ai-manual-test-start check-external-ai-calibration-run check-external-ai-calibration-defer check-internal-self-play check-semantic-dominance check-strategy-intake check-strategy-intake-dry-run check-public-signal-run-001 check-public-signal-review-draft check-public-signal-final-review check-public-signal-documentation-execution check-commercial-boundary check-auth-readiness check-operations-readiness check-operations-readiness-api check-operations-alert-policy check-support-readiness check-privacy-security-readiness check-privacy-security-readiness-api check-vulnerability-management-readiness check-pilot-validation-readiness check-billing-pricing-readiness check-controlled-trial-quickstart check-local-mvp-tryout-guide check-local-trial-handoff-packet check-local-tryout-readiness-card check-controlled-trial-local-e2e check-controlled-preview-env-template check-controlled-preview-tenant-storage check-commercial-go-no-go check-operations-telemetry check-operations-telemetry-api check-incident-response-runbook check-tenant-boundary check-request-limits check-persistence check-request-audit check-commercial-preflight check-data-retention check-data-backup check-data-restore-drill kernel-demo kernel-smoke kernel-v0-2-demo kernel-v0-2-smoke saee-v0-3-demo saee-v0-3-smoke saee-v0-4-demo saee-v0-4-smoke saee-v0-5-demo saee-v0-5-smoke saee-v0-6-demo saee-v0-6-smoke saee-v0-7-demo saee-v0-7-smoke saee-v0-8-demo saee-v0-8-smoke phase2-demo phase2-smoke saee-v1-0-demo saee-v1-0-smoke experiment-demo experiment-smoke saee-v1-2-demo saee-v1-2-smoke global-state-check mvp-api-smoke landing-smoke landing-api-integration-smoke first-user-test-smoke agent-recommendation-smoke agent-recommendation-validation-smoke external-ai-recommendation-test-smoke external-ai-manual-run-smoke external-ai-manual-test-start-smoke external-ai-calibration-run-smoke external-ai-calibration-defer-smoke internal-self-play-smoke semantic-dominance-smoke strategy-intake-smoke strategy-intake-dry-run-smoke public-signal-run-001-smoke public-signal-review-draft-smoke public-signal-final-review-smoke public-signal-documentation-execution-smoke commercial-boundary-smoke auth-readiness-smoke operations-readiness-smoke operations-readiness-api-smoke operations-alert-policy-smoke operations-telemetry-api-smoke support-readiness-smoke privacy-security-readiness-smoke privacy-security-readiness-api-smoke vulnerability-management-readiness-smoke pilot-validation-readiness-smoke billing-pricing-readiness-smoke controlled-trial-quickstart-smoke local-mvp-tryout-guide-smoke local-trial-handoff-packet-smoke local-tryout-readiness-card-smoke controlled-trial-local-e2e-smoke controlled-preview-env-template-smoke controlled-preview-tenant-storage-smoke commercial-go-no-go-smoke commercial-next-action-summary-smoke operations-telemetry-smoke incident-response-runbook-smoke tenant-boundary-smoke request-limits-smoke persistence-smoke request-audit-smoke commercial-preflight-smoke data-retention-smoke data-backup-smoke data-restore-drill-smoke
.PHONY: check-commercial-evidence-request-draft-packet commercial-evidence-request-draft-packet-smoke
.PHONY: check-saee-environment-requirements saee-environment-requirements-smoke
.PHONY: check-saee-research-artifact saee-research-artifact-smoke
.PHONY: check-saee-paper-draft saee-paper-draft-smoke
.PHONY: check-saee-evaluation-design saee-evaluation-design-smoke
.PHONY: check-saee-evaluation-prototype saee-evaluation-prototype-smoke
.PHONY: check-saee-pilot-preparation saee-pilot-preparation-smoke
.PHONY: check-saee-dataset-specification saee-dataset-specification-smoke
.PHONY: check-saee-pilot-readiness saee-pilot-readiness-smoke
.PHONY: check-saee-pilot-gap-resolution saee-pilot-gap-resolution-smoke
.PHONY: check-saee-evidence-acquisition-plan saee-evidence-acquisition-plan-smoke
.PHONY: check-saee-phase1-synthetic-vertical-slice saee-phase1-synthetic-vertical-slice-smoke
.PHONY: check-saee-phase1-5-case-corpus saee-phase1-5-case-corpus-smoke
.PHONY: check-saee-observation-contract saee-observation-contract-smoke
.PHONY: check-saee-observation-replay-contract saee-observation-replay-contract-smoke
.PHONY: check-saee-replay-evaluation-contract saee-replay-evaluation-contract-smoke
.PHONY: check-saee-evaluation-run-contract saee-evaluation-run-contract-smoke
.PHONY: check-saee-run-termination-contract saee-run-termination-contract-smoke
.PHONY: check-saee-phase2a-readiness-gate saee-phase2a-readiness-gate
.PHONY: check-saee-phase2a-execution saee-phase2a-execution-smoke
.PHONY: check-saee-phase2b-adapter-readiness-gate saee-phase2b-adapter-readiness-gate
.PHONY: check-saee-adapter-provenance-contract saee-adapter-provenance-contract-smoke
.PHONY: check-saee-synthetic-observation-adapter saee-synthetic-observation-adapter-smoke
.PHONY: check-saee-phase2b-completion-review saee-phase2b-completion-review-smoke
.PHONY: check-saee-review-report saee-review-report-smoke
.PHONY: check-saee-design-partner-validation saee-design-partner-validation-smoke
.PHONY: check-saee-agent-native-commercial-logic saee-agent-native-commercial-logic-smoke
.PHONY: check-saee-agent-native-capability saee-agent-native-capability-smoke
.PHONY: controlled-preview-request-smoke check-controlled-preview-request
.PHONY: commercial-quote-request-smoke check-commercial-quote-request
.PHONY: check-external-customer-validation-minimum-session-answer-converter external-customer-validation-minimum-session-answer-converter-smoke
.PHONY: check-online-experience online-experience-smoke check-online-experience-human-review online-experience-human-review-smoke
.PHONY: check-commercial-evidence-request-approval-input-validator commercial-evidence-request-approval-input-validator-smoke
.PHONY: check-commercial-evidence-request-approval-completion-helper commercial-evidence-request-approval-completion-helper-smoke
.PHONY: check-commercial-evidence-request-approval-readiness-board commercial-evidence-request-approval-readiness-board-smoke
.PHONY: check-commercial-next-action-summary commercial-next-action-summary-smoke
.PHONY: check-commercial-trial-operator-status commercial-trial-operator-status-smoke commercial-trial-operator-status
.PHONY: check-commercial-evidence-sprint-sequencer commercial-evidence-sprint-sequencer-smoke
.PHONY: check-commercial-sprint-human-input-quick-fill-guidance commercial-sprint-human-input-quick-fill-guidance-smoke
.PHONY: check-commercial-sprint-human-input-readiness-audit commercial-sprint-human-input-readiness-audit-smoke
.PHONY: check-commercial-sprint-human-input-quick-fill-quality-gate commercial-sprint-human-input-quick-fill-quality-gate-smoke
.PHONY: check-commercial-sprint-human-input-execution-stop-gate commercial-sprint-human-input-execution-stop-gate-smoke
.PHONY: check-commercial-review-batch-human-fill-card commercial-review-batch-human-fill-card-smoke
.PHONY: check-commercial-review-batch-human-execution-packet commercial-review-batch-human-execution-packet-smoke
.PHONY: check-commercial-review-batch-safe-prefill-audit commercial-review-batch-safe-prefill-audit-smoke
.PHONY: check-commercial-review-batch-template-preflight commercial-review-batch-template-preflight-smoke
.PHONY: check-commercial-review-batch-post-fill-validation-runbook commercial-review-batch-post-fill-validation-runbook-smoke
.PHONY: check-commercial-review-batch-post-fill-readiness-preview commercial-review-batch-post-fill-readiness-preview-smoke
.PHONY: check-commercial-review-batch-post-fill-check commercial-review-batch-post-fill-check-smoke
.PHONY: check-commercial-sprint-human-input-quick-fill-workbook-importer commercial-sprint-human-input-quick-fill-workbook-importer-smoke
.PHONY: check-commercial-sprint-workbook-import-execution-request-packet commercial-sprint-workbook-import-execution-request-packet-smoke
.PHONY: check-commercial-sprint-human-confirmed-recommended-values commercial-sprint-human-confirmed-recommended-values-smoke check-commercial-sprint-human-confirmed-values-import-preview commercial-sprint-human-confirmed-values-import-preview-smoke check-commercial-sprint-remaining-recommended-values-draft commercial-sprint-remaining-recommended-values-draft-smoke check-commercial-sprint-remaining-human-confirmed-values commercial-sprint-remaining-human-confirmed-values-smoke check-commercial-sprint-all-confirmed-values-source-apply commercial-sprint-all-confirmed-values-source-apply-smoke
.PHONY: check-commercial-sprint-human-input-quick-fill-owner-packets-validator commercial-sprint-human-input-quick-fill-owner-packets-validator-smoke
.PHONY: check-commercial-sprint-human-input-quick-fill-owner-packets-merge-dry-run commercial-sprint-human-input-quick-fill-owner-packets-merge-dry-run-smoke
.PHONY: check-commercial-sprint-human-input-template-transfer-applier commercial-sprint-human-input-template-transfer-applier-smoke
.PHONY: check-commercial-sprint-post-transfer-validator-sequencer commercial-sprint-post-transfer-validator-sequencer-smoke
.PHONY: check-commercial-sprint-validator-approval-request-packet commercial-sprint-validator-approval-request-packet-smoke
.PHONY: check-commercial-sprint-validator-execution-run commercial-sprint-validator-execution-run-smoke
.PHONY: check-commercial-sprint-validator-hold-output-review commercial-sprint-validator-hold-output-review-smoke
.PHONY: check-commercial-sprint-human-input-pipeline-synthetic-proof commercial-sprint-human-input-pipeline-synthetic-proof-smoke
.PHONY: check-commercial-sprint-human-input-safety-preflight commercial-sprint-human-input-safety-preflight-smoke
.PHONY: check-public-claim-lint public-claim-lint-smoke
.PHONY: check-commercial-readiness-status-snapshot commercial-readiness-status-snapshot-smoke
.PHONY: check-commercial-readiness-gap-audit commercial-readiness-gap-audit-smoke
.PHONY: check-commercial-blocker-priority-index commercial-blocker-priority-index-smoke commercial-blocker-priority-index
.PHONY: check-support-contact-first-priority-packet support-contact-first-priority-packet-smoke support-contact-first-priority-packet
.PHONY: check-formal-security-review-minimum-human-input-workspace formal-security-review-minimum-human-input-workspace-smoke formal-security-review-minimum-human-input-workspace check-formal-security-review-state-reconciliation formal-security-review-state-reconciliation-smoke
.PHONY: check-production-restore-policy-minimum-human-input-workspace production-restore-policy-minimum-human-input-workspace-smoke production-restore-policy-minimum-human-input-workspace check-production-restore-policy-state-reconciliation production-restore-policy-state-reconciliation-smoke check-production-monitoring-state-reconciliation production-monitoring-state-reconciliation-smoke check-operations-followup-state-reconciliation operations-followup-state-reconciliation-smoke check-privacy-security-legal-followup-state-reconciliation privacy-security-legal-followup-state-reconciliation-smoke check-billing-followup-state-reconciliation billing-followup-state-reconciliation-smoke check-phase1-identity-tenant-state-reconciliation phase1-identity-tenant-state-reconciliation-smoke
.PHONY: check-partial-evidence-promotion-queue partial-evidence-promotion-queue-smoke
.PHONY: check-commercial-review-ready-marker-catalog commercial-review-ready-marker-catalog-smoke
.PHONY: check-commercial-matrix-update-scope-refresh commercial-matrix-update-scope-refresh-smoke
.PHONY: check-commercial-matrix-update-scope-refresh-approval-intake commercial-matrix-update-scope-refresh-approval-intake-smoke
.PHONY: check-restore-tested-promotion-review-packet restore-tested-promotion-review-packet-smoke
.PHONY: check-restore-tested-promotion-decision-validator restore-tested-promotion-decision-validator-smoke
.PHONY: check-commercial-readiness-begin-here commercial-readiness-begin-here-smoke commercial-readiness-begin-here
.PHONY: check-commercial-readiness-state-consistency-audit commercial-readiness-state-consistency-audit-smoke
.PHONY: check-local-trial-cold-start-preflight local-trial-cold-start-preflight-smoke
.PHONY: check-local-trial-http-e2e local-trial-http-e2e-smoke
.PHONY: check-local-trial-lifecycle-proof local-trial-lifecycle-proof-smoke
.PHONY: check-baidu-cloud-handoff-preflight baidu-cloud-handoff-preflight-smoke
.PHONY: check-baidu-cloud-handoff-package baidu-cloud-handoff-package-smoke
.PHONY: check-local-trial-make-targets local-trial-make-targets-smoke local-trial-preflight local-trial-start local-trial-status local-trial-stop try-local
.PHONY: check-legal-readiness check-legal-readiness-api legal-readiness-smoke legal-readiness-api-smoke
.PHONY: check-commercial-launch-blocker-work-order commercial-launch-blocker-work-order-smoke
.PHONY: check-production-auth-requirements production-auth-requirements-smoke
.PHONY: check-production-auth-evidence-readiness production-auth-evidence-readiness-smoke
.PHONY: check-auth-evidence-runner auth-evidence-runner-smoke
.PHONY: check-production-auth-evidence-path production-auth-evidence-path-smoke
.PHONY: check-production-identity-provider-readiness-board production-identity-provider-readiness-board-smoke
.PHONY: check-production-identity-provider-input-completion-helper production-identity-provider-input-completion-helper-smoke
.PHONY: check-production-identity-provider-human-decision-runbook production-identity-provider-human-decision-runbook-smoke
.PHONY: check-production-identity-provider-evidence-builder-request-template production-identity-provider-evidence-builder-request-template-smoke
.PHONY: check-production-identity-provider-decision-packet production-identity-provider-decision-packet-smoke
.PHONY: check-production-identity-provider-approval-input-validator production-identity-provider-approval-input-validator-smoke
.PHONY: check-oauth-oidc-approval-input-validator oauth-oidc-approval-input-validator-smoke
.PHONY: check-rbac-approval-input-validator rbac-approval-input-validator-smoke
.PHONY: check-rbac-approval-input-prompt rbac-approval-input-prompt-smoke rbac-approval-input-prompt
.PHONY: check-tenant-storage-approval-input-validator tenant-storage-approval-input-validator-smoke
.PHONY: check-tenant-storage-remaining-gap-packet tenant-storage-remaining-gap-packet-smoke
.PHONY: check-auth-oidc-rbac-fixture-dry-run auth-oidc-rbac-fixture-dry-run-smoke
.PHONY: check-jwt-preview-auth jwt-preview-auth-smoke
.PHONY: check-jwt-preview-operator-packet jwt-preview-operator-packet-smoke
.PHONY: check-landing-jwt-preview-auth landing-jwt-preview-auth-smoke
.PHONY: check-tax-review-approval-input-validator tax-review-approval-input-validator-smoke
.PHONY: check-identity-provider-readiness identity-provider-readiness-smoke
.PHONY: check-rbac-policy-template rbac-policy-template-smoke
.PHONY: check-rbac-preview-enforcement rbac-preview-enforcement-smoke
.PHONY: check-production-support-evidence-readiness production-support-evidence-readiness-smoke
.PHONY: check-support-evidence-runner support-evidence-runner-smoke
.PHONY: check-support-sla-on-call-review-packet support-sla-on-call-review-packet-smoke
.PHONY: check-support-contact-decision-packet support-contact-decision-packet-smoke
.PHONY: check-support-contact-preflight support-contact-preflight-smoke
.PHONY: check-support-contact-readiness-board support-contact-readiness-board-smoke
.PHONY: check-support-contact-human-input-bridge support-contact-human-input-bridge-smoke
.PHONY: check-support-contact-human-input-bridge-completion-helper support-contact-human-input-bridge-completion-helper-smoke
.PHONY: check-support-contact-human-input-entrypoint support-contact-human-input-entrypoint-smoke
.PHONY: check-support-group-human-filled-evidence-refresh support-group-human-filled-evidence-refresh-smoke
.PHONY: check-support-contact-bridge-validator-dry-run support-contact-bridge-validator-dry-run-smoke
.PHONY: check-support-contact-bridge-human-handoff-checkpoint support-contact-bridge-human-handoff-checkpoint-smoke
.PHONY: check-support-contact-approval-input-validator support-contact-approval-input-validator-smoke
.PHONY: check-support-contact-approval-input-prompt support-contact-approval-input-prompt-smoke
.PHONY: check-support-contact-evidence-builder support-contact-evidence-builder-smoke
.PHONY: check-support-contact-evidence-builder-request-template support-contact-evidence-builder-request-template-smoke
.PHONY: check-support-contact-evidence-builder-execution-request support-contact-evidence-builder-execution-request-smoke
.PHONY: check-support-contact-evidence-path support-contact-evidence-path-smoke
.PHONY: check-customer-support-approval-input-validator customer-support-approval-input-validator-smoke
.PHONY: check-customer-support-approval-input-prompt customer-support-approval-input-prompt-smoke
.PHONY: check-customer-support-evidence-builder customer-support-evidence-builder-smoke
.PHONY: check-customer-support-evidence-path customer-support-evidence-path-smoke
.PHONY: check-sla-approval-input-validator sla-approval-input-validator-smoke
.PHONY: check-sla-approval-input-prompt sla-approval-input-prompt-smoke
.PHONY: check-sla-evidence-builder sla-evidence-builder-smoke
.PHONY: check-sla-evidence-path sla-evidence-path-smoke
.PHONY: check-on-call-approval-input-validator on-call-approval-input-validator-smoke
.PHONY: check-on-call-approval-input-prompt on-call-approval-input-prompt-smoke
.PHONY: check-on-call-evidence-builder on-call-evidence-builder-smoke
.PHONY: check-on-call-evidence-path on-call-evidence-path-smoke
.PHONY: check-support-sla-evidence-profile support-sla-evidence-profile-smoke
.PHONY: check-production-data-operations-evidence-readiness production-data-operations-evidence-readiness-smoke
.PHONY: check-data-operations-evidence-runner data-operations-evidence-runner-smoke
.PHONY: check-restore-tested-evidence-profile restore-tested-evidence-profile-smoke
.PHONY: check-restore-tested-local-evidence-promotion-request restore-tested-local-evidence-promotion-request-smoke
.PHONY: check-production-restore-policy-evidence-builder production-restore-policy-evidence-builder-smoke
.PHONY: check-production-restore-policy-approval-input-validator production-restore-policy-approval-input-validator-smoke
.PHONY: check-data-operations-evidence-profile data-operations-evidence-profile-smoke
.PHONY: check-production-restore-policy-review-packet production-restore-policy-review-packet-smoke
.PHONY: check-production-restore-policy-draft production-restore-policy-draft-smoke
.PHONY: check-production-operations-evidence-readiness production-operations-evidence-readiness-smoke
.PHONY: check-operations-evidence-runner operations-evidence-runner-smoke
.PHONY: check-operations-evidence-profile operations-evidence-profile-smoke
.PHONY: check-production-monitoring-evidence-builder production-monitoring-evidence-builder-smoke
.PHONY: check-production-monitoring-approval-input-validator production-monitoring-approval-input-validator-smoke
.PHONY: check-external-alert-delivery-approval-input-validator external-alert-delivery-approval-input-validator-smoke
.PHONY: check-external-alert-delivery-approval-input-prompt external-alert-delivery-approval-input-prompt-smoke external-alert-delivery-approval-input-prompt
.PHONY: check-external-alert-delivery-evidence-builder external-alert-delivery-evidence-builder-smoke
.PHONY: check-operations-on-call-rotation-approval-input-validator operations-on-call-rotation-approval-input-validator-smoke
.PHONY: check-operations-on-call-rotation-approval-input-prompt operations-on-call-rotation-approval-input-prompt-smoke operations-on-call-rotation-approval-input-prompt
.PHONY: check-operations-on-call-rotation-evidence-builder operations-on-call-rotation-evidence-builder-smoke
.PHONY: check-operations-on-call-rotation-evidence-path operations-on-call-rotation-evidence-path-smoke
.PHONY: check-operations-monitoring-alert-review-packet operations-monitoring-alert-review-packet-smoke
.PHONY: check-production-privacy-security-legal-evidence-readiness production-privacy-security-legal-evidence-readiness-smoke
.PHONY: check-privacy-security-legal-evidence-runner privacy-security-legal-evidence-runner-smoke
.PHONY: check-privacy-security-legal-evidence-path privacy-security-legal-evidence-path-smoke
.PHONY: check-formal-security-review-scope-draft formal-security-review-scope-draft-smoke
.PHONY: check-formal-security-review-evidence-builder formal-security-review-evidence-builder-smoke
.PHONY: check-formal-security-review-approval-input-validator formal-security-review-approval-input-validator-smoke
.PHONY: check-formal-security-review-approval-input-prompt formal-security-review-approval-input-prompt-smoke
.PHONY: check-privacy-legal-dpa-evidence-builder privacy-legal-dpa-evidence-builder-smoke
.PHONY: check-privacy-legal-dpa-approval-input-prompt privacy-legal-dpa-approval-input-prompt-smoke privacy-legal-dpa-approval-input-validator privacy-legal-dpa-approval-input-validator-smoke check-privacy-legal-dpa-approval-input-validator
.PHONY: check-vulnerability-management-evidence-builder vulnerability-management-evidence-builder-smoke
.PHONY: check-vulnerability-management-approval-input-prompt vulnerability-management-approval-input-prompt-smoke vulnerability-management-approval-input-validator vulnerability-management-approval-input-validator-smoke check-vulnerability-management-approval-input-validator
.PHONY: check-privacy-legal-review-packet privacy-legal-review-packet-smoke
.PHONY: check-data-processing-agreement-review-packet data-processing-agreement-review-packet-smoke
.PHONY: check-production-billing-revenue-evidence-readiness production-billing-revenue-evidence-readiness-smoke
.PHONY: check-billing-revenue-evidence-runner billing-revenue-evidence-runner-smoke
.PHONY: check-pricing-page-review-packet pricing-page-review-packet-smoke
.PHONY: check-pricing-page-closure-review-packet pricing-page-closure-review-packet-smoke
.PHONY: check-pricing-page-copy-draft pricing-page-copy-draft-smoke
.PHONY: check-pricing-page-evidence-builder pricing-page-evidence-builder-smoke
.PHONY: check-pricing-page-approval-input-prompt pricing-page-approval-input-prompt-smoke
.PHONY: check-pricing-page-approval-input-validator pricing-page-approval-input-validator-smoke
.PHONY: check-customer-validation-approval-input-prompt customer-validation-approval-input-prompt-smoke customer-validation-approval-input-prompt check-customer-validation-approval-input-validator customer-validation-approval-input-validator-smoke
.PHONY: check-payment-provider-review-packet payment-provider-review-packet-smoke
.PHONY: check-payment-provider-evidence-builder payment-provider-evidence-builder-smoke
.PHONY: check-payment-provider-approval-input-prompt payment-provider-approval-input-prompt-smoke
.PHONY: check-payment-provider-approval-input-validator payment-provider-approval-input-validator-smoke
.PHONY: check-invoice-process-review-packet invoice-process-review-packet-smoke
.PHONY: check-invoice-process-evidence-builder invoice-process-evidence-builder-smoke
.PHONY: check-invoice-process-approval-input-prompt invoice-process-approval-input-prompt-smoke
.PHONY: check-invoice-process-approval-input-validator invoice-process-approval-input-validator-smoke
.PHONY: check-tax-review-packet tax-review-packet-smoke
.PHONY: check-tax-review-evidence-builder tax-review-evidence-builder-smoke
.PHONY: check-tax-review-approval-input-prompt tax-review-approval-input-prompt-smoke
.PHONY: check-refund-policy-review-packet refund-policy-review-packet-smoke
.PHONY: check-refund-policy-evidence-builder refund-policy-evidence-builder-smoke
.PHONY: check-refund-policy-approval-input-prompt refund-policy-approval-input-prompt-smoke
.PHONY: check-refund-policy-approval-input-validator refund-policy-approval-input-validator-smoke
.PHONY: check-tenant-billing-isolation-approval-input-prompt tenant-billing-isolation-approval-input-prompt-smoke
.PHONY: check-tenant-billing-isolation-approval-input-validator tenant-billing-isolation-approval-input-validator-smoke
.PHONY: check-tenant-billing-isolation-review-packet tenant-billing-isolation-review-packet-smoke
.PHONY: check-tenant-billing-isolation-evidence-builder tenant-billing-isolation-evidence-builder-smoke
.PHONY: check-billing-revenue-evidence-profile billing-revenue-evidence-profile-smoke
.PHONY: check-billing-revenue-evidence-path billing-revenue-evidence-path-smoke
.PHONY: check-billing-revenue-human-filled-evidence-run billing-revenue-human-filled-evidence-run-smoke
.PHONY: check-phase1-identity-tenant-human-filled-evidence-run phase1-identity-tenant-human-filled-evidence-run-smoke
.PHONY: check-internal-founder-pilot-evidence-run internal-founder-pilot-evidence-run-smoke
.PHONY: check-support-contact-closure-gap-review support-contact-closure-gap-review-smoke check-support-contact-state-reconciliation support-contact-state-reconciliation-smoke
.PHONY: check-support-group-closure-review-packet support-group-closure-review-packet-smoke
.PHONY: check-support-group-final-closure-decision-request support-group-final-closure-decision-request-smoke
.PHONY: check-support-group-final-closure-decision-validator support-group-final-closure-decision-validator-smoke
.PHONY: check-support-group-final-closure-decision-completion-helper support-group-final-closure-decision-completion-helper-smoke
.PHONY: check-commercial-matrix-update-request-packet commercial-matrix-update-request-packet-smoke
.PHONY: check-commercial-matrix-update-execution-request-packet commercial-matrix-update-execution-request-packet-smoke
.PHONY: check-commercial-matrix-update-execution-approval-input commercial-matrix-update-execution-approval-input-smoke
.PHONY: check-commercial-matrix-update-execution-approval-phrase-intake commercial-matrix-update-execution-approval-phrase-intake-smoke
.PHONY: check-commercial-matrix-update-execution-approval-copy-card commercial-matrix-update-execution-approval-copy-card-smoke check-commercial-matrix-update-execution-next-step-router commercial-matrix-update-execution-next-step-router-smoke
.PHONY: check-commercial-matrix-update-execution-dry-run commercial-matrix-update-execution-dry-run-smoke
.PHONY: check-commercial-matrix-update-execution-applier commercial-matrix-update-execution-applier-smoke
.PHONY: check-scenario-template scenario-template-smoke
.PHONY: check-commercial-final-human-inspection-record commercial-final-human-inspection-record-smoke check-commercial-blocker-convergence-audit commercial-blocker-convergence-audit-smoke check-customer-validation-last-mile-packet customer-validation-last-mile-packet-smoke check-customer-validation-answer-intake-helper customer-validation-answer-intake-helper-smoke check-customer-validation-human-confirmation-boundary-record customer-validation-human-confirmation-boundary-record-smoke check-customer-validation-answer-sheet-preflight customer-validation-answer-sheet-preflight-smoke check-customer-validation-plain-chinese-worksheet customer-validation-plain-chinese-worksheet-smoke check-customer-validation-3-minute-worksheet customer-validation-3-minute-worksheet-smoke check-customer-validation-one-page-run-card customer-validation-one-page-run-card-smoke check-customer-validation-next-step-router customer-validation-next-step-router-smoke
.PHONY: check-customer-validation-answer-to-session-entry-converter customer-validation-answer-to-session-entry-converter-smoke
.PHONY: check-customer-validation-answer-to-evidence-pipeline customer-validation-answer-to-evidence-pipeline-smoke check-customer-validation-live-fill-queue customer-validation-live-fill-queue-smoke check-customer-validation-live-interview-card customer-validation-live-interview-card-smoke check-customer-validation-interview-answer-stager customer-validation-interview-answer-stager-smoke check-customer-validation-official-answer-completion-helper customer-validation-official-answer-completion-helper-smoke
.PHONY: check-external-customer-validation-next-action external-customer-validation-next-action-smoke
.PHONY: check-external-customer-validation-session-kit external-customer-validation-session-kit-smoke
.PHONY: check-external-customer-validation-session-entry-importer external-customer-validation-session-entry-importer-smoke
.PHONY: check-external-customer-validation-session-entry-workbench external-customer-validation-session-entry-workbench-smoke
.PHONY: check-commercial-readiness-state-reconciliation commercial-readiness-state-reconciliation-smoke
.PHONY: check-external-customer-validation-run-001 external-customer-validation-run-001-smoke
.PHONY: check-external-customer-validation-recruitment-consent external-customer-validation-recruitment-consent-smoke
.PHONY: check-external-customer-validation-action-board external-customer-validation-action-board-smoke
.PHONY: check-external-customer-validation-facilitator external-customer-validation-facilitator-smoke
.PHONY: check-current-commercial-primary-action current-commercial-primary-action-smoke
.PHONY: check-external-customer-validation-minimum-session-packet external-customer-validation-minimum-session-packet-smoke
.PHONY: check-external-customer-validation-post-session-processor external-customer-validation-post-session-processor-smoke
.PHONY: check-production-tenant-storage-evidence-readiness production-tenant-storage-evidence-readiness-smoke
.PHONY: check-tenant-storage-isolation-evidence-runner tenant-storage-isolation-evidence-runner-smoke check-tenant-required-storage-guard check-tenant-secret-boundary tenant-secret-boundary-smoke check-bound-tenant-authorization bound-tenant-authorization-smoke check-tenant-agent-review-evidence tenant-agent-review-evidence-smoke check-tenant-privacy-agent-review tenant-privacy-agent-review-smoke
.PHONY: check-production-tenant-storage-evidence-path production-tenant-storage-evidence-path-smoke
.PHONY: check-tenant-security-privacy-review-packet tenant-security-privacy-review-packet-smoke
.PHONY: check-production-customer-validation-evidence-readiness production-customer-validation-evidence-readiness-smoke
.PHONY: check-customer-validation-evidence-runner customer-validation-evidence-runner-smoke
.PHONY: check-customer-validation-evidence-builder customer-validation-evidence-builder-smoke
.PHONY: check-customer-validation-evidence-path customer-validation-evidence-path-smoke
.PHONY: check-production-evidence-templates production-evidence-templates-smoke
.PHONY: check-production-evidence-intake-audit production-evidence-intake-audit-smoke
.PHONY: check-commercial-evidence-profile commercial-evidence-profile-smoke
.PHONY: check-production-blocker-gap-matrix production-blocker-gap-matrix-smoke
.PHONY: check-production-blocker-evidence-path-coverage-audit production-blocker-evidence-path-coverage-audit-smoke
.PHONY: check-commercial-review-packet-canonical-aliases commercial-review-packet-canonical-aliases-smoke
.PHONY: check-commercial-blocker-dependency-plan commercial-blocker-dependency-plan-smoke
.PHONY: check-phase1-identity-tenant-evidence-task phase1-identity-tenant-evidence-task-smoke
.PHONY: check-phase2-data-operations-evidence-task phase2-data-operations-evidence-task-smoke
.PHONY: check-phase2-data-operations-gap-audit phase2-data-operations-gap-audit-smoke
.PHONY: check-phase3-support-security-legal-gap-audit phase3-support-security-legal-gap-audit-smoke
.PHONY: check-phase4-commercial-packaging-billing-gap-audit phase4-commercial-packaging-billing-gap-audit-smoke
.PHONY: check-phase5-customer-validation-launch-gap-audit phase5-customer-validation-launch-gap-audit-smoke
.PHONY: check-commercial-production-evidence-collection-packet commercial-production-evidence-collection-packet-smoke
.PHONY: check-phase1-identity-tenant-priority-evidence-collection phase1-identity-tenant-priority-evidence-collection-smoke
.PHONY: check-phase2-data-operations-priority-evidence-collection phase2-data-operations-priority-evidence-collection-smoke
.PHONY: check-phase3-support-security-legal-priority-evidence-collection phase3-support-security-legal-priority-evidence-collection-smoke
.PHONY: check-phase4-commercial-packaging-billing-priority-evidence-collection phase4-commercial-packaging-billing-priority-evidence-collection-smoke
.PHONY: check-phase5-customer-validation-launch-priority-evidence-collection phase5-customer-validation-launch-priority-evidence-collection-smoke
.PHONY: check-phase1-identity-tenant-gap-audit phase1-identity-tenant-gap-audit-smoke
.PHONY: check-phase1-identity-tenant-evidence-builder phase1-identity-tenant-evidence-builder-smoke
.PHONY: check-phase1-identity-tenant-evidence-profile phase1-identity-tenant-evidence-profile-smoke
.PHONY: check-production-operations-requirements production-operations-requirements-smoke
.PHONY: check-production-support-sla-requirements production-support-sla-requirements-smoke
.PHONY: check-production-privacy-security-legal-requirements production-privacy-security-legal-requirements-smoke
.PHONY: check-production-billing-revenue-requirements production-billing-revenue-requirements-smoke
.PHONY: check-production-data-operations-requirements production-data-operations-requirements-smoke
.PHONY: check-production-tenant-storage-isolation-requirements production-tenant-storage-isolation-requirements-smoke
.PHONY: check-production-customer-validation-requirements production-customer-validation-requirements-smoke
.PHONY: check-preview-readiness-api preview-readiness-api-smoke
.PHONY: check-controlled-trial-operator-packet controlled-trial-operator-packet-smoke
.PHONY: check-controlled-trial-observation-runner controlled-trial-observation-runner-smoke
.PHONY: check-local-trial-session-manager local-trial-session-manager-smoke
.PHONY: check-commercial-readiness-dashboard commercial-readiness-dashboard-smoke
.PHONY: check-commercial-human-action-board commercial-human-action-board-smoke
.PHONY: check-commercial-next-evidence-sprint commercial-next-evidence-sprint-smoke
.PHONY: check-commercial-sprint-handoff-pack commercial-sprint-handoff-pack-smoke
.PHONY: check-commercial-sprint-human-input-workbook-validator commercial-sprint-human-input-workbook-validator-smoke
.PHONY: check-commercial-sprint-human-input-transfer-map commercial-sprint-human-input-transfer-map-smoke
.PHONY: check-commercial-sprint-human-input-transfer-resolver-dry-run commercial-sprint-human-input-transfer-resolver-dry-run-smoke
.PHONY: check-commercial-sprint-human-input-completion-queue commercial-sprint-human-input-completion-queue-smoke
.PHONY: check-commercial-sprint-human-input-quick-fill-packet commercial-sprint-human-input-quick-fill-packet-smoke
.PHONY: check-commercial-sprint-human-input-quick-fill-packet-validator commercial-sprint-human-input-quick-fill-packet-validator-smoke
.PHONY: check-commercial-sprint-human-input-quick-fill-workbook-import-dry-run commercial-sprint-human-input-quick-fill-workbook-import-dry-run-smoke
.PHONY: check-commercial-evidence-sprint-owner-assignment commercial-evidence-sprint-owner-assignment-smoke
.PHONY: check-commercial-evidence-sprint-owner-assignment-input-validator commercial-evidence-sprint-owner-assignment-input-validator-smoke
.PHONY: check-commercial-evidence-sprint-owner-assignment-completion-helper commercial-evidence-sprint-owner-assignment-completion-helper-smoke
.PHONY: check-commercial-evidence-sprint-owner-assignment-readiness-board commercial-evidence-sprint-owner-assignment-readiness-board-smoke
.PHONY: check-commercial-evidence-sprint-first-owner-action-packet commercial-evidence-sprint-first-owner-action-packet-smoke
.PHONY: check-commercial-evidence-sprint-first-owner-input-validator commercial-evidence-sprint-first-owner-input-validator-smoke
.PHONY: check-commercial-evidence-sprint-first-owner-input-completion-helper commercial-evidence-sprint-first-owner-input-completion-helper-smoke
.PHONY: check-commercial-evidence-sprint-first-owner-input-request-packet commercial-evidence-sprint-first-owner-input-request-packet-smoke
.PHONY: check-commercial-evidence-sprint-human-sequence-packet commercial-evidence-sprint-human-sequence-packet-smoke
.PHONY: check-commercial-launch-evidence-path commercial-launch-evidence-path-smoke
.PHONY: check-production-monitoring-evidence-path production-monitoring-evidence-path-smoke
.PHONY: check-external-alert-delivery-evidence-path external-alert-delivery-evidence-path-smoke
.PHONY: check-local-trial-preflight-snapshot local-trial-preflight-snapshot-smoke
.PHONY: check-parasitic-phase parasitic-phase-smoke parasitic-phase-demo

check:
	python3 scripts/saee_check_isolation.py check

check-generated:
	python3 scripts/saee_check_isolation.py check-generated

check-provider-evidence:
	python3 scripts/saee_controlled_reasoning_live_evidence_smoke.py --require-evidence

generate:
	SAEE_CHECK_ISOLATED=1 SAEE_PROVIDER_EVIDENCE_MODE=optional python3 scripts/mainline_guard.py

check-in-place:
	python3 scripts/mainline_guard.py
	python3 scripts/saee_check_idempotency_smoke.py
	python3 scripts/codex_context_check.py
	python3 scripts/saee_public_claim_lint_smoke.py
	python3 scripts/saee_v1_0_smoke.py
	python3 scripts/saee_experiment_smoke.py
	python3 scripts/saee_v1_2_smoke.py
	python3 scripts/saee_parasitic_phase_smoke.py
	python3 scripts/saee_global_state_check.py
	python3 scripts/saee_mvp_api_smoke.py
	python3 scripts/saee_landing_page_smoke.py
	python3 scripts/saee_online_experience_smoke.py
	python3 scripts/saee_online_experience_human_review_smoke.py
	python3 scripts/saee_commercial_readiness_state_reconciliation_smoke.py
	python3 scripts/saee_external_customer_validation_run_001_smoke.py
	python3 scripts/saee_external_customer_validation_recruitment_consent_smoke.py
	python3 scripts/saee_external_customer_validation_action_board_smoke.py
	python3 scripts/saee_external_customer_validation_facilitator_smoke.py
	python3 scripts/saee_current_commercial_primary_action_smoke.py
	python3 scripts/saee_external_customer_validation_minimum_session_packet_smoke.py
	python3 scripts/saee_external_customer_validation_minimum_session_answer_converter_smoke.py
	python3 scripts/saee_external_customer_validation_post_session_processor_smoke.py
	python3 scripts/saee_external_customer_validation_local_session_launcher_smoke.py
	python3 scripts/saee_external_customer_validation_launcher_human_inspection_record_smoke.py
	python3 scripts/saee_customer_validation_answer_intake_helper_smoke.py
	python3 scripts/saee_customer_validation_human_confirmation_boundary_record_smoke.py
	python3 scripts/saee_customer_validation_answer_sheet_preflight_smoke.py
	python3 scripts/saee_customer_validation_answer_to_session_entry_converter_smoke.py
	python3 scripts/saee_customer_validation_answer_to_evidence_pipeline_smoke.py
	python3 scripts/saee_customer_validation_live_fill_queue_smoke.py
	python3 scripts/saee_customer_validation_live_interview_card_smoke.py
	python3 scripts/saee_customer_validation_interview_answer_stager_smoke.py
	python3 scripts/saee_customer_validation_official_answer_completion_helper_smoke.py
	python3 scripts/saee_customer_validation_plain_chinese_worksheet_smoke.py
	python3 scripts/saee_customer_validation_3_minute_worksheet_smoke.py
	python3 scripts/saee_customer_validation_one_page_run_card_smoke.py
	python3 scripts/saee_customer_validation_next_step_router_smoke.py
	python3 scripts/saee_landing_api_integration_smoke.py
	python3 scripts/saee_landing_jwt_preview_auth_smoke.py
	python3 scripts/saee_first_user_test_plan_smoke.py
	python3 scripts/saee_pilot_validation_readiness_smoke.py
	python3 scripts/saee_agent_recommendation_surface_smoke.py
	python3 scripts/saee_agent_recommendation_validation_smoke.py
	python3 scripts/saee_external_ai_recommendation_test_smoke.py
	python3 scripts/saee_external_ai_manual_run_smoke.py
	python3 scripts/saee_external_ai_manual_test_start_smoke.py
	python3 scripts/saee_external_ai_calibration_run_smoke.py
	python3 scripts/saee_external_ai_calibration_defer_smoke.py
	python3 scripts/saee_internal_self_play_smoke.py
	python3 scripts/saee_semantic_dominance_smoke.py
	python3 scripts/saee_strategy_intake_smoke.py
	python3 scripts/saee_strategy_intake_dry_run_smoke.py
	python3 scripts/saee_public_signal_run_001_smoke.py
	python3 scripts/saee_public_signal_review_draft_smoke.py
	python3 scripts/saee_public_signal_final_review_smoke.py
	python3 scripts/saee_public_signal_documentation_execution_smoke.py
	python3 scripts/saee_commercial_boundary_smoke.py
	python3 scripts/saee_auth_readiness_smoke.py
	python3 scripts/saee_identity_provider_readiness_smoke.py
	python3 scripts/saee_rbac_policy_template_smoke.py
	python3 scripts/saee_rbac_preview_enforcement_smoke.py
	python3 scripts/saee_jwt_preview_auth_smoke.py
	python3 scripts/saee_jwt_preview_operator_packet_smoke.py
	python3 scripts/saee_production_auth_evidence_readiness_smoke.py
	python3 scripts/saee_auth_evidence_runner_smoke.py
	python3 scripts/saee_production_auth_evidence_path_smoke.py
	python3 scripts/saee_production_identity_provider_decision_packet_smoke.py
	python3 scripts/saee_production_identity_provider_readiness_board_smoke.py
	python3 scripts/saee_production_identity_provider_input_completion_helper_smoke.py
	python3 scripts/saee_production_identity_provider_human_decision_runbook_smoke.py
	python3 scripts/saee_production_identity_provider_evidence_builder_request_template_smoke.py
	python3 scripts/saee_production_identity_provider_approval_input_validator_smoke.py
	python3 scripts/saee_oauth_oidc_approval_input_validator_smoke.py
	python3 scripts/saee_oauth_oidc_approval_input_prompt_smoke.py
	python3 scripts/saee_rbac_approval_input_validator_smoke.py
	python3 scripts/saee_rbac_approval_input_prompt_smoke.py
	python3 scripts/saee_tenant_storage_approval_input_validator_smoke.py
	python3 scripts/saee_tenant_storage_approval_input_prompt_smoke.py
	python3 scripts/saee_scenario_template_smoke.py
	python3 scripts/saee_auth_oidc_rbac_fixture_dry_run_smoke.py
	python3 scripts/saee_production_support_evidence_readiness_smoke.py
	python3 scripts/saee_support_evidence_runner_smoke.py
	python3 scripts/saee_support_sla_on_call_review_packet_smoke.py
	python3 scripts/saee_support_contact_decision_packet_smoke.py
	python3 scripts/saee_support_contact_preflight_smoke.py
	python3 scripts/saee_support_contact_readiness_board_smoke.py
	python3 scripts/saee_support_contact_human_input_bridge_smoke.py
	python3 scripts/saee_support_contact_human_input_bridge_completion_helper_smoke.py
	python3 scripts/saee_support_contact_human_input_entrypoint_smoke.py
	python3 scripts/saee_support_contact_first_priority_packet_smoke.py
	python3 scripts/saee_support_contact_minimum_human_input_workspace_smoke.py
	python3 scripts/saee_support_contact_human_filled_evidence_refresh_smoke.py
	python3 scripts/saee_support_contact_closure_gap_review_smoke.py
	python3 scripts/saee_support_contact_state_reconciliation_smoke.py
	python3 scripts/saee_support_group_closure_review_packet_smoke.py
	python3 scripts/saee_support_group_final_closure_decision_request_smoke.py
	python3 scripts/saee_support_group_final_closure_decision_validator_smoke.py
	python3 scripts/saee_support_group_final_closure_decision_completion_helper_smoke.py
	python3 scripts/saee_commercial_matrix_update_request_packet_smoke.py
	python3 scripts/saee_commercial_matrix_update_execution_request_packet_smoke.py
	python3 scripts/saee_commercial_matrix_update_execution_approval_input_smoke.py
	python3 scripts/saee_commercial_matrix_update_execution_approval_phrase_intake_smoke.py
	python3 scripts/saee_commercial_matrix_update_execution_approval_copy_card_smoke.py
	python3 scripts/saee_commercial_matrix_update_execution_next_step_router_smoke.py
	python3 scripts/saee_commercial_matrix_update_execution_dry_run_smoke.py
	python3 scripts/saee_commercial_matrix_update_execution_applier_smoke.py
	python3 scripts/saee_pricing_page_closure_review_packet_smoke.py
	python3 scripts/saee_pricing_page_minimum_human_input_workspace_smoke.py
	python3 scripts/saee_formal_security_review_minimum_human_input_workspace_smoke.py
	python3 scripts/saee_production_restore_policy_minimum_human_input_workspace_smoke.py
	python3 scripts/saee_support_contact_bridge_validator_dry_run_smoke.py
	python3 scripts/saee_support_contact_bridge_human_handoff_checkpoint_smoke.py
	python3 scripts/saee_support_contact_approval_input_validator_smoke.py
	python3 scripts/saee_support_contact_approval_input_prompt_smoke.py
	python3 scripts/saee_support_contact_evidence_builder_smoke.py
	python3 scripts/saee_support_contact_evidence_builder_request_template_smoke.py
	python3 scripts/saee_support_contact_evidence_builder_execution_request_smoke.py
	python3 scripts/saee_support_contact_evidence_path_smoke.py
	python3 scripts/saee_customer_support_approval_input_validator_smoke.py
	python3 scripts/saee_customer_support_approval_input_prompt_smoke.py
	python3 scripts/saee_customer_support_evidence_builder_smoke.py
	python3 scripts/saee_customer_support_evidence_path_smoke.py
	python3 scripts/saee_sla_approval_input_validator_smoke.py
	python3 scripts/saee_sla_approval_input_prompt_smoke.py
	python3 scripts/saee_sla_evidence_builder_smoke.py
	python3 scripts/saee_sla_evidence_path_smoke.py
	python3 scripts/saee_on_call_approval_input_validator_smoke.py
	python3 scripts/saee_on_call_approval_input_prompt_smoke.py
	python3 scripts/saee_on_call_evidence_builder_smoke.py
	python3 scripts/saee_on_call_evidence_path_smoke.py
	python3 scripts/saee_support_sla_evidence_profile_smoke.py
	python3 scripts/saee_production_data_operations_evidence_readiness_smoke.py
	python3 scripts/saee_data_operations_evidence_runner_smoke.py
	python3 scripts/saee_restore_tested_evidence_profile_smoke.py
	python3 scripts/saee_restore_tested_local_evidence_promotion_request_smoke.py
	python3 scripts/saee_production_restore_policy_evidence_builder_smoke.py
	python3 scripts/saee_production_restore_policy_approval_input_validator_smoke.py
	python3 scripts/saee_production_restore_policy_approval_input_prompt_smoke.py
	python3 scripts/saee_data_operations_evidence_profile_smoke.py
	python3 scripts/saee_production_restore_policy_review_packet_smoke.py
	python3 scripts/saee_production_restore_policy_draft_smoke.py
	python3 scripts/saee_production_operations_evidence_readiness_smoke.py
	python3 scripts/saee_operations_evidence_runner_smoke.py
	python3 scripts/saee_production_monitoring_evidence_builder_smoke.py
	python3 scripts/saee_production_monitoring_approval_input_validator_smoke.py
	python3 scripts/saee_production_monitoring_approval_input_prompt_smoke.py
	python3 scripts/saee_production_monitoring_evidence_path_smoke.py
	python3 scripts/saee_external_alert_delivery_evidence_builder_smoke.py
	python3 scripts/saee_external_alert_delivery_approval_input_validator_smoke.py
	python3 scripts/saee_external_alert_delivery_approval_input_prompt_smoke.py
	python3 scripts/saee_external_alert_delivery_evidence_path_smoke.py
	python3 scripts/saee_operations_on_call_rotation_approval_input_validator_smoke.py
	python3 scripts/saee_operations_on_call_rotation_approval_input_prompt_smoke.py
	python3 scripts/saee_operations_on_call_rotation_evidence_builder_smoke.py
	python3 scripts/saee_operations_on_call_rotation_evidence_path_smoke.py
	python3 scripts/saee_operations_monitoring_alert_review_packet_smoke.py
	python3 scripts/saee_operations_evidence_profile_smoke.py
	python3 scripts/saee_operations_human_filled_evidence_run_smoke.py
	python3 scripts/saee_production_privacy_security_legal_evidence_readiness_smoke.py
	python3 scripts/saee_privacy_security_legal_evidence_runner_smoke.py
	python3 scripts/saee_privacy_security_legal_evidence_path_smoke.py
	python3 scripts/saee_formal_security_review_scope_draft_smoke.py
	python3 scripts/saee_formal_security_review_evidence_builder_smoke.py
	python3 scripts/saee_formal_security_review_approval_input_validator_smoke.py
	python3 scripts/saee_formal_security_review_approval_input_prompt_smoke.py
	python3 scripts/saee_privacy_legal_dpa_evidence_builder_smoke.py
	python3 scripts/saee_privacy_legal_dpa_approval_input_prompt_smoke.py
	python3 scripts/saee_privacy_legal_dpa_approval_input_validator_smoke.py
	python3 scripts/saee_vulnerability_management_evidence_builder_smoke.py
	python3 scripts/saee_vulnerability_management_approval_input_prompt_smoke.py
	python3 scripts/saee_vulnerability_management_approval_input_validator_smoke.py
	python3 scripts/saee_privacy_legal_review_packet_smoke.py
	python3 scripts/saee_data_processing_agreement_review_packet_smoke.py
	python3 scripts/saee_privacy_security_legal_human_filled_evidence_run_smoke.py
	python3 scripts/saee_privacy_security_legal_followup_state_reconciliation_smoke.py
	python3 scripts/saee_production_billing_revenue_evidence_readiness_smoke.py
	python3 scripts/saee_billing_revenue_evidence_runner_smoke.py
	python3 scripts/saee_pricing_page_review_packet_smoke.py
	python3 scripts/saee_pricing_page_copy_draft_smoke.py
	python3 scripts/saee_pricing_page_evidence_builder_smoke.py
	python3 scripts/saee_pricing_page_approval_input_prompt_smoke.py
	python3 scripts/saee_pricing_page_approval_input_validator_smoke.py
	python3 scripts/saee_payment_provider_review_packet_smoke.py
	python3 scripts/saee_payment_provider_evidence_builder_smoke.py
	python3 scripts/saee_payment_provider_approval_input_prompt_smoke.py
	python3 scripts/saee_payment_provider_approval_input_validator_smoke.py
	python3 scripts/saee_invoice_process_review_packet_smoke.py
	python3 scripts/saee_invoice_process_evidence_builder_smoke.py
	python3 scripts/saee_invoice_process_approval_input_prompt_smoke.py
	python3 scripts/saee_invoice_process_approval_input_validator_smoke.py
	python3 scripts/saee_tax_review_packet_smoke.py
	python3 scripts/saee_tax_review_evidence_builder_smoke.py
	python3 scripts/saee_tax_review_approval_input_prompt_smoke.py
	python3 scripts/saee_tax_review_approval_input_validator_smoke.py
	python3 scripts/saee_refund_policy_review_packet_smoke.py
	python3 scripts/saee_refund_policy_evidence_builder_smoke.py
	python3 scripts/saee_refund_policy_approval_input_prompt_smoke.py
	python3 scripts/saee_refund_policy_approval_input_validator_smoke.py
	python3 scripts/saee_tenant_billing_isolation_review_packet_smoke.py
	python3 scripts/saee_tenant_billing_isolation_evidence_builder_smoke.py
	python3 scripts/saee_tenant_billing_isolation_approval_input_prompt_smoke.py
	python3 scripts/saee_tenant_billing_isolation_approval_input_validator_smoke.py
	python3 scripts/saee_billing_revenue_evidence_profile_smoke.py
	python3 scripts/saee_billing_revenue_evidence_path_smoke.py
	python3 scripts/saee_billing_revenue_human_filled_evidence_run_smoke.py
	python3 scripts/saee_billing_followup_state_reconciliation_smoke.py
	python3 scripts/saee_phase1_identity_tenant_human_filled_evidence_run_smoke.py
	python3 scripts/saee_phase1_identity_tenant_state_reconciliation_smoke.py
	python3 scripts/saee_internal_founder_pilot_evidence_run_smoke.py
	python3 scripts/saee_commercial_final_human_inspection_record_smoke.py
	python3 scripts/saee_commercial_blocker_convergence_audit_smoke.py
	python3 scripts/saee_customer_validation_last_mile_packet_smoke.py
	python3 scripts/saee_external_customer_validation_next_action_smoke.py
	python3 scripts/saee_external_customer_validation_session_kit_smoke.py
	python3 scripts/saee_external_customer_validation_session_entry_importer_smoke.py
	python3 scripts/saee_external_customer_validation_session_entry_workbench_smoke.py
	python3 scripts/saee_production_tenant_storage_evidence_readiness_smoke.py
	python3 scripts/saee_tenant_storage_isolation_evidence_runner_smoke.py
	python3 scripts/saee_production_tenant_storage_evidence_path_smoke.py
	python3 scripts/saee_tenant_security_privacy_review_packet_smoke.py
	python3 scripts/saee_tenant_storage_remaining_gap_packet_smoke.py
	python3 scripts/saee_production_customer_validation_evidence_readiness_smoke.py
	python3 scripts/saee_customer_validation_evidence_runner_smoke.py
	python3 scripts/saee_customer_validation_evidence_builder_smoke.py
	python3 scripts/saee_customer_validation_approval_input_prompt_smoke.py
	python3 scripts/saee_customer_validation_approval_input_validator_smoke.py
	python3 scripts/saee_customer_validation_evidence_path_smoke.py
	python3 scripts/saee_production_evidence_templates_smoke.py
	python3 scripts/saee_production_evidence_intake_audit_smoke.py
	python3 scripts/saee_production_auth_requirements_smoke.py
	python3 scripts/saee_production_operations_requirements_smoke.py
	python3 scripts/saee_production_support_sla_requirements_smoke.py
	python3 scripts/saee_production_privacy_security_legal_requirements_smoke.py
	python3 scripts/saee_production_billing_revenue_requirements_smoke.py
	python3 scripts/saee_production_customer_validation_requirements_smoke.py
	python3 scripts/saee_production_data_operations_requirements_smoke.py
	python3 scripts/saee_production_tenant_storage_isolation_requirements_smoke.py
	python3 scripts/saee_operations_telemetry_smoke.py
	python3 scripts/saee_operations_alert_policy_smoke.py
	python3 scripts/saee_operations_telemetry_api_smoke.py
	python3 scripts/saee_support_readiness_smoke.py
	python3 scripts/saee_preview_readiness_api_smoke.py
	python3 scripts/saee_data_operations_readiness_api_smoke.py
	python3 scripts/saee_billing_pricing_readiness_api_smoke.py
	python3 scripts/saee_operations_readiness_api_smoke.py
	python3 scripts/saee_privacy_security_readiness_api_smoke.py
	python3 scripts/saee_legal_readiness_api_smoke.py
	python3 scripts/saee_privacy_security_readiness_smoke.py
	python3 scripts/saee_legal_readiness_smoke.py
	python3 scripts/saee_vulnerability_management_readiness_smoke.py
	python3 scripts/saee_billing_pricing_readiness_smoke.py
	python3 scripts/saee_controlled_trial_quickstart_smoke.py
	python3 scripts/saee_local_mvp_tryout_guide_smoke.py
	python3 scripts/saee_local_trial_handoff_packet_smoke.py
	python3 scripts/saee_local_trial_session_smoke.py
	python3 scripts/saee_local_trial_make_targets_smoke.py
	python3 scripts/saee_local_trial_preflight_snapshot_smoke.py
	python3 scripts/saee_local_trial_cold_start_preflight_smoke.py
	python3 scripts/saee_local_trial_http_e2e_smoke.py
	python3 scripts/saee_local_trial_lifecycle_proof_smoke.py
	python3 scripts/saee_baidu_cloud_handoff_preflight_smoke.py
	python3 scripts/saee_baidu_cloud_handoff_package_smoke.py
	python3 scripts/saee_local_tryout_readiness_card_smoke.py
	python3 scripts/saee_controlled_trial_local_e2e_smoke.py
	python3 scripts/saee_controlled_trial_operator_packet_smoke.py
	python3 scripts/saee_controlled_trial_observation_runner_smoke.py
	python3 scripts/saee_controlled_preview_env_template_smoke.py
	python3 scripts/saee_operations_readiness_smoke.py
	python3 scripts/saee_incident_response_runbook_smoke.py
	python3 scripts/saee_tenant_boundary_smoke.py
	python3 scripts/saee_request_limits_smoke.py
	python3 scripts/saee_persistence_smoke.py
	python3 scripts/saee_request_audit_smoke.py
	python3 scripts/saee_commercial_preflight_smoke.py
	python3 scripts/saee_commercial_go_no_go_smoke.py
	python3 scripts/saee_commercial_status_api_smoke.py
	python3 scripts/saee_commercial_next_action_summary_smoke.py
	python3 scripts/saee_commercial_trial_operator_status_smoke.py
	python3 scripts/saee_commercial_evidence_sprint_sequencer_smoke.py
	python3 scripts/saee_commercial_launch_evidence_path_smoke.py
	python3 scripts/saee_commercial_launch_blocker_work_order_smoke.py
	python3 scripts/saee_commercial_evidence_profile_smoke.py
	python3 scripts/saee_production_blocker_gap_matrix_smoke.py
	python3 scripts/saee_commercial_blocker_dependency_plan_smoke.py
	python3 scripts/saee_phase1_identity_tenant_evidence_task_smoke.py
	python3 scripts/saee_phase2_data_operations_evidence_task_smoke.py
	python3 scripts/saee_phase2_data_operations_gap_audit_smoke.py
	python3 scripts/saee_phase3_support_security_legal_gap_audit_smoke.py
	python3 scripts/saee_phase4_commercial_packaging_billing_gap_audit_smoke.py
	python3 scripts/saee_phase5_customer_validation_launch_gap_audit_smoke.py
	python3 scripts/saee_commercial_production_evidence_collection_packet_smoke.py
	python3 scripts/saee_phase1_identity_tenant_priority_evidence_collection_smoke.py
	python3 scripts/saee_phase2_data_operations_priority_evidence_collection_smoke.py
	python3 scripts/saee_phase3_support_security_legal_priority_evidence_collection_smoke.py
	python3 scripts/saee_phase4_commercial_packaging_billing_priority_evidence_collection_smoke.py
	python3 scripts/saee_phase5_customer_validation_launch_priority_evidence_collection_smoke.py
	python3 scripts/saee_commercial_readiness_dashboard_smoke.py
	python3 scripts/saee_commercial_human_action_board_smoke.py
	python3 scripts/saee_commercial_blocker_closure_readiness_board_smoke.py
	python3 scripts/saee_commercial_next_evidence_sprint_smoke.py
	python3 scripts/saee_commercial_sprint_handoff_pack_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_workbook_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_workbook_validator_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_transfer_map_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_transfer_resolver_dry_run_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_completion_queue_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet_validator_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_import_dry_run_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_guidance_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_readiness_audit_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_validator_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_smoke.py
	python3 scripts/saee_commercial_review_batch_human_fill_card_smoke.py
	python3 scripts/saee_commercial_review_batch_human_execution_packet_smoke.py
	python3 scripts/saee_commercial_review_batch_human_entry_quality_guide_smoke.py
	python3 scripts/saee_commercial_review_batch_template_preflight_smoke.py
	python3 scripts/saee_commercial_review_batch_post_fill_validation_runbook_smoke.py
	python3 scripts/saee_commercial_review_batch_post_fill_readiness_preview_smoke.py
	python3 scripts/saee_commercial_review_batch_post_fill_check_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_execution_stop_gate_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_human_worksheet_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_validator_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer_smoke.py
	python3 scripts/saee_commercial_sprint_human_confirmed_recommended_values_smoke.py
	python3 scripts/saee_commercial_sprint_human_confirmed_values_import_preview_smoke.py
	python3 scripts/saee_commercial_sprint_remaining_recommended_values_draft_smoke.py
	python3 scripts/saee_commercial_sprint_remaining_human_confirmed_values_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_template_transfer_applier_smoke.py
	python3 scripts/saee_commercial_sprint_post_transfer_validator_sequencer_smoke.py
	python3 scripts/saee_commercial_sprint_validator_approval_request_packet_smoke.py
	python3 scripts/saee_commercial_sprint_validator_execution_run_smoke.py
	python3 scripts/saee_commercial_sprint_validator_hold_output_review_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_pipeline_synthetic_proof_smoke.py
	python3 scripts/saee_commercial_sprint_all_confirmed_values_source_apply_smoke.py
	python3 scripts/saee_commercial_sprint_human_input_safety_preflight_smoke.py
	python3 scripts/saee_commercial_sprint_workbook_import_approval_request_packet_smoke.py
	python3 scripts/saee_commercial_sprint_workbook_import_execution_request_packet_smoke.py
	python3 scripts/saee_commercial_sprint_workbook_import_execution_applied_smoke.py
	python3 scripts/saee_commercial_sprint_template_transfer_execution_request_packet_smoke.py
	python3 scripts/saee_commercial_sprint_active_human_input_board_smoke.py
	python3 scripts/saee_commercial_readiness_status_snapshot_smoke.py
	python3 scripts/saee_commercial_readiness_gap_audit_smoke.py
	python3 scripts/saee_commercial_blocker_priority_index_smoke.py
	python3 scripts/saee_partial_evidence_promotion_queue_smoke.py
	python3 scripts/saee_commercial_review_ready_marker_catalog_smoke.py
	python3 scripts/saee_commercial_matrix_update_scope_refresh_smoke.py
	python3 scripts/saee_commercial_matrix_update_scope_refresh_approval_intake_smoke.py
	python3 scripts/saee_restore_tested_promotion_review_packet_smoke.py
	python3 scripts/saee_restore_tested_promotion_decision_validator_smoke.py
	python3 scripts/saee_commercial_readiness_begin_here_smoke.py
	python3 scripts/saee_commercial_readiness_state_consistency_audit_smoke.py
	python3 scripts/saee_commercial_review_packet_canonical_aliases_smoke.py
	python3 scripts/saee_production_blocker_evidence_path_coverage_audit_smoke.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_smoke.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator_smoke.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper_smoke.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_readiness_board_smoke.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_action_packet_smoke.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator_smoke.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper_smoke.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_request_packet_smoke.py
	python3 scripts/saee_commercial_next_human_input_prompt_smoke.py
	python3 scripts/saee_commercial_evidence_sprint_human_sequence_packet_smoke.py
	python3 scripts/saee_commercial_evidence_request_draft_packet_smoke.py
	python3 scripts/saee_commercial_evidence_request_approval_input_validator_smoke.py
	python3 scripts/saee_commercial_evidence_request_approval_completion_helper_smoke.py
	python3 scripts/saee_commercial_evidence_request_approval_readiness_board_smoke.py
	python3 scripts/saee_commercial_review_batch_safe_prefill_audit_smoke.py
	python3 scripts/saee_phase1_identity_tenant_gap_audit_smoke.py
	python3 scripts/saee_phase1_identity_tenant_evidence_builder_smoke.py
	python3 scripts/saee_phase1_identity_tenant_evidence_profile_smoke.py
	python3 scripts/saee_controlled_preview_tenant_storage_smoke.py
	python3 scripts/saee_data_retention_smoke.py
	python3 scripts/saee_data_backup_smoke.py
	python3 scripts/saee_data_restore_drill_smoke.py

check-experimental:
	python3 scripts/kernel_smoke.py
	python3 scripts/kernel_v0_2_smoke.py
	python3 scripts/saee_v0_3_smoke.py
	python3 scripts/saee_v0_4_smoke.py
	python3 scripts/saee_v0_5_smoke.py
	python3 scripts/saee_v0_6_smoke.py
	python3 scripts/saee_v0_7_smoke.py
	python3 scripts/saee_v0_8_smoke.py
	python3 scripts/saee_phase2_smoke.py

public-claim-lint-smoke:
	python3 scripts/saee_public_claim_lint.py
	python3 scripts/saee_public_claim_lint_smoke.py

check-public-claim-lint:
	python3 scripts/saee_public_claim_lint.py
	python3 scripts/saee_public_claim_lint_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/public_claim_lint/public_claim_lint.local.json
	python3 -m json.tool agent-index.json

kernel-demo:
	python3 -m kernel.runtime --generations 3 --output-dir kernel/output/demo-run

kernel-smoke:
	python3 scripts/kernel_smoke.py

kernel-v0-2-demo:
	python3 -m kernel_v0_2.runtime_v0_2 --generations 4 --output-dir kernel_v0_2/output/demo-run

kernel-v0-2-smoke:
	python3 scripts/kernel_v0_2_smoke.py

saee-v0-3-demo:
	python3 saee_v0_3/KERNEL_BOOTSTRAP_SCRIPT.py --generations 3 --output-dir saee_v0_3/output/demo-run

saee-v0-3-smoke:
	python3 scripts/saee_v0_3_smoke.py

saee-v0-4-demo:
	python3 saee_v0_4/KERNEL_BOOTSTRAP_SCRIPT.py --generations 5 --output-dir saee_v0_4/output/demo-run

saee-v0-4-smoke:
	python3 scripts/saee_v0_4_smoke.py

saee-v0-5-demo:
	python3 saee_v0_5/bootstrap/v0_5_bootstrap.py --generations 6 --output-dir saee_v0_5/output/demo-run

saee-v0-5-smoke:
	python3 scripts/saee_v0_5_smoke.py

saee-v0-6-demo:
	python3 saee_v0_6/bootstrap/v0_6_bootstrap.py --generations 6 --output-dir saee_v0_6/output/demo-run

saee-v0-6-smoke:
	python3 scripts/saee_v0_6_smoke.py

saee-v0-7-demo:
	python3 saee_v0_7/bootstrap/v0_7_bootstrap.py --generations 6 --output-dir saee_v0_7/output/demo-run

saee-v0-7-smoke:
	python3 scripts/saee_v0_7_smoke.py

saee-v0-8-demo:
	python3 saee_v0_8/bootstrap/v0_8_bootstrap.py --generations 6 --output-dir saee_v0_8/output/demo-run

saee-v0-8-smoke:
	python3 scripts/saee_v0_8_smoke.py

phase2-demo:
	python3 saee_phase2/bootstrap/phase2_bootstrap.py --generations 6 --output-dir saee_phase2/output/demo-run

phase2-smoke:
	python3 scripts/saee_phase2_smoke.py

saee-v1-0-demo:
	python3 saee_v1_0/bootstrap/v1_0_bootstrap.py --generations 12 --population-size 8 --output-dir saee_v1_0/output/demo-run

saee-v1-0-smoke:
	python3 scripts/saee_v1_0_smoke.py

experiment-demo:
	python3 saee_experiments/bootstrap/experiment_bootstrap.py --generation-count 100 --output-dir saee_experiments/output/demo-run

experiment-smoke:
	python3 scripts/saee_experiment_smoke.py

saee-v1-2-demo:
	python3 saee_v1_2/bootstrap/v1_2_bootstrap.py --generations 24 --population-size 12 --output-dir saee_v1_2/results/demo-run

saee-v1-2-smoke:
	python3 scripts/saee_v1_2_smoke.py

parasitic-phase-demo:
	python3 saee_v1_2/parasitic_phase/run_parasitic_phase_experiment.py --output-dir saee_v1_2/results/parasitic-phase-demo

parasitic-phase-smoke:
	python3 scripts/saee_parasitic_phase_smoke.py

check-parasitic-phase: parasitic-phase-smoke

global-state-check:
	python3 scripts/saee_global_state_check.py

mvp-api-smoke:
	python3 scripts/saee_mvp_api_smoke.py

check-tenant-scoped-experiment-listing:
	python3 scripts/saee_mvp_api_smoke.py
	python3 scripts/saee_controlled_preview_tenant_storage_smoke.py
	python3 -m json.tool schemas/saee_mvp_api.schema.json
	python3 -m json.tool agent-index.json

controlled-preview-request-smoke:
	python3 scripts/saee_controlled_preview_request_smoke.py

check-controlled-preview-request:
	python3 scripts/saee_controlled_preview_request_smoke.py
	python3 scripts/saee_controlled_preview_request_validator.py --json
	python3 -m json.tool agent-interface/schemas/controlled-preview-request.schema.json
	python3 -m json.tool agent-interface/examples/controlled-preview-request.json

commercial-quote-request-smoke:
	python3 scripts/saee_commercial_quote_request_smoke.py

check-commercial-quote-request:
	python3 scripts/saee_commercial_quote_request_smoke.py
	python3 scripts/saee_commercial_quote_request_validator.py --json
	python3 -m json.tool agent-interface/schemas/commercial-quote-request.schema.json
	python3 -m json.tool agent-interface/schemas/commercial-quote-response.schema.json
	python3 -m json.tool agent-interface/examples/commercial-quote-request.json

agent-support-case-smoke:
	python3 scripts/saee_agent_support_case_smoke.py

check-agent-support-case:
	python3 scripts/saee_agent_support_case_smoke.py
	python3 scripts/saee_agent_support_case_validator.py --json
	python3 -m json.tool agent-interface/schemas/agent-support-case-request.schema.json
	python3 -m json.tool agent-interface/schemas/agent-support-case-response.schema.json
	python3 -m json.tool agent-interface/examples/agent-support-case-request.json

landing-smoke:
	python3 scripts/saee_landing_page_smoke.py

landing-api-integration-smoke:
	python3 scripts/saee_landing_api_integration_smoke.py

landing-jwt-preview-auth-smoke:
	python3 scripts/saee_landing_jwt_preview_auth_smoke.py

check-landing-jwt-preview-auth:
	python3 scripts/saee_landing_jwt_preview_auth_smoke.py
	python3 scripts/saee_landing_page_smoke.py
	python3 scripts/saee_landing_api_integration_smoke.py
	python3 -m py_compile scripts/saee_landing_jwt_preview_auth_smoke.py
	python3 -m json.tool agent-index.json

first-user-test-smoke:
	python3 scripts/saee_first_user_test_plan_smoke.py

agent-recommendation-smoke:
	python3 scripts/saee_agent_recommendation_surface_smoke.py

agent-recommendation-validation-smoke:
	python3 scripts/saee_agent_recommendation_validation_smoke.py

external-ai-recommendation-test-smoke:
	python3 scripts/saee_external_ai_recommendation_test_smoke.py

external-ai-manual-run-smoke:
	python3 scripts/saee_external_ai_manual_run_smoke.py

external-ai-manual-test-start-smoke:
	python3 scripts/saee_external_ai_manual_test_start_smoke.py

external-ai-calibration-run-smoke:
	python3 scripts/saee_external_ai_calibration_run_smoke.py

external-ai-calibration-defer-smoke:
	python3 scripts/saee_external_ai_calibration_defer_smoke.py

check-external-ai-calibration-run:
	python3 scripts/saee_external_ai_calibration_run_smoke.py
	python3 -m json.tool agent_recommendation/external_test/manual_runs/run_001/calibration_001/CALIBRATION_STATUS.json
	python3 -m json.tool agent_recommendation/external_test/manual_runs/run_001/calibration_001/CALIBRATION_RESULT_ENTRY.json
	python3 -m json.tool agent-index.json

check-external-ai-calibration-defer:
	python3 scripts/saee_external_ai_calibration_defer_smoke.py
	python3 -m json.tool agent_recommendation/external_test/manual_runs/run_001/calibration_001/CALIBRATION_DEFER_RECORD.json
	python3 -m json.tool agent-index.json

internal-self-play-smoke:
	python3 scripts/saee_internal_self_play_smoke.py

check-internal-self-play:
	python3 scripts/saee_internal_self_play_smoke.py
	python3 -m json.tool agent_recommendation/internal_self_play/SELF_PLAY_RESULTS.json
	python3 -m json.tool agent-index.json

semantic-dominance-smoke:
	python3 scripts/saee_semantic_dominance_smoke.py

check-semantic-dominance:
	python3 scripts/saee_semantic_dominance_smoke.py
	python3 -m json.tool agent-index.json

strategy-intake-smoke:
	python3 scripts/saee_strategy_intake_smoke.py

strategy-intake-dry-run-smoke:
	python3 scripts/saee_strategy_intake_dry_run_smoke.py

check-external-ai-test:
	python3 scripts/saee_external_ai_recommendation_test_smoke.py
	python3 -m json.tool agent_recommendation/external_test/EXTERNAL_VALIDATION_RESULTS.json
	python3 -m json.tool agent-index.json

check-external-ai-manual-run:
	python3 scripts/saee_external_ai_manual_run_smoke.py
	python3 -m json.tool agent_recommendation/external_test/manual_runs/run_001/manual_results_entry.json
	python3 -m json.tool agent_recommendation/external_test/manual_runs/run_001/run_status.json
	python3 -m json.tool agent-index.json

check-external-ai-manual-test-start:
	python3 scripts/saee_external_ai_manual_test_start_smoke.py
	python3 -m json.tool agent_recommendation/external_test/manual_runs/run_001/ACTIVE_TEST_SESSION.json
	python3 -m json.tool agent_recommendation/external_test/manual_runs/run_001/run_status.json
	python3 -m json.tool agent-index.json

check-strategy-intake:
	python3 scripts/saee_strategy_intake_smoke.py
	python3 -m json.tool agent-index.json

check-strategy-intake-dry-run:
	python3 scripts/saee_strategy_intake_dry_run_smoke.py
	python3 -m json.tool strategy_intake/dry_runs/run_001/DRY_RUN_SUMMARY.json
	python3 -m json.tool agent-index.json

public-signal-run-001-smoke:
	python3 scripts/saee_public_signal_run_001_smoke.py

check-public-signal-run-001:
	python3 scripts/saee_public_signal_run_001_smoke.py
	python3 -m json.tool strategy_intake/public_signal_runs/run_001/SIGNAL_SUMMARY.json
	python3 -m json.tool agent-index.json

public-signal-review-draft-smoke:
	python3 scripts/saee_public_signal_review_draft_smoke.py

check-public-signal-review-draft:
	python3 scripts/saee_public_signal_review_draft_smoke.py
	python3 -m json.tool strategy_intake/public_signal_runs/run_001/HUMAN_REVIEW_DECISION_DRAFT.json
	python3 -m json.tool agent-index.json

public-signal-final-review-smoke:
	python3 scripts/saee_public_signal_final_review_smoke.py

check-public-signal-final-review:
	python3 scripts/saee_public_signal_final_review_smoke.py
	python3 -m json.tool strategy_intake/public_signal_runs/run_001/FINAL_HUMAN_REVIEW_DECISION.json
	python3 -m json.tool agent-index.json

public-signal-documentation-execution-smoke:
	python3 scripts/saee_public_signal_documentation_execution_smoke.py

check-public-signal-documentation-execution:
	python3 scripts/saee_public_signal_documentation_execution_smoke.py
	python3 -m json.tool strategy_intake/public_signal_runs/run_001/documentation_execution/DOCUMENTATION_EXECUTION_SUMMARY.json
	python3 -m json.tool agent_recommendation/PRODUCT_FACTS.json
	python3 -m json.tool agent-index.json

commercial-boundary-smoke:
	python3 scripts/saee_commercial_boundary_smoke.py

check-commercial-boundary:
	python3 scripts/saee_commercial_boundary_smoke.py
	python3 -m json.tool agent-index.json

auth-readiness-smoke:
	python3 scripts/saee_auth_readiness_smoke.py

check-auth-readiness:
	python3 scripts/saee_auth_readiness_smoke.py
	python3 scripts/saee_auth_readiness.py
	python3 -m json.tool agent-index.json

identity-provider-readiness-smoke:
	python3 scripts/saee_identity_provider_readiness_smoke.py

check-identity-provider-readiness:
	python3 scripts/saee_identity_provider_readiness_smoke.py
	python3 scripts/saee_identity_provider_readiness.py
	python3 -m json.tool agent-index.json

rbac-policy-template-smoke:
	python3 scripts/generate_rbac_policy_template.py
	python3 scripts/saee_rbac_policy_template_smoke.py

check-rbac-policy-template:
	python3 scripts/generate_rbac_policy_template.py
	python3 scripts/saee_rbac_policy_template_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/rbac_policy_templates/production_rbac_policy.template.json
	python3 -m json.tool agent-index.json

rbac-preview-enforcement-smoke:
	python3 scripts/saee_rbac_preview_enforcement_smoke.py
	python3 scripts/saee_rbac_policy_consistency_smoke.py

check-rbac-preview-enforcement:
	python3 scripts/saee_rbac_preview_enforcement_smoke.py
	python3 scripts/saee_rbac_policy_consistency_smoke.py
	python3 -m py_compile saee_backend/config.py saee_backend/api/security.py saee_backend/main.py saee_backend/api/experiment.py saee_backend/api/operations.py saee_backend/api/readiness.py saee_backend/api/commercial.py saee_backend/services/rbac_policy.py
	python3 -m json.tool agent-index.json

rbac-role-permission-consistency-smoke:
	python3 scripts/saee_rbac_role_permission_consistency_profile_smoke.py
	python3 scripts/saee_rbac_policy_consistency_smoke.py

check-rbac-role-permission-consistency:
	python3 scripts/saee_rbac_role_permission_consistency_profile.py
	python3 scripts/saee_rbac_role_permission_consistency_profile_smoke.py
	python3 scripts/saee_rbac_policy_consistency_smoke.py
	python3 scripts/saee_identity_provider_readiness_smoke.py
	python3 scripts/saee_phase1_local_execution_authorization_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/auth_evidence/rbac_role_permission_consistency.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_local_execution_authorization/authorization.local.json
	python3 -m py_compile saee_backend/services/rbac_policy.py saee_backend/services/identity_provider_readiness.py

jwt-preview-auth-smoke:
	python3 scripts/saee_jwt_preview_auth_smoke.py

check-jwt-preview-auth:
	python3 scripts/saee_jwt_preview_auth_smoke.py
	python3 -m py_compile saee_backend/config.py saee_backend/api/security.py saee_backend/main.py saee_backend/api/experiment.py saee_backend/api/operations.py saee_backend/api/readiness.py saee_backend/api/commercial.py saee_backend/services/jwt_preview_auth.py saee_backend/services/rbac_policy.py
	python3 -m json.tool agent-index.json

jwt-preview-operator-packet-smoke:
	python3 scripts/saee_jwt_preview_operator_packet_smoke.py

check-jwt-preview-operator-packet:
	python3 scripts/saee_jwt_preview_operator_packet_smoke.py
	python3 -m py_compile scripts/saee_jwt_preview_token.py scripts/saee_jwt_preview_operator_packet_smoke.py saee_backend/services/jwt_preview_auth.py saee_backend/config.py
	python3 -m json.tool agent-index.json

production-support-evidence-readiness-smoke:
	python3 scripts/saee_production_support_evidence_readiness_smoke.py

check-production-support-evidence-readiness:
	python3 scripts/saee_production_support_evidence_readiness_smoke.py
	python3 scripts/saee_production_support_evidence_readiness.py
	python3 -m json.tool agent-index.json

support-evidence-runner-smoke:
	python3 scripts/saee_support_evidence_runner.py
	python3 scripts/saee_support_evidence_runner_smoke.py

check-support-evidence-runner:
	python3 scripts/saee_support_evidence_runner.py
	python3 scripts/saee_support_evidence_runner_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_evidence.local.json
	python3 -m json.tool agent-index.json

support-sla-on-call-review-packet-smoke:
	python3 scripts/saee_support_sla_on_call_review_packet.py
	python3 scripts/saee_support_sla_on_call_review_packet_smoke.py

check-support-sla-on-call-review-packet:
	python3 scripts/saee_support_sla_on_call_review_packet.py
	python3 scripts/saee_support_sla_on_call_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_sla_on_call_review_packet.local.json
	python3 -m json.tool agent-index.json

support-contact-decision-packet-smoke:
	python3 scripts/saee_support_contact_decision_packet.py
	python3 scripts/saee_support_contact_decision_packet_smoke.py

check-support-contact-decision-packet:
	python3 scripts/saee_support_contact_decision_packet.py
	python3 scripts/saee_support_contact_decision_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_decision_packet.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.template.json
	python3 -m json.tool agent-index.json

support-contact-preflight-smoke:
	python3 scripts/saee_support_contact_preflight.py
	python3 scripts/saee_support_contact_preflight_smoke.py

check-support-contact-preflight:
	python3 scripts/saee_support_contact_preflight.py
	python3 scripts/saee_support_contact_preflight_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_preflight.local.json
	python3 -m json.tool agent-index.json

support-contact-readiness-board-smoke:
	python3 scripts/saee_support_contact_readiness_board.py
	python3 scripts/saee_support_contact_readiness_board_smoke.py

check-support-contact-readiness-board:
	python3 scripts/saee_support_contact_readiness_board.py
	python3 scripts/saee_support_contact_readiness_board_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_readiness_board.local.json
	python3 -m json.tool agent-index.json

support-contact-human-input-bridge-smoke:
	python3 scripts/saee_support_contact_human_input_bridge.py
	python3 scripts/saee_support_contact_human_input_bridge_smoke.py

check-support-contact-human-input-bridge:
	python3 scripts/saee_support_contact_human_input_bridge.py
	python3 scripts/saee_support_contact_human_input_bridge_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge.local.json
	python3 -m json.tool agent-index.json

support-contact-human-input-bridge-completion-helper-smoke:
	python3 scripts/saee_support_contact_human_input_bridge_completion_helper.py
	python3 scripts/saee_support_contact_human_input_bridge_completion_helper_smoke.py

check-support-contact-human-input-bridge-completion-helper:
	python3 scripts/saee_support_contact_human_input_bridge_completion_helper.py
	python3 scripts/saee_support_contact_human_input_bridge_completion_helper_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.template.json
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_completion_status.local.json
	python3 -m json.tool agent-index.json

support-contact-human-input-entrypoint-smoke:
	python3 scripts/saee_support_contact_human_input_entrypoint.py
	python3 scripts/saee_support_contact_human_input_entrypoint_smoke.py

check-support-contact-human-input-entrypoint:
	python3 scripts/saee_support_contact_human_input_entrypoint.py
	python3 scripts/saee_support_contact_human_input_entrypoint_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_entrypoint.local.json
	python3 -m json.tool agent-index.json

support-contact-first-priority-packet:
	python3 scripts/saee_support_contact_first_priority_packet.py

support-contact-first-priority-packet-smoke:
	python3 scripts/saee_support_contact_first_priority_packet.py
	python3 scripts/saee_support_contact_first_priority_packet_smoke.py

check-support-contact-first-priority-packet:
	python3 scripts/saee_support_contact_first_priority_packet.py
	python3 scripts/saee_support_contact_first_priority_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_first_priority_packet/support_contact_first_priority_packet.local.json
	python3 -m json.tool agent-index.json

support-contact-minimum-human-input-workspace:
	python3 scripts/saee_support_contact_minimum_human_input_workspace.py

support-contact-minimum-human-input-workspace-smoke:
	python3 scripts/saee_support_contact_minimum_human_input_workspace.py
	python3 scripts/saee_support_contact_minimum_human_input_workspace_smoke.py

check-support-contact-minimum-human-input-workspace:
	python3 scripts/saee_support_contact_minimum_human_input_workspace.py
	python3 scripts/saee_support_contact_minimum_human_input_workspace_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_minimum_human_input_workspace/support_contact_minimum_human_input_workspace.local.json
	python3 -m json.tool agent-index.json

pricing-page-minimum-human-input-workspace:
	python3 scripts/saee_pricing_page_minimum_human_input_workspace.py

pricing-page-minimum-human-input-workspace-smoke:
	python3 scripts/saee_pricing_page_minimum_human_input_workspace.py
	python3 scripts/saee_pricing_page_minimum_human_input_workspace_smoke.py

check-pricing-page-minimum-human-input-workspace:
	python3 scripts/saee_pricing_page_minimum_human_input_workspace.py
	python3 scripts/saee_pricing_page_minimum_human_input_workspace_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_minimum_human_input_workspace/pricing_page_minimum_human_input_workspace.local.json
	python3 -m json.tool agent-index.json

formal-security-review-minimum-human-input-workspace:
	python3 scripts/saee_formal_security_review_minimum_human_input_workspace.py

formal-security-review-minimum-human-input-workspace-smoke:
	python3 scripts/saee_formal_security_review_minimum_human_input_workspace.py
	python3 scripts/saee_formal_security_review_minimum_human_input_workspace_smoke.py

check-formal-security-review-minimum-human-input-workspace:
	python3 scripts/saee_formal_security_review_minimum_human_input_workspace.py
	python3 scripts/saee_formal_security_review_minimum_human_input_workspace_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_minimum_human_input_workspace/formal_security_review_minimum_human_input_workspace.local.json
	python3 -m json.tool agent-index.json

formal-security-review-state-reconciliation-smoke:
	python3 scripts/saee_formal_security_review_state_reconciliation_smoke.py

check-formal-security-review-state-reconciliation:
	python3 scripts/saee_formal_security_review_state_reconciliation.py
	python3 scripts/saee_formal_security_review_state_reconciliation_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_state_reconciliation/formal_security_review_state_reconciliation.local.json
	python3 -m json.tool agent-index.json

production-restore-policy-minimum-human-input-workspace:
	python3 scripts/saee_production_restore_policy_minimum_human_input_workspace.py

production-restore-policy-minimum-human-input-workspace-smoke:
	python3 scripts/saee_production_restore_policy_minimum_human_input_workspace.py
	python3 scripts/saee_production_restore_policy_minimum_human_input_workspace_smoke.py

check-production-restore-policy-minimum-human-input-workspace:
	python3 scripts/saee_production_restore_policy_minimum_human_input_workspace.py
	python3 scripts/saee_production_restore_policy_minimum_human_input_workspace_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_minimum_human_input_workspace/production_restore_policy_minimum_human_input_workspace.local.json
	python3 -m json.tool agent-index.json

production-restore-policy-state-reconciliation-smoke:
	python3 scripts/saee_production_restore_policy_state_reconciliation_smoke.py

check-production-restore-policy-state-reconciliation:
	python3 scripts/saee_production_restore_policy_state_reconciliation.py
	python3 scripts/saee_production_restore_policy_state_reconciliation_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_state_reconciliation/production_restore_policy_state_reconciliation.local.json
	python3 -m json.tool agent-index.json

production-monitoring-state-reconciliation-smoke:
	python3 scripts/saee_production_monitoring_state_reconciliation_smoke.py

check-production-monitoring-state-reconciliation:
	python3 scripts/saee_production_monitoring_state_reconciliation.py
	python3 scripts/saee_production_monitoring_state_reconciliation_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/production_monitoring_state_reconciliation/production_monitoring_state_reconciliation.local.json
	python3 -m json.tool agent-index.json

operations-followup-state-reconciliation-smoke:
	python3 scripts/saee_operations_followup_state_reconciliation_smoke.py

check-operations-followup-state-reconciliation:
	python3 scripts/saee_operations_followup_state_reconciliation.py
	python3 scripts/saee_operations_followup_state_reconciliation_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/operations_followup_state_reconciliation/operations_followup_state_reconciliation.local.json
	python3 -m json.tool agent-index.json

privacy-security-legal-followup-state-reconciliation-smoke:
	python3 scripts/saee_privacy_security_legal_followup_state_reconciliation_smoke.py

check-privacy-security-legal-followup-state-reconciliation:
	python3 scripts/saee_privacy_security_legal_followup_state_reconciliation.py
	python3 scripts/saee_privacy_security_legal_followup_state_reconciliation_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_followup_state_reconciliation/privacy_security_legal_followup_state_reconciliation.local.json
	python3 -m json.tool agent-index.json

billing-followup-state-reconciliation-smoke:
	python3 scripts/saee_billing_followup_state_reconciliation_smoke.py

check-billing-followup-state-reconciliation:
	python3 scripts/saee_billing_followup_state_reconciliation.py
	python3 scripts/saee_billing_followup_state_reconciliation_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/billing_followup_state_reconciliation/billing_followup_state_reconciliation.local.json
	python3 -m json.tool agent-index.json

phase1-identity-tenant-state-reconciliation-smoke:
	python3 scripts/saee_phase1_identity_tenant_state_reconciliation_smoke.py

check-phase1-identity-tenant-state-reconciliation:
	python3 scripts/saee_phase1_identity_tenant_state_reconciliation.py
	python3 scripts/saee_phase1_identity_tenant_state_reconciliation_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_state_reconciliation/phase_1_identity_tenant_state_reconciliation.local.json
	python3 -m json.tool agent-index.json

support-contact-bridge-validator-dry-run-smoke:
	python3 scripts/saee_support_contact_bridge_validator_dry_run.py
	python3 scripts/saee_support_contact_bridge_validator_dry_run_smoke.py

check-support-contact-bridge-validator-dry-run:
	python3 scripts/saee_support_contact_bridge_validator_dry_run.py
	python3 scripts/saee_support_contact_bridge_validator_dry_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_bridge_validator_dry_run.local.json
	python3 -m json.tool agent-index.json

support-contact-bridge-human-handoff-checkpoint-smoke:
	python3 scripts/saee_support_contact_bridge_human_handoff_checkpoint.py
	python3 scripts/saee_support_contact_bridge_human_handoff_checkpoint_smoke.py

check-support-contact-bridge-human-handoff-checkpoint:
	python3 scripts/saee_support_contact_bridge_human_handoff_checkpoint.py
	python3 scripts/saee_support_contact_bridge_human_handoff_checkpoint_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_bridge_human_handoff_checkpoint.local.json
	python3 -m json.tool agent-index.json

support-contact-approval-input-validator-smoke:
	python3 scripts/saee_support_contact_approval_input_validator.py
	python3 scripts/saee_support_contact_approval_input_validator_smoke.py

check-support-contact-approval-input-validator:
	python3 scripts/saee_support_contact_approval_input_validator.py
	python3 scripts/saee_support_contact_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

support-contact-approval-input-prompt-smoke:
	python3 scripts/saee_support_contact_approval_input_prompt.py
	python3 scripts/saee_support_contact_approval_input_prompt_smoke.py

check-support-contact-approval-input-prompt:
	python3 scripts/saee_support_contact_approval_input_prompt.py
	python3 scripts/saee_support_contact_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

support-contact-evidence-builder-smoke:
	python3 scripts/saee_support_contact_evidence_builder.py
	python3 scripts/saee_support_contact_evidence_builder_smoke.py

check-support-contact-evidence-builder:
	python3 scripts/saee_support_contact_decision_packet.py
	python3 scripts/saee_support_contact_evidence_builder.py
	python3 scripts/saee_support_contact_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.from_support_contact.local.json
	python3 -m json.tool agent-index.json

support-contact-evidence-builder-request-template-smoke:
	python3 scripts/saee_support_contact_evidence_builder_request_template.py
	python3 scripts/saee_support_contact_evidence_builder_request_template_smoke.py

check-support-contact-evidence-builder-request-template:
	python3 scripts/saee_support_contact_evidence_builder_request_template.py
	python3 scripts/saee_support_contact_evidence_builder_request_template_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_request.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_request.template.json
	python3 -m json.tool agent-index.json

support-contact-evidence-builder-execution-request-smoke:
	python3 scripts/saee_support_contact_evidence_builder_execution_request.py
	python3 scripts/saee_support_contact_evidence_builder_execution_request_smoke.py

check-support-contact-evidence-builder-execution-request:
	python3 scripts/saee_support_contact_evidence_builder_execution_request.py
	python3 scripts/saee_support_contact_evidence_builder_execution_request_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_execution_request.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_builder_output.human_filled.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.from_support_contact.human_filled.local.json
	python3 -m json.tool agent-index.json

support-contact-evidence-path-smoke:
	python3 scripts/saee_support_contact_evidence_path.py
	python3 scripts/saee_support_contact_evidence_path_smoke.py

check-support-contact-evidence-path:
	python3 scripts/saee_support_contact_evidence_path.py
	python3 scripts/saee_support_contact_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_evidence_path.local.json
	python3 -m json.tool agent-index.json

customer-support-approval-input-validator-smoke:
	python3 scripts/saee_customer_support_approval_input_validator.py
	python3 scripts/saee_customer_support_approval_input_validator_smoke.py

check-customer-support-approval-input-validator:
	python3 scripts/saee_customer_support_approval_input_validator.py
	python3 scripts/saee_customer_support_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/customer_support_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

customer-support-approval-input-prompt-smoke:
	python3 scripts/saee_customer_support_approval_input_prompt.py
	python3 scripts/saee_customer_support_approval_input_prompt_smoke.py

check-customer-support-approval-input-prompt:
	python3 scripts/saee_customer_support_approval_input_prompt.py
	python3 scripts/saee_customer_support_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/customer_support_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

customer-support-evidence-builder-smoke:
	python3 scripts/saee_customer_support_evidence_builder.py
	python3 scripts/saee_customer_support_evidence_builder_smoke.py

check-customer-support-evidence-builder:
	python3 scripts/saee_customer_support_evidence_builder.py
	python3 scripts/saee_customer_support_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/customer_support_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.from_customer_support.local.json
	python3 -m json.tool agent-index.json

customer-support-evidence-path-smoke:
	python3 scripts/saee_customer_support_evidence_path.py
	python3 scripts/saee_customer_support_evidence_path_smoke.py

check-customer-support-evidence-path:
	python3 scripts/saee_customer_support_evidence_path.py
	python3 scripts/saee_customer_support_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/customer_support_evidence_path.local.json
	python3 -m json.tool agent-index.json

sla-approval-input-validator-smoke:
	python3 scripts/saee_sla_approval_input_validator.py
	python3 scripts/saee_sla_approval_input_validator_smoke.py

check-sla-approval-input-validator:
	python3 scripts/saee_sla_approval_input_validator.py
	python3 scripts/saee_sla_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/sla_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

sla-approval-input-prompt:
	python3 scripts/saee_sla_approval_input_prompt.py

sla-approval-input-prompt-smoke:
	python3 scripts/saee_sla_approval_input_prompt.py
	python3 scripts/saee_sla_approval_input_prompt_smoke.py

check-sla-approval-input-prompt:
	python3 scripts/saee_sla_approval_input_prompt.py
	python3 scripts/saee_sla_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/sla_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

sla-evidence-builder-smoke:
	python3 scripts/saee_sla_evidence_builder.py
	python3 scripts/saee_sla_evidence_builder_smoke.py

check-sla-evidence-builder:
	python3 scripts/saee_sla_evidence_builder.py
	python3 scripts/saee_sla_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/sla_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.from_sla.local.json
	python3 -m json.tool agent-index.json

sla-evidence-path-smoke:
	python3 scripts/saee_sla_evidence_path.py
	python3 scripts/saee_sla_evidence_path_smoke.py

check-sla-evidence-path:
	python3 scripts/saee_sla_evidence_path.py
	python3 scripts/saee_sla_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/sla_evidence_path.local.json
	python3 -m json.tool agent-index.json

on-call-approval-input-validator-smoke:
	python3 scripts/saee_on_call_approval_input_validator.py
	python3 scripts/saee_on_call_approval_input_validator_smoke.py

check-on-call-approval-input-validator:
	python3 scripts/saee_on_call_approval_input_validator.py
	python3 scripts/saee_on_call_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/on_call_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

on-call-approval-input-prompt:
	python3 scripts/saee_on_call_approval_input_prompt.py

on-call-approval-input-prompt-smoke:
	python3 scripts/saee_on_call_approval_input_prompt.py
	python3 scripts/saee_on_call_approval_input_prompt_smoke.py

check-on-call-approval-input-prompt:
	python3 scripts/saee_on_call_approval_input_prompt.py
	python3 scripts/saee_on_call_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/on_call_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

on-call-evidence-builder-smoke:
	python3 scripts/saee_on_call_evidence_builder.py
	python3 scripts/saee_on_call_evidence_builder_smoke.py

check-on-call-evidence-builder:
	python3 scripts/saee_on_call_evidence_builder.py
	python3 scripts/saee_on_call_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/on_call_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.from_on_call.local.json
	python3 -m json.tool agent-index.json

on-call-evidence-path-smoke:
	python3 scripts/saee_on_call_evidence_path.py
	python3 scripts/saee_on_call_evidence_path_smoke.py

check-on-call-evidence-path:
	python3 scripts/saee_on_call_evidence_path.py
	python3 scripts/saee_on_call_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/on_call_evidence_path.local.json
	python3 -m json.tool agent-index.json

support-sla-evidence-profile-smoke:
	python3 scripts/saee_support_sla_evidence_profile.py
	python3 scripts/saee_support_sla_evidence_profile_smoke.py

check-support-sla-evidence-profile:
	python3 scripts/saee_support_sla_evidence_profile.py
	python3 scripts/saee_support_sla_evidence_profile_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_sla_evidence_profile.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.combined_profile.local.json
	python3 -m json.tool agent-index.json

production-data-operations-evidence-readiness-smoke:
	python3 scripts/saee_production_data_operations_evidence_readiness_smoke.py

check-production-data-operations-evidence-readiness:
	python3 scripts/saee_production_data_operations_evidence_readiness_smoke.py
	python3 scripts/saee_production_data_operations_evidence_readiness.py
	python3 -m json.tool agent-index.json

data-operations-evidence-runner-smoke:
	python3 scripts/saee_data_operations_evidence_runner.py
	python3 scripts/saee_data_operations_evidence_runner_smoke.py

check-data-operations-evidence-runner:
	python3 scripts/saee_data_operations_evidence_runner.py
	python3 scripts/saee_data_operations_evidence_runner_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/restore_test_plan.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/restore_test_report.local.json
	python3 -m json.tool agent-index.json

restore-tested-evidence-profile-smoke:
	python3 scripts/saee_restore_tested_evidence_profile.py
	python3 scripts/saee_restore_tested_evidence_profile_smoke.py

check-restore-tested-evidence-profile:
	python3 scripts/saee_restore_tested_evidence_profile.py
	python3 scripts/saee_restore_tested_evidence_profile_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/restore_tested_evidence_profile.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/production_data_operations_evidence.from_restore_tested.local.json
	python3 -m json.tool agent-index.json

restore-tested-local-evidence-promotion-request-smoke:
	python3 scripts/saee_restore_tested_local_evidence_promotion_request.py
	python3 scripts/saee_restore_tested_local_evidence_promotion_request_smoke.py

check-restore-tested-local-evidence-promotion-request:
	python3 scripts/saee_restore_tested_local_evidence_promotion_request.py
	python3 scripts/saee_restore_tested_local_evidence_promotion_request_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/local_evidence_promotion_requests/restore_tested_local_evidence_promotion_request.local.json
	python3 -m json.tool agent-index.json

production-restore-policy-evidence-builder-smoke:
	python3 scripts/saee_production_restore_policy_evidence_builder.py
	python3 scripts/saee_production_restore_policy_evidence_builder_smoke.py

check-production-restore-policy-evidence-builder:
	python3 scripts/saee_production_restore_policy_evidence_builder.py
	python3 scripts/saee_production_restore_policy_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.template.json
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/production_data_operations_evidence.from_restore_policy.local.json
	python3 -m json.tool agent-index.json

production-restore-policy-approval-input-validator-smoke:
	python3 scripts/saee_production_restore_policy_approval_input_validator.py
	python3 scripts/saee_production_restore_policy_approval_input_validator_smoke.py

check-production-restore-policy-approval-input-validator:
	python3 scripts/saee_production_restore_policy_approval_input_validator.py
	python3 scripts/saee_production_restore_policy_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

production-restore-policy-approval-input-prompt:
	python3 scripts/saee_production_restore_policy_approval_input_prompt.py

production-restore-policy-approval-input-prompt-smoke:
	python3 scripts/saee_production_restore_policy_approval_input_prompt.py
	python3 scripts/saee_production_restore_policy_approval_input_prompt_smoke.py

check-production-restore-policy-approval-input-prompt:
	python3 scripts/saee_production_restore_policy_approval_input_prompt.py
	python3 scripts/saee_production_restore_policy_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

data-operations-evidence-profile-smoke:
	python3 scripts/saee_data_operations_evidence_profile.py
	python3 scripts/saee_data_operations_evidence_profile_smoke.py

check-data-operations-evidence-profile:
	python3 scripts/saee_data_operations_evidence_profile.py
	python3 scripts/saee_data_operations_evidence_profile_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence_profile.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/production_data_operations_evidence.combined_profile.local.json
	python3 -m json.tool agent-index.json

production-restore-policy-review-packet-smoke:
	python3 scripts/saee_production_restore_policy_review_packet.py
	python3 scripts/saee_production_restore_policy_review_packet_smoke.py

check-production-restore-policy-review-packet:
	python3 scripts/saee_production_restore_policy_review_packet.py
	python3 scripts/saee_production_restore_policy_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_review_packet.local.json
	python3 -m json.tool agent-index.json

production-restore-policy-draft-smoke:
	python3 scripts/saee_production_restore_policy_draft.py
	python3 scripts/saee_production_restore_policy_draft_smoke.py

check-production-restore-policy-draft:
	python3 scripts/saee_production_restore_policy_draft.py
	python3 scripts/saee_production_restore_policy_draft_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_draft.local.json
	python3 -m json.tool agent-index.json

production-operations-evidence-readiness-smoke:
	python3 scripts/saee_production_operations_evidence_readiness_smoke.py

check-production-operations-evidence-readiness:
	python3 scripts/saee_production_operations_evidence_readiness_smoke.py
	python3 scripts/saee_production_operations_evidence_readiness.py
	python3 -m json.tool agent-index.json

operations-evidence-runner-smoke:
	python3 scripts/saee_operations_evidence_runner.py
	python3 scripts/saee_operations_evidence_runner_smoke.py

check-operations-evidence-runner:
	python3 scripts/saee_operations_evidence_runner.py
	python3 scripts/saee_operations_evidence_runner_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/operations_evidence.local.json
	python3 -m json.tool agent-index.json

operations-evidence-profile-smoke:
	python3 scripts/saee_operations_evidence_profile.py
	python3 scripts/saee_operations_evidence_profile_smoke.py

check-operations-evidence-profile:
	python3 scripts/saee_operations_evidence_profile.py
	python3 scripts/saee_operations_evidence_profile_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/operations_evidence_profile.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/production_operations_evidence.combined_profile.local.json
	python3 -m json.tool agent-index.json

production-monitoring-evidence-builder-smoke:
	python3 scripts/saee_production_monitoring_evidence_builder.py
	python3 scripts/saee_production_monitoring_evidence_builder_smoke.py

check-production-monitoring-evidence-builder:
	python3 scripts/saee_production_monitoring_evidence_builder.py
	python3 scripts/saee_production_monitoring_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/production_operations_evidence.from_production_monitoring.local.json
	python3 -m json.tool agent-index.json

production-monitoring-approval-input-validator-smoke:
	python3 scripts/saee_production_monitoring_approval_input_validator.py
	python3 scripts/saee_production_monitoring_approval_input_validator_smoke.py

check-production-monitoring-approval-input-validator:
	python3 scripts/saee_production_monitoring_approval_input_validator.py
	python3 scripts/saee_production_monitoring_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/production_monitoring_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

production-monitoring-approval-input-prompt:
	python3 scripts/saee_production_monitoring_approval_input_prompt.py

production-monitoring-approval-input-prompt-smoke:
	python3 scripts/saee_production_monitoring_approval_input_prompt.py
	python3 scripts/saee_production_monitoring_approval_input_prompt_smoke.py

check-production-monitoring-approval-input-prompt:
	python3 scripts/saee_production_monitoring_approval_input_prompt.py
	python3 scripts/saee_production_monitoring_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/production_monitoring_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

production-monitoring-evidence-path-smoke:
	python3 scripts/saee_production_monitoring_evidence_path.py
	python3 scripts/saee_production_monitoring_evidence_path_smoke.py

check-production-monitoring-evidence-path:
	python3 scripts/saee_production_monitoring_evidence_path.py
	python3 scripts/saee_production_monitoring_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_path.local.json
	python3 -m json.tool agent-index.json

external-alert-delivery-evidence-builder-smoke:
	python3 scripts/saee_external_alert_delivery_evidence_builder.py
	python3 scripts/saee_external_alert_delivery_evidence_builder_smoke.py

check-external-alert-delivery-evidence-builder:
	python3 scripts/saee_external_alert_delivery_evidence_builder.py
	python3 scripts/saee_external_alert_delivery_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/production_operations_evidence.from_external_alert_delivery.local.json
	python3 -m json.tool agent-index.json

external-alert-delivery-approval-input-validator-smoke:
	python3 scripts/saee_external_alert_delivery_approval_input_validator.py
	python3 scripts/saee_external_alert_delivery_approval_input_validator_smoke.py

check-external-alert-delivery-approval-input-validator:
	python3 scripts/saee_external_alert_delivery_approval_input_validator.py
	python3 scripts/saee_external_alert_delivery_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

external-alert-delivery-approval-input-prompt:
	python3 scripts/saee_external_alert_delivery_approval_input_prompt.py

external-alert-delivery-approval-input-prompt-smoke:
	python3 scripts/saee_external_alert_delivery_approval_input_prompt.py
	python3 scripts/saee_external_alert_delivery_approval_input_prompt_smoke.py

check-external-alert-delivery-approval-input-prompt:
	python3 scripts/saee_external_alert_delivery_approval_input_prompt.py
	python3 scripts/saee_external_alert_delivery_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

external-alert-delivery-evidence-path-smoke:
	python3 scripts/saee_external_alert_delivery_evidence_path.py
	python3 scripts/saee_external_alert_delivery_evidence_path_smoke.py

check-external-alert-delivery-evidence-path:
	python3 scripts/saee_external_alert_delivery_evidence_path.py
	python3 scripts/saee_external_alert_delivery_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/external_alert_delivery_evidence_path.local.json
	python3 -m json.tool agent-index.json

operations-on-call-rotation-approval-input-validator-smoke:
	python3 scripts/saee_operations_on_call_rotation_approval_input_validator.py
	python3 scripts/saee_operations_on_call_rotation_approval_input_validator_smoke.py

check-operations-on-call-rotation-approval-input-validator:
	python3 scripts/saee_operations_on_call_rotation_approval_input_validator.py
	python3 scripts/saee_operations_on_call_rotation_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

operations-on-call-rotation-approval-input-prompt:
	python3 scripts/saee_operations_on_call_rotation_approval_input_prompt.py

operations-on-call-rotation-approval-input-prompt-smoke:
	python3 scripts/saee_operations_on_call_rotation_approval_input_prompt.py
	python3 scripts/saee_operations_on_call_rotation_approval_input_prompt_smoke.py

check-operations-on-call-rotation-approval-input-prompt:
	python3 scripts/saee_operations_on_call_rotation_approval_input_prompt.py
	python3 scripts/saee_operations_on_call_rotation_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

operations-on-call-rotation-evidence-builder-smoke:
	python3 scripts/saee_operations_on_call_rotation_evidence_builder.py
	python3 scripts/saee_operations_on_call_rotation_evidence_builder_smoke.py

check-operations-on-call-rotation-evidence-builder:
	python3 scripts/saee_operations_on_call_rotation_evidence_builder.py
	python3 scripts/saee_operations_on_call_rotation_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/production_operations_evidence.from_operations_on_call_rotation.local.json
	python3 -m json.tool agent-index.json

operations-on-call-rotation-evidence-path-smoke:
	python3 scripts/saee_operations_on_call_rotation_evidence_path.py
	python3 scripts/saee_operations_on_call_rotation_evidence_path_smoke.py

check-operations-on-call-rotation-evidence-path:
	python3 scripts/saee_operations_on_call_rotation_evidence_path.py
	python3 scripts/saee_operations_on_call_rotation_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/operations_on_call_rotation_evidence_path.local.json
	python3 -m json.tool agent-index.json

operations-monitoring-alert-review-packet-smoke:
	python3 scripts/saee_operations_monitoring_alert_review_packet.py
	python3 scripts/saee_operations_monitoring_alert_review_packet_smoke.py

check-operations-monitoring-alert-review-packet:
	python3 scripts/saee_operations_monitoring_alert_review_packet.py
	python3 scripts/saee_operations_monitoring_alert_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/operations_monitoring_alert_review_packet.local.json
	python3 -m json.tool agent-index.json

production-privacy-security-legal-evidence-readiness-smoke:
	python3 scripts/saee_production_privacy_security_legal_evidence_readiness_smoke.py

check-production-privacy-security-legal-evidence-readiness:
	python3 scripts/saee_production_privacy_security_legal_evidence_readiness_smoke.py
	python3 scripts/saee_production_privacy_security_legal_evidence_readiness.py
	python3 -m json.tool agent-index.json

privacy-security-legal-evidence-runner-smoke:
	python3 scripts/saee_privacy_security_legal_evidence_runner.py
	python3 scripts/saee_privacy_security_legal_evidence_runner_smoke.py

check-privacy-security-legal-evidence-runner:
	python3 scripts/saee_privacy_security_legal_evidence_runner.py
	python3 scripts/saee_privacy_security_legal_evidence_runner_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence.local.json
	python3 -m json.tool agent-index.json

privacy-security-legal-evidence-path-smoke:
	python3 scripts/saee_privacy_security_legal_evidence_path_smoke.py

check-privacy-security-legal-evidence-path:
	python3 scripts/saee_privacy_security_legal_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence_path.local.json
	python3 -m json.tool agent-index.json

formal-security-review-scope-draft-smoke:
	python3 scripts/saee_formal_security_review_scope_draft.py
	python3 scripts/saee_formal_security_review_scope_draft_smoke.py

check-formal-security-review-scope-draft:
	python3 scripts/saee_formal_security_review_scope_draft.py
	python3 scripts/saee_formal_security_review_scope_draft_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_scope_draft.local.json
	python3 -m json.tool agent-index.json

formal-security-review-evidence-builder-smoke:
	python3 scripts/saee_formal_security_review_evidence_builder.py
	python3 scripts/saee_formal_security_review_evidence_builder_smoke.py

check-formal-security-review-evidence-builder:
	python3 scripts/saee_formal_security_review_evidence_builder.py
	python3 scripts/saee_formal_security_review_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/production_privacy_security_legal_evidence.from_formal_security_review.local.json
	python3 -m json.tool agent-index.json

formal-security-review-approval-input-validator-smoke:
	python3 scripts/saee_formal_security_review_approval_input_validator.py
	python3 scripts/saee_formal_security_review_approval_input_validator_smoke.py

check-formal-security-review-approval-input-validator:
	python3 scripts/saee_formal_security_review_approval_input_validator.py
	python3 scripts/saee_formal_security_review_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

formal-security-review-approval-input-prompt:
	python3 scripts/saee_formal_security_review_approval_input_prompt.py

formal-security-review-approval-input-prompt-smoke:
	python3 scripts/saee_formal_security_review_approval_input_prompt.py
	python3 scripts/saee_formal_security_review_approval_input_prompt_smoke.py

check-formal-security-review-approval-input-prompt:
	python3 scripts/saee_formal_security_review_approval_input_prompt.py
	python3 scripts/saee_formal_security_review_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

privacy-legal-dpa-evidence-builder-smoke:
	python3 scripts/saee_privacy_legal_dpa_evidence_builder.py
	python3 scripts/saee_privacy_legal_dpa_evidence_builder_smoke.py

check-privacy-legal-dpa-evidence-builder:
	python3 scripts/saee_privacy_legal_dpa_evidence_builder.py
	python3 scripts/saee_privacy_legal_dpa_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/production_privacy_security_legal_evidence.from_privacy_legal_dpa.local.json
	python3 -m json.tool agent-index.json

privacy-legal-dpa-approval-input-prompt:
	python3 scripts/saee_privacy_legal_dpa_approval_input_prompt.py

privacy-legal-dpa-approval-input-prompt-smoke:
	python3 scripts/saee_privacy_legal_dpa_approval_input_prompt.py
	python3 scripts/saee_privacy_legal_dpa_approval_input_prompt_smoke.py

check-privacy-legal-dpa-approval-input-prompt:
	python3 scripts/saee_privacy_legal_dpa_approval_input_prompt.py
	python3 scripts/saee_privacy_legal_dpa_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

privacy-legal-dpa-approval-input-validator:
	python3 scripts/saee_privacy_legal_dpa_approval_input_validator.py

privacy-legal-dpa-approval-input-validator-smoke:
	python3 scripts/saee_privacy_legal_dpa_approval_input_validator.py
	python3 scripts/saee_privacy_legal_dpa_approval_input_validator_smoke.py

check-privacy-legal-dpa-approval-input-validator:
	python3 scripts/saee_privacy_legal_dpa_approval_input_validator.py
	python3 scripts/saee_privacy_legal_dpa_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

vulnerability-management-evidence-builder-smoke:
	python3 scripts/saee_vulnerability_management_evidence_builder.py
	python3 scripts/saee_vulnerability_management_evidence_builder_smoke.py

check-vulnerability-management-evidence-builder:
	python3 scripts/saee_vulnerability_management_evidence_builder.py
	python3 scripts/saee_vulnerability_management_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/vulnerability_management_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/production_privacy_security_legal_evidence.from_vulnerability_management.local.json
	python3 -m json.tool agent-index.json

vulnerability-management-approval-input-prompt:
	python3 scripts/saee_vulnerability_management_approval_input_prompt.py

vulnerability-management-approval-input-prompt-smoke:
	python3 scripts/saee_vulnerability_management_approval_input_prompt.py
	python3 scripts/saee_vulnerability_management_approval_input_prompt_smoke.py

check-vulnerability-management-approval-input-prompt:
	python3 scripts/saee_vulnerability_management_approval_input_prompt.py
	python3 scripts/saee_vulnerability_management_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/vulnerability_management_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

vulnerability-management-approval-input-validator:
	python3 scripts/saee_vulnerability_management_approval_input_validator.py

vulnerability-management-approval-input-validator-smoke:
	python3 scripts/saee_vulnerability_management_approval_input_validator.py
	python3 scripts/saee_vulnerability_management_approval_input_validator_smoke.py

check-vulnerability-management-approval-input-validator:
	python3 scripts/saee_vulnerability_management_approval_input_validator.py
	python3 scripts/saee_vulnerability_management_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/vulnerability_management_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

privacy-legal-review-packet-smoke:
	python3 scripts/saee_privacy_legal_review_packet.py
	python3 scripts/saee_privacy_legal_review_packet_smoke.py

check-privacy-legal-review-packet:
	python3 scripts/saee_privacy_legal_review_packet.py
	python3 scripts/saee_privacy_legal_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_review_packet.local.json
	python3 -m json.tool agent-index.json

data-processing-agreement-review-packet-smoke:
	python3 scripts/saee_data_processing_agreement_review_packet.py
	python3 scripts/saee_data_processing_agreement_review_packet_smoke.py

check-data-processing-agreement-review-packet:
	python3 scripts/saee_data_processing_agreement_review_packet.py
	python3 scripts/saee_data_processing_agreement_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/data_processing_agreement_review_packet.local.json
	python3 -m json.tool agent-index.json

production-billing-revenue-evidence-readiness-smoke:
	python3 scripts/saee_production_billing_revenue_evidence_readiness_smoke.py

check-production-billing-revenue-evidence-readiness:
	python3 scripts/saee_production_billing_revenue_evidence_readiness_smoke.py
	python3 scripts/saee_production_billing_revenue_evidence_readiness.py
	python3 -m json.tool agent-index.json

billing-revenue-evidence-runner-smoke:
	python3 scripts/saee_billing_revenue_evidence_runner.py
	python3 scripts/saee_billing_revenue_evidence_runner_smoke.py

check-billing-revenue-evidence-runner:
	python3 scripts/saee_billing_revenue_evidence_runner.py
	python3 scripts/saee_billing_revenue_evidence_runner_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence.local.json
	python3 -m json.tool agent-index.json

pricing-page-review-packet-smoke:
	python3 scripts/saee_pricing_page_review_packet.py
	python3 scripts/saee_pricing_page_review_packet_smoke.py

check-pricing-page-review-packet:
	python3 scripts/saee_pricing_page_review_packet.py
	python3 scripts/saee_pricing_page_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_review_packet.local.json
	python3 -m json.tool agent-index.json

pricing-page-closure-review-packet-smoke:
	python3 scripts/saee_pricing_page_closure_review_packet_smoke.py

check-pricing-page-closure-review-packet:
	python3 scripts/saee_pricing_page_closure_review_packet.py
	python3 scripts/saee_pricing_page_closure_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet.local.json
	python3 -m json.tool agent-index.json

pricing-page-copy-draft-smoke:
	python3 scripts/saee_pricing_page_copy_draft.py
	python3 scripts/saee_pricing_page_copy_draft_smoke.py

check-pricing-page-copy-draft:
	python3 scripts/saee_pricing_page_copy_draft.py
	python3 scripts/saee_pricing_page_copy_draft_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_copy_draft.local.json
	python3 -m json.tool agent-index.json

pricing-page-evidence-builder-smoke:
	python3 scripts/saee_pricing_page_evidence_builder.py
	python3 scripts/saee_pricing_page_evidence_builder_smoke.py

check-pricing-page-evidence-builder:
	python3 scripts/saee_pricing_page_evidence_builder.py
	python3 scripts/saee_pricing_page_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_pricing_page.local.json
	python3 -m json.tool agent-index.json

pricing-page-approval-input-prompt:
	python3 scripts/saee_pricing_page_approval_input_prompt.py

pricing-page-approval-input-prompt-smoke:
	python3 scripts/saee_pricing_page_approval_input_prompt.py
	python3 scripts/saee_pricing_page_approval_input_prompt_smoke.py

check-pricing-page-approval-input-prompt:
	python3 scripts/saee_pricing_page_approval_input_prompt.py
	python3 scripts/saee_pricing_page_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

pricing-page-approval-input-validator-smoke:
	python3 scripts/saee_pricing_page_approval_input_validator.py
	python3 scripts/saee_pricing_page_approval_input_validator_smoke.py

check-pricing-page-approval-input-validator:
	python3 scripts/saee_pricing_page_approval_input_validator.py
	python3 scripts/saee_pricing_page_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

payment-provider-review-packet-smoke:
	python3 scripts/saee_payment_provider_review_packet.py
	python3 scripts/saee_payment_provider_review_packet_smoke.py

check-payment-provider-review-packet:
	python3 scripts/saee_payment_provider_review_packet.py
	python3 scripts/saee_payment_provider_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/payment_provider_review_packet.local.json
	python3 -m json.tool agent-index.json

payment-provider-evidence-builder-smoke:
	python3 scripts/saee_payment_provider_evidence_builder.py
	python3 scripts/saee_payment_provider_evidence_builder_smoke.py

check-payment-provider-evidence-builder:
	python3 scripts/saee_payment_provider_evidence_builder.py
	python3 scripts/saee_payment_provider_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/payment_provider_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_payment_provider.local.json
	python3 -m json.tool agent-index.json

payment-provider-approval-input-prompt:
	python3 scripts/saee_payment_provider_approval_input_prompt.py

payment-provider-approval-input-prompt-smoke:
	python3 scripts/saee_payment_provider_approval_input_prompt.py
	python3 scripts/saee_payment_provider_approval_input_prompt_smoke.py

check-payment-provider-approval-input-prompt:
	python3 scripts/saee_payment_provider_approval_input_prompt.py
	python3 scripts/saee_payment_provider_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/payment_provider_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

payment-provider-approval-input-validator-smoke:
	python3 scripts/saee_payment_provider_approval_input_validator.py
	python3 scripts/saee_payment_provider_approval_input_validator_smoke.py

check-payment-provider-approval-input-validator:
	python3 scripts/saee_payment_provider_approval_input_validator.py
	python3 scripts/saee_payment_provider_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/payment_provider_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

invoice-process-review-packet-smoke:
	python3 scripts/saee_invoice_process_review_packet.py
	python3 scripts/saee_invoice_process_review_packet_smoke.py

check-invoice-process-review-packet:
	python3 scripts/saee_invoice_process_review_packet.py
	python3 scripts/saee_invoice_process_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_review_packet.local.json
	python3 -m json.tool agent-index.json

invoice-process-evidence-builder-smoke:
	python3 scripts/saee_invoice_process_evidence_builder.py
	python3 scripts/saee_invoice_process_evidence_builder_smoke.py

check-invoice-process-evidence-builder:
	python3 scripts/saee_invoice_process_evidence_builder.py
	python3 scripts/saee_invoice_process_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_invoice_process.local.json
	python3 -m json.tool agent-index.json

invoice-process-approval-input-prompt:
	python3 scripts/saee_invoice_process_approval_input_prompt.py

invoice-process-approval-input-prompt-smoke:
	python3 scripts/saee_invoice_process_approval_input_prompt.py
	python3 scripts/saee_invoice_process_approval_input_prompt_smoke.py

check-invoice-process-approval-input-prompt:
	python3 scripts/saee_invoice_process_approval_input_prompt.py
	python3 scripts/saee_invoice_process_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

invoice-process-approval-input-validator-smoke:
	python3 scripts/saee_invoice_process_approval_input_validator.py
	python3 scripts/saee_invoice_process_approval_input_validator_smoke.py

check-invoice-process-approval-input-validator:
	python3 scripts/saee_invoice_process_approval_input_validator.py
	python3 scripts/saee_invoice_process_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

tax-review-packet-smoke:
	python3 scripts/saee_tax_review_packet.py
	python3 scripts/saee_tax_review_packet_smoke.py

check-tax-review-packet:
	python3 scripts/saee_tax_review_packet.py
	python3 scripts/saee_tax_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_packet.local.json
	python3 -m json.tool agent-index.json

tax-review-evidence-builder-smoke:
	python3 scripts/saee_tax_review_evidence_builder.py
	python3 scripts/saee_tax_review_evidence_builder_smoke.py

check-tax-review-evidence-builder:
	python3 scripts/saee_tax_review_evidence_builder.py
	python3 scripts/saee_tax_review_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_tax_review.local.json
	python3 -m json.tool agent-index.json

tax-review-approval-input-prompt:
	python3 scripts/saee_tax_review_approval_input_prompt.py

tax-review-approval-input-prompt-smoke:
	python3 scripts/saee_tax_review_approval_input_prompt.py
	python3 scripts/saee_tax_review_approval_input_prompt_smoke.py

check-tax-review-approval-input-prompt:
	python3 scripts/saee_tax_review_approval_input_prompt.py
	python3 scripts/saee_tax_review_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

tax-review-approval-input-validator-smoke:
	python3 scripts/saee_tax_review_approval_input_validator.py
	python3 scripts/saee_tax_review_approval_input_validator_smoke.py

check-tax-review-approval-input-validator:
	python3 scripts/saee_tax_review_approval_input_validator.py
	python3 scripts/saee_tax_review_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

refund-policy-review-packet-smoke:
	python3 scripts/saee_refund_policy_review_packet.py
	python3 scripts/saee_refund_policy_review_packet_smoke.py

check-refund-policy-review-packet:
	python3 scripts/saee_refund_policy_review_packet.py
	python3 scripts/saee_refund_policy_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_review_packet.local.json
	python3 -m json.tool agent-index.json

refund-policy-evidence-builder-smoke:
	python3 scripts/saee_refund_policy_evidence_builder.py
	python3 scripts/saee_refund_policy_evidence_builder_smoke.py

check-refund-policy-evidence-builder:
	python3 scripts/saee_refund_policy_evidence_builder.py
	python3 scripts/saee_refund_policy_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_refund_policy.local.json
	python3 -m json.tool agent-index.json

refund-policy-approval-input-prompt:
	python3 scripts/saee_refund_policy_approval_input_prompt.py

refund-policy-approval-input-prompt-smoke:
	python3 scripts/saee_refund_policy_approval_input_prompt.py
	python3 scripts/saee_refund_policy_approval_input_prompt_smoke.py

check-refund-policy-approval-input-prompt:
	python3 scripts/saee_refund_policy_approval_input_prompt.py
	python3 scripts/saee_refund_policy_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

refund-policy-approval-input-validator-smoke:
	python3 scripts/saee_refund_policy_approval_input_validator.py
	python3 scripts/saee_refund_policy_approval_input_validator_smoke.py

check-refund-policy-approval-input-validator:
	python3 scripts/saee_refund_policy_approval_input_validator.py
	python3 scripts/saee_refund_policy_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

tenant-billing-isolation-review-packet-smoke:
	python3 scripts/saee_tenant_billing_isolation_review_packet.py
	python3 scripts/saee_tenant_billing_isolation_review_packet_smoke.py

check-tenant-billing-isolation-review-packet:
	python3 scripts/saee_tenant_billing_isolation_review_packet.py
	python3 scripts/saee_tenant_billing_isolation_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_review_packet.local.json
	python3 -m json.tool agent-index.json

tenant-billing-isolation-evidence-builder-smoke:
	python3 scripts/saee_tenant_billing_isolation_evidence_builder.py
	python3 scripts/saee_tenant_billing_isolation_evidence_builder_smoke.py

check-tenant-billing-isolation-evidence-builder:
	python3 scripts/saee_tenant_billing_isolation_evidence_builder.py
	python3 scripts/saee_tenant_billing_isolation_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_tenant_billing_isolation.local.json
	python3 -m json.tool agent-index.json

tenant-billing-isolation-approval-input-prompt:
	python3 scripts/saee_tenant_billing_isolation_approval_input_prompt.py

tenant-billing-isolation-approval-input-prompt-smoke:
	python3 scripts/saee_tenant_billing_isolation_approval_input_prompt.py
	python3 scripts/saee_tenant_billing_isolation_approval_input_prompt_smoke.py

check-tenant-billing-isolation-approval-input-prompt:
	python3 scripts/saee_tenant_billing_isolation_approval_input_prompt.py
	python3 scripts/saee_tenant_billing_isolation_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

tenant-billing-isolation-approval-input-validator-smoke:
	python3 scripts/saee_tenant_billing_isolation_approval_input_validator.py
	python3 scripts/saee_tenant_billing_isolation_approval_input_validator_smoke.py

check-tenant-billing-isolation-approval-input-validator:
	python3 scripts/saee_tenant_billing_isolation_approval_input_validator.py
	python3 scripts/saee_tenant_billing_isolation_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

billing-revenue-evidence-profile-smoke:
	python3 scripts/saee_billing_revenue_evidence_profile.py
	python3 scripts/saee_billing_revenue_evidence_profile_smoke.py

check-billing-revenue-evidence-profile:
	python3 scripts/saee_billing_revenue_evidence_profile.py
	python3 scripts/saee_billing_revenue_evidence_profile_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_profile.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.combined_profile.local.json
	python3 -m json.tool agent-index.json

billing-revenue-evidence-path-smoke:
	python3 scripts/saee_billing_revenue_evidence_path.py
	python3 scripts/saee_billing_revenue_evidence_path_smoke.py

check-billing-revenue-evidence-path:
	python3 scripts/saee_billing_revenue_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_path.local.json
	python3 -m json.tool agent-index.json

billing-revenue-human-filled-evidence-run-smoke:
	python3 scripts/saee_billing_revenue_human_filled_evidence_run_smoke.py

check-billing-revenue-human-filled-evidence-run:
	python3 scripts/saee_billing_revenue_human_filled_evidence_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_human_filled_evidence_run_summary.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_profile.from_pricing_payment_invoice_tax_refund_tenant_billing_human_filled.local.json
	python3 -m json.tool agent-index.json

phase1-identity-tenant-human-filled-evidence-run-smoke:
	python3 scripts/saee_phase1_identity_tenant_human_filled_evidence_run_smoke.py

check-phase1-identity-tenant-human-filled-evidence-run:
	python3 scripts/saee_phase1_identity_tenant_human_filled_evidence_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_human_filled_evidence_run_summary.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_evidence_profile.human_filled.local.json
	python3 -m json.tool agent-index.json

internal-founder-pilot-evidence-run-smoke:
	python3 scripts/saee_internal_founder_pilot_evidence_run_smoke.py

check-internal-founder-pilot-evidence-run:
	python3 scripts/saee_internal_founder_pilot_evidence_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/internal_founder_pilot_evidence_run_summary.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence.from_internal_founder_pilot.local.json
	python3 -m json.tool agent-index.json

commercial-final-human-inspection-record-smoke:
	python3 scripts/saee_commercial_final_human_inspection_record_smoke.py

check-commercial-final-human-inspection-record:
	python3 scripts/saee_commercial_final_human_inspection_record.py
	python3 scripts/saee_commercial_final_human_inspection_record_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_final_human_inspection/commercial_final_human_inspection_record.local.json
	python3 -m json.tool agent-index.json

commercial-blocker-convergence-audit-smoke:
	python3 scripts/saee_commercial_blocker_convergence_audit_smoke.py

check-commercial-blocker-convergence-audit:
	python3 scripts/saee_commercial_blocker_convergence_audit.py
	python3 scripts/saee_commercial_blocker_convergence_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_blocker_convergence_audit/commercial_blocker_convergence_audit.local.json
	python3 -m json.tool agent-index.json

customer-validation-last-mile-packet-smoke:
	python3 scripts/saee_customer_validation_last_mile_packet_smoke.py

check-customer-validation-last-mile-packet:
	python3 scripts/saee_customer_validation_last_mile_packet.py
	python3 scripts/saee_customer_validation_last_mile_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/customer_validation_last_mile_packet.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_last_mile_packet/external_customer_validation_session_entry.blank_draft.local.json
	python3 -m json.tool agent-index.json

customer-validation-answer-intake-helper-smoke:
	python3 scripts/saee_customer_validation_answer_intake_helper_smoke.py

check-customer-validation-answer-intake-helper:
	python3 scripts/saee_customer_validation_answer_intake_helper.py
	python3 scripts/saee_customer_validation_answer_intake_helper_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_intake_helper/customer_validation_answer_intake_helper.local.json
	python3 -m json.tool agent-index.json

customer-validation-human-confirmation-boundary-record-smoke:
	python3 scripts/saee_customer_validation_human_confirmation_boundary_record_smoke.py

check-customer-validation-human-confirmation-boundary-record:
	python3 scripts/saee_customer_validation_human_confirmation_boundary_record.py
	python3 scripts/saee_customer_validation_human_confirmation_boundary_record_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_human_confirmation_boundary_record/customer_validation_human_confirmation_boundary_record.local.json
	python3 -m json.tool agent-index.json

customer-validation-answer-sheet-preflight-smoke:
	python3 scripts/saee_customer_validation_answer_sheet_preflight_smoke.py

check-customer-validation-answer-sheet-preflight:
	python3 scripts/saee_customer_validation_answer_sheet_preflight.py
	python3 scripts/saee_customer_validation_answer_sheet_preflight_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_sheet_preflight/customer_validation_answer_sheet_preflight.local.json
	python3 -m json.tool agent-index.json

customer-validation-answer-to-session-entry-converter-smoke:
	python3 scripts/saee_customer_validation_answer_to_session_entry_converter_smoke.py

check-customer-validation-answer-to-session-entry-converter:
	python3 scripts/saee_customer_validation_answer_to_session_entry_converter.py
	python3 scripts/saee_customer_validation_answer_to_session_entry_converter_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_session_entry_converter/customer_validation_answer_to_session_entry_converter.local.json
	python3 -m json.tool agent-index.json

customer-validation-answer-to-evidence-pipeline-smoke:
	python3 scripts/saee_customer_validation_answer_to_evidence_pipeline_smoke.py

check-customer-validation-answer-to-evidence-pipeline:
	python3 scripts/saee_customer_validation_answer_to_evidence_pipeline.py
	python3 scripts/saee_customer_validation_answer_to_evidence_pipeline_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_answer_to_evidence_pipeline/customer_validation_answer_to_evidence_pipeline.local.json
	python3 -m json.tool agent-index.json

customer-validation-live-fill-queue-smoke:
	python3 scripts/saee_customer_validation_live_fill_queue_smoke.py

check-customer-validation-live-fill-queue:
	python3 scripts/saee_customer_validation_live_fill_queue.py
	python3 scripts/saee_customer_validation_live_fill_queue_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_fill_queue/customer_validation_live_fill_queue.local.json
	python3 -m json.tool agent-index.json

customer-validation-live-interview-card-smoke:
	python3 scripts/saee_customer_validation_live_interview_card_smoke.py

check-customer-validation-live-interview-card:
	python3 scripts/saee_customer_validation_live_interview_card.py
	python3 scripts/saee_customer_validation_live_interview_card_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_interview_card/customer_validation_live_interview_card.local.json
	python3 -m json.tool agent-index.json

customer-validation-interview-answer-stager-smoke:
	python3 scripts/saee_customer_validation_interview_answer_stager_smoke.py

check-customer-validation-interview-answer-stager:
	python3 scripts/saee_customer_validation_interview_answer_stager.py
	python3 scripts/saee_customer_validation_interview_answer_stager_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_interview_answer_stager/customer_validation_interview_answer_stager.local.json
	python3 -m json.tool agent-index.json

customer-validation-official-answer-completion-helper-smoke:
	python3 scripts/saee_customer_validation_official_answer_completion_helper_smoke.py

check-customer-validation-official-answer-completion-helper:
	python3 scripts/saee_customer_validation_official_answer_completion_helper.py
	python3 scripts/saee_customer_validation_official_answer_completion_helper_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_official_answer_completion_helper/customer_validation_official_answer_completion_helper.local.json
	python3 -m json.tool agent-index.json

customer-validation-plain-chinese-worksheet-smoke:
	python3 scripts/saee_customer_validation_plain_chinese_worksheet_smoke.py

check-customer-validation-plain-chinese-worksheet:
	python3 scripts/saee_customer_validation_plain_chinese_worksheet.py
	python3 scripts/saee_customer_validation_plain_chinese_worksheet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_plain_chinese_worksheet/customer_validation_plain_chinese_worksheet.local.json
	python3 -m json.tool agent-index.json

customer-validation-3-minute-worksheet-smoke:
	python3 scripts/saee_customer_validation_3_minute_worksheet_smoke.py

check-customer-validation-3-minute-worksheet:
	python3 scripts/saee_customer_validation_3_minute_worksheet.py
	python3 scripts/saee_customer_validation_3_minute_worksheet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_3_minute_worksheet/customer_validation_3_minute_worksheet.local.json
	python3 -m json.tool agent-index.json

customer-validation-one-page-run-card-smoke:
	python3 scripts/saee_customer_validation_one_page_run_card_smoke.py

check-customer-validation-one-page-run-card:
	python3 scripts/saee_customer_validation_one_page_run_card.py
	python3 scripts/saee_customer_validation_one_page_run_card_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_one_page_run_card/customer_validation_one_page_run_card.local.json
	python3 -m json.tool agent-index.json

customer-validation-next-step-router-smoke:
	python3 scripts/saee_customer_validation_next_step_router_smoke.py

check-customer-validation-next-step-router:
	python3 scripts/saee_customer_validation_next_step_router.py
	python3 scripts/saee_customer_validation_next_step_router_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_next_step_router/customer_validation_next_step_router.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-next-action-smoke:
	python3 scripts/saee_external_customer_validation_next_action_smoke.py

check-external-customer-validation-next-action:
	python3 scripts/saee_external_customer_validation_next_action.py
	python3 scripts/saee_external_customer_validation_next_action_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_next_action.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-session-kit-smoke:
	python3 scripts/saee_external_customer_validation_session_kit_smoke.py

check-external-customer-validation-session-kit:
	python3 scripts/saee_external_customer_validation_session_kit.py
	python3 scripts/saee_external_customer_validation_session_kit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_kit.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-session-entry-importer-smoke:
	python3 scripts/saee_external_customer_validation_session_entry_importer_smoke.py

check-external-customer-validation-session-entry-importer:
	python3 scripts/saee_external_customer_validation_session_entry_importer.py
	python3 scripts/saee_external_customer_validation_session_entry_importer_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_import_summary.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.template.json
	python3 -m json.tool agent-index.json

external-customer-validation-session-entry-workbench-smoke:
	python3 scripts/saee_external_customer_validation_session_entry_workbench_smoke.py

check-external-customer-validation-session-entry-workbench:
	python3 scripts/saee_external_customer_validation_session_entry_workbench.py
	python3 scripts/saee_external_customer_validation_session_entry_workbench_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry_workbench.local.json
	python3 -m json.tool agent-index.json

production-tenant-storage-evidence-readiness-smoke:
	python3 scripts/saee_production_tenant_storage_evidence_readiness_smoke.py

check-production-tenant-storage-evidence-readiness:
	python3 scripts/saee_production_tenant_storage_evidence_readiness_smoke.py
	python3 scripts/saee_production_tenant_storage_evidence_readiness.py
	python3 -m json.tool agent-index.json

tenant-storage-isolation-evidence-runner-smoke:
	python3 scripts/saee_tenant_storage_isolation_evidence_runner.py
	python3 scripts/saee_tenant_storage_isolation_evidence_runner_smoke.py

check-tenant-storage-isolation-evidence-runner:
	python3 scripts/saee_tenant_storage_isolation_evidence_runner.py
	python3 scripts/saee_tenant_storage_isolation_evidence_runner_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_model_boundary.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_operations_boundary.local.json
	python3 -m json.tool agent-index.json

check-tenant-required-storage-guard:
	python3 scripts/saee_tenant_storage_key_smoke.py
	python3 scripts/saee_controlled_preview_tenant_storage_smoke.py
	python3 scripts/saee_persistence_smoke.py
	python3 scripts/saee_tenant_storage_isolation_evidence_runner.py
	python3 scripts/saee_tenant_storage_isolation_evidence_runner_smoke.py

tenant-secret-boundary-smoke:
	python3 scripts/saee_tenant_secret_boundary_smoke.py
	python3 scripts/saee_tenant_secret_boundary_profile_smoke.py

check-tenant-secret-boundary:
	python3 scripts/saee_tenant_secret_boundary_smoke.py
	python3 scripts/saee_tenant_secret_boundary_profile.py
	python3 scripts/saee_tenant_secret_boundary_profile_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/tenant_secret_boundary/tenant_secret_boundary.local.json

bound-tenant-authorization-smoke:
	python3 scripts/saee_bound_tenant_authorization_smoke.py
	python3 scripts/saee_bound_tenant_authorization_profile_smoke.py

check-bound-tenant-authorization:
	python3 scripts/saee_bound_tenant_authorization_smoke.py
	python3 scripts/saee_bound_tenant_authorization_profile.py
	python3 scripts/saee_bound_tenant_authorization_profile_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/tenant_authorization/tenant_authorization.local.json

tenant-agent-review-evidence-smoke:
	python3 scripts/saee_tenant_agent_review_evidence_smoke.py

check-tenant-agent-review-evidence:
	python3 scripts/saee_tenant_agent_review_evidence.py
	python3 scripts/saee_tenant_agent_review_evidence_smoke.py
	python3 scripts/saee_tenant_storage_isolation_evidence_runner_smoke.py
	python3 scripts/saee_phase1_identity_tenant_gap_audit_smoke.py
	python3 scripts/saee_tenant_storage_remaining_gap_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/tenant_agent_review/tenant_agent_review.local.json

tenant-privacy-agent-review-smoke:
	python3 scripts/saee_synthetic_data_only_mode_smoke.py
	python3 scripts/saee_personal_data_boundary_smoke.py
	python3 scripts/saee_tenant_privacy_data_flow_smoke.py
	python3 scripts/saee_tenant_privacy_agent_review_smoke.py

check-tenant-privacy-agent-review:
	python3 scripts/saee_tenant_privacy_data_flow_profile.py
	python3 scripts/saee_tenant_privacy_agent_review_profile.py
	python3 scripts/saee_tenant_privacy_agent_review_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/tenant_privacy_agent_review/tenant_privacy_agent_review.local.json

production-tenant-storage-evidence-path-smoke:
	python3 scripts/saee_production_tenant_storage_evidence_path_smoke.py

check-production-tenant-storage-evidence-path:
	python3 scripts/saee_production_tenant_storage_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/production_tenant_storage_evidence_path.local.json
	python3 -m json.tool agent-index.json

tenant-security-privacy-review-packet-smoke:
	python3 scripts/saee_tenant_security_privacy_review_packet.py
	python3 scripts/saee_tenant_security_privacy_review_packet_smoke.py

check-tenant-security-privacy-review-packet:
	python3 scripts/saee_tenant_security_privacy_review_packet.py
	python3 scripts/saee_tenant_security_privacy_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_security_privacy_review_packet.local.json
	python3 -m json.tool agent-index.json

tenant-storage-remaining-gap-packet-smoke:
	python3 scripts/saee_tenant_storage_remaining_gap_packet.py
	python3 scripts/saee_tenant_storage_remaining_gap_packet_smoke.py

check-tenant-storage-remaining-gap-packet:
	python3 scripts/saee_tenant_storage_remaining_gap_packet.py
	python3 scripts/saee_tenant_storage_remaining_gap_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_remaining_gap_packet.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_remaining_gap_decision_template.json
	python3 -m json.tool agent-index.json

production-customer-validation-evidence-readiness-smoke:
	python3 scripts/saee_production_customer_validation_evidence_readiness_smoke.py

check-production-customer-validation-evidence-readiness:
	python3 scripts/saee_production_customer_validation_evidence_readiness_smoke.py
	python3 scripts/saee_production_customer_validation_evidence_readiness.py
	python3 -m json.tool agent-index.json

customer-validation-evidence-runner-smoke:
	python3 scripts/saee_customer_validation_evidence_runner.py
	python3 scripts/saee_customer_validation_evidence_runner_smoke.py

check-customer-validation-evidence-runner:
	python3 scripts/saee_customer_validation_evidence_runner.py
	python3 scripts/saee_customer_validation_evidence_runner_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence.local.json
	python3 -m json.tool agent-index.json

customer-validation-evidence-builder-smoke:
	python3 scripts/saee_customer_validation_evidence_builder_smoke.py

check-customer-validation-evidence-builder:
	python3 scripts/saee_customer_validation_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.template.json
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence.from_pilot.local.json
	python3 -m json.tool agent-index.json

customer-validation-approval-input-prompt:
	python3 scripts/saee_customer_validation_approval_input_prompt.py

customer-validation-approval-input-prompt-smoke:
	python3 scripts/saee_customer_validation_approval_input_prompt.py
	python3 scripts/saee_customer_validation_approval_input_prompt_smoke.py

check-customer-validation-approval-input-prompt:
	python3 scripts/saee_customer_validation_approval_input_prompt.py
	python3 scripts/saee_customer_validation_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

customer-validation-approval-input-validator-smoke:
	python3 scripts/saee_customer_validation_approval_input_validator.py
	python3 scripts/saee_customer_validation_approval_input_validator_smoke.py

check-customer-validation-approval-input-validator:
	python3 scripts/saee_customer_validation_approval_input_validator.py
	python3 scripts/saee_customer_validation_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

customer-validation-evidence-path-smoke:
	python3 scripts/saee_customer_validation_evidence_path.py
	python3 scripts/saee_customer_validation_evidence_path_smoke.py

check-customer-validation-evidence-path:
	python3 scripts/saee_customer_validation_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_path.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_path.fixture_evidence.local.json
	python3 -m json.tool agent-index.json

production-evidence-templates-smoke:
	python3 scripts/generate_production_evidence_templates.py
	python3 scripts/saee_production_evidence_templates_smoke.py

check-production-evidence-templates:
	python3 scripts/generate_production_evidence_templates.py
	python3 scripts/saee_production_evidence_templates_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/production_evidence_templates/PRODUCTION_EVIDENCE_TEMPLATE_INDEX.json
	python3 -m json.tool agent-index.json

production-evidence-intake-audit-smoke:
	python3 scripts/saee_production_evidence_intake_audit.py
	python3 scripts/saee_production_evidence_intake_audit_smoke.py

check-production-evidence-intake-audit:
	python3 scripts/saee_production_evidence_intake_audit.py
	python3 scripts/saee_production_evidence_intake_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/production_evidence_intake/production_evidence_intake.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-profile-smoke:
	python3 scripts/saee_commercial_evidence_profile.py
	python3 scripts/saee_commercial_evidence_profile_smoke.py

check-commercial-evidence-profile:
	python3 scripts/saee_commercial_evidence_profile.py
	python3 scripts/saee_commercial_evidence_profile_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_evidence_profile/local_evidence_profile.json
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_evidence_profile/local_evidence_profile_result.json
	python3 -m json.tool agent-index.json

production-blocker-gap-matrix-smoke:
	python3 scripts/saee_production_blocker_gap_matrix.py
	python3 scripts/saee_production_blocker_gap_matrix_smoke.py

check-production-blocker-gap-matrix:
	python3 scripts/saee_production_blocker_gap_matrix.py
	python3 scripts/saee_production_blocker_gap_matrix_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json
	python3 -m json.tool agent-index.json

production-blocker-evidence-path-coverage-audit-smoke:
	python3 scripts/saee_commercial_review_packet_canonical_aliases.py
	python3 scripts/saee_production_blocker_evidence_path_coverage_audit.py
	python3 scripts/saee_production_blocker_evidence_path_coverage_audit_smoke.py

check-production-blocker-evidence-path-coverage-audit:
	python3 scripts/saee_commercial_review_packet_canonical_aliases.py
	python3 scripts/saee_production_blocker_evidence_path_coverage_audit.py
	python3 scripts/saee_production_blocker_evidence_path_coverage_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage/coverage.local.json
	python3 -m json.tool agent-index.json

commercial-review-packet-canonical-aliases-smoke:
	python3 scripts/saee_commercial_review_packet_canonical_aliases.py
	python3 scripts/saee_production_blocker_evidence_path_coverage_audit.py
	python3 scripts/saee_commercial_review_packet_canonical_aliases_smoke.py

check-commercial-review-packet-canonical-aliases:
	python3 scripts/saee_commercial_review_packet_canonical_aliases.py
	python3 scripts/saee_production_blocker_evidence_path_coverage_audit.py
	python3 scripts/saee_commercial_review_packet_canonical_aliases_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/review_packet_canonical_aliases/review_packet_canonical_aliases.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/production_blocker_evidence_path_coverage/coverage.local.json
	python3 -m json.tool agent-index.json

commercial-blocker-dependency-plan-smoke:
	python3 scripts/saee_commercial_blocker_dependency_plan.py
	python3 scripts/saee_commercial_blocker_dependency_plan_smoke.py

check-commercial-blocker-dependency-plan:
	python3 scripts/saee_commercial_blocker_dependency_plan.py
	python3 scripts/saee_commercial_blocker_dependency_plan_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json
	python3 -m json.tool agent-index.json

phase1-identity-tenant-evidence-task-smoke:
	python3 scripts/saee_phase1_identity_tenant_evidence_task.py
	python3 scripts/saee_phase1_identity_tenant_evidence_task_smoke.py

check-phase1-identity-tenant-evidence-task:
	python3 scripts/saee_phase1_identity_tenant_evidence_task.py
	python3 scripts/saee_phase1_identity_tenant_evidence_task_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_task/phase_1_identity_tenant_evidence_task.local.json
	python3 -m json.tool agent-index.json

phase2-data-operations-evidence-task-smoke:
	python3 scripts/saee_phase2_data_operations_evidence_task.py
	python3 scripts/saee_phase2_data_operations_evidence_task_smoke.py

check-phase2-data-operations-evidence-task:
	python3 scripts/saee_phase2_data_operations_evidence_task.py
	python3 scripts/saee_phase2_data_operations_evidence_task_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_2_data_operations_evidence_task/phase_2_data_operations_evidence_task.local.json
	python3 -m json.tool agent-index.json

phase2-data-operations-gap-audit-smoke:
	python3 scripts/saee_phase2_data_operations_gap_audit.py
	python3 scripts/saee_phase2_data_operations_gap_audit_smoke.py

check-phase2-data-operations-gap-audit:
	python3 scripts/saee_phase2_data_operations_gap_audit.py
	python3 scripts/saee_phase2_data_operations_gap_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_2_data_operations_gap_audit/phase_2_data_operations_gap_audit.local.json
	python3 -m json.tool agent-index.json

phase3-support-security-legal-gap-audit-smoke:
	python3 scripts/saee_phase3_support_security_legal_gap_audit.py
	python3 scripts/saee_phase3_support_security_legal_gap_audit_smoke.py

check-phase3-support-security-legal-gap-audit:
	python3 scripts/saee_phase3_support_security_legal_gap_audit.py
	python3 scripts/saee_phase3_support_security_legal_gap_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_3_support_security_legal_gap_audit/phase_3_support_security_legal_gap_audit.local.json
	python3 -m json.tool agent-index.json

phase4-commercial-packaging-billing-gap-audit-smoke:
	python3 scripts/saee_phase4_commercial_packaging_billing_gap_audit.py
	python3 scripts/saee_phase4_commercial_packaging_billing_gap_audit_smoke.py

check-phase4-commercial-packaging-billing-gap-audit:
	python3 scripts/saee_phase4_commercial_packaging_billing_gap_audit.py
	python3 scripts/saee_phase4_commercial_packaging_billing_gap_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_4_commercial_packaging_billing_gap_audit/phase_4_commercial_packaging_billing_gap_audit.local.json
	python3 -m json.tool agent-index.json

phase5-customer-validation-launch-gap-audit-smoke:
	python3 scripts/saee_phase5_customer_validation_launch_gap_audit.py
	python3 scripts/saee_phase5_customer_validation_launch_gap_audit_smoke.py

check-phase5-customer-validation-launch-gap-audit:
	python3 scripts/saee_phase5_customer_validation_launch_gap_audit.py
	python3 scripts/saee_phase5_customer_validation_launch_gap_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_5_customer_validation_launch_gap_audit/phase_5_customer_validation_launch_gap_audit.local.json
	python3 -m json.tool agent-index.json

commercial-production-evidence-collection-packet-smoke:
	python3 scripts/saee_commercial_production_evidence_collection_packet.py
	python3 scripts/saee_commercial_production_evidence_collection_packet_smoke.py

check-commercial-production-evidence-collection-packet:
	python3 scripts/saee_commercial_production_evidence_collection_packet.py
	python3 scripts/saee_commercial_production_evidence_collection_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_production_evidence_collection_packet/commercial_production_evidence_collection_packet.local.json
	python3 -m json.tool agent-index.json

phase1-identity-tenant-priority-evidence-collection-smoke:
	python3 scripts/saee_phase1_identity_tenant_priority_evidence_collection.py
	python3 scripts/saee_phase1_identity_tenant_priority_evidence_collection_smoke.py

check-phase1-identity-tenant-priority-evidence-collection:
	python3 scripts/saee_phase1_identity_tenant_priority_evidence_collection.py
	python3 scripts/saee_phase1_identity_tenant_priority_evidence_collection_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_priority_evidence_collection/phase_1_identity_tenant_priority_evidence_collection.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_priority_evidence_collection/phase_1_identity_tenant_evidence_input.priority.template.json
	python3 -m json.tool agent-index.json

phase2-data-operations-priority-evidence-collection-smoke:
	python3 scripts/saee_phase2_data_operations_priority_evidence_collection.py
	python3 scripts/saee_phase2_data_operations_priority_evidence_collection_smoke.py

check-phase2-data-operations-priority-evidence-collection:
	python3 scripts/saee_phase2_data_operations_priority_evidence_collection.py
	python3 scripts/saee_phase2_data_operations_priority_evidence_collection_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_2_data_operations_priority_evidence_collection/phase_2_data_operations_priority_evidence_collection.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/phase_2_data_operations_priority_evidence_collection/phase_2_data_operations_evidence_input.priority.template.json
	python3 -m json.tool agent-index.json

phase3-support-security-legal-priority-evidence-collection-smoke:
	python3 scripts/saee_phase3_support_security_legal_priority_evidence_collection.py
	python3 scripts/saee_phase3_support_security_legal_priority_evidence_collection_smoke.py

check-phase3-support-security-legal-priority-evidence-collection:
	python3 scripts/saee_phase3_support_security_legal_priority_evidence_collection.py
	python3 scripts/saee_phase3_support_security_legal_priority_evidence_collection_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_3_support_security_legal_priority_evidence_collection/phase_3_support_security_legal_priority_evidence_collection.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/phase_3_support_security_legal_priority_evidence_collection/phase_3_support_security_legal_evidence_input.priority.template.json
	python3 -m json.tool agent-index.json

phase4-commercial-packaging-billing-priority-evidence-collection-smoke:
	python3 scripts/saee_phase4_commercial_packaging_billing_priority_evidence_collection.py
	python3 scripts/saee_phase4_commercial_packaging_billing_priority_evidence_collection_smoke.py

check-phase4-commercial-packaging-billing-priority-evidence-collection:
	python3 scripts/saee_phase4_commercial_packaging_billing_priority_evidence_collection.py
	python3 scripts/saee_phase4_commercial_packaging_billing_priority_evidence_collection_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_4_commercial_packaging_billing_priority_evidence_collection/phase_4_commercial_packaging_billing_priority_evidence_collection.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/phase_4_commercial_packaging_billing_priority_evidence_collection/phase_4_commercial_packaging_billing_evidence_input.priority.template.json
	python3 -m json.tool agent-index.json

phase5-customer-validation-launch-priority-evidence-collection-smoke:
	python3 scripts/saee_phase5_customer_validation_launch_priority_evidence_collection.py
	python3 scripts/saee_phase5_customer_validation_launch_priority_evidence_collection_smoke.py

check-phase5-customer-validation-launch-priority-evidence-collection:
	python3 scripts/saee_phase5_customer_validation_launch_priority_evidence_collection.py
	python3 scripts/saee_phase5_customer_validation_launch_priority_evidence_collection_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_5_customer_validation_launch_priority_evidence_collection/phase_5_customer_validation_launch_priority_evidence_collection.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/phase_5_customer_validation_launch_priority_evidence_collection/phase_5_customer_validation_launch_evidence_input.priority.template.json
	python3 -m json.tool agent-index.json

commercial-readiness-dashboard-smoke:
	python3 scripts/saee_commercial_readiness_dashboard.py
	python3 scripts/saee_commercial_readiness_dashboard_smoke.py

check-commercial-readiness-dashboard:
	python3 scripts/saee_commercial_readiness_dashboard.py
	python3 scripts/saee_commercial_readiness_dashboard_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_readiness_dashboard/commercial_readiness_dashboard.local.json
	python3 -m json.tool agent-index.json

commercial-human-action-board-smoke:
	python3 scripts/saee_commercial_human_action_board.py
	python3 scripts/saee_commercial_human_action_board_smoke.py

check-commercial-human-action-board:
	python3 scripts/saee_commercial_human_action_board.py
	python3 scripts/saee_commercial_human_action_board_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_human_action_board/commercial_human_action_board.local.json
	python3 -m json.tool agent-index.json

commercial-blocker-closure-readiness-board-smoke:
	python3 scripts/saee_commercial_blocker_closure_readiness_board.py
	python3 scripts/saee_commercial_blocker_closure_readiness_board_smoke.py

check-commercial-blocker-closure-readiness-board:
	python3 scripts/saee_commercial_blocker_closure_readiness_board.py
	python3 scripts/saee_commercial_blocker_closure_readiness_board_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_blocker_closure_readiness_board/closure_readiness_board.local.json
	python3 -m json.tool agent-index.json

commercial-next-evidence-sprint-smoke:
	python3 scripts/saee_commercial_next_evidence_sprint.py
	python3 scripts/saee_commercial_next_evidence_sprint_smoke.py

check-commercial-next-evidence-sprint:
	python3 scripts/saee_commercial_next_evidence_sprint.py
	python3 scripts/saee_commercial_next_evidence_sprint_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_next_evidence_sprint.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-handoff-pack-smoke:
	python3 scripts/saee_commercial_sprint_handoff_pack.py
	python3 scripts/saee_commercial_sprint_handoff_pack_smoke.py

check-commercial-sprint-handoff-pack:
	python3 scripts/saee_commercial_sprint_handoff_pack.py
	python3 scripts/saee_commercial_sprint_handoff_pack_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_handoff_pack.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-workbook-smoke:
	python3 scripts/saee_commercial_sprint_human_input_workbook.py
	python3 scripts/saee_commercial_sprint_human_input_workbook_smoke.py

check-commercial-sprint-human-input-workbook:
	python3 scripts/saee_commercial_sprint_human_input_workbook.py
	python3 scripts/saee_commercial_sprint_human_input_workbook_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_workbook.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-workbook-validator-smoke:
	python3 scripts/saee_commercial_sprint_human_input_workbook_validator.py
	python3 scripts/saee_commercial_sprint_human_input_workbook_validator_smoke.py

check-commercial-sprint-human-input-workbook-validator:
	python3 scripts/saee_commercial_sprint_human_input_workbook_validator.py
	python3 scripts/saee_commercial_sprint_human_input_workbook_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_workbook_validation.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-transfer-map-smoke:
	python3 scripts/saee_commercial_sprint_human_input_transfer_map.py
	python3 scripts/saee_commercial_sprint_human_input_transfer_map_smoke.py

check-commercial-sprint-human-input-transfer-map:
	python3 scripts/saee_commercial_sprint_human_input_transfer_map.py
	python3 scripts/saee_commercial_sprint_human_input_transfer_map_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_transfer_map.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-transfer-resolver-dry-run-smoke:
	python3 scripts/saee_commercial_sprint_human_input_transfer_resolver_dry_run.py
	python3 scripts/saee_commercial_sprint_human_input_transfer_resolver_dry_run_smoke.py

check-commercial-sprint-human-input-transfer-resolver-dry-run:
	python3 scripts/saee_commercial_sprint_human_input_transfer_resolver_dry_run.py
	python3 scripts/saee_commercial_sprint_human_input_transfer_resolver_dry_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_transfer_resolver_dry_run.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-completion-queue-smoke:
	python3 scripts/saee_commercial_sprint_human_input_completion_queue.py
	python3 scripts/saee_commercial_sprint_human_input_completion_queue_smoke.py

check-commercial-sprint-human-input-completion-queue:
	python3 scripts/saee_commercial_sprint_human_input_completion_queue.py
	python3 scripts/saee_commercial_sprint_human_input_completion_queue_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_completion_queue.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-packet-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet_smoke.py

check-commercial-sprint-human-input-quick-fill-packet:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_packet.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-packet-validator-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet_validator.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet_validator_smoke.py

check-commercial-sprint-human-input-quick-fill-packet-validator:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet_validator.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_packet_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_packet_validation.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-workbook-import-dry-run-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_import_dry_run.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_import_dry_run_smoke.py

check-commercial-sprint-human-input-quick-fill-workbook-import-dry-run:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_import_dry_run.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_import_dry_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_workbook_import_dry_run.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-guidance-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_guidance.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_guidance_smoke.py

check-commercial-sprint-human-input-quick-fill-guidance:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_guidance.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_guidance_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_guidance.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-readiness-audit-smoke:
	python3 scripts/saee_commercial_sprint_human_input_readiness_audit.py
	python3 scripts/saee_commercial_sprint_human_input_readiness_audit_smoke.py

check-commercial-sprint-human-input-readiness-audit:
	python3 scripts/saee_commercial_sprint_human_input_readiness_audit.py
	python3 scripts/saee_commercial_sprint_human_input_readiness_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_readiness_audit.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-quality-gate-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate_smoke.py

check-commercial-sprint-human-input-quick-fill-quality-gate:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_quality_gate.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-review-batch-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_smoke.py

check-commercial-sprint-human-input-quick-fill-review-batch:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-review-batch-validator-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_validator.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_validator_smoke.py

check-commercial-sprint-human-input-quick-fill-review-batch-validator:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_validator.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_validation.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-review-batch-input-template-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_smoke.py

check-commercial-sprint-human-input-quick-fill-review-batch-input-template:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template.local.json
	python3 -m json.tool agent-index.json

commercial-review-batch-human-fill-card-smoke:
	python3 scripts/saee_commercial_review_batch_human_fill_card.py
	python3 scripts/saee_commercial_review_batch_human_fill_card_smoke.py

check-commercial-review-batch-human-fill-card:
	python3 scripts/saee_commercial_review_batch_human_fill_card.py
	python3 scripts/saee_commercial_review_batch_human_fill_card_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_human_fill_card.local.json
	python3 -m json.tool agent-index.json

commercial-review-batch-human-execution-packet-smoke:
	python3 scripts/saee_commercial_review_batch_human_execution_packet.py
	python3 scripts/saee_commercial_review_batch_human_execution_packet_smoke.py

check-commercial-review-batch-human-execution-packet:
	python3 scripts/saee_commercial_review_batch_human_execution_packet.py
	python3 scripts/saee_commercial_review_batch_human_execution_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_human_execution_packet.local.json
	python3 -m json.tool agent-index.json

commercial-review-batch-human-entry-quality-guide-smoke:
	python3 scripts/saee_commercial_review_batch_human_entry_quality_guide.py
	python3 scripts/saee_commercial_review_batch_human_entry_quality_guide_smoke.py

check-commercial-review-batch-human-entry-quality-guide:
	python3 scripts/saee_commercial_review_batch_human_entry_quality_guide.py
	python3 scripts/saee_commercial_review_batch_human_entry_quality_guide_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_human_entry_quality_guide.local.json
	python3 -m json.tool agent-index.json

commercial-review-batch-safe-prefill-audit-smoke:
	python3 scripts/saee_commercial_review_batch_safe_prefill_audit.py
	python3 scripts/saee_commercial_review_batch_safe_prefill_audit_smoke.py

check-commercial-review-batch-safe-prefill-audit:
	python3 scripts/saee_commercial_review_batch_safe_prefill_audit.py
	python3 scripts/saee_commercial_review_batch_safe_prefill_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_safe_prefill_audit.local.json
	python3 -m json.tool agent-index.json

commercial-review-batch-template-preflight-smoke:
	python3 scripts/saee_commercial_review_batch_template_preflight.py
	python3 scripts/saee_commercial_review_batch_template_preflight_smoke.py

check-commercial-review-batch-template-preflight:
	python3 scripts/saee_commercial_review_batch_template_preflight.py
	python3 scripts/saee_commercial_review_batch_template_preflight_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_template_preflight.local.json
	python3 -m json.tool agent-index.json

commercial-review-batch-post-fill-validation-runbook-smoke:
	python3 scripts/saee_commercial_review_batch_post_fill_validation_runbook.py
	python3 scripts/saee_commercial_review_batch_post_fill_validation_runbook_smoke.py

check-commercial-review-batch-post-fill-validation-runbook:
	python3 scripts/saee_commercial_review_batch_post_fill_validation_runbook.py
	python3 scripts/saee_commercial_review_batch_post_fill_validation_runbook_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_post_fill_validation_runbook.local.json
	python3 -m json.tool agent-index.json

commercial-review-batch-post-fill-readiness-preview-smoke:
	python3 scripts/saee_commercial_review_batch_post_fill_readiness_preview.py
	python3 scripts/saee_commercial_review_batch_post_fill_readiness_preview_smoke.py

check-commercial-review-batch-post-fill-readiness-preview:
	python3 scripts/saee_commercial_review_batch_post_fill_readiness_preview.py
	python3 scripts/saee_commercial_review_batch_post_fill_readiness_preview_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_post_fill_readiness_preview.local.json
	python3 -m json.tool agent-index.json

commercial-review-batch-post-fill-check-smoke:
	python3 scripts/saee_commercial_review_batch_post_fill_check.py
	python3 scripts/saee_commercial_review_batch_post_fill_check_smoke.py

check-commercial-review-batch-post-fill-check:
	python3 scripts/saee_commercial_review_batch_post_fill_check.py
	python3 scripts/saee_commercial_review_batch_post_fill_check_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_review_batch_post_fill_check.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-review-batch-input-template-importer-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_smoke.py

check-commercial-sprint-human-input-quick-fill-review-batch-input-template-importer:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_importer_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template_importer.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-review-batch-template-e2e-dry-run-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_smoke.py

check-commercial-sprint-human-input-quick-fill-review-batch-template-e2e-dry-run:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_template_e2e_dry_run.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-execution-stop-gate-smoke:
	python3 scripts/saee_commercial_sprint_human_input_execution_stop_gate.py
	python3 scripts/saee_commercial_sprint_human_input_execution_stop_gate_smoke.py

check-commercial-sprint-human-input-execution-stop-gate:
	python3 scripts/saee_commercial_sprint_human_input_execution_stop_gate.py
	python3 scripts/saee_commercial_sprint_human_input_execution_stop_gate_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_execution_stop_gate.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-human-worksheet-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_human_worksheet.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_human_worksheet_smoke.py

check-commercial-sprint-human-input-quick-fill-human-worksheet:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_human_worksheet.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_human_worksheet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_human_worksheet.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-owner-packets-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_smoke.py

check-commercial-sprint-human-input-quick-fill-owner-packets:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/quick_fill_owner_packets/commercial_sprint_human_input_quick_fill_owner_packets.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-owner-packets-validator-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_validator.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_validator_smoke.py

check-commercial-sprint-human-input-quick-fill-owner-packets-validator:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_validator.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/quick_fill_owner_packets/commercial_sprint_human_input_quick_fill_owner_packets_validation.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-owner-packets-merge-dry-run-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run_smoke.py

check-commercial-sprint-human-input-quick-fill-owner-packets-merge-dry-run:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/quick_fill_owner_packets/commercial_sprint_human_input_quick_fill_owner_packets_merge_dry_run.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-quick-fill-workbook-importer-smoke:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer_smoke.py

check-commercial-sprint-human-input-quick-fill-workbook-importer:
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer.py
	python3 scripts/saee_commercial_sprint_human_input_quick_fill_workbook_importer_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_workbook_importer.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-confirmed-recommended-values-smoke:
	python3 scripts/saee_commercial_sprint_human_confirmed_recommended_values_smoke.py

check-commercial-sprint-human-confirmed-recommended-values:
	python3 scripts/saee_commercial_sprint_human_confirmed_recommended_values_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_confirmed_recommended_values.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-confirmed-values-import-preview-smoke:
	python3 scripts/saee_commercial_sprint_human_confirmed_values_import_preview_smoke.py

check-commercial-sprint-human-confirmed-values-import-preview:
	python3 scripts/saee_commercial_sprint_human_confirmed_values_import_preview_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_confirmed_values_import_preview.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-remaining-recommended-values-draft-smoke:
	python3 scripts/saee_commercial_sprint_remaining_recommended_values_draft_smoke.py

check-commercial-sprint-remaining-recommended-values-draft:
	python3 scripts/saee_commercial_sprint_remaining_recommended_values_draft_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_remaining_recommended_values_draft.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-remaining-human-confirmed-values-smoke:
	python3 scripts/saee_commercial_sprint_remaining_human_confirmed_values_smoke.py

check-commercial-sprint-remaining-human-confirmed-values:
	python3 scripts/saee_commercial_sprint_remaining_human_confirmed_values_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_remaining_human_confirmed_recommended_values.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_all_confirmed_values_import_preview.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-all-confirmed-values-source-apply-smoke:
	python3 scripts/saee_commercial_sprint_all_confirmed_values_source_apply_smoke.py

check-commercial-sprint-all-confirmed-values-source-apply:
	python3 scripts/saee_commercial_sprint_all_confirmed_values_source_apply_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_all_confirmed_values_source_apply.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_packet.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-template-transfer-applier-smoke:
	python3 scripts/saee_commercial_sprint_human_input_template_transfer_applier.py
	python3 scripts/saee_commercial_sprint_human_input_template_transfer_applier_smoke.py

check-commercial-sprint-human-input-template-transfer-applier:
	python3 scripts/saee_commercial_sprint_human_input_template_transfer_applier.py
	python3 scripts/saee_commercial_sprint_human_input_template_transfer_applier_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_template_transfer_applier.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-post-transfer-validator-sequencer-smoke:
	python3 scripts/saee_commercial_sprint_post_transfer_validator_sequencer.py
	python3 scripts/saee_commercial_sprint_post_transfer_validator_sequencer_smoke.py

check-commercial-sprint-post-transfer-validator-sequencer:
	python3 scripts/saee_commercial_sprint_post_transfer_validator_sequencer.py
	python3 scripts/saee_commercial_sprint_post_transfer_validator_sequencer_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_post_transfer_validator_sequence.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-validator-approval-request-packet-smoke:
	python3 scripts/saee_commercial_sprint_validator_approval_request_packet.py
	python3 scripts/saee_commercial_sprint_validator_approval_request_packet_smoke.py

check-commercial-sprint-validator-approval-request-packet:
	python3 scripts/saee_commercial_sprint_validator_approval_request_packet.py
	python3 scripts/saee_commercial_sprint_validator_approval_request_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_validator_approval_request_packet.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-pipeline-synthetic-proof-smoke:
	python3 scripts/saee_commercial_sprint_human_input_pipeline_synthetic_proof.py
	python3 scripts/saee_commercial_sprint_human_input_pipeline_synthetic_proof_smoke.py

check-commercial-sprint-human-input-pipeline-synthetic-proof:
	python3 scripts/saee_commercial_sprint_human_input_pipeline_synthetic_proof.py
	python3 scripts/saee_commercial_sprint_human_input_pipeline_synthetic_proof_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_pipeline_synthetic_proof.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-human-input-safety-preflight-smoke:
	python3 scripts/saee_commercial_sprint_human_input_safety_preflight.py
	python3 scripts/saee_commercial_sprint_human_input_safety_preflight_smoke.py

check-commercial-sprint-human-input-safety-preflight:
	python3 scripts/saee_commercial_sprint_human_input_safety_preflight.py
	python3 scripts/saee_commercial_sprint_human_input_safety_preflight_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_safety_preflight.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-workbook-import-approval-request-packet-smoke:
	python3 scripts/saee_commercial_sprint_workbook_import_approval_request_packet.py
	python3 scripts/saee_commercial_sprint_workbook_import_approval_request_packet_smoke.py

check-commercial-sprint-workbook-import-approval-request-packet:
	python3 scripts/saee_commercial_sprint_workbook_import_approval_request_packet.py
	python3 scripts/saee_commercial_sprint_workbook_import_approval_request_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_workbook_import_approval_request_packet.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-workbook-import-execution-request-packet-smoke:
	python3 scripts/saee_commercial_sprint_workbook_import_execution_request_packet.py
	python3 scripts/saee_commercial_sprint_workbook_import_execution_request_packet_smoke.py

check-commercial-sprint-workbook-import-execution-request-packet:
	python3 scripts/saee_commercial_sprint_workbook_import_execution_request_packet.py
	python3 scripts/saee_commercial_sprint_workbook_import_execution_request_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_workbook_import_execution_request_packet.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-workbook-import-execution-applied-smoke:
	python3 scripts/saee_commercial_sprint_workbook_import_execution_applied.py
	python3 scripts/saee_commercial_sprint_workbook_import_execution_applied_smoke.py

check-commercial-sprint-workbook-import-execution-applied:
	python3 scripts/saee_commercial_sprint_workbook_import_execution_applied.py
	python3 scripts/saee_commercial_sprint_workbook_import_execution_applied_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_workbook_import_execution_applied.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-template-transfer-execution-request-packet-smoke:
	python3 scripts/saee_commercial_sprint_template_transfer_execution_request_packet.py
	python3 scripts/saee_commercial_sprint_template_transfer_execution_request_packet_smoke.py

check-commercial-sprint-template-transfer-execution-request-packet:
	python3 scripts/saee_commercial_sprint_template_transfer_execution_request_packet.py
	python3 scripts/saee_commercial_sprint_template_transfer_execution_request_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_template_transfer_execution_request_packet.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-active-human-input-board-smoke:
	python3 scripts/saee_commercial_sprint_active_human_input_board.py
	python3 scripts/saee_commercial_sprint_active_human_input_board_smoke.py

check-commercial-sprint-active-human-input-board:
	python3 scripts/saee_commercial_sprint_active_human_input_board.py
	python3 scripts/saee_commercial_sprint_active_human_input_board_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_active_human_input_board.local.json
	python3 -m json.tool agent-index.json

commercial-readiness-status-snapshot-smoke:
	python3 scripts/saee_commercial_readiness_status_snapshot.py
	python3 scripts/saee_commercial_readiness_status_snapshot_smoke.py

check-commercial-readiness-status-snapshot:
	python3 scripts/saee_commercial_readiness_status_snapshot.py
	python3 scripts/saee_commercial_readiness_status_snapshot_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_go_no_go.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_readiness_status.local.json
	python3 -m json.tool agent-index.json

commercial-readiness-gap-audit-smoke:
	python3 scripts/saee_commercial_readiness_gap_audit.py
	python3 scripts/saee_commercial_readiness_gap_audit_smoke.py

check-commercial-readiness-gap-audit:
	python3 scripts/saee_commercial_readiness_gap_audit.py
	python3 scripts/saee_commercial_readiness_gap_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_readiness_gap_audit/commercial_readiness_gap_audit.local.json
	python3 -m json.tool agent-index.json

commercial-blocker-priority-index:
	python3 scripts/saee_commercial_blocker_priority_index.py

commercial-blocker-priority-index-smoke:
	python3 scripts/saee_commercial_blocker_priority_index.py
	python3 scripts/saee_commercial_blocker_priority_index_smoke.py

check-commercial-blocker-priority-index:
	python3 scripts/saee_commercial_blocker_priority_index.py
	python3 scripts/saee_commercial_blocker_priority_index_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_blocker_priority_index/commercial_blocker_priority_index.local.json
	python3 -m json.tool agent-index.json

partial-evidence-promotion-queue-smoke:
	python3 scripts/saee_partial_evidence_promotion_queue.py
	python3 scripts/saee_partial_evidence_promotion_queue_smoke.py

check-partial-evidence-promotion-queue:
	python3 scripts/saee_partial_evidence_promotion_queue.py
	python3 scripts/saee_partial_evidence_promotion_queue_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/partial_evidence_promotion_queue/partial_evidence_promotion_queue.local.json
	python3 -m json.tool agent-index.json

commercial-review-ready-marker-catalog-smoke:
	python3 scripts/saee_commercial_review_ready_marker_catalog_smoke.py

check-commercial-review-ready-marker-catalog:
	python3 scripts/saee_commercial_review_ready_marker_catalog.py
	python3 scripts/saee_commercial_review_ready_marker_catalog_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_review_ready_marker_catalog/commercial_review_ready_marker_catalog.local.json
	python3 -m json.tool agent-index.json

commercial-matrix-update-scope-refresh-smoke:
	python3 scripts/saee_commercial_matrix_update_scope_refresh_smoke.py

check-commercial-matrix-update-scope-refresh:
	python3 scripts/saee_commercial_review_ready_marker_catalog.py
	python3 scripts/saee_commercial_matrix_update_scope_refresh.py
	python3 scripts/saee_commercial_matrix_update_scope_refresh_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh/commercial_matrix_update_scope_refresh.local.json
	python3 -m json.tool agent-index.json

commercial-matrix-update-scope-refresh-approval-intake-smoke:
	python3 scripts/saee_commercial_matrix_update_scope_refresh_approval_intake_smoke.py

check-commercial-matrix-update-scope-refresh-approval-intake:
	python3 scripts/saee_commercial_review_ready_marker_catalog.py
	python3 scripts/saee_commercial_matrix_update_scope_refresh.py
	python3 scripts/saee_commercial_matrix_update_scope_refresh_approval_intake.py
	python3 scripts/saee_commercial_matrix_update_scope_refresh_approval_intake_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_input.template.json
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_scope_refresh_approval/scope_refresh_approval_intake.local.json
	python3 -m json.tool agent-index.json

restore-tested-promotion-review-packet-smoke:
	python3 scripts/saee_restore_tested_promotion_review_packet.py
	python3 scripts/saee_restore_tested_promotion_review_packet_smoke.py

check-restore-tested-promotion-review-packet:
	python3 scripts/saee_restore_tested_promotion_review_packet.py
	python3 scripts/saee_restore_tested_promotion_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/local_evidence_promotion_requests/restore_tested_promotion_review_packet.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/local_evidence_promotion_requests/restore_tested_promotion_decision_template.json
	python3 -m json.tool agent-index.json

restore-tested-promotion-decision-validator-smoke:
	python3 scripts/saee_restore_tested_promotion_decision_validator.py
	python3 scripts/saee_restore_tested_promotion_decision_validator_smoke.py

check-restore-tested-promotion-decision-validator:
	python3 scripts/saee_restore_tested_promotion_decision_validator.py
	python3 scripts/saee_restore_tested_promotion_decision_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/local_evidence_promotion_requests/restore_tested_promotion_decision_validation.local.json
	python3 -m json.tool agent-index.json

commercial-readiness-begin-here:
	python3 scripts/saee_commercial_readiness_begin_here.py

commercial-readiness-begin-here-smoke:
	python3 scripts/saee_commercial_readiness_begin_here.py
	python3 scripts/saee_commercial_readiness_begin_here_smoke.py

check-commercial-readiness-begin-here:
	python3 scripts/saee_commercial_readiness_begin_here.py
	python3 scripts/saee_commercial_readiness_begin_here_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_readiness_begin_here/commercial_readiness_begin_here.local.json
	python3 -m json.tool agent-index.json

commercial-readiness-state-consistency-audit-smoke:
	python3 scripts/saee_commercial_readiness_state_consistency_audit.py
	python3 scripts/saee_commercial_readiness_state_consistency_audit_smoke.py

check-commercial-readiness-state-consistency-audit:
	python3 scripts/saee_commercial_readiness_state_consistency_audit.py
	python3 scripts/saee_commercial_readiness_state_consistency_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_readiness_state_consistency_audit/commercial_readiness_state_consistency_audit.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-sprint-owner-assignment-smoke:
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_smoke.py

check-commercial-evidence-sprint-owner-assignment:
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_packet.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-sprint-owner-assignment-input-validator-smoke:
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator_smoke.py

check-commercial-evidence-sprint-owner-assignment-input-validator:
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input.template.json
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_input_validation.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-sprint-owner-assignment-completion-helper-smoke:
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper_smoke.py

check-commercial-evidence-sprint-owner-assignment-completion-helper:
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_completion_helper_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_completion_status.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-sprint-owner-assignment-readiness-board-smoke:
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_readiness_board.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_readiness_board_smoke.py

check-commercial-evidence-sprint-owner-assignment-readiness-board:
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_readiness_board.py
	python3 scripts/saee_commercial_evidence_sprint_owner_assignment_readiness_board_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/owner_assignment_readiness_board.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-sprint-first-owner-action-packet-smoke:
	python3 scripts/saee_commercial_evidence_sprint_first_owner_action_packet.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_action_packet_smoke.py

check-commercial-evidence-sprint-first-owner-action-packet:
	python3 scripts/saee_commercial_evidence_sprint_first_owner_action_packet.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_action_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_action_packet.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-sprint-first-owner-input-validator-smoke:
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator_smoke.py

check-commercial-evidence-sprint-first-owner-input-validator:
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.template.json
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_validation.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-sprint-first-owner-input-completion-helper-smoke:
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper_smoke.py

check-commercial-evidence-sprint-first-owner-input-completion-helper:
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_completion_helper_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_completion_status.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-sprint-first-owner-input-request-packet-smoke:
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_request_packet.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_request_packet_smoke.py

check-commercial-evidence-sprint-first-owner-input-request-packet:
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_request_packet.py
	python3 scripts/saee_commercial_evidence_sprint_first_owner_input_request_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_request_packet.local.json
	python3 -m json.tool agent-index.json

commercial-next-human-input:
	python3 scripts/saee_commercial_next_human_input_prompt.py

commercial-next-human-input-prompt-smoke:
	python3 scripts/saee_commercial_next_human_input_prompt.py
	python3 scripts/saee_commercial_next_human_input_prompt_smoke.py

check-commercial-next-human-input-prompt:
	python3 scripts/saee_commercial_next_human_input_prompt.py
	python3 scripts/saee_commercial_next_human_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_human_input_prompt.local.json
	python3 -m json.tool agent-index.json

commercial-next-action-summary-smoke:
	python3 scripts/saee_commercial_next_action_summary.py
	python3 scripts/saee_commercial_next_action_summary_smoke.py

check-commercial-next-action-summary:
	python3 scripts/saee_commercial_next_action_summary.py
	python3 scripts/saee_commercial_next_action_summary_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_action_summary.local.json
	python3 -m json.tool agent-index.json

commercial-trial-operator-status:
	python3 scripts/saee_commercial_trial_operator_status.py

commercial-trial-operator-status-smoke:
	python3 scripts/saee_commercial_trial_operator_status.py
	python3 scripts/saee_commercial_trial_operator_status_smoke.py

check-commercial-trial-operator-status:
	python3 scripts/saee_commercial_trial_operator_status.py
	python3 scripts/saee_commercial_trial_operator_status_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_trial_operator_status/commercial_trial_operator_status.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-sprint-sequencer-smoke:
	python3 scripts/saee_commercial_evidence_sprint_sequencer.py
	python3 scripts/saee_commercial_evidence_sprint_sequencer_smoke.py

check-commercial-evidence-sprint-sequencer:
	python3 scripts/saee_commercial_evidence_sprint_sequencer.py
	python3 scripts/saee_commercial_evidence_sprint_sequencer_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_evidence_sprint_sequencer/commercial_evidence_sprint_sequencer.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-sprint-human-sequence-packet-smoke:
	python3 scripts/saee_commercial_evidence_sprint_human_sequence_packet.py
	python3 scripts/saee_commercial_evidence_sprint_human_sequence_packet_smoke.py

check-commercial-evidence-sprint-human-sequence-packet:
	python3 scripts/saee_commercial_evidence_sprint_human_sequence_packet.py
	python3 scripts/saee_commercial_evidence_sprint_human_sequence_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/human_sequence_packet.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-request-draft-packet-smoke:
	python3 scripts/saee_commercial_evidence_request_draft_packet.py
	python3 scripts/saee_commercial_evidence_request_draft_packet_smoke.py

check-commercial-evidence-request-draft-packet:
	python3 scripts/saee_commercial_evidence_request_draft_packet.py
	python3 scripts/saee_commercial_evidence_request_draft_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_draft_packet.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-request-approval-input-validator-smoke:
	python3 scripts/saee_commercial_evidence_request_approval_input_validator.py
	python3 scripts/saee_commercial_evidence_request_approval_input_validator_smoke.py

check-commercial-evidence-request-approval-input-validator:
	python3 scripts/saee_commercial_evidence_request_approval_input_validator.py
	python3 scripts/saee_commercial_evidence_request_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input.template.json
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-request-approval-completion-helper-smoke:
	python3 scripts/saee_commercial_evidence_request_approval_completion_helper.py
	python3 scripts/saee_commercial_evidence_request_approval_completion_helper_smoke.py

check-commercial-evidence-request-approval-completion-helper:
	python3 scripts/saee_commercial_evidence_request_approval_completion_helper.py
	python3 scripts/saee_commercial_evidence_request_approval_completion_helper_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_completion_status.local.json
	python3 -m json.tool agent-index.json

commercial-evidence-request-approval-readiness-board-smoke:
	python3 scripts/saee_commercial_evidence_request_approval_readiness_board.py
	python3 scripts/saee_commercial_evidence_request_approval_readiness_board_smoke.py

check-commercial-evidence-request-approval-readiness-board:
	python3 scripts/saee_commercial_evidence_request_approval_readiness_board.py
	python3 scripts/saee_commercial_evidence_request_approval_readiness_board_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_readiness_board.local.json
	python3 -m json.tool agent-index.json

phase1-identity-tenant-gap-audit-smoke:
	python3 scripts/saee_phase1_identity_tenant_gap_audit.py
	python3 scripts/saee_phase1_identity_tenant_gap_audit_smoke.py

check-phase1-identity-tenant-gap-audit:
	python3 scripts/saee_phase1_identity_tenant_gap_audit.py
	python3 scripts/saee_phase1_identity_tenant_gap_audit_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_gap_audit/phase_1_identity_tenant_gap_audit.local.json
	python3 -m json.tool agent-index.json

phase1-identity-tenant-evidence-builder-smoke:
	python3 scripts/saee_phase1_identity_tenant_evidence_builder.py
	python3 scripts/saee_phase1_identity_tenant_evidence_builder_smoke.py

check-phase1-identity-tenant-evidence-builder:
	python3 scripts/saee_phase1_identity_tenant_evidence_builder.py
	python3 scripts/saee_phase1_identity_tenant_evidence_builder_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_builder_output.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_input.template.json
	python3 -m json.tool agent-index.json

phase1-identity-tenant-evidence-profile-smoke:
	python3 scripts/saee_phase1_identity_tenant_evidence_profile.py
	python3 scripts/saee_phase1_identity_tenant_evidence_profile_smoke.py

check-phase1-identity-tenant-evidence-profile:
	python3 scripts/saee_phase1_identity_tenant_evidence_profile.py
	python3 scripts/saee_phase1_identity_tenant_evidence_profile_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_evidence_profile.local.json
	python3 -m json.tool agent-index.json

production-auth-requirements-smoke:
	python3 scripts/saee_production_auth_requirements_smoke.py

check-production-auth-requirements:
	python3 scripts/saee_production_auth_requirements_smoke.py
	python3 scripts/saee_production_auth_requirements.py
	python3 -m json.tool phase_b_product/commercial_readiness/PRODUCTION_AUTH_REQUIREMENTS_V0_1.json
	python3 -m json.tool agent-index.json

production-auth-evidence-readiness-smoke:
	python3 scripts/saee_production_auth_evidence_readiness_smoke.py

check-production-auth-evidence-readiness:
	python3 scripts/saee_production_auth_evidence_readiness_smoke.py
	python3 scripts/saee_production_auth_evidence_readiness.py
	python3 -m json.tool agent-index.json

auth-evidence-runner-smoke:
	python3 scripts/saee_auth_evidence_runner.py
	python3 scripts/saee_auth_evidence_runner_smoke.py

check-auth-evidence-runner:
	python3 scripts/saee_auth_evidence_runner.py
	python3 scripts/saee_auth_evidence_runner_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/auth_evidence/auth_evidence.local.json
	python3 -m json.tool agent-index.json

production-auth-evidence-path-smoke:
	python3 scripts/saee_production_auth_evidence_path.py
	python3 scripts/saee_production_auth_evidence_path_smoke.py

check-production-auth-evidence-path:
	python3 scripts/saee_production_auth_evidence_path.py
	python3 scripts/saee_production_auth_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/auth_evidence/production_auth_evidence_path.local.json
	python3 -m json.tool agent-index.json

production-identity-provider-readiness-board-smoke:
	python3 scripts/saee_production_identity_provider_readiness_board.py
	python3 scripts/saee_production_identity_provider_readiness_board_smoke.py

check-production-identity-provider-readiness-board:
	python3 scripts/saee_production_identity_provider_readiness_board.py
	python3 scripts/saee_production_identity_provider_readiness_board_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_readiness_board.local.json
	python3 -m json.tool agent-index.json

production-identity-provider-input-completion-helper-smoke:
	python3 scripts/saee_production_identity_provider_input_completion_helper.py
	python3 scripts/saee_production_identity_provider_input_completion_helper_smoke.py

check-production-identity-provider-input-completion-helper:
	python3 scripts/saee_production_identity_provider_input_completion_helper.py
	python3 scripts/saee_production_identity_provider_input_completion_helper_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_input_completion.local.json
	python3 -m json.tool agent-index.json

production-identity-provider-human-decision-runbook-smoke:
	python3 scripts/saee_production_identity_provider_human_decision_runbook.py
	python3 scripts/saee_production_identity_provider_human_decision_runbook_smoke.py

check-production-identity-provider-human-decision-runbook:
	python3 scripts/saee_production_identity_provider_human_decision_runbook.py
	python3 scripts/saee_production_identity_provider_human_decision_runbook_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_human_decision_runbook.local.json
	python3 -m json.tool agent-index.json

production-identity-provider-evidence-builder-request-template-smoke:
	python3 scripts/saee_production_identity_provider_evidence_builder_request_template.py
	python3 scripts/saee_production_identity_provider_evidence_builder_request_template_smoke.py

check-production-identity-provider-evidence-builder-request-template:
	python3 scripts/saee_production_identity_provider_evidence_builder_request_template.py
	python3 scripts/saee_production_identity_provider_evidence_builder_request_template_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_evidence_builder_request.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_evidence_builder_request.template.json
	python3 -m json.tool agent-index.json

production-identity-provider-decision-packet-smoke:
	python3 scripts/saee_production_identity_provider_decision_packet.py
	python3 scripts/saee_production_identity_provider_decision_packet_smoke.py

check-production-identity-provider-decision-packet:
	python3 scripts/saee_production_identity_provider_decision_packet.py
	python3 scripts/saee_production_identity_provider_decision_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_packet.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_input.template.json
	python3 -m json.tool agent-index.json

production-identity-provider-approval-input-validator-smoke:
	python3 scripts/saee_production_identity_provider_approval_input_validator.py
	python3 scripts/saee_production_identity_provider_approval_input_validator_smoke.py

check-production-identity-provider-approval-input-validator:
	python3 scripts/saee_production_identity_provider_approval_input_validator.py
	python3 scripts/saee_production_identity_provider_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

oauth-oidc-approval-input-validator-smoke:
	python3 scripts/saee_oauth_oidc_approval_input_validator.py
	python3 scripts/saee_oauth_oidc_approval_input_validator_smoke.py

check-oauth-oidc-approval-input-validator:
	python3 scripts/saee_oauth_oidc_approval_input_validator.py
	python3 scripts/saee_oauth_oidc_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/oauth_oidc_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

oauth-oidc-approval-input-prompt:
	python3 scripts/saee_oauth_oidc_approval_input_validator.py
	python3 scripts/saee_oauth_oidc_approval_input_prompt.py

oauth-oidc-approval-input-prompt-smoke:
	python3 scripts/saee_oauth_oidc_approval_input_prompt_smoke.py

check-oauth-oidc-approval-input-prompt:
	python3 scripts/saee_oauth_oidc_approval_input_validator.py
	python3 scripts/saee_oauth_oidc_approval_input_prompt.py
	python3 scripts/saee_oauth_oidc_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/oauth_oidc_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

rbac-approval-input-validator-smoke:
	python3 scripts/saee_rbac_approval_input_validator.py
	python3 scripts/saee_rbac_approval_input_validator_smoke.py

check-rbac-approval-input-validator:
	python3 scripts/saee_rbac_approval_input_validator.py
	python3 scripts/saee_rbac_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/rbac_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

rbac-approval-input-prompt:
	python3 scripts/saee_rbac_approval_input_prompt.py

rbac-approval-input-prompt-smoke:
	python3 scripts/saee_rbac_approval_input_prompt.py
	python3 scripts/saee_rbac_approval_input_prompt_smoke.py

check-rbac-approval-input-prompt:
	python3 scripts/saee_rbac_approval_input_prompt.py
	python3 scripts/saee_rbac_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/rbac_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

tenant-storage-approval-input-validator-smoke:
	python3 scripts/saee_tenant_storage_approval_input_validator.py
	python3 scripts/saee_tenant_storage_approval_input_validator_smoke.py

check-tenant-storage-approval-input-validator:
	python3 scripts/saee_tenant_storage_approval_input_validator.py
	python3 scripts/saee_tenant_storage_approval_input_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/tenant_storage_approval_input_validation.local.json
	python3 -m json.tool agent-index.json

tenant-storage-approval-input-prompt:
	python3 scripts/saee_tenant_storage_approval_input_prompt.py

tenant-storage-approval-input-prompt-smoke:
	python3 scripts/saee_tenant_storage_approval_input_prompt.py
	python3 scripts/saee_tenant_storage_approval_input_prompt_smoke.py

check-tenant-storage-approval-input-prompt:
	python3 scripts/saee_tenant_storage_approval_input_prompt.py
	python3 scripts/saee_tenant_storage_approval_input_prompt_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/tenant_storage_approval_input_prompt.local.json
	python3 -m json.tool agent-index.json

auth-oidc-rbac-fixture-dry-run-smoke:
	python3 scripts/saee_auth_oidc_rbac_fixture_dry_run.py
	python3 scripts/saee_auth_oidc_rbac_fixture_dry_run_smoke.py

check-auth-oidc-rbac-fixture-dry-run:
	python3 scripts/saee_auth_oidc_rbac_fixture_dry_run.py
	python3 scripts/saee_auth_oidc_rbac_fixture_dry_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/auth_oidc_rbac_fixture_dry_run/auth_oidc_rbac_fixture_dry_run.local.json
	python3 -m json.tool agent-index.json

production-operations-requirements-smoke:
	python3 scripts/saee_production_operations_requirements_smoke.py

check-production-operations-requirements:
	python3 scripts/saee_production_operations_requirements_smoke.py
	python3 scripts/saee_production_operations_requirements.py
	python3 -m json.tool phase_b_product/commercial_readiness/PRODUCTION_OPERATIONS_REQUIREMENTS_V0_1.json
	python3 -m json.tool agent-index.json

production-support-sla-requirements-smoke:
	python3 scripts/saee_production_support_sla_requirements_smoke.py

check-production-support-sla-requirements:
	python3 scripts/saee_production_support_sla_requirements_smoke.py
	python3 scripts/saee_production_support_sla_requirements.py
	python3 -m json.tool phase_b_product/commercial_readiness/PRODUCTION_SUPPORT_SLA_REQUIREMENTS_V0_1.json
	python3 -m json.tool agent-index.json

production-privacy-security-legal-requirements-smoke:
	python3 scripts/saee_production_privacy_security_legal_requirements_smoke.py

check-production-privacy-security-legal-requirements:
	python3 scripts/saee_production_privacy_security_legal_requirements_smoke.py
	python3 scripts/saee_production_privacy_security_legal_requirements.py
	python3 -m json.tool phase_b_product/commercial_readiness/PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_V0_1.json
	python3 -m json.tool agent-index.json

production-billing-revenue-requirements-smoke:
	python3 scripts/saee_production_billing_revenue_requirements_smoke.py

check-production-billing-revenue-requirements:
	python3 scripts/saee_production_billing_revenue_requirements_smoke.py
	python3 scripts/saee_production_billing_revenue_requirements.py
	python3 -m json.tool phase_b_product/commercial_readiness/PRODUCTION_BILLING_REVENUE_REQUIREMENTS_V0_1.json
	python3 -m json.tool agent-index.json

production-customer-validation-requirements-smoke:
	python3 scripts/saee_production_customer_validation_requirements_smoke.py

check-production-customer-validation-requirements:
	python3 scripts/saee_production_customer_validation_requirements_smoke.py
	python3 scripts/saee_production_customer_validation_requirements.py
	python3 -m json.tool phase_b_product/commercial_readiness/PRODUCTION_CUSTOMER_VALIDATION_REQUIREMENTS_V0_1.json
	python3 -m json.tool agent-index.json

production-data-operations-requirements-smoke:
	python3 scripts/saee_production_data_operations_requirements_smoke.py

check-production-data-operations-requirements:
	python3 scripts/saee_production_data_operations_requirements_smoke.py
	python3 scripts/saee_production_data_operations_requirements.py
	python3 -m json.tool phase_b_product/commercial_readiness/PRODUCTION_DATA_OPERATIONS_REQUIREMENTS_V0_1.json
	python3 -m json.tool agent-index.json

production-tenant-storage-isolation-requirements-smoke:
	python3 scripts/saee_production_tenant_storage_isolation_requirements_smoke.py

check-production-tenant-storage-isolation-requirements:
	python3 scripts/saee_production_tenant_storage_isolation_requirements_smoke.py
	python3 scripts/saee_production_tenant_storage_isolation_requirements.py
	python3 -m json.tool phase_b_product/commercial_readiness/PRODUCTION_TENANT_STORAGE_ISOLATION_REQUIREMENTS_V0_1.json
	python3 -m json.tool agent-index.json

operations-readiness-smoke:
	python3 scripts/saee_operations_readiness_smoke.py

check-operations-readiness:
	python3 scripts/saee_operations_readiness_smoke.py
	python3 scripts/saee_operations_readiness.py
	python3 -m json.tool agent-index.json

operations-alert-policy-smoke:
	python3 scripts/saee_operations_alert_policy_smoke.py

check-operations-alert-policy:
	python3 scripts/saee_operations_alert_policy_smoke.py
	python3 scripts/saee_operations_alert_policy.py
	python3 -m json.tool agent-index.json

support-readiness-smoke:
	python3 scripts/saee_support_readiness_smoke.py

check-support-readiness:
	python3 scripts/saee_support_readiness_smoke.py
	python3 scripts/saee_support_readiness.py
	python3 -m json.tool agent-index.json

preview-readiness-api-smoke:
	python3 scripts/saee_preview_readiness_api_smoke.py

check-preview-readiness-api:
	python3 scripts/saee_preview_readiness_api_smoke.py
	python3 -m py_compile saee_backend/api/readiness.py saee_backend/main.py
	python3 -m json.tool agent-index.json

data-operations-readiness-api-smoke:
	python3 scripts/saee_data_operations_readiness_api_smoke.py

check-data-operations-readiness-api:
	python3 scripts/saee_data_operations_readiness_api_smoke.py
	python3 -m py_compile saee_backend/api/readiness.py saee_backend/main.py saee_backend/services/production_data_operations_evidence.py
	python3 -m json.tool agent-index.json

billing-pricing-readiness-api-smoke:
	python3 scripts/saee_billing_pricing_readiness_api_smoke.py

check-billing-pricing-readiness-api:
	python3 scripts/saee_billing_pricing_readiness_api_smoke.py
	python3 -m py_compile saee_backend/api/readiness.py saee_backend/main.py saee_backend/services/billing_pricing_readiness.py
	python3 -m json.tool agent-index.json

operations-readiness-api-smoke:
	python3 scripts/saee_operations_readiness_api_smoke.py

check-operations-readiness-api:
	python3 scripts/saee_operations_readiness_api_smoke.py
	python3 -m py_compile saee_backend/api/readiness.py saee_backend/main.py saee_backend/services/operations_readiness.py
	python3 -m json.tool agent-index.json

privacy-security-readiness-api-smoke:
	python3 scripts/saee_privacy_security_readiness_api_smoke.py

check-privacy-security-readiness-api:
	python3 scripts/saee_privacy_security_readiness_api_smoke.py
	python3 -m py_compile saee_backend/api/readiness.py saee_backend/main.py saee_backend/services/privacy_security_readiness.py
	python3 -m json.tool agent-index.json

legal-readiness-api-smoke:
	python3 scripts/saee_legal_readiness_api_smoke.py

check-legal-readiness-api:
	python3 scripts/saee_legal_readiness_api_smoke.py
	python3 -m py_compile saee_backend/api/readiness.py saee_backend/main.py saee_backend/services/legal_readiness.py
	python3 -m json.tool agent-index.json

privacy-security-readiness-smoke:
	python3 scripts/saee_privacy_security_readiness_smoke.py

check-privacy-security-readiness:
	python3 scripts/saee_privacy_security_readiness_smoke.py
	python3 scripts/saee_privacy_security_readiness.py
	python3 -m json.tool agent-index.json

legal-readiness-smoke:
	python3 scripts/saee_legal_readiness_smoke.py

check-legal-readiness:
	python3 scripts/saee_legal_readiness_smoke.py
	python3 scripts/saee_legal_readiness.py
	python3 -m json.tool agent-index.json

vulnerability-management-readiness-smoke:
	python3 scripts/saee_vulnerability_management_readiness_smoke.py

check-vulnerability-management-readiness:
	python3 scripts/saee_vulnerability_management_readiness_smoke.py
	python3 scripts/saee_vulnerability_management_readiness.py
	python3 -m json.tool agent-index.json

pilot-validation-readiness-smoke:
	python3 scripts/saee_pilot_validation_readiness_smoke.py

check-pilot-validation-readiness:
	python3 scripts/saee_pilot_validation_readiness_smoke.py
	python3 scripts/saee_pilot_validation_readiness.py
	python3 -m json.tool phase_b_product/validation/PILOT_RESULT_TEMPLATE.json
	python3 -m json.tool agent-index.json

billing-pricing-readiness-smoke:
	python3 scripts/saee_billing_pricing_readiness_smoke.py

check-billing-pricing-readiness:
	python3 scripts/saee_billing_pricing_readiness_smoke.py
	python3 scripts/saee_billing_pricing_readiness.py
	python3 -m json.tool agent-index.json

controlled-trial-quickstart-smoke:
	python3 scripts/saee_controlled_trial_quickstart_smoke.py

check-controlled-trial-quickstart:
	python3 scripts/saee_controlled_trial_quickstart_smoke.py
	python3 -m json.tool agent-index.json

local-mvp-tryout-guide-smoke:
	python3 scripts/saee_local_mvp_tryout_guide_smoke.py

check-local-mvp-tryout-guide:
	python3 scripts/saee_local_mvp_tryout_guide_smoke.py
	python3 -m json.tool phase_b_product/validation/local_mvp_tryout_status.json
	python3 -m json.tool agent-index.json

local-trial-handoff-packet-smoke:
	python3 scripts/saee_local_trial_handoff_packet.py
	python3 scripts/saee_local_trial_handoff_packet_smoke.py

check-local-trial-handoff-packet:
	python3 scripts/saee_local_trial_handoff_packet.py
	python3 scripts/saee_local_trial_handoff_packet_smoke.py
	python3 -m json.tool phase_b_product/validation/local_trial_handoff_packet.local.json
	python3 -m json.tool agent-index.json

local-trial-session-manager-smoke:
	python3 scripts/saee_local_trial_session_smoke.py

check-local-trial-session-manager:
	python3 scripts/saee_local_trial_session_smoke.py
	python3 scripts/saee_local_trial_session.py --json describe | python3 -m json.tool
	python3 scripts/saee_local_trial_session.py --json preflight | python3 -m json.tool
	python3 -m json.tool agent-index.json

local-trial-make-targets-smoke:
	python3 scripts/saee_local_trial_make_targets_smoke.py

check-local-trial-make-targets:
	python3 scripts/saee_local_trial_make_targets_smoke.py
	python3 -m json.tool agent-index.json

local-trial-preflight:
	python3 scripts/saee_local_trial_session.py --json preflight

try-local: local-trial-start

local-trial-start:
	python3 scripts/saee_local_trial_session.py start --wait-seconds 20
	python3 scripts/saee_local_trial_session.py status
	python3 scripts/saee_commercial_trial_operator_status.py

local-trial-status:
	python3 scripts/saee_local_trial_session.py status
	python3 scripts/saee_commercial_trial_operator_status.py

local-trial-stop:
	python3 scripts/saee_local_trial_session.py stop
	python3 scripts/saee_commercial_trial_operator_status.py

local-trial-preflight-snapshot-smoke:
	python3 scripts/saee_local_trial_preflight_snapshot_smoke.py

check-local-trial-preflight-snapshot:
	python3 scripts/saee_local_trial_preflight_snapshot.py
	python3 scripts/saee_local_trial_preflight_snapshot_smoke.py
	python3 -m json.tool phase_b_product/validation/local_trial_preflight_snapshot.local.json
	python3 -m json.tool agent-index.json

local-trial-cold-start-preflight-smoke:
	python3 scripts/saee_local_trial_cold_start_preflight.py
	python3 scripts/saee_local_trial_cold_start_preflight_smoke.py

check-local-trial-cold-start-preflight:
	python3 scripts/saee_local_trial_cold_start_preflight.py
	python3 scripts/saee_local_trial_cold_start_preflight_smoke.py
	python3 -m json.tool phase_b_product/validation/local_trial_cold_start_preflight.local.json
	python3 -m json.tool agent-index.json

local-trial-http-e2e-smoke:
	python3 scripts/saee_local_trial_http_e2e_smoke.py

check-local-trial-http-e2e:
	python3 scripts/saee_local_trial_http_e2e.py
	python3 scripts/saee_local_trial_http_e2e_smoke.py
	python3 -m json.tool phase_b_product/validation/local_trial_http_e2e/local_trial_http_e2e.local.json
	python3 -m json.tool agent-index.json

local-trial-lifecycle-proof-smoke:
	python3 scripts/saee_local_trial_lifecycle_proof_smoke.py

check-local-trial-lifecycle-proof:
	python3 scripts/saee_local_trial_lifecycle_proof.py
	python3 scripts/saee_local_trial_lifecycle_proof_smoke.py
	python3 -m json.tool phase_b_product/validation/local_trial_lifecycle_proof/local_trial_lifecycle_proof.local.json
	python3 -m json.tool agent-index.json

baidu-cloud-handoff-preflight-smoke:
	python3 scripts/saee_baidu_cloud_handoff_preflight_smoke.py

check-baidu-cloud-handoff-preflight:
	python3 scripts/saee_baidu_cloud_handoff_preflight.py
	python3 scripts/saee_baidu_cloud_handoff_preflight_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/cloud_handoff/baidu_cloud_handoff_preflight.local.json
	python3 -m json.tool agent-index.json

baidu-cloud-handoff-package-smoke:
	python3 scripts/saee_baidu_cloud_handoff_package_smoke.py

check-baidu-cloud-handoff-package:
	python3 scripts/saee_baidu_cloud_handoff_preflight.py
	python3 scripts/saee_baidu_cloud_handoff_package.py
	python3 scripts/saee_baidu_cloud_handoff_package_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/cloud_handoff/package_001/baidu_cloud_handoff_package.local.json
	python3 -m json.tool agent-index.json

local-tryout-readiness-card-smoke:
	python3 scripts/saee_local_tryout_readiness_card.py
	python3 scripts/saee_local_tryout_readiness_card_smoke.py

check-local-tryout-readiness-card:
	python3 scripts/saee_local_tryout_readiness_card.py
	python3 scripts/saee_local_tryout_readiness_card_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/local_tryout_readiness_card/local_tryout_readiness_card.local.json
	python3 -m json.tool agent-index.json

controlled-trial-local-e2e-smoke:
	python3 scripts/saee_controlled_trial_local_e2e_smoke.py

check-controlled-trial-local-e2e:
	python3 scripts/saee_controlled_trial_local_e2e_smoke.py
	python3 -m json.tool agent-index.json

controlled-trial-operator-packet-smoke:
	python3 scripts/saee_controlled_trial_operator_packet_smoke.py

check-controlled-trial-operator-packet:
	python3 scripts/saee_controlled_trial_operator_packet_smoke.py
	python3 -m json.tool phase_b_product/validation/controlled_trial_operator_packet/local_trial_session_template.json
	python3 -m json.tool agent-index.json

controlled-trial-observation-runner-smoke:
	python3 scripts/saee_controlled_trial_observation_runner_smoke.py

check-controlled-trial-observation-runner:
	python3 scripts/saee_controlled_trial_observation_runner.py
	python3 scripts/saee_controlled_trial_observation_runner_smoke.py
	python3 -m json.tool phase_b_product/validation/controlled_trial_observations/local_trial_observation_input.json
	python3 -m json.tool phase_b_product/validation/controlled_trial_observations/local_trial_observation_result.json
	python3 -m json.tool agent-index.json

controlled-preview-env-template-smoke:
	python3 scripts/saee_controlled_preview_env_template_smoke.py

check-controlled-preview-env-template:
	python3 scripts/saee_controlled_preview_env_template_smoke.py
	python3 -m json.tool agent-index.json

incident-response-runbook-smoke:
	python3 scripts/saee_incident_response_runbook_smoke.py

check-incident-response-runbook:
	python3 scripts/saee_incident_response_runbook_smoke.py
	python3 -m json.tool agent-index.json

operations-telemetry-smoke:
	python3 scripts/saee_operations_telemetry_smoke.py

check-operations-telemetry:
	python3 scripts/saee_operations_telemetry_smoke.py
	python3 scripts/saee_operations_telemetry.py
	python3 -m json.tool agent-index.json

operations-telemetry-api-smoke:
	python3 scripts/saee_operations_telemetry_api_smoke.py

check-operations-telemetry-api:
	python3 scripts/saee_operations_telemetry_api_smoke.py
	python3 -m py_compile saee_backend/api/operations.py saee_backend/main.py
	python3 -m json.tool agent-index.json

tenant-boundary-smoke:
	python3 scripts/saee_tenant_boundary_smoke.py

check-tenant-boundary:
	python3 scripts/saee_tenant_boundary_smoke.py
	python3 -m json.tool agent-index.json

request-limits-smoke:
	python3 scripts/saee_request_limits_smoke.py

check-request-limits:
	python3 scripts/saee_request_limits_smoke.py
	python3 -m json.tool agent-index.json

persistence-smoke:
	python3 scripts/saee_persistence_smoke.py

check-persistence:
	python3 scripts/saee_persistence_smoke.py
	python3 -m json.tool agent-index.json

request-audit-smoke:
	python3 scripts/saee_request_audit_smoke.py

check-request-audit:
	python3 scripts/saee_request_audit_smoke.py
	python3 -m json.tool agent-index.json

commercial-preflight-smoke:
	python3 scripts/saee_commercial_preflight_smoke.py

check-commercial-preflight:
	python3 scripts/saee_commercial_preflight_smoke.py
	python3 scripts/saee_commercial_preflight.py
	python3 -m json.tool agent-index.json

commercial-go-no-go-smoke:
	python3 scripts/saee_commercial_go_no_go_smoke.py

check-commercial-go-no-go:
	python3 scripts/saee_commercial_go_no_go_smoke.py
	python3 scripts/saee_commercial_go_no_go.py
	python3 -m json.tool agent-index.json

commercial-status-api-smoke:
	python3 scripts/saee_commercial_status_api_smoke.py

check-commercial-status-api:
	python3 scripts/saee_commercial_status_api_smoke.py
	python3 -m json.tool agent-index.json

commercial-launch-evidence-path-smoke:
	python3 scripts/saee_commercial_launch_evidence_path_smoke.py

check-commercial-launch-evidence-path:
	python3 scripts/saee_commercial_launch_evidence_path.py
	python3 scripts/saee_commercial_launch_evidence_path_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_launch_evidence_path/commercial_launch_evidence_path.local.json
	python3 -m json.tool agent-index.json

commercial-launch-blocker-work-order-smoke:
	python3 scripts/saee_commercial_launch_blocker_work_order_smoke.py

check-commercial-launch-blocker-work-order:
	python3 scripts/saee_commercial_launch_blocker_work_order_smoke.py
	python3 scripts/saee_commercial_launch_blocker_work_order.py
	python3 -m json.tool phase_b_product/commercial_readiness/COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_V0_1.json
	python3 -m json.tool agent-index.json

controlled-preview-tenant-storage-smoke:
	python3 scripts/saee_controlled_preview_tenant_storage_smoke.py
	python3 scripts/saee_tenant_storage_key_smoke.py

check-controlled-preview-tenant-storage:
	python3 scripts/saee_controlled_preview_tenant_storage_smoke.py
	python3 scripts/saee_tenant_storage_key_smoke.py
	python3 -m json.tool agent-index.json

data-retention-smoke:
	python3 scripts/saee_data_retention_smoke.py

data-backup-smoke:
	python3 scripts/saee_data_backup_smoke.py

check-data-backup:
	python3 scripts/saee_data_backup_smoke.py
	python3 -m json.tool agent-index.json

data-restore-drill-smoke:
	python3 scripts/saee_data_restore_drill_smoke.py

check-data-restore-drill:
	python3 scripts/saee_data_restore_drill_smoke.py
	python3 -m json.tool agent-index.json

check-data-retention:
	python3 scripts/saee_data_retention_smoke.py
	python3 scripts/saee_data_retention.py
	python3 -m json.tool agent-index.json

.PHONY: check-operations-human-filled-evidence-run operations-human-filled-evidence-run-smoke

operations-human-filled-evidence-run-smoke:
	python3 scripts/saee_operations_human_filled_evidence_run_smoke.py

check-operations-human-filled-evidence-run:
	python3 scripts/saee_operations_human_filled_evidence_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/operations_human_filled_evidence_run_summary.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/operations_evidence/operations_evidence_profile.from_monitoring_alert_on_call_human_filled.local.json
	python3 -m json.tool agent-index.json

.PHONY: check-privacy-security-legal-human-filled-evidence-run privacy-security-legal-human-filled-evidence-run-smoke

privacy-security-legal-human-filled-evidence-run-smoke:
	python3 scripts/saee_privacy_security_legal_human_filled_evidence_run_smoke.py

check-privacy-security-legal-human-filled-evidence-run:
	python3 scripts/saee_privacy_security_legal_human_filled_evidence_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_human_filled_evidence_run_summary.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence_profile.from_formal_privacy_dpa_vulnerability_human_filled.local.json
	python3 -m json.tool agent-index.json

online-experience-smoke:
	python3 scripts/saee_online_experience_smoke.py

check-online-experience:
	python3 scripts/saee_online_experience_smoke.py
	python3 -m json.tool agent-index.json

online-experience-human-review-smoke:
	python3 scripts/saee_online_experience_human_review_smoke.py

check-online-experience-human-review:
	python3 scripts/saee_online_experience_human_review_smoke.py
	python3 -m json.tool phase_b_product/landing/online_experience_human_review.local.json
	python3 -m json.tool agent-index.json

commercial-readiness-state-reconciliation-smoke:
	python3 scripts/saee_commercial_readiness_state_reconciliation_smoke.py

check-commercial-readiness-state-reconciliation:
	python3 scripts/saee_commercial_readiness_state_reconciliation.py
	python3 scripts/saee_commercial_readiness_state_reconciliation_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_readiness_state_reconciliation/commercial_readiness_state_reconciliation.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-run-001-smoke:
	python3 scripts/saee_external_customer_validation_run_001_smoke.py

check-external-customer-validation-run-001:
	python3 scripts/saee_external_customer_validation_run_001.py
	python3 scripts/saee_external_customer_validation_run_001_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_run_001/external_customer_validation_run_001_status.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-recruitment-consent-smoke:
	python3 scripts/saee_external_customer_validation_recruitment_consent_smoke.py

check-external-customer-validation-recruitment-consent:
	python3 scripts/saee_external_customer_validation_recruitment_consent.py
	python3 scripts/saee_external_customer_validation_recruitment_consent_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/external_customer_validation_recruitment_consent.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-action-board-smoke:
	python3 scripts/saee_external_customer_validation_action_board_smoke.py

check-external-customer-validation-action-board:
	python3 scripts/saee_external_customer_validation_action_board.py
	python3 scripts/saee_external_customer_validation_action_board_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_action_board/external_customer_validation_action_board.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-facilitator-smoke:
	python3 scripts/saee_external_customer_validation_facilitator_smoke.py

check-external-customer-validation-facilitator:
	python3 scripts/saee_external_customer_validation_facilitator.py
	python3 scripts/saee_external_customer_validation_facilitator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/external_customer_validation_facilitator.local.json
	python3 -m json.tool agent-index.json

current-commercial-primary-action-smoke:
	python3 scripts/saee_current_commercial_primary_action_smoke.py

check-current-commercial-primary-action:
	python3 scripts/saee_current_commercial_primary_action.py
	python3 scripts/saee_current_commercial_primary_action_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/current_commercial_primary_action/current_commercial_primary_action.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-minimum-session-packet-smoke:
	python3 scripts/saee_external_customer_validation_minimum_session_packet_smoke.py

check-external-customer-validation-minimum-session-packet:
	python3 scripts/saee_external_customer_validation_minimum_session_packet.py
	python3 scripts/saee_external_customer_validation_minimum_session_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/external_customer_validation_minimum_session_packet.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_packet/minimum_session_human_filled_template.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-minimum-session-answer-converter-smoke:
	python3 scripts/saee_external_customer_validation_minimum_session_answer_converter_smoke.py

check-external-customer-validation-minimum-session-answer-converter:
	python3 scripts/saee_external_customer_validation_minimum_session_answer_converter.py
	python3 scripts/saee_external_customer_validation_minimum_session_answer_converter_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_minimum_session_answer_converter/minimum_session_answer_converter.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-post-session-processor-smoke:
	python3 scripts/saee_external_customer_validation_post_session_processor_smoke.py

check-external-customer-validation-post-session-processor:
	python3 scripts/saee_external_customer_validation_post_session_processor.py
	python3 scripts/saee_external_customer_validation_post_session_processor_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_post_session_processor/external_customer_validation_post_session_processor.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-local-session-launcher-smoke:
	python3 scripts/saee_external_customer_validation_local_session_launcher_smoke.py

check-external-customer-validation-local-session-launcher:
	python3 scripts/saee_external_customer_validation_local_session_launcher.py
	python3 scripts/saee_external_customer_validation_local_session_launcher_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/external_customer_validation_local_session_launcher.local.json
	python3 -m json.tool agent-index.json

external-customer-validation-launcher-human-inspection-record-smoke:
	python3 scripts/saee_external_customer_validation_launcher_human_inspection_record_smoke.py

check-external-customer-validation-launcher-human-inspection-record:
	python3 scripts/saee_external_customer_validation_launcher_human_inspection_record.py
	python3 scripts/saee_external_customer_validation_launcher_human_inspection_record_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_local_session_launcher/launcher_human_inspection_record.local.json
	python3 -m json.tool agent-index.json

support-contact-human-filled-evidence-refresh-smoke:
	python3 scripts/saee_support_contact_human_filled_evidence_refresh_smoke.py

check-support-contact-human-filled-evidence-refresh:
	python3 scripts/saee_support_contact_human_filled_evidence_refresh.py
	python3 scripts/saee_support_contact_human_filled_evidence_refresh_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_human_filled_evidence_refresh.local.json
	python3 -m json.tool agent-index.json

support-contact-closure-gap-review-smoke:
	python3 scripts/saee_support_contact_closure_gap_review_smoke.py

check-support-contact-closure-gap-review:
	python3 scripts/saee_support_contact_closure_gap_review.py
	python3 scripts/saee_support_contact_closure_gap_review_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_closure_gap_review.local.json
	python3 -m json.tool agent-index.json

support-contact-state-reconciliation-smoke:
	python3 scripts/saee_support_contact_state_reconciliation_smoke.py

check-support-contact-state-reconciliation:
	python3 scripts/saee_support_contact_state_reconciliation.py
	python3 scripts/saee_support_contact_state_reconciliation_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_contact_state_reconciliation/support_contact_state_reconciliation.local.json
	python3 -m json.tool agent-index.json

support-group-closure-review-packet-smoke:
	python3 scripts/saee_support_group_closure_review_packet_smoke.py

check-support-group-closure-review-packet:
	python3 scripts/saee_support_group_closure_review_packet.py
	python3 scripts/saee_support_group_closure_review_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_group_closure_review_packet.local.json
	python3 -m json.tool agent-index.json

support-group-final-closure-decision-request-smoke:
	python3 scripts/saee_support_group_final_closure_decision_request_smoke.py

check-support-group-final-closure-decision-request:
	python3 scripts/saee_support_group_final_closure_decision_request.py
	python3 scripts/saee_support_group_final_closure_decision_request_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_request.local.json
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_template.json
	python3 -m json.tool agent-index.json

support-group-final-closure-decision-validator-smoke:
	python3 scripts/saee_support_group_final_closure_decision_validator_smoke.py

check-support-group-final-closure-decision-validator:
	python3 scripts/saee_support_group_final_closure_decision_validator.py
	python3 scripts/saee_support_group_final_closure_decision_validator_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation.local.json
	python3 -m json.tool agent-index.json

support-group-final-closure-decision-completion-helper-smoke:
	python3 scripts/saee_support_group_final_closure_decision_completion_helper_smoke.py

check-support-group-final-closure-decision-completion-helper:
	python3 scripts/saee_support_group_final_closure_decision_completion_helper.py
	python3 scripts/saee_support_group_final_closure_decision_completion_helper_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_completion_helper.local.json
	python3 -m json.tool agent-index.json

commercial-matrix-update-request-packet-smoke:
	python3 scripts/saee_commercial_matrix_update_request_packet_smoke.py

check-commercial-matrix-update-request-packet:
	python3 scripts/saee_commercial_matrix_update_request_packet.py
	python3 scripts/saee_commercial_matrix_update_request_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet.local.json
	python3 -m json.tool agent-index.json

commercial-matrix-update-execution-request-packet-smoke:
	python3 scripts/saee_commercial_matrix_update_execution_request_packet_smoke.py

check-commercial-matrix-update-execution-request-packet:
	python3 scripts/saee_commercial_matrix_update_execution_request_packet.py
	python3 scripts/saee_commercial_matrix_update_execution_request_packet_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.local.json
	python3 -m json.tool agent-index.json

commercial-matrix-update-execution-approval-input-smoke:
	python3 scripts/saee_commercial_matrix_update_execution_approval_input_smoke.py

check-commercial-matrix-update-execution-approval-input:
	python3 scripts/saee_commercial_matrix_update_execution_approval_input.py
	python3 scripts/saee_commercial_matrix_update_execution_approval_validator.py
	python3 scripts/saee_commercial_matrix_update_execution_approval_input_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_input.template.json
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_validation.local.json
	python3 -m json.tool agent-index.json

commercial-matrix-update-execution-approval-phrase-intake-smoke:
	python3 scripts/saee_commercial_matrix_update_execution_approval_phrase_intake_smoke.py

check-commercial-matrix-update-execution-approval-phrase-intake:
	python3 scripts/saee_commercial_matrix_update_execution_approval_phrase_intake.py
	python3 scripts/saee_commercial_matrix_update_execution_approval_phrase_intake_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_phrase_intake.local.json
	python3 -m json.tool agent-index.json

commercial-matrix-update-execution-approval-copy-card-smoke:
	python3 scripts/saee_commercial_matrix_update_execution_approval_copy_card_smoke.py

check-commercial-matrix-update-execution-approval-copy-card:
	python3 scripts/saee_commercial_matrix_update_execution_approval_copy_card.py
	python3 scripts/saee_commercial_matrix_update_execution_approval_copy_card_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card.local.json
	python3 -m json.tool agent-index.json

commercial-matrix-update-execution-next-step-router-smoke:
	python3 scripts/saee_commercial_matrix_update_execution_next_step_router_smoke.py

check-commercial-matrix-update-execution-next-step-router:
	python3 scripts/saee_commercial_matrix_update_execution_next_step_router.py
	python3 scripts/saee_commercial_matrix_update_execution_next_step_router_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_next_step_router.local.json
	python3 -m json.tool agent-index.json

pricing-page-state-reconciliation-smoke:
	python3 scripts/saee_pricing_page_state_reconciliation_smoke.py

check-pricing-page-state-reconciliation:
	python3 scripts/saee_pricing_page_state_reconciliation.py
	python3 scripts/saee_pricing_page_state_reconciliation_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_state_reconciliation/pricing_page_state_reconciliation.local.json
	python3 -m json.tool agent-index.json

commercial-matrix-update-execution-dry-run-smoke:
	python3 scripts/saee_commercial_matrix_update_execution_dry_run_smoke.py

check-commercial-matrix-update-execution-dry-run:
	python3 scripts/saee_commercial_matrix_update_execution_dry_run.py
	python3 scripts/saee_commercial_matrix_update_execution_dry_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run.local.json
	python3 -m json.tool agent-index.json

commercial-matrix-update-execution-applier-smoke:
	python3 scripts/saee_commercial_matrix_update_execution_applier_smoke.py

check-commercial-matrix-update-execution-applier:
	python3 scripts/saee_commercial_matrix_update_execution_applier.py
	python3 scripts/saee_commercial_matrix_update_execution_applier_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier.local.json
	python3 -m json.tool agent-index.json

scenario-template-smoke:
	python3 scripts/saee_scenario_template_smoke.py

check-scenario-template:
	python3 scripts/saee_scenario_template_smoke.py
	python3 -m json.tool phase_b_product/scenario_templates/registry.json
	python3 -m json.tool agent-index.json

support-group-human-filled-evidence-refresh-smoke:
	python3 scripts/saee_support_group_human_filled_evidence_refresh_smoke.py

check-support-group-human-filled-evidence-refresh:
	python3 scripts/saee_support_group_human_filled_evidence_refresh.py
	python3 scripts/saee_support_group_human_filled_evidence_refresh_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/support_evidence/support_group_human_filled_evidence_refresh.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-validator-execution-run-smoke:
	python3 scripts/saee_commercial_sprint_validator_execution_run_smoke.py

check-commercial-sprint-validator-execution-run:
	python3 scripts/saee_commercial_sprint_validator_execution_run_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_validator_execution_run.local.json
	python3 -m json.tool agent-index.json

commercial-sprint-validator-hold-output-review-smoke:
	python3 scripts/saee_commercial_sprint_validator_hold_output_review_smoke.py

check-commercial-sprint-validator-hold-output-review:
	python3 scripts/saee_commercial_sprint_validator_hold_output_review_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_validator_hold_output_review.local.json
	python3 -m json.tool agent-index.json

codex-context-check:
	python3 scripts/codex_context_check.py

check-codex-context:
	python3 scripts/codex_context_check.py
	python3 -m json.tool agent-index.json

resource-resolution-receipt-smoke:
	python3 scripts/saee_resource_resolution_receipt_smoke.py

check-resource-resolution-receipt:
	python3 scripts/saee_resource_resolution_receipt_smoke.py
	python3 scripts/saee_agent_cli.py validate-resource-resolution --input agent-interface/examples/verified-resource-resolution.json
	python3 -m json.tool agent-interface/schemas/resource-resolution-receipt.schema.json
	python3 -m json.tool agent-interface/examples/verified-resource-resolution.json
	python3 -m json.tool agent-index.json

evidence-adequacy-smoke:
	python3 scripts/saee_evidence_adequacy_smoke.py

check-evidence-adequacy:
	python3 scripts/saee_evidence_adequacy_smoke.py
	python3 scripts/saee_agent_cli.py validate-evidence-adequacy --profile RESOURCE_AUTHENTICITY --input agent-interface/examples/evidence-adequacy/resource_authenticity_pass.json
	python3 -m json.tool agent-interface/schemas/evidence-adequacy-profile.schema.json
	python3 -m json.tool agent-index.json

otel-candidate-mapping-smoke:
	python3 scripts/saee_otel_candidate_mapping_smoke.py

check-otel-candidate-mapping:
	python3 scripts/saee_otel_candidate_mapping_smoke.py
	python3 scripts/saee_agent_cli.py evaluate-trace-candidate --profile RESOURCE_AUTHENTICITY --input agent-interface/examples/otel-mapping/trace_candidate_resource_retrieval.json
	python3 -m json.tool agent-interface/schemas/otel-candidate-evidence-mapping.schema.json
	python3 -m json.tool agent-index.json

.PHONY: capability-progress-ledger-smoke check-capability-progress-ledger
.PHONY: canonical-capability-inventory-smoke check-canonical-capability-inventory

capability-progress-ledger-smoke:
	python3 scripts/saee_capability_progress_ledger_smoke.py

check-capability-progress-ledger:
	python3 scripts/saee_capability_progress_ledger_smoke.py
	python3 -m json.tool agent-index.json

canonical-capability-inventory-smoke:
	python3 scripts/saee_canonical_capability_inventory_smoke.py

check-canonical-capability-inventory:
	python3 scripts/saee_canonical_capability_inventory_smoke.py
	python3 -m json.tool capability-package/manifest.json
	python3 -m json.tool schemas/saee-canonical-capability-inventory.schema.v1.json

agent-receipt-crosswalk-smoke:
	python3 scripts/saee_agent_receipt_crosswalk_smoke.py

check-agent-receipt-crosswalk:
	python3 scripts/saee_agent_receipt_crosswalk_smoke.py
	python3 -m json.tool agent-interface/mappings/agent-receipt-crosswalk.v0.1.json
	python3 -m json.tool agent-index.json

evidence-adequacy-benchmark-smoke:
	python3 scripts/saee_evidence_adequacy_benchmark_smoke.py

check-evidence-adequacy-benchmark:
	python3 scripts/saee_evidence_adequacy_benchmark_smoke.py
	python3 scripts/saee_agent_cli.py benchmark-evidence-adequacy --input agent-interface/benchmarks/evidence-adequacy/
	python3 -m json.tool agent-interface/schemas/evidence-adequacy-benchmark.schema.json
	python3 -m json.tool agent-interface/benchmarks/evidence-adequacy/benchmark.v0.1.json
	python3 -m json.tool agent-index.json

saee-reproducibility-smoke:
	python3 scripts/saee_reproducibility_smoke.py

check-saee-reproducibility:
	python3 scripts/saee_reproducibility_smoke.py
	python3 -m json.tool agent-interface/schemas/reproducibility-manifest.schema.json
	python3 -m json.tool agent-interface/reproducibility/saee-reproducibility-manifest.v0.1.json
	python3 -m json.tool agent-interface/reproducibility/expected-results.v0.1.json
	python3 -m json.tool agent-index.json

saee-environment-requirements-smoke:
	python3 scripts/saee_environment_requirements_smoke.py

check-saee-environment-requirements:
	python3 scripts/saee_environment_requirements_smoke.py
	python3 -m json.tool agent-interface/schemas/reproducibility-manifest.schema.json
	python3 -m json.tool agent-interface/reproducibility/saee-reproducibility-manifest.v0.1.json
	python3 -m json.tool agent-index.json

saee-research-artifact-smoke:
	python3 scripts/saee_research_artifact_smoke.py

check-saee-research-artifact:
	python3 scripts/saee_research_artifact_smoke.py
	python3 -m json.tool agent-interface/research-artifact/saee-artifact-manifest.v0.1.json
	python3 -m json.tool agent-index.json

saee-paper-draft-smoke:
	python3 scripts/saee_paper_draft_smoke.py

check-saee-paper-draft:
	python3 scripts/saee_paper_draft_smoke.py
	python3 -m json.tool agent-index.json

saee-evaluation-design-smoke:
	python3 scripts/saee_evaluation_design_smoke.py

check-saee-evaluation-design:
	python3 scripts/saee_evaluation_design_smoke.py
	python3 -m json.tool agent-interface/evaluation/saee-external-evaluation-design.v0.1.json
	python3 -m json.tool agent-index.json

saee-evaluation-prototype-smoke:
	python3 scripts/saee_evaluation_prototype_smoke.py

check-saee-evaluation-prototype:
	python3 scripts/saee_evaluation_prototype_smoke.py
	python3 scripts/saee_agent_cli.py run-evaluation-prototype --input agent-interface/evaluation/scenarios/ >/dev/null
	python3 -m json.tool agent-interface/schemas/saee-evaluation-scenario.schema.json
	python3 -m json.tool agent-interface/evaluation/results/prototype-results.v0.1.json
	python3 -m json.tool agent-index.json

saee-pilot-preparation-smoke:
	python3 scripts/saee_pilot_preparation_smoke.py

check-saee-pilot-preparation:
	python3 scripts/saee_pilot_preparation_smoke.py
	python3 -m json.tool agent-interface/evaluation/saee-pilot-preparation.v0.1.json
	python3 -m json.tool agent-index.json

saee-dataset-specification-smoke:
	python3 scripts/saee_dataset_specification_smoke.py

check-saee-dataset-specification:
	python3 scripts/saee_dataset_specification_smoke.py
	python3 -m json.tool agent-interface/evaluation/dataset-specification/task-record.schema.json >/dev/null
	python3 -m json.tool agent-interface/evaluation/dataset-specification/trace-record.schema.json >/dev/null
	python3 -m json.tool agent-interface/evaluation/dataset-specification/evidence-bundle.schema.json >/dev/null
	python3 -m json.tool agent-interface/evaluation/dataset-specification/annotation-record.schema.json >/dev/null
	python3 -m json.tool agent-interface/evaluation/saee-pilot-dataset-manifest.v0.1.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-pilot-readiness-smoke:
	python3 scripts/saee_pilot_readiness_smoke.py

check-saee-pilot-readiness:
	python3 scripts/saee_pilot_readiness_smoke.py
	python3 scripts/saee_agent_cli.py review-pilot-readiness --input agent-interface/evaluation/saee-pilot-readiness-review.v0.1.json >/dev/null
	python3 -m json.tool agent-interface/evaluation/saee-pilot-readiness-review.v0.1.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-pilot-gap-resolution-smoke:
	python3 scripts/saee_pilot_gap_resolution_smoke.py

check-saee-pilot-gap-resolution:
	python3 scripts/saee_pilot_gap_resolution_smoke.py
	python3 scripts/saee_agent_cli.py review-pilot-gaps --input agent-interface/evaluation/saee-pilot-readiness-gap-plan.v0.1.json >/dev/null
	python3 -m json.tool agent-interface/evaluation/saee-pilot-readiness-gap-plan.v0.1.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-evidence-acquisition-plan-smoke:
	python3 scripts/saee_evidence_acquisition_plan_smoke.py

check-saee-evidence-acquisition-plan:
	python3 scripts/saee_evidence_acquisition_plan_smoke.py
	python3 scripts/saee_agent_cli.py review-evidence-acquisition-plan --input agent-interface/evaluation/saee-pilot-evidence-acquisition-plan.v0.1.json >/dev/null
	python3 -m json.tool agent-interface/evaluation/saee-pilot-evidence-acquisition-plan.v0.1.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-phase1-synthetic-vertical-slice-smoke:
	python3 scripts/saee_phase1_synthetic_vertical_slice_smoke.py

check-saee-phase1-synthetic-vertical-slice:
	python3 scripts/saee_phase1_synthetic_vertical_slice_smoke.py
	python3 scripts/saee_v3_architecture_smoke.py
	python3 scripts/saee_agent_cli.py run-assurance-case --input agent-interface/architecture/examples/saee-evidence-case-synthetic-001.json >/dev/null
	python3 -m json.tool agent-interface/architecture/saee-evidence-case.v0.1.schema.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/saee-evidence-case-synthetic-001.json >/dev/null
	python3 -m json.tool agent-interface/architecture/saee-v3-system-architecture.v0.1.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-phase1-5-case-corpus-smoke:
	python3 scripts/saee_phase1_5_case_corpus_smoke.py

check-saee-phase1-5-case-corpus:
	python3 scripts/saee_phase1_5_case_corpus_smoke.py
	python3 scripts/saee_phase1_synthetic_vertical_slice_smoke.py
	python3 scripts/saee_v3_architecture_smoke.py
	python3 -m json.tool agent-interface/architecture/examples/phase1_5_cases/case-001-baseline-stability.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/phase1_5_cases/case-002-context-drift.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/phase1_5_cases/case-003-tool-failure.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/phase1_5_cases/case-004-instruction-conflict.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/phase1_5_cases/case-005-adversarial-input.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-observation-contract-smoke:
	python3 scripts/saee_observation_contract_smoke.py

check-saee-observation-contract:
	python3 scripts/saee_observation_contract_smoke.py
	python3 scripts/saee_phase1_5_case_corpus_smoke.py
	python3 scripts/saee_v3_architecture_smoke.py
	python3 -m json.tool agent-interface/architecture/saee-observation-envelope.v0.1.schema.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/observation/synthetic-observation.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/observation/runtime-observation.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/observation/tool-trace-observation.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-observation-replay-contract-smoke:
	python3 scripts/saee_observation_replay_contract_smoke.py

check-saee-observation-replay-contract:
	python3 scripts/saee_observation_replay_contract_smoke.py
	python3 scripts/saee_observation_contract_smoke.py
	python3 scripts/saee_phase1_5_case_corpus_smoke.py
	python3 scripts/saee_v3_architecture_smoke.py
	python3 -m json.tool agent-interface/architecture/saee-observation-replay-contract.v0.1.schema.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/replay/synthetic-replay-case.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/replay/consent-replay-case.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/replay/transformed-replay-case.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-replay-evaluation-contract-smoke:
	python3 scripts/saee_replay_evaluation_contract_smoke.py

check-saee-replay-evaluation-contract:
	python3 scripts/saee_replay_evaluation_contract_smoke.py
	python3 scripts/saee_observation_replay_contract_smoke.py
	python3 scripts/saee_observation_contract_smoke.py
	python3 scripts/saee_phase1_5_case_corpus_smoke.py
	python3 scripts/saee_v3_architecture_smoke.py
	python3 -m json.tool agent-interface/architecture/saee-replay-evaluation-contract.v0.1.schema.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/replay-evaluation/synthetic-replay-evaluation.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/replay-evaluation/transformed-replay-evaluation.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/replay-evaluation/consent-bound-replay-evaluation.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-evaluation-run-contract-smoke:
	python3 scripts/saee_evaluation_run_contract_smoke.py

check-saee-evaluation-run-contract:
	python3 scripts/saee_evaluation_run_contract_smoke.py
	python3 scripts/saee_replay_evaluation_contract_smoke.py
	python3 scripts/saee_observation_replay_contract_smoke.py
	python3 scripts/saee_observation_contract_smoke.py
	python3 scripts/saee_phase1_5_case_corpus_smoke.py
	python3 scripts/saee_v3_architecture_smoke.py
	python3 -m json.tool agent-interface/architecture/saee-evaluation-run-contract.v0.1.schema.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/evaluation-run/synthetic-evaluation-run.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/evaluation-run/failed-evaluation-run.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/evaluation-run/repeated-evaluation-run.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-run-termination-contract-smoke:
	python3 scripts/saee_run_termination_contract_smoke.py

check-saee-run-termination-contract:
	python3 scripts/saee_run_termination_contract_smoke.py
	python3 scripts/saee_evaluation_run_contract_smoke.py
	python3 scripts/saee_replay_evaluation_contract_smoke.py
	python3 scripts/saee_observation_replay_contract_smoke.py
	python3 scripts/saee_observation_contract_smoke.py
	python3 scripts/saee_phase1_5_case_corpus_smoke.py
	python3 scripts/saee_v3_architecture_smoke.py
	python3 -m json.tool agent-interface/architecture/saee-evaluation-run-termination-contract.v0.1.schema.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/run-termination/manual-abort-termination.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/run-termination/runtime-failure-termination.json >/dev/null
	python3 -m json.tool agent-interface/architecture/examples/run-termination/input-rejected-termination.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-phase2a-readiness-gate:
	python3 scripts/saee_phase2a_readiness_gate.py

check-saee-phase2a-readiness-gate:
	python3 scripts/saee_phase2a_readiness_gate.py
	python3 scripts/saee_run_termination_contract_smoke.py
	python3 scripts/saee_evaluation_run_contract_smoke.py
	python3 scripts/saee_replay_evaluation_contract_smoke.py
	python3 scripts/saee_observation_replay_contract_smoke.py
	python3 -m json.tool agent-index.json >/dev/null

saee-phase2a-execution-smoke:
	python3 scripts/saee_phase2a_execution_smoke.py

check-saee-phase2a-execution:
	python3 scripts/saee_phase2a_readiness_gate.py
	python3 scripts/saee_phase2a_execution_smoke.py
	python3 scripts/saee_run_termination_contract_smoke.py
	python3 scripts/saee_evaluation_run_contract_smoke.py
	python3 scripts/saee_replay_evaluation_contract_smoke.py
	python3 -m json.tool agent-index.json >/dev/null

saee-phase2b-adapter-readiness-gate:
	python3 scripts/saee_phase2b_adapter_readiness_gate.py

check-saee-phase2b-adapter-readiness-gate:
	python3 scripts/saee_phase2b_adapter_readiness_gate.py
	python3 scripts/saee_phase2a_execution_smoke.py
	python3 -m json.tool agent-index.json >/dev/null

saee-adapter-provenance-contract-smoke:
	python3 scripts/saee_adapter_provenance_contract_smoke.py

check-saee-adapter-provenance-contract:
	python3 scripts/saee_adapter_provenance_contract_smoke.py
	python3 scripts/saee_phase2b_adapter_readiness_gate.py
	python3 -m json.tool agent-interface/architecture/saee-adapter-provenance-contract.v0.1.schema.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-synthetic-observation-adapter-smoke:
	python3 scripts/saee_synthetic_observation_adapter_smoke.py

check-saee-synthetic-observation-adapter:
	python3 scripts/saee_phase2b_adapter_readiness_gate.py
	python3 scripts/saee_adapter_provenance_contract_smoke.py
	python3 scripts/saee_synthetic_observation_adapter_smoke.py
	python3 -m json.tool agent-interface/architecture/saee-synthetic-external-observation.v0.1.schema.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-phase2b-completion-review-smoke:
	python3 scripts/saee_phase2b_completion_review_smoke.py

check-saee-phase2b-completion-review:
	python3 scripts/saee_phase2b_completion_review_smoke.py
	python3 scripts/saee_synthetic_observation_adapter_smoke.py
	python3 scripts/saee_adapter_provenance_contract_smoke.py
	python3 -m json.tool agent-interface/architecture/saee-phase2b-completion-review.v0.1.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-review-report-smoke:
	python3 scripts/saee_review_report_smoke.py

check-saee-review-report:
	python3 scripts/saee_review_report_smoke.py
	python3 scripts/saee_agent_cli.py generate-review-report --input agent-interface/commercial/review-cases/synthetic-code-agent-review-case.json >/dev/null
	python3 -m json.tool agent-interface/commercial/saee-evidence-review-report.schema.json >/dev/null
	python3 -m json.tool agent-interface/commercial/review-cases/synthetic-code-agent-review-case.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-design-partner-validation-smoke:
	python3 scripts/saee_design_partner_validation_smoke.py

check-saee-design-partner-validation:
	python3 scripts/saee_design_partner_validation_smoke.py
	python3 -m json.tool agent-interface/commercial/saee-design-partner-validation-plan.v0.1.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-agent-native-commercial-logic-smoke:
	python3 scripts/saee_agent_native_commercial_logic_smoke.py

check-saee-agent-native-commercial-logic:
	python3 scripts/saee_agent_native_commercial_logic_smoke.py
	python3 scripts/saee_design_partner_validation_smoke.py
	python3 -m json.tool agent-interface/commercial/saee-agent-native-commercial-logic.v2.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

saee-agent-native-capability-smoke:
	python3 scripts/saee_agent_native_capability_smoke.py

check-saee-agent-native-capability:
	python3 scripts/saee_agent_native_capability_smoke.py
	python3 scripts/saee_agent_native_commercial_logic_smoke.py
	python3 -m json.tool agent-interface/capabilities/saee-capability-manifest.v0.1.json >/dev/null
	python3 -m json.tool agent-index.json >/dev/null

oidc-jwks-verifier-smoke:
	python3 scripts/saee_oidc_jwks_verifier_smoke.py
	python3 scripts/saee_oidc_rbac_handler_boundary_smoke.py

check-agent-blocker-priority-index:
	python3 scripts/saee_agent_blocker_priority_index.py
	python3 -m json.tool phase_b_product/commercial_readiness/agent_blocker_priority_index/agent_blocker_priority_index.local.json

check-oidc-jwks-validation-profile:
	python3 scripts/saee_oidc_jwks_validation_profile.py
	python3 scripts/saee_oidc_jwks_verifier_smoke.py
	python3 scripts/saee_oidc_rbac_handler_boundary_smoke.py
	python3 -m json.tool phase_b_product/commercial_readiness/oidc_jwks_verifier_evidence/oidc_jwks_verifier_evidence.local.json
	python3 -m json.tool agent-index.json
