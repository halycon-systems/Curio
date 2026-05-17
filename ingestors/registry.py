from ingestors.bog_bodies import BogBodiesIngestor
from ingestors.handcrafted_json import discover as discover_handcrafted
from ingestors.monasteries import MonasteriesIngestor


def get_ingestors():
    return [
        BogBodiesIngestor(),
        MonasteriesIngestor(),
        *discover_handcrafted(),
    ]
