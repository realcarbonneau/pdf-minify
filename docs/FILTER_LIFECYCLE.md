# Filter recipes, live drafts, and real filtered files — canon (§§122/149)

The designer's full ruling is preserved verbatim in `DESIGNER_VERBATIM.md`
§149. This specification supersedes split preview/mini/estimator jobs and
the old file-slot/spec-slot cache design. Cross-refs: `ARCHITECTURE.md`,
`UI_LAYOUT.md`, `PERSISTENCE_AND_TEMP.md`, `TODO.md` §§150–157, issues B74–B79.

## One processing path and one source of truth

On document open, queue EVERY saved filter in strip order, selected first.
One immutable full effective recipe + input-file identity identifies the
processing result; the owning filter UUID separates stored artifacts. Run
the real saver once for a missing recipe, then read that
file back for both preview pages and minis. Amount = exact file byte size,
including PDF overhead, fonts, masks, and metadata. Export copies this file;
it never reruns a separate transformation. No payload estimators in GUI work.

Selecting a filter, including its first visit, only displays its existing
result or waits for that already queued result. It never starts another
processing job. Zoom, pan, page changes, and DnD reorder are view changes:
reframe existing pages and observe the actual PDFs at display resolution
(§§172–175 supersede prepared-raster-only zoom). Native geometry redraw is
read-only display, not filter reprocessing. Evicting optional display bitmaps must not
invalidate or rerun a real filtered file. Only a new input or an actual
effective recipe change authorizes filtering work.

## Saved recipe and live draft are separate states

§§203–205: compression is part of that editable recipe, not immutable preset
metadata. Image mode and native-stream policy are authoritative saved/draft
inputs: enable controls/readouts from this state, include both in cache keys,
and persist/reload them even when overriding a built-in filter. Save As must
copy the draft's actual mode/policy, not the source template's original mode.
Changes use the same 300ms timer and explicit switch transaction described
below. UUID/name/order remain unchanged on Save; a named copy gets a new UUID.

§§262–264 add the common Quality control: `jpeg_q` for JPEG, `jpx_q` for
JPEG2000, with a q75 starting point and a versioned one-time saved-filter
migration (§264 replaces §263's q90; revision 2 must migrate revision 1 stores).
Quality edits use this same transaction and timer. Lossless JPX ignores its
retained inactive quality. Keep explicit legacy ratio recipes distinct from
quality in effective keys; see [LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md).
§265 also versions the fixed JPEG/JPEG2000 encoder profiles in effective keys.
§267 versions the study-based JPX quality mapping and its reference JPEG
profile as well. Saved q values remain unchanged; a changed encoding policy
invalidates old completed results, not filter UUIDs or saved/draft ownership.
No new user-facing encoder controls or independent preview transformation are
introduced. Selection still observes the actual saved result only.

Each filter keeps a saved recipe/result and, while dirty, a live draft.
Loading controls under signal blockers is not an edit. Effective comparisons
exclude irrelevant disabled controls and normalize defaults, so selection
cannot accidentally change threshold/DPI/lossless or other recipes.

User edits create/update the selected filter's draft immediately, show `*`
in its mini/dropdown/header, and restart ONE shared single-shot 300ms trailing
debounce (§183; proposed default replacing 200ms). All recipe inputs feed the
same edit path: native slider drag/keys, spin arrows/typed numbers, DPI/strategy/
page-size dropdowns, FFPR and JPX-lossless toggles. Use a precise timer so it
cannot fire before the trailing interval; Qt event-loop load may delay it.
Processing uses an immutable recipe snapshot. Stale completions cannot
replace newer edits. Other saved filter results remain untouched. Editing
back to the saved recipe clears `*` and reuses its artifact without work.
Already ready identical recipes can update immediately; §149 forbids forcing
another saver run just to provide edit feedback. View-only reframe debounce
is separate: combining view events with the processing timer would let zoom/
resize interfere with edits or authorize processing, contradicting §149.

Each filter's persistent internal UUID is separate from its editable name and
position-dependent number (§§154/155). UUIDs are generated with `uuid.uuid4()`;
load validates uniqueness and repairs pasted duplicates, and Save As gets a
new UUID. Neither rename nor reorder changes it. Files live under that UUID
inside the GUI PID directory, with immutable saved/live artifact-key children.
Copies materialize their own paths from prepared files rather than re-filter.

The original saved artifact is retained throughout live editing. Obsolete
draft artifacts are retired only when no saved/draft/worker reference needs
them. A draft may be saved while its processing is pending; that same
in-flight recipe completes under the new saved ownership, without rerunning.

## Leaving a dirty filter

"Changed chosen filter" is interpreted as selecting another filter. Show a
modal decision before changing the active recipe/controls/preview:

Dialog wording (§160): its destructive choice is explicitly **Discard Changes**,
not the platform's application-close-oriented "Close without saving" label.
Keep Qt's Discard button identity/role and Cancel as the escape action.

Canceled mini switches (§161): the edited filter remains both current AND
visibly selected after the complete Qt mouse press/release, not only during
the dialog callback. Dropdown, preview, controls, dirty marker, saved/live
files and processing ownership all remain unchanged. Test actual mini
gestures with the real modal Escape/Cancel/close, not just programmatic combo
changes or a mocked decision.

The activation boundary is the completed native input handler, not an
intermediate `currentRowChanged` or `itemSelectionChanged`: mousePress first
changes current index, then selection; keyboard navigation can select twice.
Opening a modal and rolling back inside those steps lets unfinished Qt work
overwrite the restored highlight or reopen the prompt. Run Qt's normal
press/release/key handler with view notifications signal-blocked, then notify
the shared switch controller once if the actual selection changed. Ordinary
programmatic row changes retain their normal final current-row notification.
No timer rollback, extra repaint, or replacement mouse/drag controller.
See [Qt native input sequences](https://github.com/qt/qtbase/blob/6.10/src/widgets/itemviews/qabstractitemview.cpp)
and [QSignalBlocker](https://doc.qt.io/qt-6/qsignalblocker.html).

| Action | Recipe ownership | Filtered files |
| --- | --- | --- |
| Save | Promote current draft into the same saved filter | Keep new result; retire obsolete old result when unreferenced |
| Save As… | Ask for a name, create AND select a saved filter with the draft (§189) | Keep original saved result and new result |
| Discard Changes | Restore the saved recipe | Keep old result; retire live draft result when safe |
| Cancel / Escape / close dialog | Stay on the current filter and draft | Keep both; selection and controls unchanged |

Save As… is the conventional term for a separately named saved recipe, not
PDF export. §189 specifies its destination: both explicit Save As and Save As
inside a dirty-filter switch select the newly named filter, not the mini/
dropdown/keyboard target that triggered the prompt. Current/selected mini,
dropdown, controls, dirty marker, header and prepared preview must all agree;
scroll the selected copy into view. Return an explicit resolution carrying
the new filter ID so the outer switch cannot silently overwrite this choice.
Save and Discard still continue to the requested filter; Cancel stays edited.
Canceling its name dialog also cancels the switch. The existing
explicit Save Filter and Copy Filter actions follow these same ownership
rules; saving must not invalidate completed work. Opening another document
or closing the application also resolves an unsaved draft before losing it.
In those contexts, successful Save As selects the new copy while preserving
the requested open/close action; it must not accidentally cancel document
open or application close. A canceled/blank name cancels the entire action.
Processing completion for an active pending copy must apply its prepared
result when ready, whereas other late arrivals cannot steal selection.

Explicit Revert Changes (§162): an icon-only action beside the filter
dropdown with tooltip "Revert Changes". §197 replaces the custom arrow with
the standard `document-revert` theme/Breeze icon, not history Undo. Enable it only
while the active filter has a live draft. Its explicit action discards that
draft, restores saved controls/preview/mini and clears `*`, using the same
safe artifact ownership as Discard Changes. Keep selection and other filters
unchanged; reuse the saved prepared file, never re-filter to revert.

## Verification obligations

Count real saver calls, not status strings. After all filters complete,
first visits to every mini and zoom/pan/reorder must add zero calls/jobs.
Compare every amount with the actual completed PDF's byte size; export bytes
must match. Cover debounce, dirty markers, returning to saved values,
programmatic control loading, each prompt decision, canceled naming, and
switching while work is pending. Check exact file retention/deletion and
late arrivals after discard and copies of identical recipes in separate UUID
directories. Pending copies retain their source; subsequent edits cannot
delete another filter's saved files. Validate IDs and pasted aliases on load.
Tests cannot mark these issues designer-confirmed.

## Related rulings consolidated (§150 audit)

The quotes remain unchanged in `DESIGNER_VERBATIM.md`; this index records
their operative meaning and routes it to its canonical topic, without making
old implementation descriptions into designer decisions.

| Topic | Designer rulings | Operative canon / topic |
| --- | --- | --- |
| All filters processed, GUI responsive | §§9, 32, 37, 43, 51, 90, 128, 149 | Real-file jobs in background, half-core cap, selected first then strip order; per-filter progress. `ARCHITECTURE.md` |
| No processing on selection/view | §§37, 44, 45, 47, 48, 90, 92, 108, 115, 149 | Selection only shows prepared results; zoom/pan/page/crop only reframes; trailing view debounce. This doc / `UI_LAYOUT.md` |
| Exact final size, not estimate | §§32, 53, 55, 59, 60, 61, 106, 122, 149 | Byte size of the real whole filtered PDF; rounded original-relative percentage; include overhead/fonts/masks. `ARCHITECTURE.md` |
| One saved-file observation path | §§48, 111, 113, 121, 122, 149 | Real saver → kept temp PDF → prepared pixels, minis, final bytes, export copy. This doc / `ARCHITECTURE.md` |
| Isolated per-filter changes | §§65, 67, 83, 85, 100, 103, 105, 106, 116, 127, 129, 131, 149 | Full effective recipe snapshot; one dirty draft; debounce only that filter; selection cannot seed other recipes. This doc |
| Rename/copy/save versus live edit | §§109, 112, 120, 149 | Explicit persistence actions; `*` dirty state; Save promotes, Save As preserves a named copy, Discard restores saved, Cancel stays. This doc / `UI_LAYOUT.md` |
| Temp versus persistence | §§15, 91, 93, 123, 149, 151, 152, 153 | Runtime scratch in Qt OS temp under one locked GUI PID directory, removed on normal exit; no extra session/history layer. Recipes/last-file in QSettings; repo `.tmp/` only developer artifacts. `PERSISTENCE_AND_TEMP.md` |
| Stable filter identity | §§128, 148, 154, 155 | Persistent unique random UUID, validated on load and never displayed; name and number are presentation. UUID-named directories; recipe-key children keep saved/live data separate; copies reuse prepared files. This doc / `PERSISTENCE_AND_TEMP.md` |
| Transform semantics | §§10, 57, 64, 74, 81, 85, 103, 119, 121, 126, 127, 129 | Original page size by default; FFPR OFF preserves text/vectors, ON flattens; exact DPI before transforms supersedes old ceiling-only prose. `COMPRESSION.md` |
| Progress, cancellation, safe close | §§3, 37, 43, 85, 89, 94, 95, 149 | No artificial 50% milestone; true work progress; Cancel Save isn't Undo; closing never destroys live QThreads. `ARCHITECTURE.md` / this doc |
| Verification and acceptance | §§14, 19, 59, 62, 90, 102, 104, 125, 137, 139, 147, 149, 150 | Docs lead; logs/real artifacts/call counts, full suite, viewed screenshots, restart; only dated explicit designer acceptance closes issues. `DEVELOPER_GUIDELINES.md` |

## Contradiction and implementation audit

1. `DESIGN.md` put page/crop in the processing key and allowed reprocessing
   on those changes, contradicting §§37/44/47/48. Only input identity and
   full effective saver parameters identify processing work.
2. Worker notes attributed "two background slots" to §90; the actual ruling
   says not to restart filters on selection. That architecture was never a
   designer requirement and is retired.
3. Architecture called the single path "locked/not yet implemented" while
   behavior/README described exact final sizes as done. Inspection found
   neither a `save_with_spec` entry point nor saved files in the GUI flow.
   The implementation was preview transformations plus payload sums. The
   replacement creates real PDFs and measures their entire file size.
4. `jobs.py` independently applied transforms at preview and mini DPI, then
   computed estimates separately; export ran a fourth path. These functions
   are removed from GUI code. Minis are just scaled derivatives of prepared
   pixels read from the real filtered PDF, not another filter application.
5. The preview cache held only two visited filters, so initial and later
   visits necessarily dispatched work. Prepared pages now live beside the
   real PDF in disk-backed buffers; selecting any completed filter needs no
   job, without keeping every full document in RAM.
6. Control-loading signals restarted timers; some key inputs (quality/rate/
   page-size and all live mini parameters) were missing. Recipe identity now
   contains every effective saver input, excludes disabled controls and names,
   and control loading blocks signals. Saved JPEG2000 lossless state is kept.
7. Save Filter invalidated completed output; Copy copied saved parameters,
   not the live edit. Both now use explicit saved/draft ownership, reusing
   completed or already queued results instead of rerunning them.
8. Compression notes called payload totals "real" with overhead intentionally
   omitted and an open mask-count gap. Neither is permissible under
   §§53/55/122/149; whole-file measurement removes both discrepancies.
9. `UX_DESIGN.md` still described Tk, a page list, on-click rendering and
   estimates; `00_OVERVIEW.md` advertised similar superseded UI. Those are
   marked historical, with current canon routed to the topic docs.
10. §64's older DPI-ceiling wording is superseded by §129's exact-DPI ruling.
    Core compression still has documented small-image/alpha/1-bit preservation
    exceptions and a keep-original-if-smaller policy. These are explicit
    remaining constraints, not a claim that every source has been resampled;
    their broader policy review is tracked under existing B60 in
    `COMPRESSION.md`. This flow repair makes preview/size/export agree with
    what the real saver does; it does not silently change codec policy.
11. Real-file concurrent smoke exposed the startup sweeper removing every
    empty directory, including fresh workers belonging to another running
    app (B78). One PID directory per process, a held Qt process lock, and
    age-gated empty-directory cleanup protect live work. Encoder scratch is
    inside that owned job directory, not anonymous global temp. An extra
    `session-…` level was a worker addition rejected in §153, not canon.
12. Reading actual saved files exposed corrupted JPEG/JPX/JBIG2/Flate streams
    hidden by simulated previews (B79). PyMuPDF automatic compression wrapped
    pre-encoded bytes before code assigned the inner codec's Filter metadata.
    Encoded updates now disable automatic compression. Zopfli's default gzip
    wrapper was another independent error: use and validate zlib-wrapped
    Deflate. Real saved-image and page readback tests cover these paths; corrupt
    output cannot be published as a successful preview. The formerly blamed
    sparse JBIG2 fixture now decodes correctly; genuine invalid-stream fallback
    is tested separately.
13. Submitting jobs from concurrently starting manager QThreads could reorder
    selected-first/strip-order priority. Submission now occurs in the GUI's
    ordered queue; heavy processing still runs in spawn processes.

14. B81 (§§156/157): the custom mouseMove drag left Qt's own pressed index/
    DraggingState armed. Later mouse movement could start Qt's unoverridden
    default drag and its source-row removal, after the custom drop already
    moved the row. A separate mutable ID/order array then addressed the wrong
    item or a nonexistent one. The regression reproduces that pre-fix state.
    One Qt startDrag override, UUID-only MIME, one model move, model-derived
    order, and UUID-addressed content updates repair the ownership; no repaint
    patches or missing-item suppression. Duplicate persisted ordering is also
    normalized so it cannot instantiate the same UUID twice.

Historical TODO entries are implementation history, not current acceptance.
TODO §122 correctly remained OPEN, but surrounding documents contradicted
that status by describing a completed single path. Its stated open design
questions were settled by §127 and reiterated by §149; do not ask again.

Historical implementation/verification for §§149–162 is tracked by TODO
§§150–162 and issues
B74–B81. The original 124-test flow/identity suite, real lifecycle GUI smoke, and native
drag gestures at 100%/200% passed, with captures actually viewed. The B81
extension brought the suite to 131 tests and checks eight native
gestures plus 33 post-reorder clicks at each scale. B81 is explicitly
designer-confirmed on 2026-10-14 (§159); B74–B80 remain unconfirmed.
The new mini-padding/background issues B82/B83 are tracked separately;
their three regression cases brought the suite to 134 tests. §§160–162 add
16 selection/revert regressions for a then-total of 150. The real modal
tests include mouse, keyboard and post-reorder cancellation, both visible and
current selection, repeated attempts with one prompt each, retained drafts/
files, and revert before/during/after processing without new work.

Latest integration (§§203–205, 2026-10-15): six image modes and independent
native-stream policy use these same saved/draft transactions and shared
300ms timer. Effective keys ignore inactive fields; Save As persists the
draft's actual mode/policy and selects the new copy, and built-in override
reload restores the saved mode. Seven new lifecycle cases are included in
the final **429 passed** suite; real-file modal smoke and both-scale captures
were viewed. See `TEST_PLAN.md`, `COMPRESSION.md` and
`NATIVE_STREAM_COMPRESSION.md`. B105/B106 remain unconfirmed.
The separate native callback cancellation/serialization defect observed on
shutdown is B107 OPEN; it is not certified repaired by these tests.
