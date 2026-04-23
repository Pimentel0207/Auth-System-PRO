"""
Rate limiter configuration using slowapi.

Provides IP-based rate limiting for auth endpoints
to prevent brute-force attacks.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)
