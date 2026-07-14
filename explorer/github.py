from urllib.parse import urlparse


def normalize_repository(value: str) -> str:
    value = value.strip().rstrip("/")

    if value.startswith("https://github.com/"):
        parts = [p for p in urlparse(value).path.split("/") if p]
        if len(parts) < 2:
            raise ValueError("Invalid GitHub repository URL.")
        return f"https://github.com/{parts[0]}/{parts[1]}"

    if value.count("/") == 1:
        return f"https://github.com/{value}"

    raise ValueError("Use owner/repository or a GitHub repository URL.")
