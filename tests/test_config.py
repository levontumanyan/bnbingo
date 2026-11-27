from bnbingo.config import (
	AMENITIES_PATH,
	BENCHMARKS_PATH,
	CACHE_DIR,
	CONFIG_DIR,
	DATA_DIR,
)


def test_data_dir_resolution():
	"""Verify that DATA_DIR points to the source root when running from source."""
	assert DATA_DIR.exists()
	assert (DATA_DIR / "pyproject.toml").exists()
	assert (DATA_DIR / "bnbingo").exists()


def test_config_paths():
	"""Verify that configs live in CONFIG_DIR, separate from data."""
	assert BENCHMARKS_PATH == CONFIG_DIR / "benchmarks.json"
	assert CACHE_DIR == DATA_DIR / ".cache"


def test_amenities_ship_with_package():
	"""Amenity mappings must live inside the package for installed use."""
	assert AMENITIES_PATH.exists()
	assert AMENITIES_PATH.parent.name == "bnbingo"
