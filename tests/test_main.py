import logging
from types import SimpleNamespace

from bnbingo.main import (
	filter_by_bounds,
	parse_cities,
	resolve_price_filters,
	run_survey,
	within_price_bounds,
)


def test_nightly_is_scaled_by_stay_length():
	assert resolve_price_filters(20, 45, None, None, 28) == (560, 1260, "nightly")
	assert resolve_price_filters(20, 45, None, None, 3) == (60, 135, "nightly")


def test_total_passes_through_unchanged():
	assert resolve_price_filters(None, None, 100, 1600, 28) == (100, 1600, "total")
	assert resolve_price_filters(None, None, 0, 400, 28) == (0, 400, "total")


def test_one_sided_nightly_leaves_other_bound_unfiltered():
	assert resolve_price_filters(None, 45, None, None, 28) == (0, 1260, "nightly")
	assert resolve_price_filters(20, None, None, None, 28) == (560, 0, "nightly")


def test_no_price_flags_means_no_filter():
	assert resolve_price_filters(None, None, None, None, 28) == (0, 0, "total")


def test_nightly_family_takes_precedence():
	assert resolve_price_filters(20, 45, 100, 1600, 28) == (560, 1260, "nightly")


def test_within_price_bounds():
	assert within_price_bounds(100, 0, 200)
	assert not within_price_bounds(201, 0, 200)
	assert not within_price_bounds(99, 100, 200)
	assert within_price_bounds(150, 0, 0)
	assert within_price_bounds(0, 100, 200)


def test_filter_by_bounds_drops_stale_over_budget_rows():
	rows = [{"total_price": 900}, {"total_price": 1500}, {"total_price": 0}]
	assert filter_by_bounds(rows, 0, 1000) == [rows[0], rows[2]]
	assert filter_by_bounds(rows, 0, 0) == rows


def test_parse_cities_keeps_city_country_names():
	assert parse_cities("Lisbon, Portugal") == ["Lisbon, Portugal"]
	assert parse_cities("Porto,Portugal") == ["Porto, Portugal"]
	assert parse_cities("Lima") == ["Lima"]
	assert parse_cities("") == []


def test_parse_cities_splits_explicit_and_paired_lists():
	assert parse_cities("Lima, Peru; Buenos Aires, Argentina") == [
		"Lima, Peru",
		"Buenos Aires, Argentina",
	]
	assert parse_cities("Lima, Peru,Buenos Aires, Argentina") == [
		"Lima, Peru",
		"Buenos Aires, Argentina",
	]
	assert parse_cities("Lima, Peru, Porto") == ["Lima, Peru", "Porto"]


def test_survey_enforces_price_cap(monkeypatch):
	def item(total):
		return {
			"price": {"unit": {"amount": total}},
			"rating": {"value": 5, "reviewCount": 100},
		}

	monkeypatch.setattr(
		"bnbingo.main.get_city_coords",
		lambda city: {"ne_lat": 1, "sw_lat": 0, "ne_long": 1, "sw_long": 0},
	)
	monkeypatch.setattr(
		"bnbingo.main.search_listings", lambda *args, **kwargs: [item(100), item(500)]
	)
	captured = {}
	monkeypatch.setattr(
		"bnbingo.main.generate_survey_report",
		lambda results, **kwargs: captured.update(results=results),
	)
	args = SimpleNamespace(
		cities="Test City, Nowhere",
		check_in="2027-01-10",
		check_out="2027-01-24",
		currency="CAD",
		language="en",
		free_cancellation=False,
		complete=False,
		place_type="Entire home/apt",
		json=False,
		min_rating=4.7,
		min_reviews=10,
		min_nightly=None,
		max_nightly=None,
		min_total=None,
		max_total=200,
	)
	run_survey(args, [], logging.getLogger("bnbingo-test"))
	assert captured["results"][0]["total_found"] == 1
	assert captured["results"][0]["median_total"] == 100


def test_load_scoring_policy_amenity_flag():
	from types import SimpleNamespace as NS

	from bnbingo.main import _load_scoring_policy
	from bnbingo.utils import load_amenity_map

	amenity_map = load_amenity_map()
	args = NS(benchmarks=None, amenities="wifi,kitchen,25")
	_, search_amenities = _load_scoring_policy(args, amenity_map)

	assert amenity_map.get("wifi") in search_amenities
	assert amenity_map.get("kitchen") in search_amenities
	assert 25 in search_amenities
	assert len(search_amenities) == len(set(search_amenities))
