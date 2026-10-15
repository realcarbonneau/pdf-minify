# Persistence vs temp work dirs (designer §123)

Two buckets, never mixed. Temp is disposable and regenerable; persistence is
user data that must survive restarts. Cross-refs: `ARCHITECTURE.md`
(single-path flow), `DESIGN.md` (behavior), `issues.md` B54, `TODO.md` 123.
Saved/live filter ownership is canon in `FILTER_LIFECYCLE.md` (§149).

## Temp — OS standard temp dir via Qt (designer ruling §123)

- Source of truth: `QStandardPaths.writableLocation(QStandardPaths.TempLocation)`
  → `/tmp` on Linux, `GetTempPath` on Windows, `$TMPDIR` on macOS.
  Central helper: `pdf_minimalist/ui_qt/paths.py: app_temp_dir(*parts)`
  (stdlib-`tempfile` fallback if Qt ever reports nothing).
- Layout: `<os-temp>/pdf-minimalist/` — private
  `saves/<GUI-PID>/<filter-UUID>/<artifact-key>/filtered.pdf` directories with prepared page buffers
  (single-path saver temps, §122), plus the app log
  (`<os-temp>/pdf-minimalist/pdf-minimalist.log`, written by `run.sh`).
- Lifecycle: swept once at startup (`sweep_stale_temps`, default >48h) —
  nothing of value is lost because every temp regenerates from
  (input file + spec). A crashed worker leaves at most an orphan temp,
  never a corrupt document. Temps are keyed, never trusted blindly:
  the process store maps (owning UUID + file identity + full effective spec) to one result;
  filter names, selection, and view state are not identity inputs.
- `core/` stays Qt-free: the GUI passes its private filter directory as
  `save_with_spec(..., workdir=...)`; JBIG2/Zopfli encoder intermediates and
  anonymous disk-backed full-color composition scratch stay there too.
  The RGBX scratch is mapped without a whole-source copy, closed/unlinked
  on success/failure/cancellation, and is not another session/history file.
  Standalone headless calls fall back to stdlib OS temp.
- Each GUI process owns its own artifact directory: completed filtered PDFs
  and disk-backed prepared page buffers are kept together. Their exact PDF
  byte size is the amount shown; PDF export copies those bytes unchanged.
- A live edit retains the old saved artifact. Discard deletes only unreferenced
  draft files; Save deletes only unreferenced obsolete saved files; Save As…
  retains both. Never remove shared files or files still used by workers/export.
  Retired pending jobs cannot publish stale output; cleanup occurs when their
  users have finished. Cleanup is scoped to explicit process-owned paths, not
  the whole OS temp tree. Input files are never deletion targets.

Runtime ownership (§§152/153, B78): one numeric directory identifies the owning
GUI process. There is no additional session directory or session-history store;
two live processes in the same PID namespace cannot share a PID. The process
holds a Qt `QLockFile` in that directory until all workers/exporters finish,
then removes its generated files and empty PID directory on normal exit.
Startup sweeping skips locked/live processes and does not remove fresh empty
directories. Only expired, unlocked disposable data left by a crash is eligible.
Qt recommends disabling age-based stale
lock detection for long-held resources
([QLockFile](https://doc.qt.io/qt-6/qlockfile.html)); process-liveness checks remain.

Filter identity (§§154/155): each filter has a persistent internal UUID,
separate from its editable name and position-dependent number. Generate it
with Python's `uuid.uuid4()`, which is random, not network-card based
([Python UUID documentation](https://docs.python.org/3/library/uuid.html#uuid.uuid4)).
Validate and canonicalize all UUIDs on loading; keep the first occurrence
and assign fresh unique UUIDs to missing, invalid, or duplicated entries.
Persist identity repairs so the next load retains them. Legacy slug `id`
values are compatibility aliases, not artifact directory names. Pasted
records with duplicate aliases must not silently overwrite another copy.

Use the UUID as the filter-directory name under the PID. Immutable artifacts
for (input-file identity + effective recipe) coexist inside that directory;
their key-named child folders allow saved/live results and pending edits to
remain separate. Only referenced results are retained, not an edit history.
Rename/reorder never change the UUID, paths, or recipe. Save As assigns a new
UUID and materializes its own files from the existing output/buffers, without
filtering again; it retains the original filter's saved files. File copying
runs in background (hard links for immutable files where supported, copying
otherwise). Pending copies retain their source until completed safely.

## Persistence — Qt QSettings platform locations (unchanged)

- What persists: last opened file (§91), custom/renamed/copied/saved
  filter presets (§§109/112), window prefs. These are user data, not
  regenerable — they live where each OS keeps app config (e.g.
  `~/.config` on Linux), managed by `QSettings("pdf-minimalist",
  "pdf-minimalist")`. Tests isolate it via `XDG_CONFIG_HOME` (B23).
- Rule: recipe persistence is written only on explicit user action (open file,
  save/copy/rename filter), never as a side effect of background work. Internal
  UUID/schema repairs on load (§155) are identity migration, not recipe edits;
  they do not set `*` or restart filtering.

## Deliberately NOT in OS temp — repo `./.tmp/` (gitignored)

Dev-tool review outputs, not app scratch: offscreen screenshots
(`tools/shot.py`), benchmark CSVs (`tools/bench_*.py`), demo PDFs
(`tools/make_demo.py` — explicitly never `/tmp`, so review files stay
findable next to the project). The app itself writes nothing here.
