import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PACKAGE_DIR = Path(__file__).resolve().parent


def _resolve_data_dir() -> Path:
	if env_home := os.getenv("BNBINGO_HOME"):
		return Path(env_home).expanduser()
	if (PACKAGE_DIR.parent / "pyproject.toml").exists():
		return PACKAGE_DIR.parent
	return Path.home() / ".local" / "share" / "bnbingo"


DATA_DIR = _resolve_data_dir()
CONFIG_DIR = Path(
	os.getenv("BNBINGO_CONFIG_DIR", Path.home() / ".config" / "bnbingo")
).expanduser()

BENCHMARKS_PATH = CONFIG_DIR / "benchmarks.json"
DEFAULT_BENCHMARKS_PATH = PACKAGE_DIR / "benchmarks.json"
AMENITIES_PATH = PACKAGE_DIR / "amenities.json"

CACHE_DIR = DATA_DIR / ".cache"
LISTING_CACHE = CACHE_DIR / "listings"
CITY_CACHE = CACHE_DIR / "cities.json"
CLIMATE_CACHE = CACHE_DIR / "climate.json"

LOG_DIR = Path(tempfile.gettempdir()) / "bnbingo-logs"
LOG_FILE = LOG_DIR / "app.log"

REPORTS_DIR = DATA_DIR / "reports"

for _dir in (LISTING_CACHE, LOG_DIR, REPORTS_DIR, CONFIG_DIR):
	try:
		_dir.mkdir(parents=True, exist_ok=True)
	except OSError:
		pass

TEST_DATA_DIR = PACKAGE_DIR.parent / "tests" / "data"
TEST_LISTING_ID = "19643333"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AIRBNB_COOKIE = os.getenv("AIRBNB_COOKIE")
COOKIE_FILE = CONFIG_DIR / "cookies.txt"
USER_COOKIE_FILE = Path.home() / ".config" / "airbnb" / "cookies.txt"

if not AIRBNB_COOKIE:
	if COOKIE_FILE.exists():
		try:
			AIRBNB_COOKIE = COOKIE_FILE.read_text(encoding="utf-8").strip()
		except Exception:
			pass
	elif USER_COOKIE_FILE.exists():
		try:
			AIRBNB_COOKIE = USER_COOKIE_FILE.read_text(encoding="utf-8").strip()
		except Exception:
			pass
