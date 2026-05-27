from uuid import (
    NAMESPACE_DNS,
    NAMESPACE_OID,
    NAMESPACE_URL,
    NAMESPACE_X500,
    RESERVED_FUTURE,
    RESERVED_MICROSOFT,
    RESERVED_NCS,
    RFC_4122,
    UUID,
    SafeUUID,
    getnode,
)

import uuid_utils
from uuid_utils import _uuid4_int, _uuid7_int

NIL = UUID("00000000-0000-0000-0000-000000000000")
MAX = UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")


def _from_int(n: int) -> UUID:
    u = object.__new__(UUID)
    object.__setattr__(u, "int", n)
    object.__setattr__(u, "is_safe", SafeUUID.unknown)
    return u


def uuid1(node=None, clock_seq=None):
    """Generate a UUID from a host ID, sequence number, and the current time.
    If 'node' is not given, getnode() is used to obtain the hardware
    address.  If 'clock_seq' is given, it is used as the sequence number;
    otherwise a random 14-bit sequence number is chosen."""
    return _from_int(uuid_utils.uuid1(node, clock_seq).int)


def uuid3(namespace, name):
    """Generate a UUID from the MD5 hash of a namespace UUID and a name."""
    namespace = uuid_utils.UUID(namespace.hex) if namespace else namespace
    return _from_int(uuid_utils.uuid3(namespace, name).int)


def uuid4():
    """Generate a random UUID."""
    return _from_int(_uuid4_int())


def uuid5(namespace, name):
    """Generate a UUID from the SHA-1 hash of a namespace UUID and a name."""
    namespace = uuid_utils.UUID(namespace.hex) if namespace else namespace
    return _from_int(uuid_utils.uuid5(namespace, name).int)


def uuid6(node=None, timestamp=None):
    """Generate a version 6 UUID using the given timestamp and a host ID.
    This is similar to version 1 UUIDs,
    except that it is lexicographically sortable by timestamp.
    """
    return _from_int(uuid_utils.uuid6(node, timestamp).int)


def uuid7(timestamp=None, nanos=None):
    """Generate a version 7 UUID using a time value and random bytes."""
    return _from_int(_uuid7_int(timestamp, nanos))


def uuid8(bytes):
    """Generate a custom UUID comprised almost entirely of user-supplied bytes."""
    return _from_int(uuid_utils.uuid8(bytes).int)


__all__ = [
    "MAX",
    "NAMESPACE_DNS",
    "NAMESPACE_OID",
    "NAMESPACE_URL",
    "NAMESPACE_X500",
    "NIL",
    "RESERVED_FUTURE",
    "RESERVED_MICROSOFT",
    "RESERVED_NCS",
    "RFC_4122",
    "UUID",
    "getnode",
    "uuid1",
    "uuid3",
    "uuid4",
    "uuid5",
    "uuid6",
    "uuid7",
    "uuid8",
]
