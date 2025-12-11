from typing import Optional

from src import meta
from src.model.store import JSONStore


class StoreService:
    _instance: Optional["StoreService"] = None

    def __init__(self) -> None:
        if StoreService._instance is not None:
            raise ValueError("StoreService 只能实例化一次")

        self.store: JSONStore = JSONStore(meta.STORE_PATH)

        self.store.open()

        StoreService._instance = self

    @staticmethod
    def get_instance() -> "StoreService":
        if StoreService._instance is None:
            StoreService._instance = StoreService()

        return StoreService._instance

    def get_store(self) -> JSONStore:
        return self.store

    def dump(self):
        self.store.dump()
