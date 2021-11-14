import json
from enum import Enum
from typing import Tuple, NamedTuple, Dict, Any, Union, Optional

import jsonschema

from rotkehlchen.assets.asset import Asset
from rotkehlchen.errors import DeserializationError, EncodingError
from rotkehlchen.fval import FVal
from rotkehlchen.serialization.deserialize import deserialize_asset_amount, deserialize_timestamp
from rotkehlchen.typing import EventType, Location, EmptyStr, Timestamp


class AccountingEventType(Enum):
    """Supported schemas"""
    ACCOUNTING_HISTORY = 1
    ACCOUNTING_OVERVIEW = 2
    ACCOUNTING_EVENT = 3

    def serialize_for_db(self) -> str:
        if self == AccountingEventType.ACCOUNTING_OVERVIEW:
            return 'accounting_overview'
        if self == AccountingEventType.ACCOUNTING_EVENT:
            return 'accounting_event'
        raise RuntimeError(f'Corrupt value {self} for EventType -- Should never happen')

    @classmethod
    def deserialize_from_db(
            cls,
            value: str,
    ) -> 'AccountingEventType':
        """May raise DeserializationError if anything is wrong"""
        if value == 'accounting_overview':
            return AccountingEventType.ACCOUNTING_OVERVIEW
        if value == 'accounting_event':
            return AccountingEventType.ACCOUNTING_EVENT

        raise DeserializationError(f'Unexpected value {value} at JsonSchema deserialization')

    def __str__(self) -> str:
        if self == AccountingEventType.ACCOUNTING_OVERVIEW:
            return 'accounting_overview'
        if self == AccountingEventType.ACCOUNTING_EVENT:
            return 'accounting_event'
        raise RuntimeError(f'Corrupt value {self} for EventType -- Should never happen')

    def serialize(self) -> Dict[str, Any]:
        """May raise EncodingError if schema is invalid"""
        try:
            schema: Dict[str, Any] = {}
            if self == AccountingEventType.ACCOUNTING_OVERVIEW:
                schema = {
                    'type': 'object',
                    'properties': {
                        'ledger_actions_profit_loss': {'type': 'string'},
                        'defi_profit_loss': {'type': 'string'},
                        'loan_profit': {'type': 'string'},
                        'margin_positions_profit_loss': {'type': 'string'},
                        'settlement_losses': {'type': 'string'},
                        'ethereum_transaction_gas_costs': {'type': 'string'},
                        'asset_movement_fees': {'type': 'string'},
                        'general_trade_profit_loss': {'type': 'string'},
                        'taxable_trade_profit_loss': {'type': 'string'},
                        'total_taxable_profit_loss': {'type': 'string'},
                        'total_profit_loss': {'type': 'string'},
                    },
                    'required': [
                        'ledger_actions_profit_loss',
                        'defi_profit_loss',
                        'loan_profit',
                        'margin_positions_profit_loss',
                        'settlement_losses',
                        'ethereum_transaction_gas_costs',
                        'asset_movement_fees',
                        'general_trade_profit_loss',
                        'taxable_trade_profit_loss',
                        'total_taxable_profit_loss',
                        'total_profit_loss',
                    ]}
            if self == AccountingEventType.ACCOUNTING_EVENT:
                schema = {
                    'type': 'object',
                    'properties': {
                        'event_type': {'type': 'string'},
                        'location': {'type': 'string'},
                        'paid_in_profit_currency': {'type': 'string'},
                        'paid_asset': {'type': 'string'},
                        'paid_in_asset': {'type': 'string'},
                        'taxable_amount': {'type': 'string'},
                        'taxable_bought_cost_in_profit_currency': {'type': 'string'},
                        'received_asset': {'type': 'string'},
                        'taxable_received_in_profit_currency': {'type': 'string'},
                        'received_in_asset': {'type': 'string'},
                        'net_profit_or_loss': {'type': 'string'},
                        'time': {'type': 'number'},
                        'cost_basis': {
                            'oneOf': [{'type': 'null'}, {'$ref': '#/$defs/cost_basis'}],
                        },
                        'is_virtual': {'type': 'boolean'},
                        'link': {'oneOf': [{'type': 'string'}, {'type': 'null'}]},
                        'notes': {'oneOf': [{'type': 'string'}, {'type': 'null'}]},
                    },
                    '$defs': {
                        'cost_basis': {
                            'type': 'object',
                            'properties': {
                                'is_complete': {'type': 'boolean'},
                                'matched_acquisitions': {'type': 'array'},
                                'taxable_bought_cost': {'type': 'string'},
                                'taxfree_bought_cost': {'type': 'string'},
                            },
                        },
                    },
                    'required': [
                        'location',
                        'paid_in_profit_currency',
                        'paid_in_asset',
                        'taxable_amount',
                        'taxable_bought_cost_in_profit_currency',
                        'taxable_received_in_profit_currency',
                        'received_in_asset',
                        'net_profit_or_loss',
                        'time',
                        'cost_basis',
                        'is_virtual',
                        'link',
                        'notes',
                    ]}

            jsonschema.Draft4Validator.check_schema(schema)
            return schema

        except jsonschema.exceptions.SchemaError as e:
            raise EncodingError(f'Could not serialize the AccountingEventType. Invalid schema: {e}')  # noqa E501


NamedJsonDBTuple = (
    Tuple[
        str,  # type,
        str,  # data
    ]
)


class NamedJson(NamedTuple):
    event_type: AccountingEventType
    data: Dict[str, Any]

    @classmethod
    def deserialize_from_db(
            cls,
            json_tuple: NamedJsonDBTuple,
    ) -> 'NamedJson':
        """Turns a tuple read from the database into an appropriate JsonSchema.
        May raise:
         - a DeserializationError if something is wrong with the DB data or json validation fails.
        Event_tuple index - Schema columns
        ----------------------------------
        0 - event_type
        1 - data
        """
        try:
            event_type: AccountingEventType = AccountingEventType.deserialize_from_db(json_tuple[0])  # noqa E501
            schema: Dict[str, Any] = event_type.serialize()
            data = json.loads(json_tuple[1])
            jsonschema.validate(data, schema)
            return NamedJson(
                event_type=event_type,
                data=data)

        except jsonschema.exceptions.ValidationError as e:
            raise DeserializationError(
                f'Failed jsonschema validation of NamedJson: {json_tuple[0]} data {json_tuple[1]}:'
                f'Error was {str(e)}')
        except json.decoder.JSONDecodeError as e:
            raise DeserializationError(
                f'Could not decode json for {json_tuple} at NamedJson deserialization: {str(e)}')

    def to_db_tuple(self) -> NamedJsonDBTuple:
        """May raise:
        - ValueError if jsonschema validation fails
        - EncodingError if validation somehow passed and the value still could not be encoded"""
        try:
            schema: Dict[str, Any] = self.event_type.serialize()
            jsonschema.validate(self.data, schema)
            return (
                self.event_type.serialize_for_db(),
                json.dumps(self.data),
            )
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(
                f'Failed jsonschema validation of NamedJson: {str(e)}')
        except TypeError as e:
            raise EncodingError(
                f'Could not encode json for NamedJson: {str(e)}')

    def serialize(self) -> Dict[str, Any]:
        """May raise:
        - ValueError if jsonschema validation fails
        - EncodingError if validation somehow passed and the value still could not be encoded"""
        try:
            schema: Dict[str, Any] = self.event_type.serialize()
            jsonschema.validate(self.data, schema)
            return {
                'event_type': str(self.event_type),
                'data': json.dumps(self.data),
            }
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(
                f'Failed jsonschema validation of NamedJson: {str(e)}')
        except TypeError as e:
            raise EncodingError(
                f'Could not encode json for NamedJson: {str(e)}')


AccountingEventCacheEntryDBTuple = (
    Tuple[
        str,   # type
        str,   # location
        str,   # paid_in_profit_currency
        str,   # paid_asset
        str,   # paid_in_asset
        str,   # taxable_amount
        str,   # taxable_bought_cost_in_profit_currency
        str,   # received_asset
        str,   # taxable_received_in_profit_currency
        str,   # received_in_asset
        str,   # net_profit_or_loss
        int,   # time
        str,   # cost_basis
        bool,  # is_virtual
        str,   # link
        str,   # notes
    ]
)


class AccountingEventCacheEntry(NamedTuple):
    type: EventType
    location: Location
    paid_in_profit_currency: FVal
    paid_asset: Union[Asset, EmptyStr]
    paid_in_asset: FVal
    taxable_amount: FVal
    taxable_bought_cost_in_profit_currency: FVal
    received_asset: Union[Asset, EmptyStr]
    taxable_received_in_profit_currency: FVal
    received_in_asset: FVal
    net_profit_or_loss: FVal
    time: Timestamp
    cost_basis: Optional[Dict[str, Any]]
    is_virtual: bool
    link: Optional[str]
    notes: Optional[str]

    @classmethod
    def deserialize_from_db(
            cls,
            event_tuple: AccountingEventCacheEntryDBTuple,
    ) -> 'AccountingEventCacheEntry':
        """Turns a tuple read from the database into an appropriate AccountingEvent.
        May raise a DeserializationError if something is wrong with the DB data
        Event_tuple index - Schema columns
        ----------------------------------
        0 - type
        1 - location
        2 - aid_in_profit_currency
        3 - paid_asset
        4 - paid_in_asset
        5 - taxable_amount
        6 - taxable_bought_cost_in_profit_currency
        7 - received_asset
        8 - taxable_received_in_profit_currency
        9 - received_in_asset
        10 - net_profit_or_loss
        11 - time
        12 - cost_basis
        13 - is_virtual
        14 - link
        15 - notes
        """
        return cls(
            type=EventType(event_tuple[0]),
            location=Location.deserialize_from_db(event_tuple[1]),
            paid_in_profit_currency=deserialize_asset_amount(event_tuple[2]),
            paid_asset=Asset(event_tuple[3]),
            paid_in_asset=deserialize_asset_amount(event_tuple[4]),
            taxable_amount=deserialize_asset_amount(event_tuple[5]),
            taxable_bought_cost_in_profit_currency=deserialize_asset_amount(event_tuple[6]),
            received_asset=Asset(event_tuple[7]),
            taxable_received_in_profit_currency=deserialize_asset_amount(event_tuple[8]),
            received_in_asset=deserialize_asset_amount(event_tuple[9]),
            net_profit_or_loss=deserialize_asset_amount(event_tuple[10]),
            time=deserialize_timestamp(event_tuple[11]),
            cost_basis=json.loads(event_tuple[12]),
            is_virtual=bool(event_tuple[13]),
            link=json.loads(event_tuple[14]),
            notes=json.loads(event_tuple[15]),
        )

    def to_db_tuple(self) -> AccountingEventCacheEntryDBTuple:
        return (
            str(self.type),
            str(self.location),
            str(self.paid_in_profit_currency),
            str(self.paid_asset),
            str(self.paid_in_asset),
            str(self.taxable_amount),
            str(self.taxable_bought_cost_in_profit_currency),
            str(self.received_asset),
            str(self.taxable_received_in_profit_currency),
            str(self.received_in_asset),
            str(self.net_profit_or_loss),
            int(self.time),
            json.dumps(self.cost_basis),
            bool(self.is_virtual),
            json.dumps(self.link),
            json.dumps(self.notes),
        )

    def serialize(self) -> Dict[str, Any]:
        """Returns a dict with python primitive types compatible with the NamedJson schema"""
        exported_paid_asset = (
            self.paid_asset if isinstance(self.paid_asset, str) else str(self.paid_asset)
        )
        exported_received_asset = (
            self.received_asset if isinstance(self.received_asset, str) else str(self.received_asset)  # noqa E501
        )
        result_dict = {
            'event_type': str(self.type),
            'location': str(self.location),
            'paid_in_profit_currency': str(self.paid_in_profit_currency),
            'paid_asset': exported_paid_asset,
            'paid_in_asset': str(self.paid_in_asset),
            'taxable_amount': str(self.taxable_amount),
            'taxable_bought_cost_in_profit_currency': str(self.taxable_bought_cost_in_profit_currency),  # noqa E501
            'received_asset': exported_received_asset,
            'taxable_received_in_profit_currency': str(self.taxable_received_in_profit_currency),
            'received_in_asset': str(self.received_in_asset),
            'net_profit_or_loss': str(self.net_profit_or_loss),
            'time': int(self.time),
            'cost_basis': self.cost_basis,
            'is_virtual': self.is_virtual,
            'link': self.link,
            'notes': self.notes,
        }
        named_json: NamedJson = NamedJson(AccountingEventType.ACCOUNTING_EVENT, result_dict)
        return named_json.data
