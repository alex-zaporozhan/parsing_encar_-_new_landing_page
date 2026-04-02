from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_sqlite_path() -> str:
    return str(Path(__file__).resolve().parents[2] / "data" / "encar.db")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    sqlite_path: str = Field(default_factory=_default_sqlite_path)
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # ENCAR fetch job (see app/jobs/fetch_encar.py)
    encar_list_url: str = "https://api.encar.com/search/car/list/premium"
    encar_search_query: str = "(And.Hidden.N._.CarType.N.)"
    encar_sort: str = "ModifiedDate"
    encar_page_size: int = 20
    encar_max_pages: int = 5
    encar_request_delay_sec: float = 1.0
    encar_user_agent: str = "ENCAR-LandingBot/1.0 (+https://github.com/your-org/parser_landing; contact@example.com)"
    encar_photo_base: str = "https://ci.encar.com"
    # Карточка объявления: актуальный фронт — fem.encar.com (старый fc_cardetailview.do часто отдаёт 502).
    encar_detail_url_template: str = "https://fem.encar.com/cars/detail/{car_id}"


settings = Settings()
