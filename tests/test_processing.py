from datetime import datetime

from PIL import Image, ImageStat
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


def test_photo_strip_uses_configured_template(tmp_path):
    photo_paths = [_make_test_image(tmp_path / f"{i}.jpg") for i in range(4)]
    output = str(tmp_path / "strip.jpg")

    strip = PhotoStrip(template_name="wedding")
    strip.generate(photo_paths, output, event_name="Test Event", event_date=datetime(2026, 9, 14))

    with Image.open(output) as img:
        # Wedding template uses a distinct off-white background color.
        assert img.getpixel((5, 5)) != (255, 255, 255)


def test_photo_strip_falls_back_to_classic_for_unknown_template(tmp_path):
    photo_paths = [_make_test_image(tmp_path / f"{i}.jpg") for i in range(4)]
    output = str(tmp_path / "strip.jpg")

    strip = PhotoStrip(template_name="does-not-exist")
    strip.generate(photo_paths, output, event_name="Test Event", event_date=datetime(2026, 9, 14))

    with Image.open(output) as img:
        assert img.width > 0 and img.height > 0


def test_process_applies_configured_filter(tmp_path):
    source = _make_test_image(tmp_path / "source.jpg", color=(100, 150, 200))
    output = str(tmp_path / "processed.jpg")

    processor = ImageProcessor(target_size=(100, 100))
    processor.process(source, output, filter_name="grayscale")

    with Image.open(output) as img:
        r, g, b = img.convert("RGB").getpixel((50, 50))
        # Grayscale means R == G == B.
        assert r == g == b


def _mean_brightness(path):
    with Image.open(path) as img:
        return ImageStat.Stat(img.convert("L")).mean[0]


def test_auto_brightness_lifts_dark_image(tmp_path):
    # Gradient so autocontrast cannot mask the brightness correction.
    source = tmp_path / "dark.jpg"
    gradient = Image.linear_gradient("L").resize((200, 200)).point(lambda v: v // 4)
    Image.merge("RGB", (gradient, gradient, gradient)).save(source)

    plain = str(tmp_path / "plain.jpg")
    boosted = str(tmp_path / "boosted.jpg")
    ImageProcessor(target_size=(100, 100)).process(str(source), plain)
    ImageProcessor(target_size=(100, 100), auto_brightness=True).process(str(source), boosted)

    assert _mean_brightness(boosted) > _mean_brightness(plain)


def test_auto_brightness_gain_is_clamped(tmp_path):
    source = _make_test_image(tmp_path / "black.jpg", color=(2, 2, 2))
    output = str(tmp_path / "out.jpg")

    ImageProcessor(
        target_size=(50, 50), auto_brightness=True, max_brightness_gain=1.5
    ).process(source, output)

    # A near-black image must not be blown out to the target brightness.
    assert _mean_brightness(output) < 60


def test_saturation_and_sharpness_run_without_error(tmp_path):
    source = _make_test_image(tmp_path / "source.jpg", color=(100, 150, 200))
    output = str(tmp_path / "out.jpg")

    ImageProcessor(target_size=(100, 100), saturation=1.3, sharpness=1.5).process(source, output)

    with Image.open(output) as img:
        assert img.size == (100, 100)


def test_process_with_no_filter_preserves_color(tmp_path):
    source = _make_test_image(tmp_path / "source.jpg", color=(100, 150, 200))
    output = str(tmp_path / "processed.jpg")

    processor = ImageProcessor(target_size=(100, 100))
    processor.process(source, output, filter_name=None)

    with Image.open(output) as img:
        r, g, b = img.convert("RGB").getpixel((50, 50))
        # Allow for minor JPEG compression rounding.
        assert (abs(r - 100), abs(g - 150), abs(b - 200)) <= (2, 2, 2)
