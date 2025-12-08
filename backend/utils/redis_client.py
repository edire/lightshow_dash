import redis
import os
from typing import Optional

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

def get_redis_client() -> redis.Redis:
    """Get Redis client instance."""
    return redis.from_url(REDIS_URL, decode_responses=True)

# Refresh token storage helpers
def store_refresh_token(token_hash: str, user_email: str, expires_in_seconds: int) -> None:
    """
    Store refresh token hash in Redis.
    Key format: refresh_token:{token_hash}
    Value: JSON with user_email, created_at, last_used_at
    """
    client = get_redis_client()
    import json
    from datetime import datetime

    data = {
        "user_email": user_email,
        "created_at": datetime.utcnow().isoformat(),
        "last_used_at": datetime.utcnow().isoformat(),
        "revoked": False
    }

    client.setex(
        f"refresh_token:{token_hash}",
        expires_in_seconds,
        json.dumps(data)
    )

def get_refresh_token_data(token_hash: str) -> Optional[dict]:
    """Get refresh token data from Redis."""
    client = get_redis_client()
    import json

    data = client.get(f"refresh_token:{token_hash}")
    if data:
        return json.loads(data)
    return None

def update_refresh_token_last_used(token_hash: str) -> None:
    """Update last_used_at timestamp for refresh token."""
    client = get_redis_client()
    import json
    from datetime import datetime

    data = get_refresh_token_data(token_hash)
    if data:
        data["last_used_at"] = datetime.utcnow().isoformat()
        ttl = client.ttl(f"refresh_token:{token_hash}")
        if ttl > 0:
            client.setex(
                f"refresh_token:{token_hash}",
                ttl,
                json.dumps(data)
            )

def revoke_refresh_token(token_hash: str) -> None:
    """Revoke (delete) refresh token from Redis."""
    client = get_redis_client()
    client.delete(f"refresh_token:{token_hash}")

def revoke_all_user_tokens(user_email: str) -> None:
    """
    Revoke all refresh tokens for a user.
    WARNING: This requires scanning all keys, use sparingly.
    """
    client = get_redis_client()
    import json

    cursor = 0
    while True:
        cursor, keys = client.scan(cursor, match="refresh_token:*", count=100)

        for key in keys:
            data = client.get(key)
            if data:
                token_data = json.loads(data)
                if token_data.get("user_email") == user_email:
                    client.delete(key)

        if cursor == 0:
            break

def mark_token_as_revoked(token_hash: str) -> None:
    """
    Mark token as revoked (for reuse detection).
    Keep the token in Redis but mark it as revoked.
    """
    client = get_redis_client()
    import json

    data = get_refresh_token_data(token_hash)
    if data:
        data["revoked"] = True
        ttl = client.ttl(f"refresh_token:{token_hash}")
        if ttl > 0:
            client.setex(
                f"refresh_token:{token_hash}",
                ttl,
                json.dumps(data)
            )

def is_token_revoked(token_hash: str) -> bool:
    """Check if token is marked as revoked."""
    data = get_refresh_token_data(token_hash)
    if data:
        return data.get("revoked", False)
    return True  # If token doesn't exist, consider it revoked
