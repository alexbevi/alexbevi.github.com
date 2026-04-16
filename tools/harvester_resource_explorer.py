#!/usr/bin/env python3

from __future__ import annotations

import argparse
import dataclasses
import io
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import textwrap
import threading
import wave
from pathlib import Path, PurePosixPath

try:
    from PIL import Image

    PIL_AVAILABLE = True
    PIL_IMPORT_ERROR: Exception | None = None
except ModuleNotFoundError as exc:
    Image = None
    PIL_AVAILABLE = False
    PIL_IMPORT_ERROR = exc

try:
    from tkinter import filedialog, messagebox, ttk
    import tkinter as tk
    if PIL_AVAILABLE:
        from PIL import ImageTk
    else:
        ImageTk = None

    TK_AVAILABLE = True
    TK_IMPORT_ERROR: Exception | None = None
except ModuleNotFoundError as exc:
    filedialog = None
    messagebox = None
    ttk = None
    tk = None
    ImageTk = None
    TK_AVAILABLE = False
    TK_IMPORT_ERROR = exc


ARCHIVE_SET_TO_DATA_NAME = {
    1: "HARVEST.DAT",
    2: "SOUND.DAT",
    3: "HARVEST2.DAT",
}

INDEX_RECORD_SIZE = 0x94
INDEX_SIGNATURE = b"XFLE"
LOOSE_SUFFIXES = {".abm", ".bm", ".cmp", ".fst", ".idx", ".pal", ".scr", ".wav"}
IMAGE_SUFFIXES = {".abm", ".bm", ".fst", ".pal"}
SEARCHABLE_COLUMNS = ("source", "path", "type", "size")
INDEX_NAME_RE = re.compile(r"^(?P<prefix>\d+)?INDEX\.(?P<set>00[1-3])$", re.IGNORECASE)

DEFAULT_DATA_ROOT_CANDIDATES = [
    Path("/Users/alex/Downloads/Harvester_1996/HARVEST/iso/Harvester"),
    Path("/Users/alex/Downloads/Harvester_1996/HARVEST/1"),
]

HARVESTER_IMA_INDEX_ADJUST = (
    -1, -1, -1, -1, 2, 4, 6, 8,
    -1, -1, -1, -1, 2, 4, 6, 8,
)

HARVESTER_IMA_STEP_TABLE = (
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
    19, 21, 23, 25, 28, 31, 34, 37, 41, 45,
    50, 55, 60, 66, 73, 80, 88, 97, 107, 118,
    130, 143, 157, 173, 190, 209, 230, 253, 279, 307,
    337, 371, 408, 449, 494, 544, 598, 658, 724, 796,
    876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066,
    2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358,
    5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899,
    15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794, 32767,
)


def discover_default_data_root() -> Path:
    for candidate in DEFAULT_DATA_ROOT_CANDIDATES:
        if candidate.exists():
            return candidate
    return Path.cwd()


def normalize_harvester_path(path: str, *, strip_drive: bool = False) -> str:
    normalized = path.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.lstrip("/")
    match = re.match(r"^(?P<drive>\d):/", normalized)
    if match:
        normalized = normalized[match.end():] if strip_drive else f"{match.group('drive')}:/" + normalized[match.end():]
    return normalized.lower()


def make_grayscale_palette() -> bytes:
    return bytes(channel for value in range(256) for channel in (value, value, value))


def fit_image(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    if max_width <= 1 or max_height <= 1:
        return image
    scale = min(max_width / image.width, max_height / image.height)
    if scale <= 0:
        return image
    if scale >= 1:
        scale = int(scale)
        if scale > 1:
            return image.resize((image.width * scale, image.height * scale), Image.NEAREST)
        return image
    new_width = max(1, int(image.width * scale))
    new_height = max(1, int(image.height * scale))
    return image.resize((new_width, new_height), Image.NEAREST)


def format_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f}{unit}" if unit != "B" else f"{int(value)}B"
        value /= 1024
    return f"{size}B"


def format_hex_preview(data: bytes, limit: int = 256) -> str:
    lines = []
    sample = data[:limit]
    for offset in range(0, len(sample), 16):
        chunk = sample[offset:offset + 16]
        hex_part = " ".join(f"{byte:02x}" for byte in chunk)
        ascii_part = "".join(chr(byte) if 32 <= byte < 127 else "." for byte in chunk)
        lines.append(f"{offset:04x}  {hex_part:<47}  {ascii_part}")
    if len(data) > limit:
        lines.append("...")
    return "\n".join(lines)


def expand_6bit_color(value: int) -> int:
    return (value * 255 + 31) // 63


def convert_vga_palette(source: bytes) -> bytes:
    return bytes(expand_6bit_color(value) for value in source[:768])


def decode_archive_packed(payload: bytes, unpacked_size: int) -> bytes:
    output = bytearray()
    src = 0
    while src < len(payload) and len(output) < unpacked_size:
        control = payload[src]
        src += 1
        if control < 0x81:
            literal_count = min(control, len(payload) - src, unpacked_size - len(output))
            output.extend(payload[src:src + literal_count])
            src += literal_count
        else:
            if src >= len(payload):
                break
            value = payload[src]
            src += 1
            repeat_count = min(control - 0x80, unpacked_size - len(output))
            output.extend([value] * repeat_count)
    if len(output) != unpacked_size:
        raise ValueError(f"packed resource expanded to {len(output)} bytes, expected {unpacked_size}")
    return bytes(output)


def decode_harvester_fcmp(payload: bytes, bits_per_sample: int) -> bytes:
    decoded = bytearray()
    predictor = 0
    step_index = 0
    step_size = 7

    for byte in payload:
        for nibble in (byte & 0x0F, (byte >> 4) & 0x0F):
            delta = step_size >> 3
            if nibble & 4:
                delta += step_size
            if nibble & 2:
                delta += step_size >> 1
            if nibble & 1:
                delta += step_size >> 2
            if nibble & 8:
                delta = -delta

            predictor += delta
            predictor = max(-0x8000, min(0x7FFF, predictor))

            if bits_per_sample == 16:
                decoded.extend(struct.pack("<h", predictor))
            else:
                decoded.append(((predictor >> 8) & 0xFF) ^ 0x80)

            step_index += HARVESTER_IMA_INDEX_ADJUST[nibble]
            step_index = max(0, min(88, step_index))
            step_size = HARVESTER_IMA_STEP_TABLE[step_index]

    return bytes(decoded)


def apply_fcmp_warmup(decoded_pcm: bytes, *, mode: str) -> bytes:
    pcm = bytearray(decoded_pcm)
    if not pcm:
        return bytes(pcm)
    if mode == "music":
        mute = min(len(pcm), 100)
        pcm[:mute] = b"\x00" * mute
        return bytes(pcm)
    trim = min(len(pcm), 500)
    if trim == len(pcm):
        return b"\x00" * len(pcm)
    return bytes(pcm[trim:])


def decode_bm(data: bytes, palette: bytes | None) -> Image.Image:
    if len(data) < 12:
        raise ValueError("BM payload is too small")
    width, height, _reserved = struct.unpack_from("<III", data, 0)
    pixel_count = width * height
    if width == 0 or height == 0 or len(data) < 12 + pixel_count:
        raise ValueError("BM payload has invalid dimensions")
    image = Image.frombytes("P", (width, height), data[12:12 + pixel_count])
    image.putpalette((palette or make_grayscale_palette())[:768])
    return image.convert("RGBA")


def decode_pal_image(data: bytes) -> Image.Image:
    if len(data) < 768:
        raise ValueError("PAL payload is too small")
    image = Image.new("RGB", (16 * 16, 16 * 16))
    palette = data[:768]
    for index in range(256):
        color = tuple(palette[index * 3:index * 3 + 3])
        x0 = (index % 16) * 16
        y0 = (index // 16) * 16
        swatch = Image.new("RGB", (16, 16), color)
        image.paste(swatch, (x0, y0))
    return image


def decode_abm_frame(source: bytes, pixel_count: int, compressed: bool) -> bytes:
    if not compressed:
        if len(source) < pixel_count:
            raise ValueError("ABM frame payload is too small")
        return source[:pixel_count]
    output = bytearray(pixel_count)
    src_offset = 0
    dst_offset = 0
    while src_offset < len(source) and dst_offset < pixel_count:
        control = source[src_offset]
        src_offset += 1
        if (control & 0x80) == 0:
            literal_count = min(control, len(source) - src_offset, pixel_count - dst_offset)
            output[dst_offset:dst_offset + literal_count] = source[src_offset:src_offset + literal_count]
            src_offset += literal_count
            dst_offset += literal_count
        else:
            if src_offset >= len(source):
                raise ValueError("ABM frame RLE stream is truncated")
            repeat_count = min(control & 0x7F, pixel_count - dst_offset)
            output[dst_offset:dst_offset + repeat_count] = bytes([source[src_offset]]) * repeat_count
            src_offset += 1
            dst_offset += repeat_count
    if dst_offset != pixel_count:
        raise ValueError(f"ABM frame decoded to {dst_offset} bytes, expected {pixel_count}")
    return bytes(output)


def decode_abm(data: bytes, palette: bytes | None) -> tuple[list[Image.Image], dict[str, int]]:
    if len(data) < 8:
        raise ValueError("ABM payload is too small")
    frame_count = struct.unpack_from("<I", data, 0)[0]
    offset = 8
    raw_frames = []
    min_x = min_y = 10**9
    max_x = max_y = -10**9

    for _frame_index in range(frame_count):
        if len(data) < offset + 25:
            raise ValueError("ABM frame header is truncated")
        x_offset, y_offset, width, height = struct.unpack_from("<iiII", data, offset)
        compressed = data[offset + 16] != 0
        source_size = struct.unpack_from("<I", data, offset + 17)[0]
        payload_offset = offset + 25
        payload = data[payload_offset:payload_offset + source_size]
        if width == 0 or height == 0 or len(payload) < source_size:
            raise ValueError("ABM frame payload is invalid")
        pixel_count = width * height
        pixels = decode_abm_frame(payload, pixel_count, compressed)
        raw_frames.append((x_offset, y_offset, width, height, pixels))
        min_x = min(min_x, x_offset)
        min_y = min(min_y, y_offset)
        max_x = max(max_x, x_offset + width)
        max_y = max(max_y, y_offset + height)
        offset = payload_offset + source_size

    min_x = min(0, min_x)
    min_y = min(0, min_y)
    canvas_width = max_x - min_x
    canvas_height = max_y - min_y
    palette_bytes = (palette or make_grayscale_palette())[:768]

    frames = []
    for x_offset, y_offset, width, height, pixels in raw_frames:
        indexed = Image.frombytes("P", (width, height), pixels)
        indexed.putpalette(palette_bytes)
        rgba = indexed.convert("RGBA")
        mask = indexed.point(lambda value: 0 if value == 0 else 255, "L")
        frame = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
        frame.paste(rgba, (x_offset - min_x, y_offset - min_y), mask)
        frames.append(frame)

    meta = {
        "frame_count": frame_count,
        "width": canvas_width,
        "height": canvas_height,
    }
    return frames, meta


class FstBitReader:
    def __init__(self, data: bytes, bit_count: int) -> None:
        self._data = data
        self._bit_count = bit_count
        self._bit_index = 0

    def read_bit(self) -> bool:
        if self._bit_index >= self._bit_count:
            return False
        byte_value = self._data[self._bit_index >> 3]
        value = (byte_value & (0x80 >> (self._bit_index & 7))) != 0
        self._bit_index += 1
        return value


def decode_fst_mask_block(dest: bytearray, pitch: int, base_offset: int, source: bytes) -> None:
    color0 = source[0]
    color1 = source[1]
    mask = struct.unpack_from("<H", source, 2)[0]
    mask_rows = (
        (mask >> 8) & 0xF0,
        (mask >> 8) & 0x0F,
        mask & 0xF0,
        mask & 0x0F,
    )
    for y in range(4):
        row_offset = base_offset + y * pitch
        row_mask = mask_rows[y]
        for x in range(4):
            bit = (1 << x) if (y & 1) else (0x10 << x)
            dest[row_offset + x] = color1 if (row_mask & bit) else color0


def parse_dialogue_idx(data: bytes) -> list[tuple[int, str]]:
    decoded = bytes(byte if byte in (0x00, 0x0A, 0x0C, 0x0D) else (byte ^ 0xAA) for byte in data)
    tokens = []
    current = bytearray()
    for byte in decoded:
        if byte in (0x00, 0x0A, 0x0C, 0x0D):
            if current:
                tokens.append(current.decode("latin1", "replace"))
                current.clear()
        else:
            current.append(byte)
    if current:
        tokens.append(current.decode("latin1", "replace"))

    entries = []
    for index in range(0, len(tokens) - 1, 2):
        wav_id_text = tokens[index].strip()
        subtitle = tokens[index + 1].strip()
        if not wav_id_text.isdigit():
            continue
        entries.append((int(wav_id_text), subtitle.strip('"')))
    return entries


def decode_xor_aa_text(data: bytes) -> str:
    decoded = bytes(byte if byte in (0x0A, 0x0D) else (byte ^ 0xAA) for byte in data)
    return decoded.decode("latin1", "replace")


@dataclasses.dataclass(frozen=True)
class ResourceEntry:
    source_kind: str
    source_label: str
    logical_path: str
    path_key: str
    path_without_drive: str
    suffix: str
    size: int
    packed_flag: int = 0
    disc: int | None = None
    set_id: int | None = None
    archive_offset: int | None = None
    stored_size: int | None = None
    unpacked_size: int | None = None
    index_path: Path | None = None
    data_path: Path | None = None
    loose_path: Path | None = None

    @property
    def filename(self) -> str:
        return PurePosixPath(self.logical_path).name

    @property
    def stem(self) -> str:
        return PurePosixPath(self.logical_path).stem

    @property
    def preview_kind(self) -> str:
        if self.filename.lower() == "dialogue.idx":
            return "dialogue_idx"
        if self.suffix == ".scr":
            return "scr"
        if self.suffix in {".abm", ".bm", ".cmp", ".fst", ".pal", ".wav"}:
            return self.suffix[1:]
        return "binary"

    def load_bytes(self) -> bytes:
        if self.loose_path is not None:
            return self.loose_path.read_bytes()
        if self.data_path is None or self.archive_offset is None or self.stored_size is None:
            raise ValueError("archive entry is missing data file information")
        with self.data_path.open("rb") as handle:
            handle.seek(self.archive_offset)
            payload = handle.read(self.stored_size)
        if len(payload) != self.stored_size:
            raise ValueError(f"short read from {self.data_path}")
        if self.packed_flag:
            return decode_archive_packed(payload, self.unpacked_size or 0)
        return payload


class HarvesterInstall:
    def __init__(self, root: Path, archive_entries: list[ResourceEntry], loose_entries: list[ResourceEntry]) -> None:
        self.root = root
        self.archive_entries = sorted(archive_entries, key=lambda entry: (entry.source_label, entry.logical_path.lower()))
        self.loose_entries = sorted(loose_entries, key=lambda entry: entry.logical_path.lower())
        self.entries = self.archive_entries + self.loose_entries
        self.palette_entries = [entry for entry in self.entries if entry.suffix == ".pal"]

        self.entries_by_key: dict[str, list[ResourceEntry]] = {}
        self.entries_by_content: dict[str, list[ResourceEntry]] = {}
        self.entries_by_filename: dict[str, list[ResourceEntry]] = {}
        for entry in self.entries:
            self.entries_by_key.setdefault(entry.path_key, []).append(entry)
            self.entries_by_content.setdefault(entry.path_without_drive, []).append(entry)
            self.entries_by_filename.setdefault(entry.filename.lower(), []).append(entry)

    @classmethod
    def discover(cls, root: Path) -> "HarvesterInstall":
        root = root.expanduser().resolve()
        if not root.exists():
            raise FileNotFoundError(root)

        archive_entries: list[ResourceEntry] = []
        candidate_dirs = [root]
        candidate_dirs.extend(child for child in sorted(root.iterdir()) if child.is_dir())

        for candidate_dir in candidate_dirs:
            dir_disc: int | None = None
            dir_match = re.match(r"^(?:cd)?(?P<disc>\d+)$", candidate_dir.name, re.IGNORECASE)
            if dir_match:
                dir_disc = int(dir_match.group("disc"))

            for child in sorted(candidate_dir.iterdir()):
                if not child.is_file():
                    continue
                match = INDEX_NAME_RE.match(child.name)
                if not match:
                    continue
                prefix = match.group("prefix") or ""
                set_id = int(match.group("set")[-1])
                data_name = prefix + ARCHIVE_SET_TO_DATA_NAME[set_id]
                data_path = candidate_dir / data_name
                if not data_path.exists():
                    continue
                disc = int(prefix) if prefix else dir_disc
                archive_entries.extend(parse_index_file(child, data_path, disc=disc, set_id=set_id))

        loose_entries: list[ResourceEntry] = []
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if INDEX_NAME_RE.match(path.name):
                continue
            if re.match(r"^\d+(HARVEST\.DAT|HARVEST2\.DAT|SOUND\.DAT)$", path.name, re.IGNORECASE):
                continue
            suffix = path.suffix.lower()
            if suffix not in LOOSE_SUFFIXES and path.name.lower() != "dialogue.idx":
                continue
            loose_entries.append(
                ResourceEntry(
                    source_kind="loose",
                    source_label="Loose",
                    logical_path=relative,
                    path_key=normalize_harvester_path(relative),
                    path_without_drive=normalize_harvester_path(relative, strip_drive=True),
                    suffix=suffix,
                    size=path.stat().st_size,
                    loose_path=path,
                )
            )

        return cls(root=root, archive_entries=archive_entries, loose_entries=loose_entries)

    def load_palette_bytes(self, entry: ResourceEntry) -> bytes:
        return entry.load_bytes()[:768]

    def get_palette_by_key(self, palette_key: str) -> ResourceEntry | None:
        if palette_key in self.entries_by_key:
            return self.entries_by_key[palette_key][0]
        if palette_key in self.entries_by_content:
            return self.entries_by_content[palette_key][0]
        return None

    def resolve_palette_entry(self, entry: ResourceEntry) -> ResourceEntry | None:
        if entry.suffix not in {".abm", ".bm"}:
            return None

        parent = PurePosixPath(entry.path_without_drive).parent.as_posix()
        stem = PurePosixPath(entry.path_without_drive).stem
        drive_match = re.match(r"^(?P<drive>\d):/", entry.logical_path.replace("\\", "/"))
        drive_prefix = f"{drive_match.group('drive')}:" if drive_match else None

        candidates: list[str] = []
        if parent and parent != ".":
            candidates.append(f"{parent}/{stem}.pal")
        candidates.append(f"graphic/pal/{stem}.pal")

        if drive_prefix:
            if parent and parent != ".":
                candidates.insert(0, f"{drive_prefix}/{parent}/{stem}.pal")
            candidates.insert(1 if parent and parent != "." else 0, f"{drive_prefix}/graphic/pal/{stem}.pal")

        for candidate in candidates:
            key = normalize_harvester_path(candidate)
            if key in self.entries_by_key:
                return self.entries_by_key[key][0]
            key = normalize_harvester_path(candidate, strip_drive=True)
            if key in self.entries_by_content:
                return self.entries_by_content[key][0]

        filename = f"{stem}.pal".lower()
        matches = self.entries_by_filename.get(filename, [])
        if matches:
            return matches[0]
        return None

    def resolve_palette(self, entry: ResourceEntry) -> bytes | None:
        palette_entry = self.resolve_palette_entry(entry)
        if palette_entry is None:
            return None
        return self.load_palette_bytes(palette_entry)


def parse_index_file(index_path: Path, data_path: Path, *, disc: int | None, set_id: int) -> list[ResourceEntry]:
    data = index_path.read_bytes()
    entries: list[ResourceEntry] = []
    for offset in range(0, len(data), INDEX_RECORD_SIZE):
        record = data[offset:offset + INDEX_RECORD_SIZE]
        if len(record) < INDEX_RECORD_SIZE or record[:4] != INDEX_SIGNATURE:
            continue
        raw_path = record[4:0x84].split(b"\x00", 1)[0].decode("latin1", "replace").strip()
        if not raw_path:
            continue
        archive_offset, stored_size, packed_flag, unpacked_size = struct.unpack_from("<IIII", record, 0x84)
        logical_path = raw_path.replace("\\", "/")
        entries.append(
            ResourceEntry(
                source_kind="archive",
                source_label=f"CD{disc} Set {set_id}" if disc is not None else f"Set {set_id}",
                logical_path=logical_path,
                path_key=normalize_harvester_path(logical_path),
                path_without_drive=normalize_harvester_path(logical_path, strip_drive=True),
                suffix=PurePosixPath(logical_path).suffix.lower(),
                size=unpacked_size if packed_flag else stored_size,
                packed_flag=packed_flag,
                disc=disc,
                set_id=set_id,
                archive_offset=archive_offset,
                stored_size=stored_size,
                unpacked_size=unpacked_size,
                index_path=index_path,
                data_path=data_path,
            )
        )
    return entries


@dataclasses.dataclass
class AudioClip:
    sample_rate: int
    bits_per_sample: int
    pcm: bytes


@dataclasses.dataclass
class FstFrameInfo:
    video_offset: int
    video_size: int
    audio_offset: int
    audio_size: int


class FstMovie:
    def __init__(
        self,
        data: bytes,
        *,
        width: int,
        height: int,
        frame_rate: int,
        sample_rate: int,
        bits_per_sample: int,
        frames: list[FstFrameInfo],
    ) -> None:
        self.data = data
        self.width = width
        self.height = height
        self.frame_rate = frame_rate
        self.sample_rate = sample_rate
        self.bits_per_sample = bits_per_sample
        self.frames = frames
        self._pixels = bytearray(width * height)
        self._palette = bytearray(256 * 3)
        self._frame_index = 0

    @classmethod
    def from_bytes(cls, data: bytes) -> "FstMovie":
        if len(data) < 32:
            raise ValueError("FST payload is too small")
        magic = struct.unpack_from("<I", data, 0)[0]
        if magic not in (0x32545346, 0x46535432):
            raise ValueError("FST magic is invalid")
        width, height, _max_frame_size, frame_count, frame_rate, sample_rate = struct.unpack_from("<IIIIII", data, 4)
        bits_per_sample, _unknown2 = struct.unpack_from("<HH", data, 28)
        if width == 0 or height == 0 or frame_count == 0 or frame_rate == 0:
            raise ValueError("FST header contains invalid dimensions")

        frame_table_offset = 32
        payload_offset = frame_table_offset + frame_count * 6
        if len(data) < payload_offset:
            raise ValueError("FST frame table is truncated")

        frames: list[FstFrameInfo] = []
        cursor = payload_offset
        for index in range(frame_count):
            video_size, audio_size = struct.unpack_from("<IH", data, frame_table_offset + index * 6)
            total = video_size + audio_size
            if len(data) < cursor + total:
                raise ValueError(f"FST frame {index} is truncated")
            frames.append(
                FstFrameInfo(
                    video_offset=cursor,
                    video_size=video_size,
                    audio_offset=cursor + video_size,
                    audio_size=audio_size,
                )
            )
            cursor += total

        return cls(
            data,
            width=width,
            height=height,
            frame_rate=frame_rate,
            sample_rate=sample_rate,
            bits_per_sample=bits_per_sample,
            frames=frames,
        )

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    def reset(self) -> None:
        self._pixels[:] = b"\x00" * len(self._pixels)
        self._palette[:] = b"\x00" * len(self._palette)
        self._frame_index = 0

    def build_audio(self) -> AudioClip | None:
        if self.sample_rate == 0 or self.bits_per_sample != 16:
            return None
        trailing_skip = self._get_trailing_audio_frame_skip()
        chunks = []
        for frame_index, frame in enumerate(self.frames):
            if frame.audio_size == 0:
                continue
            if frame_index + trailing_skip >= len(self.frames):
                continue
            chunks.append(self.data[frame.audio_offset:frame.audio_offset + frame.audio_size])
        if not chunks:
            return None
        return AudioClip(sample_rate=self.sample_rate, bits_per_sample=self.bits_per_sample, pcm=b"".join(chunks))

    def _get_trailing_audio_frame_skip(self) -> int:
        if len(self.frames) < 2:
            return 0
        first = self.frames[0].audio_size
        steady = self.frames[1].audio_size
        if first == 0 or steady == 0 or first <= steady or (first % steady) != 0:
            return 0
        skip_count = first // steady - 1
        if skip_count == 0 or skip_count >= len(self.frames):
            return 0
        if any(frame.audio_size != steady for frame in self.frames[-skip_count:]):
            return 0
        return skip_count

    def next_frame(self) -> Image.Image | None:
        if self._frame_index >= len(self.frames):
            return None
        frame = self.frames[self._frame_index]
        video_data = self.data[frame.video_offset:frame.video_offset + frame.video_size]
        self._decode_frame(video_data)
        image = Image.frombytes("P", (self.width, self.height), bytes(self._pixels))
        image.putpalette(bytes(self._palette))
        self._frame_index += 1
        return image.convert("RGBA")

    def _decode_frame(self, frame_data: bytes) -> None:
        if len(frame_data) < 2:
            raise ValueError("FST frame is too small")
        bit_count = struct.unpack_from("<H", frame_data, 0)[0]
        bitstream_size = (bit_count >> 3) + 1
        if len(frame_data) < 2 + bitstream_size:
            raise ValueError("FST frame bitstream is truncated")

        bit_reader = FstBitReader(frame_data[2:2 + bitstream_size], bit_count)
        payload_offset = 2 + bitstream_size

        if bit_reader.read_bit():
            if len(frame_data) < payload_offset + 256 * 3:
                raise ValueError("FST palette chunk is truncated")
            self._palette[:] = convert_vga_palette(frame_data[payload_offset:payload_offset + 256 * 3])
            payload_offset += 256 * 3

        blocks_x = self.width // 4
        blocks_y = self.height // 4
        truncated_tail = False

        for block_y in range(blocks_y):
            for block_x in range(blocks_x):
                if not bit_reader.read_bit():
                    continue

                block_offset = block_y * 4 * self.width + block_x * 4
                if bit_reader.read_bit():
                    if len(frame_data) < payload_offset + 4:
                        truncated_tail = True
                        break
                    decode_fst_mask_block(self._pixels, self.width, block_offset, frame_data[payload_offset:payload_offset + 4])
                    payload_offset += 4
                else:
                    if len(frame_data) < payload_offset + 16:
                        truncated_tail = True
                        break
                    for y in range(4):
                        src_row = frame_data[payload_offset + y * 4:payload_offset + (y + 1) * 4]
                        dst_row_offset = block_offset + y * self.width
                        self._pixels[dst_row_offset:dst_row_offset + 4] = src_row
                    payload_offset += 16
            if truncated_tail:
                break


class HarvesterExplorerApp(tk.Tk if TK_AVAILABLE else object):
    AUTO_PALETTE_KEY = "__AUTO__"

    def __init__(self, install: HarvesterInstall) -> None:
        super().__init__()
        self.title("Harvester Resource Explorer")
        self.geometry("1420x900")
        self.install = install
        self.filtered_entries: list[ResourceEntry] = []
        self.tree_items: dict[str, ResourceEntry] = {}
        self.preview_token = 0
        self.animation_after_id: str | None = None
        self.audio_process: subprocess.Popen[bytes] | None = None
        self.audio_temp_paths: list[Path] = []
        self.current_static_image: Image.Image | None = None
        self.current_animation_frames: list[Image.Image] | None = None
        self.current_animation_delay_ms = 100
        self.current_animation_index = 0
        self.current_movie: FstMovie | None = None
        self.current_photo_image: ImageTk.PhotoImage | None = None
        self.current_entry: ResourceEntry | None = None
        self.current_palette_override_key: str | None = None
        self.palette_choice_keys: dict[str, str] = {}
        self._palette_combo_updating = False

        self.temp_dir = Path(tempfile.mkdtemp(prefix="harvester_resource_explorer_"))
        self.audio_player = self._discover_audio_player()

        self._build_ui()
        self._populate_tree()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self, padding=(10, 10, 10, 6))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Data root:").grid(row=0, column=0, sticky="w")
        self.root_var = tk.StringVar(value=str(self.install.root))
        root_entry = ttk.Entry(top, textvariable=self.root_var)
        root_entry.grid(row=0, column=1, sticky="ew", padx=(6, 6))
        ttk.Button(top, text="Browse", command=self._choose_root).grid(row=0, column=2, sticky="e")

        ttk.Label(top, text="Filter:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_args: self._populate_tree())
        filter_entry = ttk.Entry(top, textvariable=self.filter_var)
        filter_entry.grid(row=1, column=1, sticky="ew", padx=(6, 6), pady=(8, 0))
        ttk.Label(
            top,
            text=f"{len(self.install.archive_entries)} archive entries, {len(self.install.loose_entries)} loose resources",
        ).grid(row=1, column=2, sticky="e", pady=(8, 0))

        body = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        left = ttk.Frame(body, padding=6)
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        body.add(left, weight=3)

        columns = ("source", "path", "type", "size")
        self.tree = ttk.Treeview(left, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("source", text="Source")
        self.tree.heading("path", text="Path")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.column("source", width=110, stretch=False)
        self.tree.column("path", width=640, stretch=True)
        self.tree.column("type", width=80, stretch=False, anchor="center")
        self.tree.column("size", width=90, stretch=False, anchor="e")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        tree_scroll = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=tree_scroll.set)

        right = ttk.Frame(body, padding=6)
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)
        body.add(right, weight=4)

        self.metadata_var = tk.StringVar(value="Select a resource to preview it.")
        metadata = ttk.Label(right, textvariable=self.metadata_var, justify="left", anchor="nw")
        metadata.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        palette_row = ttk.Frame(right)
        palette_row.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        palette_row.columnconfigure(1, weight=1)

        ttk.Label(palette_row, text="Palette:").grid(row=0, column=0, sticky="w")
        self.palette_choice_var = tk.StringVar(value="Auto")
        self.palette_combo = ttk.Combobox(palette_row, textvariable=self.palette_choice_var, state="disabled")
        self.palette_combo.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.palette_combo.bind("<<ComboboxSelected>>", self._on_palette_selected)

        self.preview_label = ttk.Label(right, anchor="center")
        self.preview_label.grid(row=2, column=0, sticky="nsew")
        self.preview_label.bind("<Configure>", lambda _event: self._refresh_preview_image())

        details_frame = ttk.Frame(right)
        details_frame.grid(row=3, column=0, sticky="nsew", pady=(8, 0))
        details_frame.rowconfigure(0, weight=1)
        details_frame.columnconfigure(0, weight=1)

        self.details_text = tk.Text(details_frame, height=16, wrap="none", font=("Menlo", 11))
        self.details_text.grid(row=0, column=0, sticky="nsew")
        self.details_text.configure(state="disabled")
        details_scroll = ttk.Scrollbar(details_frame, orient="vertical", command=self.details_text.yview)
        details_scroll.grid(row=0, column=1, sticky="ns")
        self.details_text.configure(yscrollcommand=details_scroll.set)

    def _discover_audio_player(self) -> list[str] | None:
        for command in (["afplay"], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"], ["aplay"]):
            if shutil.which(command[0]):
                return command
        return None

    def _choose_root(self) -> None:
        selected = filedialog.askdirectory(initialdir=str(self.install.root), title="Select Harvester data root")
        if not selected:
            return
        try:
            install = HarvesterInstall.discover(Path(selected))
        except Exception as exc:
            messagebox.showerror("Unable to load data root", str(exc))
            return
        self._stop_preview()
        self.install = install
        self.root_var.set(str(install.root))
        self.filter_var.set("")
        self.metadata_var.set("Select a resource to preview it.")
        self._set_details("")
        self.preview_label.configure(image="")
        self.current_photo_image = None
        self.current_entry = None
        self.current_palette_override_key = None
        self._disable_palette_selection()
        self._populate_tree()

    def _palette_label(self, entry: ResourceEntry) -> str:
        return f"{entry.source_label} :: {entry.logical_path}"

    def _disable_palette_selection(self) -> None:
        self._palette_combo_updating = True
        self.palette_choice_keys = {}
        self.palette_choice_var.set("Auto")
        self.palette_combo.configure(values=(), state="disabled")
        self._palette_combo_updating = False

    def _configure_palette_selection(self, entry: ResourceEntry, override_key: str | None) -> None:
        if entry.preview_kind not in {"bm", "abm"}:
            self._disable_palette_selection()
            return

        auto_palette_entry = self.install.resolve_palette_entry(entry)
        auto_label = (
            f"Auto: {self._palette_label(auto_palette_entry)}"
            if auto_palette_entry is not None
            else "Auto: grayscale fallback"
        )

        choices = [(auto_label, self.AUTO_PALETTE_KEY)]
        choices.extend((self._palette_label(palette_entry), palette_entry.path_key) for palette_entry in self.install.palette_entries)

        selected_key = override_key or self.AUTO_PALETTE_KEY
        selected_label = auto_label
        for label, key in choices:
            if key == selected_key:
                selected_label = label
                break

        self._palette_combo_updating = True
        self.palette_choice_keys = {label: key for label, key in choices}
        self.palette_combo.configure(values=[label for label, _key in choices], state="readonly")
        self.palette_choice_var.set(selected_label)
        self._palette_combo_updating = False

    def _on_palette_selected(self, _event: object) -> None:
        if self._palette_combo_updating or self.current_entry is None:
            return
        selected_label = self.palette_choice_var.get()
        selected_key = self.palette_choice_keys.get(selected_label, self.AUTO_PALETTE_KEY)
        override_key = None if selected_key == self.AUTO_PALETTE_KEY else selected_key
        if override_key == self.current_palette_override_key:
            return
        self._preview_entry(self.current_entry, palette_override_key=override_key)

    def _populate_tree(self) -> None:
        filter_text = self.filter_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        self.tree_items.clear()
        self.filtered_entries = []

        for entry in self.install.entries:
            haystack = f"{entry.source_label} {entry.logical_path} {entry.preview_kind} {entry.size}".lower()
            if filter_text and filter_text not in haystack:
                continue
            item = self.tree.insert(
                "",
                "end",
                values=(entry.source_label, entry.logical_path, entry.preview_kind.upper(), format_size(entry.size)),
            )
            self.tree_items[item] = entry
            self.filtered_entries.append(entry)

        if self.filtered_entries:
            first = self.tree.get_children()[0]
            self.tree.selection_set(first)
            self.tree.focus(first)
            self.tree.see(first)

    def _on_tree_select(self, _event: object) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        entry = self.tree_items.get(selection[0])
        if entry is None:
            return
        self._preview_entry(entry)

    def _preview_entry(self, entry: ResourceEntry, *, palette_override_key: str | None = None) -> None:
        self.current_entry = entry
        self.current_palette_override_key = palette_override_key
        self._stop_preview()
        self.preview_token += 1
        token = self.preview_token
        self.metadata_var.set(self._build_metadata(entry))
        self._configure_palette_selection(entry, palette_override_key)

        if entry.preview_kind == "dialogue_idx":
            data = entry.load_bytes()
            dialogue_entries = parse_dialogue_idx(data)
            lines = [f"{wav_id:>5}  {subtitle}" for wav_id, subtitle in dialogue_entries]
            self._set_details("\n".join(lines))
            return

        if entry.preview_kind == "scr":
            data = entry.load_bytes()
            self._set_details(decode_xor_aa_text(data))
            return

        if entry.preview_kind in {"bm", "pal", "abm", "cmp", "wav", "fst"}:
            worker = threading.Thread(
                target=self._load_preview_worker,
                args=(entry, token, palette_override_key),
                daemon=True,
            )
            worker.start()
            return

        data = entry.load_bytes()
        self._set_details(
            textwrap.dedent(
                f"""
                No specialized preview for `{entry.preview_kind}`.

                First bytes:
                {format_hex_preview(data)}
                """
            ).strip()
        )

    def _load_preview_worker(self, entry: ResourceEntry, token: int, palette_override_key: str | None) -> None:
        try:
            payload = entry.load_bytes()

            if entry.preview_kind == "bm":
                palette_entry = (
                    self.install.get_palette_by_key(palette_override_key)
                    if palette_override_key
                    else self.install.resolve_palette_entry(entry)
                )
                palette = self.install.load_palette_bytes(palette_entry) if palette_entry is not None else None
                image = decode_bm(payload, palette)
                details = self._details_for_bm(entry, payload, palette_entry)
                self.after(0, lambda: self._show_static_image(entry, image, details, token))
                return

            if entry.preview_kind == "pal":
                image = decode_pal_image(payload)
                details = f"{entry.logical_path}\nPalette entries: 256\nSize: {len(payload)} bytes"
                self.after(0, lambda: self._show_static_image(entry, image, details, token))
                return

            if entry.preview_kind == "abm":
                palette_entry = (
                    self.install.get_palette_by_key(palette_override_key)
                    if palette_override_key
                    else self.install.resolve_palette_entry(entry)
                )
                palette = self.install.load_palette_bytes(palette_entry) if palette_entry is not None else None
                frames, meta = decode_abm(payload, palette)
                details = (
                    f"{entry.logical_path}\n"
                    f"Frames: {meta['frame_count']}\n"
                    f"Canvas: {meta['width']}x{meta['height']}\n"
                    f"Palette: {self._palette_label(palette_entry) if palette_entry is not None else 'grayscale fallback'}"
                )
                self.after(0, lambda: self._show_animation(entry, frames, details, token, delay_ms=100))
                return

            if entry.preview_kind == "cmp":
                clip, details = self._decode_cmp(entry, payload)
                self.after(0, lambda: self._show_audio(entry, clip, details, token))
                return

            if entry.preview_kind == "wav":
                clip, details = self._decode_wav(entry, payload)
                self.after(0, lambda: self._show_audio(entry, clip, details, token))
                return

            if entry.preview_kind == "fst":
                movie = FstMovie.from_bytes(payload)
                first_frame = movie.next_frame()
                if first_frame is None:
                    raise ValueError("FST contains no decodable frames")
                audio_clip = movie.build_audio()
                movie.reset()
                details = (
                    f"{entry.logical_path}\n"
                    f"Frames: {movie.frame_count}\n"
                    f"Video: {movie.width}x{movie.height} @ {movie.frame_rate} fps\n"
                    f"Audio: {movie.sample_rate} Hz / {movie.bits_per_sample}-bit"
                )
                self.after(0, lambda: self._show_movie(entry, movie, first_frame, audio_clip, details, token))
                return

        except Exception as exc:
            self.after(0, lambda: self._show_error(entry, exc, token))

    def _show_error(self, entry: ResourceEntry, exc: Exception, token: int) -> None:
        if token != self.preview_token:
            return
        self.current_static_image = None
        self.current_animation_frames = None
        self.current_movie = None
        self.current_photo_image = None
        self.preview_label.configure(image="")
        self._set_details(f"{entry.logical_path}\n\nPreview failed:\n{exc}")

    def _show_static_image(self, entry: ResourceEntry, image: Image.Image, details: str, token: int) -> None:
        if token != self.preview_token:
            return
        self.current_static_image = image
        self.current_animation_frames = None
        self.current_movie = None
        self.current_animation_index = 0
        self._set_details(details)
        self._refresh_preview_image()

    def _show_animation(
        self,
        entry: ResourceEntry,
        frames: list[Image.Image],
        details: str,
        token: int,
        *,
        delay_ms: int,
    ) -> None:
        if token != self.preview_token:
            return
        self.current_static_image = None
        self.current_movie = None
        self.current_animation_frames = frames
        self.current_animation_delay_ms = delay_ms
        self.current_animation_index = 0
        self._set_details(details)
        self._advance_predecoded_animation(token)

    def _show_movie(
        self,
        entry: ResourceEntry,
        movie: FstMovie,
        first_frame: Image.Image,
        audio_clip: AudioClip | None,
        details: str,
        token: int,
    ) -> None:
        if token != self.preview_token:
            return
        self.current_static_image = None
        self.current_animation_frames = None
        self.current_movie = movie
        self._set_details(details)
        self._display_image(first_frame)
        if audio_clip is not None:
            self._play_audio(audio_clip)
        self.animation_after_id = self.after(max(1, int(1000 / movie.frame_rate)), lambda: self._advance_movie(token))

    def _show_audio(self, entry: ResourceEntry, clip: AudioClip, details: str, token: int) -> None:
        if token != self.preview_token:
            return
        self.current_static_image = None
        self.current_animation_frames = None
        self.current_movie = None
        self.preview_label.configure(image="")
        self.current_photo_image = None
        self._set_details(details)
        self._play_audio(clip)

    def _advance_predecoded_animation(self, token: int) -> None:
        if token != self.preview_token or not self.current_animation_frames:
            return
        frame = self.current_animation_frames[self.current_animation_index]
        self.current_animation_index = (self.current_animation_index + 1) % len(self.current_animation_frames)
        self._display_image(frame)
        self.animation_after_id = self.after(
            self.current_animation_delay_ms,
            lambda: self._advance_predecoded_animation(token),
        )

    def _advance_movie(self, token: int) -> None:
        if token != self.preview_token or self.current_movie is None:
            return
        frame = self.current_movie.next_frame()
        if frame is None:
            self.current_movie.reset()
            return
        self._display_image(frame)
        self.animation_after_id = self.after(
            max(1, int(1000 / self.current_movie.frame_rate)),
            lambda: self._advance_movie(token),
        )

    def _display_image(self, image: Image.Image) -> None:
        self.current_static_image = image
        self._refresh_preview_image()

    def _refresh_preview_image(self) -> None:
        if self.current_static_image is None:
            return
        width = max(1, self.preview_label.winfo_width() - 8)
        height = max(1, self.preview_label.winfo_height() - 8)
        rendered = fit_image(self.current_static_image, width, height)
        self.current_photo_image = ImageTk.PhotoImage(rendered)
        self.preview_label.configure(image=self.current_photo_image)

    def _decode_cmp(self, entry: ResourceEntry, data: bytes) -> tuple[AudioClip, str]:
        if len(data) < 14 or data[:4] != b"FCMP":
            raise ValueError("CMP payload is missing the FCMP header")
        payload_size, sample_rate = struct.unpack_from("<II", data, 4)
        bits_per_sample = struct.unpack_from("<H", data, 12)[0]
        available_payload = data[14:]
        payload = available_payload[:payload_size] if payload_size else available_payload
        if sample_rate == 0 or bits_per_sample not in (8, 16) or not payload:
            raise ValueError("CMP header contains an unsupported audio format")
        warmup_mode = "music" if "/music/" in entry.path_without_drive else "sample"
        pcm = decode_harvester_fcmp(payload, bits_per_sample)
        pcm = apply_fcmp_warmup(pcm, mode=warmup_mode)
        clip = AudioClip(sample_rate=sample_rate, bits_per_sample=bits_per_sample, pcm=pcm)
        duration = len(pcm) / (sample_rate * (bits_per_sample // 8)) if sample_rate else 0
        details = (
            f"{entry.logical_path}\n"
            f"Format: FCMP\n"
            f"Sample rate: {sample_rate} Hz\n"
            f"Bits per sample: {bits_per_sample}\n"
            f"Warmup mode: {warmup_mode}\n"
            f"Decoded PCM: {format_size(len(pcm))}\n"
            f"Approx. duration: {duration:.2f}s"
        )
        return clip, details

    def _decode_wav(self, entry: ResourceEntry, data: bytes) -> tuple[AudioClip, str]:
        with wave.open(io.BytesIO(data), "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_rate = wav_file.getframerate()
            bits_per_sample = wav_file.getsampwidth() * 8
            pcm = wav_file.readframes(wav_file.getnframes())
        if channels != 1:
            raise ValueError(f"Only mono WAV preview is supported right now, got {channels} channels")
        clip = AudioClip(sample_rate=sample_rate, bits_per_sample=bits_per_sample, pcm=pcm)
        duration = len(pcm) / (sample_rate * (bits_per_sample // 8)) if sample_rate else 0
        details = (
            f"{entry.logical_path}\n"
            f"Format: WAV\n"
            f"Sample rate: {sample_rate} Hz\n"
            f"Bits per sample: {bits_per_sample}\n"
            f"Duration: {duration:.2f}s"
        )
        return clip, details

    def _details_for_bm(self, entry: ResourceEntry, payload: bytes, palette_entry: ResourceEntry | None) -> str:
        width, height, _reserved = struct.unpack_from("<III", payload, 0)
        return (
            f"{entry.logical_path}\n"
            f"Dimensions: {width}x{height}\n"
            f"Palette: {self._palette_label(palette_entry) if palette_entry is not None else 'grayscale fallback'}\n"
            f"Pixels: {format_size(width * height)}"
        )

    def _play_audio(self, clip: AudioClip) -> None:
        self._stop_audio()
        if self.audio_player is None:
            self._append_details("\n\nNo system audio player found. Install `afplay`, `ffplay`, or `aplay` to enable playback.")
            return

        path = self.temp_dir / f"preview_{len(self.audio_temp_paths):04d}.wav"
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(clip.bits_per_sample // 8)
            wav_file.setframerate(clip.sample_rate)
            wav_file.writeframes(clip.pcm)

        self.audio_temp_paths.append(path)
        self.audio_process = subprocess.Popen(
            [*self.audio_player, str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _build_metadata(self, entry: ResourceEntry) -> str:
        lines = [
            f"Source: {entry.source_label}",
            f"Path: {entry.logical_path}",
            f"Type: {entry.preview_kind.upper()}",
            f"Size: {format_size(entry.size)}",
        ]
        if entry.source_kind == "archive":
            lines.extend(
                [
                    f"Index: {entry.index_path.name if entry.index_path else 'n/a'}",
                    f"Data: {entry.data_path.name if entry.data_path else 'n/a'}",
                    f"Archive offset: 0x{entry.archive_offset:08x}" if entry.archive_offset is not None else "Archive offset: n/a",
                    f"Stored size: {entry.stored_size} bytes" if entry.stored_size is not None else "Stored size: n/a",
                    f"Packed flag: {entry.packed_flag}",
                ]
            )
        else:
            lines.append(f"File: {entry.loose_path}")
        return "\n".join(lines)

    def _set_details(self, text: str) -> None:
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", text)
        self.details_text.configure(state="disabled")

    def _append_details(self, text: str) -> None:
        self.details_text.configure(state="normal")
        self.details_text.insert("end", text)
        self.details_text.configure(state="disabled")

    def _stop_audio(self) -> None:
        if self.audio_process is None:
            return
        if self.audio_process.poll() is None:
            self.audio_process.terminate()
            try:
                self.audio_process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                self.audio_process.kill()
        self.audio_process = None

    def _stop_preview(self) -> None:
        if self.animation_after_id is not None:
            self.after_cancel(self.animation_after_id)
            self.animation_after_id = None
        self._stop_audio()
        self.current_animation_frames = None
        self.current_movie = None
        self.current_static_image = None
        self.current_photo_image = None
        self.preview_label.configure(image="")

    def _on_close(self) -> None:
        self._stop_preview()
        for path in self.audio_temp_paths:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            self.temp_dir.rmdir()
        except OSError:
            pass
        self.destroy()


def validate_install(install: HarvesterInstall) -> None:
    print(f"root={install.root}")
    print(f"archive_entries={len(install.archive_entries)} loose_entries={len(install.loose_entries)}")

    sample_bm = next(entry for entry in install.archive_entries if entry.filename.lower() == "harvlogo.bm")
    bm_payload = sample_bm.load_bytes()
    bm_image = decode_bm(bm_payload, install.resolve_palette(sample_bm))
    print(f"bm={sample_bm.logical_path} size={bm_image.width}x{bm_image.height}")

    sample_cmp = next(entry for entry in install.archive_entries if entry.filename.lower() == "7.cmp")
    cmp_payload = sample_cmp.load_bytes()
    if cmp_payload[:4] != b"FCMP":
        raise RuntimeError("sample CMP is missing FCMP magic")
    payload_size, sample_rate = struct.unpack_from("<II", cmp_payload, 4)
    bits_per_sample = struct.unpack_from("<H", cmp_payload, 12)[0]
    pcm = apply_fcmp_warmup(
        decode_harvester_fcmp(cmp_payload[14:14 + payload_size], bits_per_sample),
        mode="sample",
    )
    print(f"cmp={sample_cmp.logical_path} rate={sample_rate} bits={bits_per_sample} decoded={len(pcm)}")

    sample_fst = next(entry for entry in install.loose_entries if entry.filename.lower() == "virglogo.fst")
    movie = FstMovie.from_bytes(sample_fst.load_bytes())
    frame = movie.next_frame()
    if frame is None:
        raise RuntimeError("failed to decode first FST frame")
    print(f"fst={sample_fst.logical_path} frames={movie.frame_count} size={movie.width}x{movie.height} first_frame={frame.width}x{frame.height}")

    sample_dialogue = next(entry for entry in install.loose_entries if entry.filename.lower() == "dialogue.idx")
    dialogue_entries = parse_dialogue_idx(sample_dialogue.load_bytes())
    print(f"dialogue_idx={sample_dialogue.logical_path} entries={len(dialogue_entries)} first={dialogue_entries[:3]}")

    sample_scr = next(entry for entry in install.loose_entries if entry.filename.lower() == "harvest.scr")
    scr_lines = decode_xor_aa_text(sample_scr.load_bytes()).splitlines()[:3]
    print(f"scr={sample_scr.logical_path} first_lines={scr_lines}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Explore Harvester DAT/INDEX archives and loose media files.")
    parser.add_argument(
        "data_root",
        nargs="?",
        default=str(discover_default_data_root()),
        help="Harvester data root containing prefixed INDEX/DAT files and loose resources",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run a headless decode check against a few known resources and exit",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not PIL_AVAILABLE:
        raise RuntimeError(f"Pillow is required for decoding/preview but is not available: {PIL_IMPORT_ERROR}")
    install = HarvesterInstall.discover(Path(args.data_root))
    if args.validate:
        validate_install(install)
        return 0
    if not TK_AVAILABLE:
        raise RuntimeError(f"Tk is required for the GUI explorer but is not available: {TK_IMPORT_ERROR}")
    app = HarvesterExplorerApp(install)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
