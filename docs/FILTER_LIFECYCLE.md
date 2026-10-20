# Filter recipes, live drafts and real filtered files

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

### One processing path

**§122** (2026-10-13)

```text
The preview need to show the saved file, DO NOT have multiple paths, this is the root cause of alot of your failures!! One single path, process the file, save temp, display temp file in preview, minis come from save temp files once they are processed. This is an important design ruling, please put this in the design under architecture and flow. Do you follow this flow? Do you understand why this is robust and safe?
```

**§44** (2026-10-10)

```text
when I was clicking on a filter preview, it seemed to be restarting it processing, but that is incorrect, it should be processed once and only reprocessed if there is a change of the file or change in the filter specifications.
```

**§149** (2026-10-13)

```text
Ok, this renumbering issue seems resolved, you can document my explicit confirmation.  Next issue, this also seems like a design implementation issue, please find the root cause.  Canon design is that all filters be run for real and the previews come from the filtered files, and these files have the true final size, not an approximation, please make sure this is clear canon design ruling in the proper dev docs.  When I zoom in/out, the preview and minis update live, this is good.  However, when I click on a mini that has not been clicked yet, I see it doing a "Rendering preview..." processing.  This is obviously wrong flow because this is already fully processed to have the mini previews that work.  So something is fundamentally wrong.  There should be no reprocessing EXCEPT for changes to the filter.  And there are two types of changes to the filter, the first is live changes which should update the processing live with a debounce and mark the filter as changed with a star * (per standard GUI conventions, right?).  However, if the chosen filter is changed without saving, there should be a popup for discard/save/save-as (aka save copy, choose best modern term).  If discard, then the previous file is kept (and the temp new live changes file is deleted), inverse if save, save-as keeps both of course.  These are multiple design runlings, please document in the correct places, also document the issues and work on them.
```

### Filter identity

**§155** (2026-10-13)

```text
you should give the filter a UUID and never permit two filters to have the same UUID, check when loading, in case someone copy/paste filters.  These UUIDs are only for internal use, name tis dirs with the UUID.  I think this is modern best practices, no?  Python has UUID generation, not tied to the network card?  Or just make a random UUID generator, if python does not have.
```

### Edits and leaving a dirty filter

**§183** (2026-10-14)

```text
In the low color versions, colors are getting incorrectly converted to white instead of their closest colors. Also, when using the spinner, after a debounce, a rerender should be triggered, same for the sliders or any other change.  We should have one global debouce for this.  What do you suggest as a debounce time?
```

**§160** (2026-10-14)

```text
Change "Close without saving" to "Discard Changes"
```

**§161** (2026-10-14)

```text
Also, after clicking another filter in the minis, if I escape the "Unsaved filter changes", the filter selection changed, but nothing was saved, nor discarded, this is wrong.  Cancel should remain on the edited fiter.
```

**§162** (2026-10-14)

```text
Also, add a revert changes igon beside the dropdown, the typical counter-clockwise arrow, right?
```

**§189** (2026-10-14)

```text
I just did a change, then click mini elsewhere, then save as, but the selection did not move to the new sav-as filter, this is incorrect.   Modern GUI design would expect this.  Review anywhere this pattern would apply.  Also, I think the all just crashed, or you killed it?
```

Related pages: `ARCHITECTURE.md`, `UI_LAYOUT.md`, `PERSISTENCE_AND_TEMP.md`.

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

Each filter keeps a saved recipe/result and, while dirty, a live draft.
Loading controls under signal blockers is not an edit. Effective comparisons
exclude irrelevant disabled controls and normalize defaults, so selection
cannot accidentally change threshold/DPI/lossless or other recipes.

User edits create/update the selected filter's draft immediately, show `*`
in its mini/dropdown/header, and restart ONE shared single-shot 300ms trailing
debounce (§183; 300ms is the proposed value). All recipe inputs feed the
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

Selecting another filter while the current one is dirty shows a modal
decision before the active recipe, controls or preview change (§149):

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

## Design traps and failed attempts

- **A second processing path.** Separate preview, mini or size calculations
  disagreed with the saved file. Everything reads the one saved PDF
  (§§122/149).
- **One timer for view events and edits.** Zoom and resize then interfered
  with edits or authorized processing. The view reframe debounce stays
  separate from the edit debounce.
- **Rolling back a canceled switch inside Qt's selection signals.** Unfinished
  Qt work overwrote the restored highlight or reopened the prompt (§161). Run
  the native input handler with view notifications blocked and notify once.
- **Save As selecting the filter that triggered the prompt.** The new copy must
  become the selected filter everywhere (§189).
