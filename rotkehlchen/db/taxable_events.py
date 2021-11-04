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


def deserialize_report_from_db(report: Any) -> Dict[str, Any]:
    return {
        'identifier': report[0],
        'name': report[1],
        'created': report[2],
        'start_ts': report[3],
        'end_ts': report[4],
        'size_on_disk': report[5],
    }


def serialize_event_to_db(event: Dict[str, Any]) -> bytes:
    """
    Serialize the event for insertion into the database.
    :param event:
    :return: The bytes representation of the event
    """
    return pickle.dumps(event)


def deserialize_event_from_db(result: bytes) -> Dict[str, Any]:
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

    def get_reports(self,
                    page: int,
                    rows_per_page: int = 10,
                    report_id: int = 0) -> List[Dict[str, Any]]:
        cursor = self.db.conn_transient.cursor()
        offset = page * rows_per_page
        selected = report_id if report_id else '*'
        query = """
        SELECT ? FROM pnl_reports
        LIMIT ? OFFSET ?"""
        results = cursor.execute(query, (selected, rows_per_page, offset))

        reports = []
        for result in results:
            log.debug(f"get_reports result: {result}")
            try:
                report = deserialize_report_from_db(result)
            except DeserializationError as e:
                self.msg_aggregator.add_error(
                    f'Error deserializing PnL Report for index from the DB. Skipping it.'
                    f'Error was: {str(e)}',
                )
                continue

            reports.append(report)

        return reports

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
        cursor.execute(query, (report_id, time, serialize_event_to_db(event)))
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
            log.debug(f"get_events result: {result}")
            try:
                event = deserialize_event_from_db('event', result[0])
            except DeserializationError as e:
                self.msg_aggregator.add_error(
                    f'Error deserializing PnL Event for Report from the DB. Skipping it.'
                    f'Error was: {str(e)}',
                )
                continue

            events.append(event)

        return events

    def get_all_events(self, report_id: int) -> List[Dict[str, Any]]:
        cursor = self.db.conn_transient.cursor()
        query = """
                SELECT data from pnl_events
                WHERE report_id = ?
                ORDER BY timestamp asc;"""
        results = cursor.execute(query, report_id)

        events = []
        for result in results:
            log.debug(f"get_all_events result: {result}")
            try:
                event = deserialize_event_from_db(result[0])
            except DeserializationError as e:
                self.msg_aggregator.add_error(
                    f'Error deserializing PnL Event for Report from the DB. Skipping it.'
                    f'Error was: {str(e)}',
                )
                continue

            events.append(event)

        return events
