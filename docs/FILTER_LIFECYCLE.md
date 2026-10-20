# Filter recipes, live drafts, and real filtered files — canon (§§122/149)

The designer's full ruling is preserved verbatim in `DESIGNER_VERBATIM.md`
§149. Cross-refs: `ARCHITECTURE.md`,
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
(§§172–175). Native geometry redraw is
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

The common Quality control (§272) stores `jpeg_q` for JPEG and `jpx_q` for
JPEG2000, default 75, with a versioned saved-filter migration that also
upgrades revision 1 stores.
Quality edits use this same transaction and timer. Lossless JPX ignores its
retained inactive quality. Keep explicit legacy ratio recipes distinct from
quality in effective keys; see [LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md).
The JPEG and JPEG2000 encoder profiles and the JPEG2000 quality mapping are
versioned in effective keys. Saved q values remain unchanged; a changed encoding policy
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
dropdown with tooltip "Revert Changes", using the standard `document-revert`
theme/Breeze icon (§197), not history Undo. Enable it only
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

## Related rulings

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

## Editable compression (§§203–205)

Six image modes and the independent native-stream policy use these same
saved/draft transactions and the shared 300ms timer. Effective keys ignore inactive fields; Save As persists the
draft's actual mode/policy and selects the new copy, and built-in override
reload restores the saved mode. See `COMPRESSION.md` and
`NATIVE_STREAM_COMPRESSION.md`.
