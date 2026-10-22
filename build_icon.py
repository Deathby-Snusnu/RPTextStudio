from __future__ import annotations

import struct
from pathlib import Path

from PySide6.QtCore import QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "assets" / "rp_text_studio_icon.svg"
OUTPUT = ROOT / "build" / "RPTextStudio.ico"
SIZES = (16, 24, 32, 48, 64, 128, 256)


def render_png(renderer: QSvgRenderer, size: int) -> bytes:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()

    data = QByteArray()
    buffer = QBuffer(data)
    if not buffer.open(QIODevice.OpenModeFlag.WriteOnly):
        raise OSError("Could not open the in-memory PNG buffer.")
    if not image.save(buffer, "PNG"):
        raise OSError(f"Could not render the {size}x{size} icon.")
    buffer.close()
    return bytes(data)


def main() -> None:
    renderer = QSvgRenderer(str(SOURCE))
    if not renderer.isValid():
        raise ValueError(f"Invalid SVG icon: {SOURCE}")

    images = [render_png(renderer, size) for size in SIZES]
    header_size = 6 + 16 * len(images)
    offset = header_size
    entries = []
    for size, image in zip(SIZES, images):
        dimension = 0 if size == 256 else size
        entries.append(
            struct.pack(
                "<BBBBHHII",
                dimension,
                dimension,
                0,
                0,
                1,
                32,
                len(image),
                offset,
            )
        )
        offset += len(image)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(
        struct.pack("<HHH", 0, 1, len(images)) + b"".join(entries) + b"".join(images)
    )
    print(f"Windows-Icon erstellt: {OUTPUT}")


if __name__ == "__main__":
    main()