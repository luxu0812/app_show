from dataclasses import dataclass

@dataclass(frozen=True)
class AppEntry:
    rank: int
    app_name: str
    artist: str
    icon_url: str
    country: str
    chart_type: str
    fetched_date: str