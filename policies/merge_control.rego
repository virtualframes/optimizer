package synapse.cortex.merge_control

default allow_merge = false

# Input structure expected:
# {
#   "security_scan": { "status": "CLEAN", "high_severity": 0 },
#   "audit_anchor": { "is_anchored": true, "ledger_tx_id": "..." },
#   "requester_role": "engineer" | "security_officer"
# }

# Rule 1: Allow if all mandatory checks pass
allow_merge {
    is_security_clean
    is_audit_anchored
}

# Rule 2: Allow if security failed but overridden by authorized role
allow_merge {
    not is_security_clean
    is_audit_anchored
    input.requester_role == "security_officer"
}

# Helper functions
is_security_clean {
    input.security_scan.status == "CLEAN"
    input.security_scan.high_severity == 0
}

is_audit_anchored {
    input.audit_anchor.is_anchored == true
    # Ensure ledger_tx_id is a non-empty string
    input.audit_anchor.ledger_tx_id != ""
}

# Denial reasons (for workflow feedback)
deny_reason[msg] {
    not is_security_clean
    input.requester_role != "security_officer"
    msg := sprintf("Security scan failed (Status: %v). Override by security_officer required.", [input.security_scan.status])
}

deny_reason[msg] {
    not is_audit_anchored
    msg := "Merge blocked: Missing verified audit anchor in the immutable ledger."
}