import numpy as np

from mcp_server.services.detector import (
    decode_frame,
    detect_cubes,
    detect_cones,
    detect_object,
    detect_spheres,
    parse_description,
    select_best_match,
)


class TestDecodeFrame:
    def test_decode_valid_base64(self, sample_frame_base64):
        frame = decode_frame(sample_frame_base64)
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (480, 640, 3)

    def test_decode_invalid_base64_returns_black_frame(self):
        frame = decode_frame("AAAA")
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (480, 640, 3)


class TestParseDescription:
    def test_with_color(self):
        tipo, cor = parse_description("cubo vermelho")
        assert tipo == "cubo"
        assert cor == "vermelho"

    def test_no_color(self):
        tipo, cor = parse_description("esfera")
        assert tipo == "esfera"
        assert cor is None

    def test_unknown_word_fallback_cubo(self):
        tipo, cor = parse_description("foobar")
        assert tipo == "cubo"
        assert cor is None

    def test_color_only_fallback_cubo(self):
        tipo, cor = parse_description("azul")
        assert tipo == "cubo"
        assert cor == "azul"

    def test_cone_with_color(self):
        tipo, cor = parse_description("cone laranja")
        assert tipo == "cone"
        assert cor == "laranja"

    def test_plural_form(self):
        tipo, cor = parse_description("cubos vermelhos")
        assert tipo == "cubo"
        assert cor == "vermelho"

    def test_case_insensitive(self):
        tipo, cor = parse_description("CUBO VERMELHO")
        assert tipo == "cubo"
        assert cor == "vermelho"

    def test_bola_maps_to_esfera(self):
        tipo, cor = parse_description("bola azul")
        assert tipo == "esfera"
        assert cor == "azul"

    def test_bolas_maps_to_esfera(self):
        tipo, cor = parse_description("bolas azul")
        assert tipo == "esfera"
        assert cor == "azul"

    def test_bola_no_color(self):
        tipo, cor = parse_description("bola")
        assert tipo == "esfera"
        assert cor is None


class TestDetectCubes:
    def test_detects_cube_in_frame(self, sample_frame):
        results = detect_cubes(sample_frame)
        assert len(results) > 0
        assert results[0]["type"] == "cubo"

    def test_no_cube_in_empty_frame(self, empty_frame):
        results = detect_cubes(empty_frame)
        assert len(results) == 0

    def test_cube_with_color_mask(self, sample_frame):
        results = detect_cubes(sample_frame, color="vermelho")
        assert len(results) > 0
        assert results[0]["type"] == "cubo"


class TestDetectSpheres:
    def test_detects_sphere_in_frame(self, sphere_frame):
        results = detect_spheres(sphere_frame)
        assert len(results) > 0
        assert results[0]["type"] == "esfera"

    def test_no_sphere_in_empty_frame(self, empty_frame):
        results = detect_spheres(empty_frame)
        assert len(results) == 0


class TestDetectCones:
    def test_detects_cone_in_frame(self, cone_frame):
        results = detect_cones(cone_frame)
        assert len(results) > 0
        assert results[0]["type"] == "cone"

    def test_no_cone_in_empty_frame(self, empty_frame):
        results = detect_cones(empty_frame)
        assert len(results) == 0


class TestDetectObject:
    def test_detects_cube_with_type(self, sample_frame):
        result = detect_object(sample_frame, "cubo")
        assert result is not None
        assert result["type"] == "cubo"
        assert "bbox" in result
        assert "center" in result

    def test_detects_cube_with_color(self, sample_frame):
        result = detect_object(sample_frame, "cubo", "vermelho")
        assert result is not None
        assert result["type"] == "cubo"

    def test_no_detection_in_empty_frame(self, empty_frame):
        result = detect_object(empty_frame, "cubo", "vermelho")
        assert result is None

    def test_detects_sphere(self, sphere_frame):
        result = detect_object(sphere_frame, "esfera")
        assert result is not None
        assert result["type"] == "esfera"

    def test_detects_cone(self, cone_frame):
        result = detect_object(cone_frame, "cone")
        assert result is not None
        assert result["type"] == "cone"

    def test_bbox_fields(self, sample_frame):
        result = detect_object(sample_frame, "cubo")
        x, y, w, h = result["bbox"]
        assert w > 0
        assert h > 0
        cx, cy = result["center"]
        assert 0 <= cx <= 640
        assert 0 <= cy <= 480


class TestSelectBestMatch:
    def test_selects_largest_area(self):
        matches = [
            {"type": "cubo", "color": None, "bbox": (0, 0, 10, 10), "center": (5, 5), "area": 100},
            {"type": "cubo", "color": None, "bbox": (0, 0, 50, 50), "center": (25, 25), "area": 2500},
            {"type": "cubo", "color": None, "bbox": (0, 0, 20, 20), "center": (10, 10), "area": 400},
        ]
        best = select_best_match(matches)
        assert best["area"] == 2500

    def test_single_match(self):
        matches = [{"type": "esfera", "color": None, "bbox": (0, 0, 30, 30), "center": (15, 15), "area": 900}]
        best = select_best_match(matches)
        assert best is matches[0]


class TestTwoCubesSelectBest:
    def test_selects_larger_of_two(self, two_cubes_frame):
        results = detect_cubes(two_cubes_frame)
        assert len(results) >= 2
        best = select_best_match(results)
        assert best is not None
        x, y, w, h = best["bbox"]
        assert w * h >= 100 * 100
