from __future__ import annotations

import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


def create_icon(source: Path, destination: Path) -> None:
    app = QGuiApplication([])
    renderer = QSvgRenderer(str(source))
    if not renderer.isValid():
        raise ValueError(f"Invalid SVG logo: {source}")

    images: list[tuple[int, bytes]] = []
    for size in (16, 32, 48, 64, 128, 256):
        image = QImage(size, size, QImage.Format.Format_ARGB32)
        image.fill(0)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()

        buffer = QBuffer()
        if not buffer.open(QIODevice.OpenModeFlag.WriteOnly):
            raise OSError("Unable to open an in-memory buffer for the icon.")
        if not image.save(buffer, "PNG"):
            raise OSError(f"Unable to render the {size}px icon.")
        images.append((size, bytes(buffer.data())))
        buffer.close()

    header = struct.pack("<HHH", 0, 1, len(images))
    directory_size = 6 + 16 * len(images)
    entries = bytearray()
    payload = bytearray()
    offset = directory_size
    for size, png in images:
        dimension = 0 if size == 256 else size
        entries.extend(struct.pack(
            "<BBBBHHII",
            dimension,
            dimension,
            0,
            0,
            1,
            32,
            len(png),
            offset,
        ))
        payload.extend(png)
        offset += len(png)

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(header + entries + payload)
    app.quit()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: build_icon.py <logo.svg> <icon.ico>")
    create_icon(Path(sys.argv[1]), Path(sys.argv[2]))
