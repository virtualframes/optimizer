import hashlib


class Fingerprint:
    def generate(self, data):
        """
        Generates a fingerprint for the given data.
        Placeholder for now. Uses SHA256.
        """
        if not isinstance(data, bytes):
            data = str(data).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
