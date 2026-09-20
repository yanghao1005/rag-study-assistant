import hashlib


class EmbeddingsProvider:
    def embed(self, text: str) -> list[float]:
        if not text:
            return [0.0] * 8

        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector: list[float] = []
        for index in range(0, 16, 2):
            value = int.from_bytes(digest[index : index + 2], byteorder="big", signed=False)
            vector.append(round((value / 65535.0) * 2 - 1, 6))
        return vector
