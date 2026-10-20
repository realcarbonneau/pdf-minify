# Persistence vs temp work dirs

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

### Temp and developer files

**§123** (2026-10-13)

```text
The temp dir for the app should be the standard temp dir for the os, for linux it's /tmp/ I think, but the framework (qt?) should be able to provide this information, right? It would be different per OS, and this is what I want. Please review and do your research and correct. This is also a design ruling and an issue, please document accordingly. Also, make a persistence and temp work dir docs and cross reference accordingly.
```

**§152** (2026-10-13)

```text
So the temp dir should be in a dir with the process id number?  Is this possible?
```

**§153** (2026-10-13)

```text
Why keep all sessions?  That is not what I asked for, also, two live applications cannot share a PID, or yes?  Why did you invent something beyond my request and design ruling?
```

**§15** (2026-10-09)

```text
don't go outside the local dir, make a local ./.tmp/ and gitignore it.
```

### Saved settings

**§91** (2026-10-10)

```text
Also, the app should remember the last opened file.
```

**§155** (2026-10-13)

```text
you should give the filter a UUID and never permit two filters to have the same UUID, check when loading, in case someone copy/paste filters.  These UUIDs are only for internal use, name tis dirs with the UUID.  I think this is modern best practices, no?  Python has UUID generation, not tied to the network card?  Or just make a random UUID generator, if python does not have.
```

**§226** (2026-10-15, selected option)

```text
Change all saved filters to 300 DPI
```

**§230** (2026-10-16)

```text
Also, rename this project to "PDF Minify", rename anything in the repo and I will rename the repo itself later.  Also, why is there a dir that restates pdf_minimalist, why not app, source, code, or something like that?
```

Two buckets, never mixed. Temp is disposable and regenerable; persistence is
user data that must survive restarts. Related pages: `ARCHITECTURE.md`
(single-path flow) and `FILTER_LIFECYCLE.md` (saved/live filter ownership).

## Temp — OS standard temp dir via Qt (designer ruling §123)

- Source of truth: `QStandardPaths.writableLocation(QStandardPaths.TempLocation)`
  → `/tmp` on Linux, `GetTempPath` on Windows, `$TMPDIR` on macOS.
  Central helper: `pdf_minify/ui_qt/paths.py: app_temp_dir(*parts)`
  (stdlib-`tempfile` fallback if Qt ever reports nothing).
- Layout: `<os-temp>/pdf-minify/` — private
  `saves/<GUI-PID>/<filter-UUID>/<artifact-key>/filtered.pdf` directories with prepared page buffers
  (single-path saver temps, §122), plus the app log
  (`<os-temp>/pdf-minify/pdf-minify.log`, written by `run.sh`).
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

## Persistence — Qt QSettings platform locations

- What persists: last opened file (§91), custom/renamed/copied/saved
  filter presets (§§109/112), window prefs. These are user data, not
  regenerable — they live where each OS keeps app config (e.g.
  `~/.config` on Linux), managed by `QSettings("pdf-minify",
  "pdf-minify")`. Tests isolate it via `XDG_CONFIG_HOME` (B23).
- Rule: recipe persistence is written only on explicit user action (open file,
  save/copy/rename filter), never as a side effect of background work. Internal
  UUID/schema repairs on load (§155) are identity migration, not recipe edits;
  they do not set `*` or restart filtering.
- Versioned recipe migrations (`core/filter_defaults.py`) each run once,
  gated by a revision marker in the same settings store, inside
  `_apply_custom_presets` before saved specs and artifact keys are built:
  - 300 DPI for every saved raster recipe, including explicit DPI values
    (§226, `rasterDefaultsRevision = 1`);
  - Best as every app filter's stream policy (§257, `streamDefaultsRevision = 1`);
  - Quality 75 for JPEG and JPEG2000, replacing an old JPEG2000 ratio (§272,
    `qualityDefaultsRevision = 2`).

  Each keeps UUIDs, names, order, codecs and other parameters, and persists
  `customPresets` with its marker. A malformed marker is treated as unmigrated
  without hiding valid custom records. Later deliberate edits are saved
  normally and are not reset on later launches. Tests and screenshot tools use
  isolated settings.

### Application-name migration (§230)

PDF Minify uses `QSettings("pdf-minify", "pdf-minify")` through the shared
`ui_qt/settings.py` factory, both for initial last-file lookup and every
subsequent settings access. On first use, copy keys from the former
`QSettings("pdf-minimalist", "pdf-minimalist")` user store, keeping Qt value
types and preserving any key already in the destination. The old store is
read-only for this migration. A persisted `identityMigrationRevision` marker
makes it one-time, including when the old store is empty; later removals or
edits in the new store must not be undone by another legacy import. Failed
settings synchronization must be reported, not marked successful.

This is independent of the UUID repairs and the recipe migrations above;
their markers and all filter data travel with the settings. Runtime temps
and logs move to `<os-temp>/pdf-minify/`; there is no migration/deletion of
legacy scratch directories or saved output PDFs. Review tools read raw
settings without triggering migration, copy them into isolated review stores,
then run the application factory only inside that isolated location.

## Deliberately NOT in OS temp — repo `./.tmp/` (gitignored)

Dev-tool review outputs, not app scratch: offscreen screenshots
(`tools/shot.py`), benchmark evidence (Markdown and JSON), demo PDFs
(`tools/make_demo.py` — explicitly never `/tmp`, so review files stay
findable next to the project). The app itself writes nothing here.

## Design traps and failed attempts

- **Inventing retention.** A session-history layer kept every run's files,
  which was never asked for (§153). There is one PID directory per GUI process,
  removed on normal exit.
- **`setdefault` for test settings isolation (B23).** The shell may already
  export `XDG_CONFIG_HOME`, so tests set it explicitly; otherwise they write
  the designer's real settings.
