from __future__ import annotations
from bevy import AutoInject, detect_dependencies
from enum import IntEnum, auto
from pathlib import Path
from sympyosis import Options
import sqlite3


class ProcessStatus(IntEnum):
    RUNNING = auto()
    STARTING = auto()
    STOPPED = auto()
    STOPPING = auto()
    DELETED = auto()


class ProcessModel:
    def __init__(
        self,
        service: str,
        pid: int,
        port: int,
        status: ProcessStatus | int,
        *,
        db: Database,
    ):
        self._service = service
        self._pid = pid
        self._port = port
        self._status = ProcessStatus(status)
        self._db = db

    @property
    def service(self) -> str:
        return self._service

    @property
    def pid(self) -> int:
        return self._pid

    @property
    def port(self) -> int:
        return self._port

    @property
    def status(self) -> ProcessStatus:
        return self._status

    @status.setter
    def status(self, status: ProcessStatus):
        self._db.update_process_status(self.pid, status)
        self._status = status

    def delete(self):
        self._db.delete_process(self.pid)
        self._status = ProcessStatus.DELETED

    def __repr__(self):
        return f"{type(self).__name__}(service={self.service!r}, pid={self.pid}, port={self.port}, status={self.status})"


@detect_dependencies
class Database(AutoInject):
    options: Options

    def __init__(self):
        self.db = self._get_database()

    @property
    def version(self) -> int:
        query = "SELECT * FROM Metadata WHERE key == 'DB_VERSION';"
        row = self.db.execute(query).fetchone()
        return int(row[1])

    @property
    def file_path(self) -> Path:
        file_name = self.options.get("PROCLIST_FILE_NAME", "sympyosis_proclist")
        return Path(self.options[self.options.path_option_name]) / file_name

    def add_process(
        self, service: str, pid: int, port: int, status: ProcessStatus
    ) -> ProcessModel:
        self.db.execute(
            "INSERT INTO Processes(service, pid, port, status) VALUES(?, ?, ?, ?);",
            (service, pid, port, status.value),
        )
        self.db.commit()
        return ProcessModel(service, pid, port, status, db=self)

    def get_processes(self, status: ProcessStatus | None = None) -> list[ProcessModel]:
        query = "SELECT * FROM Processes"
        parameters = tuple()
        if status is not None:
            query += " WHERE status = ?"
            parameters = (status.value,)

        query += ";"

        return [
            ProcessModel(*row, db=self) for row in self.db.execute(query, parameters)
        ]

    def update_process_status(self, pid: int, status: ProcessStatus):
        self.db.execute(
            "UPDATE Processes SET status=? WHERE pid=?;", (status.value, pid)
        )
        self.db.commit()

    def delete_process(self, pid: int):
        self.db.execute("DELETE FROM Processes WHERE pid=?;", (pid,))
        self.db.commit()

    def _build_database(self, db: sqlite3.Connection):
        db.execute(
            "CREATE TABLE Processes("
            "    service VARCHAR(255),"
            "    pid INTEGER,"
            "    port INTEGER,"
            "    status INTEGER"
            ");"
        )

        db.execute("CREATE TABLE Metadata(key VARCHAR(64), value VARCHAR(256));")
        db.execute("INSERT INTO Metadata(key, value) VALUES('DB_VERSION', '0');")
        db.commit()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.file_path.resolve())

    def _get_database(self) -> sqlite3.Connection:
        exists = self.file_path.exists()
        db = self._connect()

        if not exists:
            self._build_database(db)

        return db
