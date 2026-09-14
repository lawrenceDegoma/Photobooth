from datetime import datetime

from PIL import Image

from app.processing.image_processor import ImageProcessor
from app.processing.photo_strip import PhotoStrip


def _make_test_image(path, size=(800, 600), color=(255, 0, 0)):
    Image.new("RGB", size, color).save(path)
    return str(path)


def test_process_resizes_image(tmp_path):
    source = _make_test_image(tmp_path / "source.jpg")
    output = str(tmp_path / "processed.jpg")

    processor = ImageProcessor(target_size=(400, 300))
    processor.process(source, output)

    with Image.open(output) as img:
        assert img.size == (400, 300)


def test_process_preserves_original(tmp_path):
    source = _make_test_image(tmp_path / "source.jpg")
    output = str(tmp_path / "processed.jpg")

    with Image.open(source) as original:
        original_size = original.size

    processor = ImageProcessor(target_size=(100, 100))
    processor.process(source, output)

    with Image.open(source) as original_after:
        assert original_after.size == original_size


def test_photo_strip_generation(tmp_path):
    photo_paths = [_make_test_image(tmp_path / f"{i}.jpg") for i in range(4)]
    output = str(tmp_path / "strip.jpg")

    strip = PhotoStrip(template_name="classic")
    strip.generate(photo_paths, output, event_name="Test Event", event_date=datetime(2026, 9, 14))

    with Image.open(output) as img:
        assert img.width > 0 and img.height > 0
