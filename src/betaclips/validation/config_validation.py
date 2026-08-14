def validate_timeout(value) -> int:
    timeout = int(value)
    if not 0 <= timeout <= 86400:
        raise ValueError(f"Timeout: {timeout} not allowed; must be set between 0 and 86400 seconds")
    else:
        return timeout
