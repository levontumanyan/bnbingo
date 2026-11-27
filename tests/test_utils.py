import json

import pytest

from bnbingo.utils import get_city_coords, load_benchmarks


def test_get_city_coords_from_cache(mocker, tmp_path):
	"""Verify coordinates are loaded from cache if present."""
	# Create a mock cache file
	mock_cache_dir = tmp_path / ".cache"
	mock_cache_dir.mkdir()
	mock_city_cache = mock_cache_dir / "cities.json"

	city_data = {
		"Montreal": {"sw_lat": 45.0, "ne_lat": 46.0, "sw_long": -74.0, "ne_long": -73.0}
	}
	with open(mock_city_cache, "w") as f:
		json.dump(city_data, f)

	# Mock the CITY_CACHE path in utils.py
	mocker.patch("bnbingo.utils.CITY_CACHE", mock_city_cache)

	# Also mock Nominatim just in case it's called (it shouldn't be)
	mock_geo = mocker.patch("bnbingo.utils.Nominatim")

	coords = get_city_coords("Montreal")

	assert coords == city_data["Montreal"]
	mock_geo.assert_not_called()


def test_get_city_coords_geocoding_success(mocker, tmp_path):
	"""Verify coordinates are fetched via geocoding when not in cache."""
	# Mock empty cache
	mock_city_cache = tmp_path / "cities.json"
	mocker.patch("bnbingo.utils.CITY_CACHE", mock_city_cache)

	# Mock Nominatim geocoder
	mock_location = mocker.Mock()
	mock_location.latitude = 45.5
	mock_location.longitude = -73.5
	mock_location.raw = {"boundingbox": ["45.0", "46.0", "-74.0", "-73.0"]}

	mock_geolocator = mocker.Mock()
	mock_geolocator.geocode.return_value = mock_location
	mocker.patch("bnbingo.utils.Nominatim", return_value=mock_geolocator)

	coords = get_city_coords("Montreal")

	assert coords["sw_lat"] == 45.0
	assert coords["ne_lat"] == 46.0
	assert coords["sw_long"] == -74.0
	assert coords["ne_long"] == -73.0

	# Verify it was saved to cache
	with open(mock_city_cache, "r") as f:
		cache_data = json.load(f)
		assert "Montreal" in cache_data


def test_load_benchmarks_explicit_path(tmp_path):
	policy = {"metrics": {}, "hard_filters": {"must_have_amenities": ["wifi"]}}
	p = tmp_path / "benchmarks.json"
	p.write_text(json.dumps(policy))
	assert load_benchmarks(str(p)) == policy


def test_load_benchmarks_missing_explicit_path_fails_loudly(tmp_path):
	with pytest.raises(FileNotFoundError):
		load_benchmarks(str(tmp_path / "nope.json"))


def test_load_benchmarks_malformed_json_fails_loudly(tmp_path):
	p = tmp_path / "benchmarks.json"
	p.write_text("{not json")
	with pytest.raises(ValueError, match="Malformed benchmarks JSON"):
		load_benchmarks(str(p))


def test_load_benchmarks_falls_back_to_packaged_default(mocker, tmp_path):
	mocker.patch("bnbingo.utils.BENCHMARKS_PATH", tmp_path / "absent.json")
	policy = load_benchmarks()
	assert policy["metrics"]
