# Test Plan

## Validation triggers (§241)

Run the full suite after code-affecting changes, including test, dependency,
build or configuration changes that affect execution. Documentation-only and
comment-only edits need relevant checks (formatting, links or table/data
consistency), not a full test run. Reuse a passing result when the tested code
is unchanged; committing or pushing does not require repeating verification.

Review runs never share a sandbox PID artifact root: run them sequentially,
with an isolated OS-temp base through the standard `TMPDIR` when needed,
without changing production PID/UUID paths or removing unverified locks.

## Designer acceptance checklist (B99/B100/B105/B106)

These issues stay OPEN until the designer confirms them; worker verification
is not acceptance. The acceptance review covers:

- All six Image compression choices, enabled parameters, precise Threshold
  method/readout and genuine JBIG2 Color output, without losing filter names
  or UUIDs. Color displays BW-only FFPR off; Revert restores its saved state.
- The independent PDF streams choices, one debounced real-file update,
  exact preview/size, Save/Save As persistence and Cancel retaining the
  edited filter. First/repeat selection and zoom must not reprocess.
- The Brotli reader requirement stated in the PDF streams help. Use a
  supporting reader for Brotli; the installed older Poppler/QPDF failures are
  expected, not hidden.
- Zopfli's encoding cost versus unchanged Flate compatibility; do not infer
  responsiveness from noisy desktop timing samples.

This is a review checklist, not a request to run heavy checks or permission
to launch the app automatically. B107 needs a targeted native-callback/
process-pool cancellation regression before any repair claim.
