from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    headless: bool = False
    max_depth: int = 3
    max_files: int = 50
    timeout_ms: int = 30000


settings = Settings()
