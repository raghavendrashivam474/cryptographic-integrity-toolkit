"""Exception classes for the integrity_toolkit.merkle package."""


class MerkleError(Exception):
    """Base exception for all Merkle subsystem errors."""


class EmptyTreeError(MerkleError, ValueError):
    """Raised when tree construction is requested on an empty leaf sequence."""


class InvalidNodeDigestError(MerkleError, ValueError):
    """Raised when an internal node child digest is invalid (malformed hex or wrong length)."""


class AdapterError(MerkleError, ValueError):
    """Raised when manifest conversion to Merkle leaf bytes fails."""


class InvalidProofError(MerkleError, ValueError):
    """Raised when a Merkle inclusion proof is structurally or mathematically invalid."""
