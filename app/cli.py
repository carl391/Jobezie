"""
Flask CLI Commands

Custom CLI commands for database management and data seeding.
"""

import csv
import logging
import os
from collections import defaultdict
from datetime import datetime

import click
import requests
from flask.cli import with_appcontext

from app.extensions import db
from app.models.labor_market import LaborMarketData, Occupation, OccupationSkill, Skill

logger = logging.getLogger(__name__)


def register_commands(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(seed_market_data)
    app.cli.add_command(reset_usage)


def _seed_onet_data(onet_path):
    """
    Core O*NET seeding logic, callable from both CLI and app startup.
    Uses logging instead of click.echo so it works in both contexts.
    """
    onet_occupation_file = os.path.join(onet_path, "Occupation Data.txt")

    if not os.path.exists(onet_occupation_file):
        logger.warning(f"O*NET occupation file not found at {onet_occupation_file}")
        return

    _seed_onet_occupations(onet_occupation_file)

    onet_files = [
        ("Skills.txt", "skills"),
        ("Abilities.txt", "abilities"),
        ("Knowledge.txt", "knowledge"),
    ]

    for filename, category in onet_files:
        filepath = os.path.join(onet_path, filename)
        if os.path.exists(filepath):
            _seed_onet_elements(filepath, category)
        else:
            logger.warning(f"{filepath} not found")

    logger.info("O*NET data seed complete!")


@click.command("seed-market-data")
@click.option("--onet-path", default="data/onet/", help="Path to O*NET CSV files")
@click.option("--skip-bls", is_flag=True, help="Skip BLS API call (use existing data)")
@with_appcontext
def seed_market_data(onet_path, skip_bls):
    """
    Seed labor market data from O*NET and BLS sources.

    Downloads and imports:
    - O*NET occupations and skills from local files
    - BLS JOLTS data from API (job openings, hires, quits)

    Example:
        flask seed-market-data --onet-path data/onet/
    """
    click.echo("Starting labor market data seed...")

    # Skip if data already seeded (idempotent for production builds)
    existing = Occupation.query.count()
    if existing > 0:
        click.echo(f"O*NET data already seeded ({existing} occupations). Skipping.")
        return

    # Check if O*NET files exist
    onet_occupation_file = os.path.join(onet_path, "Occupation Data.txt")

    if not os.path.exists(onet_occupation_file):
        click.echo(f"Warning: O*NET occupation file not found at {onet_occupation_file}")
        click.echo("Download from: https://www.onetcenter.org/database.html#individual-files")
        click.echo(
            "Place 'Occupation Data.txt', 'Skills.txt', 'Abilities.txt', 'Knowledge.txt' in the onet-path directory"
        )
    else:
        _seed_onet_occupations(onet_occupation_file)

    # Load O*NET elements (skills, abilities, knowledge)
    onet_files = [
        ("Skills.txt", "skills"),
        ("Abilities.txt", "abilities"),
        ("Knowledge.txt", "knowledge"),
    ]

    for filename, category in onet_files:
        filepath = os.path.join(onet_path, filename)
        if os.path.exists(filepath):
            _seed_onet_elements(filepath, category)
        else:
            click.echo(f"Warning: {filepath} not found")

    if not skip_bls:
        _seed_bls_data()

    click.echo("Labor market data seed complete!")


def _seed_onet_occupations(filepath):
    """Load O*NET occupation data with Job Zone cross-reference."""
    logger.info(f"Loading O*NET occupations from {filepath}...")
    click.echo(f"Loading O*NET occupations from {filepath}...")
    count = 0

    # Load Job Zones for cross-reference
    job_zones = {}
    onet_dir = os.path.dirname(filepath)
    jz_path = os.path.join(onet_dir, "db_30_1_text", "Job Zones.txt")
    if not os.path.exists(jz_path):
        jz_path = os.path.join(onet_dir, "Job Zones.txt")

    if os.path.exists(jz_path):
        click.echo(f"  Loading Job Zones from {jz_path}...")
        with open(jz_path, "r", encoding="utf-8") as jzf:
            jz_reader = csv.DictReader(jzf, delimiter="\t")
            for jz_row in jz_reader:
                code = jz_row.get("O*NET-SOC Code", "")
                zone = jz_row.get("Job Zone", "")
                if code and zone:
                    job_zones[code] = int(zone)
        click.echo(f"  Found {len(job_zones)} Job Zone assignments")
    else:
        click.echo("  Warning: Job Zones.txt not found, skipping job_zone")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                code = row.get("O*NET-SOC Code", row.get("Code", ""))
                occ = Occupation(
                    id=code,
                    title=row.get("Title", ""),
                    description=row.get("Description", ""),
                    job_zone=job_zones.get(code),
                )
                db.session.merge(occ)
                count += 1

                if count % 100 == 0:
                    db.session.commit()
                    click.echo(f"  Loaded {count} occupations...")

        db.session.commit()
        logger.info(f"Loaded {count} O*NET occupations ({len(job_zones)} with job zones)")
        click.echo(f"Loaded {count} O*NET occupations ({len(job_zones)} with job zones)")

    except Exception as e:
        logger.error(f"Error loading occupations: {e}")
        click.echo(f"Error loading occupations: {e}")
        db.session.rollback()


def _seed_onet_elements(filepath: str, category: str):
    """
    Load O*NET element data (skills, abilities, or knowledge).

    Handles dual-scale format: each (occupation, skill) pair has two rows:
    - Scale ID "IM" = Importance (1-5 scale, normalized to 0-100)
    - Scale ID "LV" = Level (0-7 scale, normalized to 0-100)
    """
    logger.info(f"Loading O*NET {category} from {filepath}...")
    click.echo(f"Loading O*NET {category} from {filepath}...")
    elements_loaded = set()

    # Collect both IM and LV values per (occupation, skill) pair
    # Key: (occ_code, element_id) -> {"importance": float, "level": float}
    pair_data: dict[tuple[str, str], dict[str, float]] = {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                element_id = row.get("Element ID", "")
                element_name = row.get("Element Name", "")
                occ_code = row.get("O*NET-SOC Code", "")
                scale_id = row.get("Scale ID", "")
                raw_value = float(row.get("Data Value", 0)) if row.get("Data Value") else 0

                # Create skill/ability/knowledge if not exists
                if element_id and element_id not in elements_loaded:
                    skill = Skill(
                        id=element_id,
                        name=element_name,
                        category=category,
                    )
                    db.session.merge(skill)
                    elements_loaded.add(element_id)

                # Collect scale values per pair
                if occ_code and element_id:
                    key = (occ_code, element_id)
                    if key not in pair_data:
                        pair_data[key] = {}

                    if scale_id == "IM":
                        # Importance: 1-5 scale -> normalize to 0-100
                        pair_data[key]["importance"] = round((raw_value - 1) / 4 * 100, 1)
                    elif scale_id == "LV":
                        # Level: 0-7 scale -> normalize to 0-100
                        pair_data[key]["level"] = round(raw_value / 7 * 100, 1)

        # Commit skills first
        db.session.commit()
        click.echo(
            f"  Found {len(elements_loaded)} unique {category}, {len(pair_data)} occupation mappings"
        )

        # Clear existing mappings for this category to avoid merge overhead
        skill_ids = list(elements_loaded)
        if skill_ids:
            OccupationSkill.query.filter(OccupationSkill.skill_id.in_(skill_ids)).delete(
                synchronize_session=False
            )
            db.session.commit()

        # Batch insert mappings
        batch = []
        for (occ_code, element_id), values in pair_data.items():
            batch.append(
                OccupationSkill(
                    occupation_id=occ_code,
                    skill_id=element_id,
                    importance=values.get("importance", 0),
                    level=values.get("level", 0),
                )
            )

            if len(batch) >= 1000:
                db.session.bulk_save_objects(batch)
                db.session.commit()
                batch = []

        if batch:
            db.session.bulk_save_objects(batch)
            db.session.commit()

        logger.info(
            f"Loaded {len(elements_loaded)} {category}, {len(pair_data)} occupation mappings"
        )
        click.echo(
            f"Loaded {len(elements_loaded)} {category}, {len(pair_data)} occupation mappings"
        )

    except FileNotFoundError:
        logger.warning(f"{filepath} not found, skipping {category}")
        click.echo(f"Warning: {filepath} not found, skipping {category}")
    except Exception as e:
        logger.error(f"Error loading {category}: {e}")
        click.echo(f"Error loading {category}: {e}")
        db.session.rollback()


def _seed_bls_data():
    """Fetch and load BLS JOLTS data."""
    click.echo("Fetching BLS JOLTS data...")

    bls_series = {
        "JTS000000000000000JOL": "openings",
        "JTS000000000000000HIL": "hires",
        "JTS000000000000000QUL": "quits",
    }

    try:
        merged_data = _fetch_bls_data_merged(bls_series)

        if not merged_data:
            click.echo("No BLS data retrieved. Check BLS_API_KEY environment variable.")
            return

        count = 0
        for date_key, values in merged_data.items():
            lmd = LaborMarketData(
                source="BLS_JOLTS",
                region="national",
                data_date=datetime.strptime(date_key, "%Y-%m-%d").date(),
                openings=values.get("openings"),
                hires=values.get("hires"),
                quits=values.get("quits"),
            )
            db.session.add(lmd)
            count += 1

        db.session.commit()
        click.echo(f"Loaded {count} BLS JOLTS records")

    except Exception as e:
        click.echo(f"Error fetching BLS data: {e}")
        db.session.rollback()


def _fetch_bls_data_merged(series_ids):
    """
    Fetch BLS data and merge by date. Falls back to public API if no key.

    Returns dict of {date: {field: value, ...}, ...}
    """
    api_key = os.getenv("BLS_API_KEY", "")

    if not api_key:
        click.echo(
            "INFO: No BLS_API_KEY set. Using public API (v1). "
            "This is fine - seed script only runs once."
        )
        url = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
        payload = {
            "seriesid": list(series_ids.keys()),
            "startyear": "2024",
            "endyear": "2026",
        }
    else:
        url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        payload = {
            "seriesid": list(series_ids.keys()),
            "startyear": "2024",
            "endyear": "2026",
            "registrationkey": api_key,
        }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

    except requests.RequestException as e:
        click.echo(f"BLS API request failed: {e}")
        return {}

    # Merge by date
    merged = defaultdict(dict)
    data = response.json()

    if data.get("status") != "REQUEST_SUCCEEDED":
        click.echo(f"BLS API error: {data.get('message', 'Unknown error')}")
        return {}

    for series in data.get("Results", {}).get("series", []):
        series_id = series["seriesID"]
        field_name = series_ids.get(series_id)

        if not field_name:
            continue

        for item in series.get("data", []):
            period = item.get("period", "")
            if not period.startswith("M"):
                continue

            month = period[1:].zfill(2)
            date_key = f"{item['year']}-{month}-01"
            value = int(float(item.get("value", 0)) * 1000)  # BLS reports in thousands
            merged[date_key][field_name] = value

    return merged


@click.command("reset-usage")
@with_appcontext
def reset_usage():
    """
    Reset monthly usage for users whose reset date has passed.

    This can be run as a cron job to ensure usage resets happen
    even if users don't log in.

    Example:
        flask reset-usage
    """
    from app.models.user import User

    click.echo("Checking for users needing usage reset...")

    users = User.query.filter(User.usage_reset_date <= datetime.utcnow()).all()

    if not users:
        click.echo("No users need usage reset.")
        return

    count = 0
    for user in users:
        user.reset_monthly_usage()
        count += 1

    db.session.commit()
    click.echo(f"Reset usage for {count} users")
