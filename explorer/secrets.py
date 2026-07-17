import subprocess


KEYCHAIN_SERVICE = "browser-code-explorer"
KEYCHAIN_ACCOUNT = "openai-api-key"


def get_openai_api_key() -> str:
    result = subprocess.run(
        [
            "security",
            "find-generic-password",
            "-s",
            KEYCHAIN_SERVICE,
            "-a",
            KEYCHAIN_ACCOUNT,
            "-w",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "OpenAI API key was not found in macOS Keychain."
        )

    api_key = result.stdout.strip()

    if not api_key:
        raise RuntimeError(
            "OpenAI API key was not found in macOS Keychain."
        )

    return api_key
