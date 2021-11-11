import logging
import pickle
from pysqlcipher3 import dbapi2 as sqlcipher
from typing import TYPE_CHECKING, Dict, List, Any, Tuple, Optional

from rotkehlchen.accounting.accountant import FREE_PNL_EVENTS_LIMIT
from rotkehlchen.db.filtering import ReportsFilterQuery, DBEventsReportIDFilter
from rotkehlchen.db.ranges import DBQueryRanges
from rotkehlchen.errors import DeserializationError
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.typing import Timestamp
from rotkehlchen.user_messages import MessagesAggregator
from rotkehlchen.utils.misc import ts_now
from rotkehlchen.utils.mixins.lockable import LockableQueryMixIn, protect_with_lock

FREE_REPORTS_LOOKUP_LIMIT = 20

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)

if TYPE_CHECKING:
    from rotkehlchen.db.dbhandler import DBHandler


def deserialize_report_from_db(report: Any) -> Dict[str, Any]:
    return {
        'identifier': report[0],
        'name': report[1],
        'timestamp': report[2],
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


def _return_reports_or_events_maybe_limit(
        entry_type: str,
        entries: List[Dict[str, Any]],
        with_limit: bool,
) -> List[Dict[str, Any]]:
    if with_limit is False:
        return entries

    if entry_type == 'events':
        limit = FREE_PNL_EVENTS_LIMIT
    else:
        limit = FREE_REPORTS_LOOKUP_LIMIT

    count: int = 0
    for _ in entries:
        count += 1

    returning_entries_length = min(limit, len(entries))

    return entries[:returning_entries_length]


class DBTaxableEvents(LockableQueryMixIn):

    def __init__(self,
                 database: 'DBHandler',
                 msg_aggregator: MessagesAggregator):
        super().__init__()
        self.db = database
        self.msg_aggregator = msg_aggregator

    @protect_with_lock()
    def query(
            self,
            filter_query: ReportsFilterQuery,
            with_limit: bool = False,
            only_cache: bool = False,
    ) -> List[Dict[str, Any]]:
        """Queries for all reports/events of a Profit and Loss Report which has been performed
        historically. Returns a list of all transactions filtered and sorted according to the
        parameters.

        If `with_limit` is true then the api limit is applied

        if `recent_first` is true then the transactions are returned with the most
        recent first on the list

        May raise:
        - TODO check what it may raise
        """
        report_id = filter_query.report_id or None

        if only_cache is False:
            # f_from_ts = filter_query.from_ts
            # f_to_ts = filter_query.to_ts
            # from_ts = Timestamp(0) if f_from_ts is None else f_from_ts
            # to_ts = ts_now() if f_to_ts is None else f_to_ts
            if report_id is not None:
                # TODO: only_cache was False, we need to hand off
                #  what we have and generate the rest
                pass

        if report_id is None:
            entries = self.get_reports(filter_=filter_query)
        else:
            report = self.get_reports(filter_=filter_query)[0]
            events_filter_query = filter_query
            events_filter_query.report_id_filter = DBEventsReportIDFilter(and_op=True,
                                                                          report_id=report_id)
            entries = self.get_events(filter_=events_filter_query)
        entry_type = 'reports' if report_id is None else 'events'
        if entry_type == 'reports':
            return _return_reports_or_events_maybe_limit(
                entry_type=entry_type,
                entries=entries,
                with_limit=with_limit,
            )
        else:
            events = _return_reports_or_events_maybe_limit(
                entry_type=entry_type,
                entries=entries,
                with_limit=with_limit,
            )
            report['events'] = events
            return [report]

    def get_reports(self,
                    filter_: ReportsFilterQuery,
                    ) -> List[Dict[str, Any]]:
        cursor = self.db.conn_transient.cursor()
        query, bindings = filter_.prepare()
        query = 'SELECT * FROM pnl_reports ' + query
        results = cursor.execute(query, bindings)

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

    def get_report(self, filter_: ReportsFilterQuery) -> Optional[Dict[str, Any]]:
        cursor = self.db.conn_transient.cursor()
        query, bindings = filter_.prepare()
        query = 'SELECT * FROM pnl_reports ' + query
        results = cursor.execute(query, bindings)
        result = results.fetchone()
        if result is None:
            return None

        try:
            report = deserialize_report_from_db(result)
        except DeserializationError as e:
            self.msg_aggregator.add_error(
                f'Error deserializing PnL Report from the DB. Skipping it.'
                f'Error was: {str(e)}',
            )
            pass

        return report

    def get_events(self, filter_: ReportsFilterQuery) -> List[Dict[str, Any]]:
        cursor = self.db.conn_transient.cursor()
        query, bindings = filter_.prepare()
        query = 'SELECT data FROM pnl_events ' + query
        results = cursor.execute(query, bindings)

        events = []
        for result in results:
            log.debug(f"get_events result: {result}")
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

    def add_report(self, start_ts: Timestamp, end_ts: Timestamp) -> int:
        cursor = self.db.conn_transient.cursor()
        timestamp = ts_now()
        query = """
        INSERT INTO pnl_reports(
            name, timestamp, start_ts, end_ts
        )
        VALUES (?, ?, ?, ?)"""
        cursor.execute(query, (f"Report from {start_ts} to {end_ts}", timestamp, start_ts, end_ts))
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

    def add_events(self, report_id: int, events: List[Dict[str, Any]]) -> None:
        """Adds taxable events to the database"""
        event_tuples: List[Tuple[Any, ...]] = []
        for event in events:
            event_tuples.append((
                report_id,
                event['time'],
                serialize_event_to_db(event),
            ))

        query = """
            INSERT INTO pnl_events(
              report_id,
              timestamp,
              event
            )
            VALUES (?, ?, ?)
        """
        self.db.write_tuples(
            tuple_type='pnl_event',
            query=query,
            tuples=event_tuples,
        )

    def get_or_query_report_events(
            self,
            report_id: int,
            start_ts: Timestamp,
            end_ts: Timestamp,
    ) -> Tuple[List[Dict[str, Any]], Optional[Timestamp], Optional[Timestamp]]:
        """Only queries cached events and prepares them for the response"""
        ranges = DBQueryRanges(self.db)
        ranges_to_query = ranges.get_location_query_ranges(
            location_string=f'pnl_events_{report_id}',
            start_ts=start_ts,
            end_ts=end_ts,
        )
        cache_data = []
        query_start_ts = None
        query_end_ts = None
        for query_start_ts, query_end_ts in ranges_to_query:
            try:
                cache_data = self.get_events(filter_=ReportsFilterQuery.make(report_id=report_id))
            except sqlcipher.DatabaseError as e:  # pylint: disable=no-member
                self.msg_aggregator.add_error(
                    f'Got error "{str(e)}" while querying the reports cache '
                    f'from rotki. Events not added to the DB '
                    f'from_ts: {query_start_ts} '
                    f'to_ts: {query_end_ts} ',
                )

        # and also set the last queried timestamps for the report
        ranges.update_used_query_range(
            location_string=f'pnl_events_{report_id}',
            start_ts=start_ts,
            end_ts=end_ts,
            ranges_to_query=ranges_to_query,
        )
        log.debug(f"___cachedata___ {cache_data[0]}")

        return cache_data, query_start_ts, query_end_ts

    # def get_events(self,
    #                report_id: int,
    #                from_ts: int,
    #                to_ts: int) -> List[Dict[str, Any]]:
    #     cursor = self.db.conn_transient.cursor()
    #     offset = page * rows_per_page
    #     query = """
    #     SELECT data from pnl_events
    #     WHERE report_id = ?
    #     ORDER BY timestamp asc
    #     LIMIT ? OFFSET ?;"""
    #     results = cursor.execute(query, (report_id, rows_per_page, offset))
    #
    #     events = []
    #     for result in results:
    #         log.debug(f"get_events result: {result}")
    #         try:
    #             event = deserialize_event_from_db(result[0])
    #         except DeserializationError as e:
    #             self.msg_aggregator.add_error(
    #                 f'Error deserializing PnL Event for Report from the DB. Skipping it.'
    #                 f'Error was: {str(e)}',
    #             )
    #             continue
    #
    #         events.append(event)
    #
    #     return events
    #
    # def get_all_events(self, report_id: int) -> List[Dict[str, Any]]:
    #     cursor = self.db.conn_transient.cursor()
    #     query = """
    #             SELECT data from pnl_events
    #             WHERE report_id = ?
    #             ORDER BY timestamp asc;"""
    #     results = cursor.execute(query, report_id)
    #
    #     events = []
    #     for result in results:
    #         log.debug(f"get_all_events result: {result}")
    #         try:
    #             event = deserialize_event_from_db(result[0])
    #         except DeserializationError as e:
    #             self.msg_aggregator.add_error(
    #                 f'Error deserializing PnL Event for Report from the DB. Skipping it.'
    #                 f'Error was: {str(e)}',
    #             )
    #             continue
    #
    #         events.append(event)
    #
    #     return events
