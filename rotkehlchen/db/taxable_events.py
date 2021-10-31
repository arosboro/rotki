import logging
import pickle
from typing import TYPE_CHECKING, Dict, List, Any

from rotkehlchen.errors import DeserializationError
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.typing import Timestamp
from rotkehlchen.user_messages import MessagesAggregator

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)

if TYPE_CHECKING:
    from rotkehlchen.db.dbhandler import DBHandler


def serialize_to_db(event: Dict[str, Any]) -> bytes:
    """
    Serialize the event for insertion into the database.
    :param event:
    :return: The bytes representation of the event
    """
    return pickle.dumps(event)


def deserialize_from_db(result: bytes) -> Dict[str, Any]:
    """
    Deserialize the event as it was stored in the database.

    :param result: A SELECT query result; specifically a bytes blob contained in the data column
    :return event: The typed event
    """
    return pickle.loads(result)


class DBTaxableEvents():

    def __init__(self, database: 'DBHandler', msg_aggregator: MessagesAggregator):
        self.db = database
        self.msg_aggregator = msg_aggregator

    def add_report(self, start_ts: Timestamp, end_ts: Timestamp) -> int:
        cursor = self.db.conn_transient.cursor()
        query = """
        INSERT INTO pnl_reports(
            name, start_ts, end_ts
        )
        VALUES (?, ?, ?)"""
        cursor.execute(query, (f"Report from {start_ts} to {end_ts}", start_ts, end_ts))
        identifier = cursor.lastrowid
        self.db.conn_transient.commit()
        return identifier

    def add_event(self, report_id: int, time: Timestamp, event: dict) -> None:
        """Adds a new event to a transient report for the PnL history in a given time range

        May raise:
        - sqlcipher.IntegrityError if there is a conflict at serialization of the event
        """
        cursor = self.db.conn_transient.cursor()
        query = """
        INSERT INTO pnl_events(
            report_id, timestamp, data
        )
        VALUES(?, ?, ?);"""
        cursor.execute(query, (report_id, time, serialize_to_db(event)))
        self.db.conn_transient.commit()

    def get_events(self,
                   report_id: int,
                   page: int = 0,
                   rows_per_page: int = 10) -> List[Dict[str, Any]]:
        cursor = self.db.conn_transient.cursor()
        offset = page * rows_per_page
        query = """
        SELECT data from pnl_events
        WHERE report_id = ?
        ORDER BY timestamp asc
        LIMIT ? OFFSET ?;"""
        results = cursor.execute(query, (report_id, rows_per_page, offset))

        events = []
        for result in results:
            log.debug(f"get_all_events result: {result}")
            try:
                event = deserialize_from_db(result[0])
            except DeserializationError as e:
                self.msg_aggregator.add_error(
                    f'Error deserializing PnL Event for Report from the DB. Skipping it.'
                    f'Error was: {str(e)}',
                )
                continue

            events.append(event)

        return events
