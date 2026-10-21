"""Real filtered PDFs, prepared disk-backed pages, and safe ownership (§149).

No independent filter previews or estimates. Each worker runs the real saver
once, then observes its output. GUI selection displays that same immutable PDF;
native geometry redraw at device resolution never reprocesses a filter.
"""

from dataclasses import dataclass, field
import logging
import os
from pathlib import Path
import hashlib

import numpy as np
from PySide6.QtCore import QLockFile, QThread, Signal

from ..core.cancel import CancelToken
from ..core.pdf_io import CancelledError
from ..core.recipes import spec_key
from ..core.identity import canonical_uuid
from .jobs import pool, PREVIEW_DPI

log = logging.getLogger("pdf_minify")


@dataclass
class FilterArtifact:
    directory: str
    pdf_path: str
    nbytes: int
    page_paths: list[str]
    mini_paths: list[str] = field(default_factory=list)
    _pages: list | None = field(default=None, repr=False)
    _minis: list | None = field(default=None, repr=False)

    @property
    def pages(self):
        if self._pages is None:
            self._pages = [np.load(path, mmap_mode="r", allow_pickle=False)
                           for path in self.page_paths]
        return self._pages

    def close_pages(self):
        if self._pages is not None:
            for page in self._pages:
                page._mmap.close()
            self._pages = None
        if self._minis is not None:
            for page in self._minis:
                page._mmap.close()
            self._minis = None

    @property
    def mini_pages(self):
        if not self.mini_paths:
            return self.pages
        if self._minis is None:
            self._minis = [np.load(path, mmap_mode="r", allow_pickle=False)
                           for path in self.mini_paths]
        return self._minis


class _FileCancelToken(CancelToken):
    def __init__(self, path):
        super().__init__()
        self.path = path

    @property
    def cancelled(self):
        return super().cancelled or os.path.exists(self.path)


def build_artifact(input_path: str, spec: dict, directory: str) -> FilterArtifact:
    """Spawn-process task: save the PDF, measure it, render THAT PDF once."""
    import pymupdf as fitz
    from ..core.pipeline import save_with_spec
    from ..core.display import render_display_page

    root = Path(directory)
    token = _FileCancelToken(str(root / "cancel"))
    progress_path = root / "progress"

    def progress(value):
        progress_path.write_text(str(value), encoding="ascii")

    partial, output = root / "filtered.partial.pdf", root / "filtered.pdf"
    save_with_spec(input_path, str(partial), spec, token,
                   lambda done, total: progress(0.85 * done / max(1, total)),
                   workdir=directory)
    if token.cancelled:
        raise CancelledError()
    os.replace(partial, output)
    progress(0.85)
    page_paths, mini_paths = [], []
    fitz.TOOLS.mupdf_warnings()  # clear expected saver fallback diagnostics
    with fitz.open(output) as doc:
        for i, page in enumerate(doc):
            if token.cancelled:
                raise CancelledError()
            pix = render_display_page(page, dpi=PREVIEW_DPI)
            warnings = fitz.TOOLS.mupdf_warnings()
            if any(marker in warnings.lower() for marker in (
                    "jpeg error", "jpx header", "zlib error", "cannot complete jbig2")):
                raise ValueError(f"Saved PDF image readback failed: {warnings}")
            arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, 3)
            path = root / f"page-{i}.npy"
            np.save(path, arr, allow_pickle=False)
            page_paths.append(str(path))
            # A view-scale derivative of these exact saved-file pixels, not
            # a second filter or PDF-processing path. Keeps pan/zoom responsive.
            from PIL import Image
            mini = Image.fromarray(arr)
            mini.thumbnail((200, 300), Image.Resampling.NEAREST)
            mini_path = root / f"page-{i}-mini.npy"
            np.save(mini_path, np.asarray(mini), allow_pickle=False)
            mini_paths.append(str(mini_path))
            progress(0.85 + 0.15 * (i + 1) / max(1, doc.page_count))
    return FilterArtifact(str(root), str(output), os.path.getsize(output), page_paths, mini_paths)


def copy_artifact(source: FilterArtifact, directory: str) -> FilterArtifact:
    """Materialize immutable prepared files for a new UUID, never filter again.

    Runs in a worker process. Hard links give independent owned paths on the
    same filesystem; unsupported filesystems use a cancellable byte copy.
    """
    root = Path(directory)
    token = _FileCancelToken(str(root / "cancel"))
    files = [source.pdf_path, *source.page_paths, *source.mini_paths]
    for i, path in enumerate(files):
        if token.cancelled:
            raise CancelledError()
        target = root / Path(path).name
        try:
            os.link(path, target)
        except OSError:
            with open(path, "rb") as src, open(target, "xb") as dst:
                while True:
                    if token.cancelled:
                        raise CancelledError()
                    block = src.read(1024 * 1024)
                    if not block:
                        break
                    dst.write(block)
        (root / "progress").write_text(str((i + 1) / len(files)), encoding="ascii")
    return FilterArtifact(str(root), str(root / "filtered.pdf"), source.nbytes,
                          [str(root / Path(p).name) for p in source.page_paths],
                          [str(root / Path(p).name) for p in source.mini_paths])


class ArtifactWorker(QThread):
    ready = Signal(object)
    failed = Signal(str)
    progressed = Signal(float)

    def __init__(self, input_path, spec, directory, executor, source=None):
        super().__init__()
        self.input_path, self.spec = input_path, dict(spec)
        self.directory, self.executor = directory, executor
        self.token = CancelToken()
        self.is_copy = source is not None
        # Submit from the GUI's ordered queue, not racing manager threads.
        # The computation still runs in a spawn process. This guarantees
        # selected-first / strip-order priority (§§51/128).
        from concurrent.futures import Future
        try:
            if source is None:
                self.future = executor.submit(build_artifact, input_path, self.spec, directory)
            else:
                # Never pickle cached arrays/memmaps; only immutable file paths.
                descriptor = FilterArtifact(source.directory, source.pdf_path,
                                            source.nbytes, source.page_paths, source.mini_paths)
                self.future = executor.submit(copy_artifact, descriptor, directory)
        except Exception as exc:
            self.future = Future()
            self.future.set_exception(exc)

    def cancel(self):
        self.token.cancel()
        Path(self.directory, "cancel").touch()
        if self.future is not None:
            self.future.cancel()

    def run(self):
        from concurrent.futures import CancelledError as FutureCancelled, TimeoutError
        try:
            while True:
                try:
                    result = self.future.result(timeout=0.1)
                    self.ready.emit(result)
                    return
                except TimeoutError:
                    try:
                        value = float(Path(self.directory, "progress").read_text(encoding="ascii"))
                        self.progressed.emit(min(1.0, max(0.0, value)))
                    except (OSError, ValueError):
                        pass
        except (CancelledError, FutureCancelled):
            self.failed.emit("Cancelled")
        except Exception as exc:  # worker failures are visible, never silent
            log.exception("filter artifact failed: %s", self.spec)
            self.failed.emit(str(exc))


class ArtifactStore:
    """PID-owned results, addressed by filter UUID and immutable input/recipe.

    The caller supplies all saved/draft/export references. Releasing ownership
    retires only unreferenced results; an in-flight result is removed AFTER the
    worker finishes. Copies hold their source until their own files are ready.
    No session-history layer, broad deletion, or input-file mutation.
    """

    def __init__(self, root: str):
        process_root = Path(root) / str(os.getpid())
        process_root.mkdir(parents=True, exist_ok=True)
        self.root = str(process_root)
        self._process_lock = QLockFile(str(process_root / ".process.lock"))
        self._process_lock.setStaleLockTime(0)
        if not self._process_lock.tryLock(0):
            raise RuntimeError("The PID artifact directory is already owned")
        self.results: dict = {}
        self.pending: dict = {}
        self.directories: dict = {}
        self.errors: dict = {}
        self.retired: set = set()
        self.copy_sources: dict = {}

    @staticmethod
    def key(file_key, spec, filter_uuid):
        uid = canonical_uuid(filter_uuid)
        if uid is None:
            raise ValueError("Filter identity must be a valid UUIDv4")
        return (uid, file_key, spec_key(spec))

    def _allocate(self, key):
        owner = Path(self.root) / key[0]
        digest = hashlib.sha256(repr(key[1:]).encode("utf-8")).hexdigest()
        directory = owner / digest
        if directory.exists():
            # A dead PID's exact regenerable artifact, never trusted as cache.
            self.directories[key] = str(directory)
            self._remove(key)
            if directory.exists():
                raise RuntimeError("Cannot safely reclaim the stale artifact directory")
        directory.mkdir(parents=True)
        self.directories[key] = str(directory)
        return str(directory)

    def copy_from(self, source_key, target_key):
        if source_key[1:] != target_key[1:]:
            raise ValueError("A filter copy must retain its input and recipe")
        if source_key == target_key:
            raise ValueError("A filter copy must have a different UUID")
        self.copy_sources[target_key] = source_key

    def start_copy(self, key, executor=None):
        if key in self.results or key in self.pending or key in self.errors:
            return None
        source = self.results.get(self.copy_sources.get(key))
        if source is None:
            return None  # wait for the already-running real recipe, not another save
        directory = self._allocate(key)
        worker = ArtifactWorker("", {}, directory, executor or pool(), source)
        self.pending[key] = worker
        return worker

    def start(self, key, path, spec, executor=None):
        if key in self.results or key in self.pending or key in self.errors:
            return None
        if key in self.copy_sources:
            return self.start_copy(key, executor)
        directory = self._allocate(key)
        worker = ArtifactWorker(path, spec, directory, executor or pool())
        self.pending[key] = worker
        return worker

    def complete(self, key, result):
        if key in self.retired:
            result.close_pages()
            return False
        self.results[key] = result
        self.errors.pop(key, None)
        self.copy_sources.pop(key, None)
        return True

    def fail(self, key, message):
        self.errors[key] = message
        for target, source in list(self.copy_sources.items()):
            if source == key:
                self.fail(target, message)

    def finish(self, key):
        self.pending.pop(key, None)
        if key in self.retired:
            self._remove(key)

    def retain(self, wanted):
        wanted = set(wanted)
        # Retain sources transitively while a wanted copy is queued/running.
        frontier = wanted | (self.pending.keys() & self.copy_sources.keys())
        visited = set()
        while frontier:
            visited.update(frontier)
            sources = {source for target, source in self.copy_sources.items()
                       if target in frontier}
            wanted.update(sources)
            frontier = sources - visited
        for target in list(self.copy_sources):
            if target not in wanted and target not in self.pending:
                self.copy_sources.pop(target, None)
        for key in wanted:
            self.retired.discard(key)
        for key in set(self.directories) - wanted:
            self.retired.add(key)
            worker = self.pending.get(key)
            if worker is None:
                self._remove(key)

    def _remove(self, key):
        artifact = self.results.pop(key, None)
        if artifact is not None:
            artifact.close_pages()
        directory = self.directories.get(key)
        if directory is None:
            return
        # Exact registered recipe directory under its canonical filter UUID.
        owner = Path(directory).parent
        if owner.parent != Path(self.root) or owner.name != key[0]:
            raise ValueError("Refusing cleanup outside the owned PID/filter")
        for entry in Path(directory).iterdir():
            if entry.is_file() and (entry.name in (
                    "filtered.pdf", "filtered.partial.pdf", "cancel", "progress")
                    or entry.name.startswith("encode-")
                    or (entry.name.startswith("page-") and entry.suffix == ".npy")):
                entry.unlink(missing_ok=True)
        try:
            Path(directory).rmdir()
        except OSError:
            log.warning("artifact directory could not be retired: %s", directory)
            return
        self.directories.pop(key, None)
        self.errors.pop(key, None)
        self.retired.discard(key)
        try:
            owner.rmdir()  # only if no saved/live recipe still owns a child
        except OSError:
            pass

    def close(self):
        if self.pending:
            raise RuntimeError("Cannot retire a process directory while its workers are active")
        self.retain(set())
        self._process_lock.unlock()
        try:
            Path(self.root).rmdir()  # empty, exact owned PID directory only
        except OSError:
            pass
