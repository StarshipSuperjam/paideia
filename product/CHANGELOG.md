# Paideia Changelog (reserved)

This file is reserved for the learner-visible product release log per [ADR 0037](../engine/adr/0037-engine-product-wall-and-changelog-rename.md). The first entry lands at Phase 9 release prep with v1.0.0 — no entries before that point.

The dated narrative for material **engine** changes (the AI build apparatus the user and Claude run together to construct Paideia) lives in [`ENGINE_LOG.md`](../engine/ENGINE_LOG.md), the third layer of the four-layer trace system named in [ADR 0036](../engine/adr/0036-expression-contract-for-inward-documents.md). `ENGINE_LOG.md` is not the product release log; that role is what this file holds open.

The expression contract governing learner-visible release-log voice settles at [`OQ-OUTWARD-VOICE`](docs/tensions.md) before Phase 7 (the third expression-contract gap, kindred-tool to [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md) and [ADR 0036](../engine/adr/0036-expression-contract-for-inward-documents.md), separately scoped to outward product surfaces — UI labels, button text, error messages, learner-facing help, public README, App Store description, learner-visible CHANGELOG entries).

A future contributor or future Claude Code session walking up cold without ADR 0037 context might otherwise re-create `CHANGELOG.md` from scratch under conventional Keep-a-Changelog assumptions. This stub names the reservation explicitly so that does not happen.
