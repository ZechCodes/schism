from sympyosis.ext.processes.database import Database, ProcessStatus
import sqlite3


class MemoryDB(Database):
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self._build_database(self.db)


def test_db_version():
    db = MemoryDB()
    assert db.version == 0


def test_get_processes():
    db = MemoryDB()
    db.add_process("Test 1", 0, 8080, ProcessStatus.STOPPED)
    db.add_process("Test 2", 1, 8081, ProcessStatus.RUNNING)

    assert len(db.get_processes()) == 2
    assert len(db.get_processes(ProcessStatus.RUNNING)) == 1


def test_delete_processes():
    db = MemoryDB()
    db.add_process("Test 1", 0, 8080, ProcessStatus.RUNNING)

    process = db.get_processes()[0]
    assert process.status == ProcessStatus.RUNNING

    process.delete()
    assert process.status == ProcessStatus.DELETED
    assert len(db.get_processes()) == 0
