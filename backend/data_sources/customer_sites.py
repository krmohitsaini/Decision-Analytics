import csv
import os
from pathlib import Path


DEFAULT_CSV_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "Dataset"
    / "synthetic_energy_customer_sites.csv"
)


class CustomerSitesSourceError(RuntimeError):
    """Raised when the configured customer sites source cannot be used."""


class CsvCustomerSitesSource:
    source_type = "csv"
    grain = "One site-level contract episode per row"

    def __init__(self, path=None):
        self.path = Path(path or DEFAULT_CSV_PATH)

    @property
    def name(self):
        return self.path.name

    def is_available(self):
        return self.path.exists()

    def iter_contract_episodes(self):
        if not self.is_available():
            raise CustomerSitesSourceError(f"Customer sites CSV not found: {self.path}")

        with self.path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            yield from reader


class DatabricksCustomerSitesSource:
    source_type = "databricks"
    grain = "One site-level contract episode per row"

    def __init__(self, table_name=None):
        self.table_name = table_name or os.getenv("CUSTOMER_SITES_DATABRICKS_TABLE", "")

    @property
    def name(self):
        return self.table_name or "Databricks customer sites table"

    def is_available(self):
        return False

    def iter_contract_episodes(self):
        raise CustomerSitesSourceError(
            "Databricks customer sites source is configured but not implemented yet."
        )


def build_customer_sites_source():
    source_type = os.getenv("CUSTOMER_SITES_SOURCE", "csv").strip().lower()

    if source_type == "csv":
        return CsvCustomerSitesSource(os.getenv("CUSTOMER_SITES_CSV_PATH") or None)

    if source_type == "databricks":
        return DatabricksCustomerSitesSource()

    raise CustomerSitesSourceError(f"Unsupported customer sites source: {source_type}")
