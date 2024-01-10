# DO NOT CHANGE THIS CODE AS THIS IS GENERATED AUTOMATICALLY

# This module contains a Python API for reading and writing data sets in
# the JSON based openLCA data exchange format. For more information see
# http://greendelta.github.io/olca-schema

import datetime
import json
import uuid

from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union


class RefType(Enum):
    Actor = 'Actor'
    Currency = 'Currency'
    DQSystem = 'DQSystem'
    Epd = 'Epd'
    Flow = 'Flow'
    FlowMap = 'FlowMap'
    FlowProperty = 'FlowProperty'
    ImpactCategory = 'ImpactCategory'
    ImpactMethod = 'ImpactMethod'
    Location = 'Location'
    NwSet = 'NwSet'
    Parameter = 'Parameter'
    Process = 'Process'
    ProductSystem = 'ProductSystem'
    Project = 'Project'
    Result = 'Result'
    RootEntity = 'RootEntity'
    SocialIndicator = 'SocialIndicator'
    Source = 'Source'
    Unit = 'Unit'
    UnitGroup = 'UnitGroup'

    @staticmethod
    def get(v: Union[str, 'RefType'],
            default: Optional['RefType'] = None) -> Optional['RefType']:
        for i in RefType:
            if i == v or i.value == v or i.name == v:
                return i
        return default


class AllocationType(Enum):

    PHYSICAL_ALLOCATION = 'PHYSICAL_ALLOCATION'
    ECONOMIC_ALLOCATION = 'ECONOMIC_ALLOCATION'
    CAUSAL_ALLOCATION = 'CAUSAL_ALLOCATION'
    USE_DEFAULT_ALLOCATION = 'USE_DEFAULT_ALLOCATION'
    NO_ALLOCATION = 'NO_ALLOCATION'

    @staticmethod
    def get(v: Union[str, 'AllocationType'],
            default: Optional['AllocationType'] = None) -> Optional['AllocationType']:
        for i in AllocationType:
            if i == v or i.value == v or i.name == v:
                return i
        return default


class Direction(Enum):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    @staticmethod
    def get(v: Union[str, 'Direction'],
            default: Optional['Direction'] = None) -> Optional['Direction']:
        for i in Direction:
            if i == v or i.value == v or i.name == v:
                return i
        return default


class FlowPropertyType(Enum):

    ECONOMIC_QUANTITY = 'ECONOMIC_QUANTITY'
    PHYSICAL_QUANTITY = 'PHYSICAL_QUANTITY'

    @staticmethod
    def get(v: Union[str, 'FlowPropertyType'],
            default: Optional['FlowPropertyType'] = None) -> Optional['FlowPropertyType']:
        for i in FlowPropertyType:
            if i == v or i.value == v or i.name == v:
                return i
        return default


class FlowType(Enum):

    ELEMENTARY_FLOW = 'ELEMENTARY_FLOW'
    PRODUCT_FLOW = 'PRODUCT_FLOW'
    WASTE_FLOW = 'WASTE_FLOW'

    @staticmethod
    def get(v: Union[str, 'FlowType'],
            default: Optional['FlowType'] = None) -> Optional['FlowType']:
        for i in FlowType:
            if i == v or i.value == v or i.name == v:
                return i
        return default


class ModelType(Enum):

    ACTOR = 'ACTOR'
    CATEGORY = 'CATEGORY'
    CURRENCY = 'CURRENCY'
    DQ_SYSTEM = 'DQ_SYSTEM'
    EPD = 'EPD'
    FLOW = 'FLOW'
    FLOW_PROPERTY = 'FLOW_PROPERTY'
    IMPACT_CATEGORY = 'IMPACT_CATEGORY'
    IMPACT_METHOD = 'IMPACT_METHOD'
    LOCATION = 'LOCATION'
    PARAMETER = 'PARAMETER'
    PROCESS = 'PROCESS'
    PRODUCT_SYSTEM = 'PRODUCT_SYSTEM'
    PROJECT = 'PROJECT'
    RESULT = 'RESULT'
    SOCIAL_INDICATOR = 'SOCIAL_INDICATOR'
    SOURCE = 'SOURCE'
    UNIT_GROUP = 'UNIT_GROUP'

    @staticmethod
    def get(v: Union[str, 'ModelType'],
            default: Optional['ModelType'] = None) -> Optional['ModelType']:
        for i in ModelType:
            if i == v or i.value == v or i.name == v:
                return i
        return default


class ParameterScope(Enum):

    PROCESS_SCOPE = 'PROCESS_SCOPE'
    IMPACT_SCOPE = 'IMPACT_SCOPE'
    GLOBAL_SCOPE = 'GLOBAL_SCOPE'

    @staticmethod
    def get(v: Union[str, 'ParameterScope'],
            default: Optional['ParameterScope'] = None) -> Optional['ParameterScope']:
        for i in ParameterScope:
            if i == v or i.value == v or i.name == v:
                return i
        return default


class ProcessType(Enum):

    LCI_RESULT = 'LCI_RESULT'
    UNIT_PROCESS = 'UNIT_PROCESS'

    @staticmethod
    def get(v: Union[str, 'ProcessType'],
            default: Optional['ProcessType'] = None) -> Optional['ProcessType']:
        for i in ProcessType:
            if i == v or i.value == v or i.name == v:
                return i
        return default


class ProviderLinking(Enum):

    IGNORE_DEFAULTS = 'IGNORE_DEFAULTS'
    PREFER_DEFAULTS = 'PREFER_DEFAULTS'
    ONLY_DEFAULTS = 'ONLY_DEFAULTS'

    @staticmethod
    def get(v: Union[str, 'ProviderLinking'],
            default: Optional['ProviderLinking'] = None) -> Optional['ProviderLinking']:
        for i in ProviderLinking:
            if i == v or i.value == v or i.name == v:
                return i
        return default


class RiskLevel(Enum):

    NO_OPPORTUNITY = 'NO_OPPORTUNITY'
    HIGH_OPPORTUNITY = 'HIGH_OPPORTUNITY'
    MEDIUM_OPPORTUNITY = 'MEDIUM_OPPORTUNITY'
    LOW_OPPORTUNITY = 'LOW_OPPORTUNITY'
    NO_RISK = 'NO_RISK'
    VERY_LOW_RISK = 'VERY_LOW_RISK'
    LOW_RISK = 'LOW_RISK'
    MEDIUM_RISK = 'MEDIUM_RISK'
    HIGH_RISK = 'HIGH_RISK'
    VERY_HIGH_RISK = 'VERY_HIGH_RISK'
    NO_DATA = 'NO_DATA'
    NOT_APPLICABLE = 'NOT_APPLICABLE'

    @staticmethod
    def get(v: Union[str, 'RiskLevel'],
            default: Optional['RiskLevel'] = None) -> Optional['RiskLevel']:
        for i in RiskLevel:
            if i == v or i.value == v or i.name == v:
                return i
        return default


class UncertaintyType(Enum):

    LOG_NORMAL_DISTRIBUTION = 'LOG_NORMAL_DISTRIBUTION'
    NORMAL_DISTRIBUTION = 'NORMAL_DISTRIBUTION'
    TRIANGLE_DISTRIBUTION = 'TRIANGLE_DISTRIBUTION'
    UNIFORM_DISTRIBUTION = 'UNIFORM_DISTRIBUTION'

    @staticmethod
    def get(v: Union[str, 'UncertaintyType'],
            default: Optional['UncertaintyType'] = None) -> Optional['UncertaintyType']:
        for i in UncertaintyType:
            if i == v or i.value == v or i.name == v:
                return i
        return default


@dataclass
class DQScore:

    description: Optional[str] = None
    label: Optional[str] = None
    position: Optional[int] = None
    uncertainty: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.description is not None:
            d['description'] = self.description
        if self.label is not None:
            d['label'] = self.label
        if self.position is not None:
            d['position'] = self.position
        if self.uncertainty is not None:
            d['uncertainty'] = self.uncertainty
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'DQScore':
        d_q_score = DQScore()
        if (v := d.get('description')) or v is not None:
            d_q_score.description = v
        if (v := d.get('label')) or v is not None:
            d_q_score.label = v
        if (v := d.get('position')) or v is not None:
            d_q_score.position = v
        if (v := d.get('uncertainty')) or v is not None:
            d_q_score.uncertainty = v
        return d_q_score


@dataclass
class DQIndicator:

    name: Optional[str] = None
    position: Optional[int] = None
    scores: Optional[List[DQScore]] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.name is not None:
            d['name'] = self.name
        if self.position is not None:
            d['position'] = self.position
        if self.scores is not None:
            d['scores'] = [e.to_dict() for e in self.scores]
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'DQIndicator':
        d_q_indicator = DQIndicator()
        if (v := d.get('name')) or v is not None:
            d_q_indicator.name = v
        if (v := d.get('position')) or v is not None:
            d_q_indicator.position = v
        if (v := d.get('scores')) or v is not None:
            d_q_indicator.scores = [DQScore.from_dict(e) for e in v]
        return d_q_indicator


@dataclass
class ExchangeRef:

    internal_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.internal_id is not None:
            d['internalId'] = self.internal_id
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ExchangeRef':
        exchange_ref = ExchangeRef()
        if (v := d.get('internalId')) or v is not None:
            exchange_ref.internal_id = v
        return exchange_ref


@dataclass
class LinkingConfig:

    cutoff: Optional[float] = None
    prefer_unit_processes: Optional[bool] = None
    provider_linking: Optional[ProviderLinking] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.cutoff is not None:
            d['cutoff'] = self.cutoff
        if self.prefer_unit_processes is not None:
            d['preferUnitProcesses'] = self.prefer_unit_processes
        if self.provider_linking is not None:
            d['providerLinking'] = self.provider_linking.value
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'LinkingConfig':
        linking_config = LinkingConfig()
        if (v := d.get('cutoff')) or v is not None:
            linking_config.cutoff = v
        if (v := d.get('preferUnitProcesses')) or v is not None:
            linking_config.prefer_unit_processes = v
        if (v := d.get('providerLinking')) or v is not None:
            linking_config.provider_linking = ProviderLinking.get(v)
        return linking_config


@dataclass
class Ref:

    id: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    flow_type: Optional[FlowType] = None
    location: Optional[str] = None
    name: Optional[str] = None
    process_type: Optional[ProcessType] = None
    ref_unit: Optional[str] = None
    ref_type: Optional[RefType] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.ref_type is not None:
            d['@type'] = self.ref_type.value
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.flow_type is not None:
            d['flowType'] = self.flow_type.value
        if self.location is not None:
            d['location'] = self.location
        if self.name is not None:
            d['name'] = self.name
        if self.process_type is not None:
            d['processType'] = self.process_type.value
        if self.ref_unit is not None:
            d['refUnit'] = self.ref_unit
        return d

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.ref_type = self.ref_type
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Ref':
        ref = Ref()
        ref.ref_type = RefType.get(d.get('@type', ''))
        if (v := d.get('@id')) or v is not None:
            ref.id = v
        if (v := d.get('category')) or v is not None:
            ref.category = v
        if (v := d.get('description')) or v is not None:
            ref.description = v
        if (v := d.get('flowType')) or v is not None:
            ref.flow_type = FlowType.get(v)
        if (v := d.get('location')) or v is not None:
            ref.location = v
        if (v := d.get('name')) or v is not None:
            ref.name = v
        if (v := d.get('processType')) or v is not None:
            ref.process_type = ProcessType.get(v)
        if (v := d.get('refUnit')) or v is not None:
            ref.ref_unit = v
        return ref


@dataclass
class Actor:

    id: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    telefax: Optional[str] = None
    telephone: Optional[str] = None
    version: Optional[str] = None
    website: Optional[str] = None
    zip_code: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'Actor'
        if self.id is not None:
            d['@id'] = self.id
        if self.address is not None:
            d['address'] = self.address
        if self.category is not None:
            d['category'] = self.category
        if self.city is not None:
            d['city'] = self.city
        if self.country is not None:
            d['country'] = self.country
        if self.description is not None:
            d['description'] = self.description
        if self.email is not None:
            d['email'] = self.email
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.tags is not None:
            d['tags'] = self.tags
        if self.telefax is not None:
            d['telefax'] = self.telefax
        if self.telephone is not None:
            d['telephone'] = self.telephone
        if self.version is not None:
            d['version'] = self.version
        if self.website is not None:
            d['website'] = self.website
        if self.zip_code is not None:
            d['zipCode'] = self.zip_code
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('Actor')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Actor':
        actor = Actor()
        if (v := d.get('@id')) or v is not None:
            actor.id = v
        if (v := d.get('address')) or v is not None:
            actor.address = v
        if (v := d.get('category')) or v is not None:
            actor.category = v
        if (v := d.get('city')) or v is not None:
            actor.city = v
        if (v := d.get('country')) or v is not None:
            actor.country = v
        if (v := d.get('description')) or v is not None:
            actor.description = v
        if (v := d.get('email')) or v is not None:
            actor.email = v
        if (v := d.get('lastChange')) or v is not None:
            actor.last_change = v
        if (v := d.get('name')) or v is not None:
            actor.name = v
        if (v := d.get('tags')) or v is not None:
            actor.tags = v
        if (v := d.get('telefax')) or v is not None:
            actor.telefax = v
        if (v := d.get('telephone')) or v is not None:
            actor.telephone = v
        if (v := d.get('version')) or v is not None:
            actor.version = v
        if (v := d.get('website')) or v is not None:
            actor.website = v
        if (v := d.get('zipCode')) or v is not None:
            actor.zip_code = v
        return actor

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'Actor':
        return Actor.from_dict(json.loads(data))


@dataclass
class AllocationFactor:

    allocation_type: Optional[AllocationType] = None
    exchange: Optional[ExchangeRef] = None
    formula: Optional[str] = None
    product: Optional[Ref] = None
    value: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.allocation_type is not None:
            d['allocationType'] = self.allocation_type.value
        if self.exchange is not None:
            d['exchange'] = self.exchange.to_dict()
        if self.formula is not None:
            d['formula'] = self.formula
        if self.product is not None:
            d['product'] = self.product.to_dict()
        if self.value is not None:
            d['value'] = self.value
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'AllocationFactor':
        allocation_factor = AllocationFactor()
        if (v := d.get('allocationType')) or v is not None:
            allocation_factor.allocation_type = AllocationType.get(v)
        if (v := d.get('exchange')) or v is not None:
            allocation_factor.exchange = ExchangeRef.from_dict(v)
        if (v := d.get('formula')) or v is not None:
            allocation_factor.formula = v
        if (v := d.get('product')) or v is not None:
            allocation_factor.product = Ref.from_dict(v)
        if (v := d.get('value')) or v is not None:
            allocation_factor.value = v
        return allocation_factor


@dataclass
class CostValue:

    amount: Optional[float] = None
    currency: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.amount is not None:
            d['amount'] = self.amount
        if self.currency is not None:
            d['currency'] = self.currency.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'CostValue':
        cost_value = CostValue()
        if (v := d.get('amount')) or v is not None:
            cost_value.amount = v
        if (v := d.get('currency')) or v is not None:
            cost_value.currency = Ref.from_dict(v)
        return cost_value


@dataclass
class Currency:

    id: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None
    conversion_factor: Optional[float] = None
    description: Optional[str] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    ref_currency: Optional[Ref] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'Currency'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.code is not None:
            d['code'] = self.code
        if self.conversion_factor is not None:
            d['conversionFactor'] = self.conversion_factor
        if self.description is not None:
            d['description'] = self.description
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.ref_currency is not None:
            d['refCurrency'] = self.ref_currency.to_dict()
        if self.tags is not None:
            d['tags'] = self.tags
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('Currency')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Currency':
        currency = Currency()
        if (v := d.get('@id')) or v is not None:
            currency.id = v
        if (v := d.get('category')) or v is not None:
            currency.category = v
        if (v := d.get('code')) or v is not None:
            currency.code = v
        if (v := d.get('conversionFactor')) or v is not None:
            currency.conversion_factor = v
        if (v := d.get('description')) or v is not None:
            currency.description = v
        if (v := d.get('lastChange')) or v is not None:
            currency.last_change = v
        if (v := d.get('name')) or v is not None:
            currency.name = v
        if (v := d.get('refCurrency')) or v is not None:
            currency.ref_currency = Ref.from_dict(v)
        if (v := d.get('tags')) or v is not None:
            currency.tags = v
        if (v := d.get('version')) or v is not None:
            currency.version = v
        return currency

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'Currency':
        return Currency.from_dict(json.loads(data))


@dataclass
class DQSystem:

    id: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    has_uncertainties: Optional[bool] = None
    indicators: Optional[List[DQIndicator]] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    source: Optional[Ref] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'DQSystem'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.has_uncertainties is not None:
            d['hasUncertainties'] = self.has_uncertainties
        if self.indicators is not None:
            d['indicators'] = [e.to_dict() for e in self.indicators]
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.source is not None:
            d['source'] = self.source.to_dict()
        if self.tags is not None:
            d['tags'] = self.tags
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('DQSystem')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'DQSystem':
        d_q_system = DQSystem()
        if (v := d.get('@id')) or v is not None:
            d_q_system.id = v
        if (v := d.get('category')) or v is not None:
            d_q_system.category = v
        if (v := d.get('description')) or v is not None:
            d_q_system.description = v
        if (v := d.get('hasUncertainties')) or v is not None:
            d_q_system.has_uncertainties = v
        if (v := d.get('indicators')) or v is not None:
            d_q_system.indicators = [DQIndicator.from_dict(e) for e in v]
        if (v := d.get('lastChange')) or v is not None:
            d_q_system.last_change = v
        if (v := d.get('name')) or v is not None:
            d_q_system.name = v
        if (v := d.get('source')) or v is not None:
            d_q_system.source = Ref.from_dict(v)
        if (v := d.get('tags')) or v is not None:
            d_q_system.tags = v
        if (v := d.get('version')) or v is not None:
            d_q_system.version = v
        return d_q_system

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'DQSystem':
        return DQSystem.from_dict(json.loads(data))


@dataclass
class EnviFlow:

    flow: Optional[Ref] = None
    is_input: Optional[bool] = None
    location: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.flow is not None:
            d['flow'] = self.flow.to_dict()
        if self.is_input is not None:
            d['isInput'] = self.is_input
        if self.location is not None:
            d['location'] = self.location.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'EnviFlow':
        envi_flow = EnviFlow()
        if (v := d.get('flow')) or v is not None:
            envi_flow.flow = Ref.from_dict(v)
        if (v := d.get('isInput')) or v is not None:
            envi_flow.is_input = v
        if (v := d.get('location')) or v is not None:
            envi_flow.location = Ref.from_dict(v)
        return envi_flow


@dataclass
class EnviFlowValue:

    amount: Optional[float] = None
    envi_flow: Optional[EnviFlow] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.amount is not None:
            d['amount'] = self.amount
        if self.envi_flow is not None:
            d['enviFlow'] = self.envi_flow.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'EnviFlowValue':
        envi_flow_value = EnviFlowValue()
        if (v := d.get('amount')) or v is not None:
            envi_flow_value.amount = v
        if (v := d.get('enviFlow')) or v is not None:
            envi_flow_value.envi_flow = EnviFlow.from_dict(v)
        return envi_flow_value


@dataclass
class EpdModule:

    multiplier: Optional[float] = None
    name: Optional[str] = None
    result: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.multiplier is not None:
            d['multiplier'] = self.multiplier
        if self.name is not None:
            d['name'] = self.name
        if self.result is not None:
            d['result'] = self.result.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'EpdModule':
        epd_module = EpdModule()
        if (v := d.get('multiplier')) or v is not None:
            epd_module.multiplier = v
        if (v := d.get('name')) or v is not None:
            epd_module.name = v
        if (v := d.get('result')) or v is not None:
            epd_module.result = Ref.from_dict(v)
        return epd_module


@dataclass
class EpdProduct:

    amount: Optional[float] = None
    flow: Optional[Ref] = None
    flow_property: Optional[Ref] = None
    unit: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.amount is not None:
            d['amount'] = self.amount
        if self.flow is not None:
            d['flow'] = self.flow.to_dict()
        if self.flow_property is not None:
            d['flowProperty'] = self.flow_property.to_dict()
        if self.unit is not None:
            d['unit'] = self.unit.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'EpdProduct':
        epd_product = EpdProduct()
        if (v := d.get('amount')) or v is not None:
            epd_product.amount = v
        if (v := d.get('flow')) or v is not None:
            epd_product.flow = Ref.from_dict(v)
        if (v := d.get('flowProperty')) or v is not None:
            epd_product.flow_property = Ref.from_dict(v)
        if (v := d.get('unit')) or v is not None:
            epd_product.unit = Ref.from_dict(v)
        return epd_product


@dataclass
class Epd:

    id: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    last_change: Optional[str] = None
    manufacturer: Optional[Ref] = None
    modules: Optional[List[EpdModule]] = None
    name: Optional[str] = None
    pcr: Optional[Ref] = None
    product: Optional[EpdProduct] = None
    program_operator: Optional[Ref] = None
    tags: Optional[List[str]] = None
    urn: Optional[str] = None
    verifier: Optional[Ref] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'Epd'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.manufacturer is not None:
            d['manufacturer'] = self.manufacturer.to_dict()
        if self.modules is not None:
            d['modules'] = [e.to_dict() for e in self.modules]
        if self.name is not None:
            d['name'] = self.name
        if self.pcr is not None:
            d['pcr'] = self.pcr.to_dict()
        if self.product is not None:
            d['product'] = self.product.to_dict()
        if self.program_operator is not None:
            d['programOperator'] = self.program_operator.to_dict()
        if self.tags is not None:
            d['tags'] = self.tags
        if self.urn is not None:
            d['urn'] = self.urn
        if self.verifier is not None:
            d['verifier'] = self.verifier.to_dict()
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('Epd')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Epd':
        epd = Epd()
        if (v := d.get('@id')) or v is not None:
            epd.id = v
        if (v := d.get('category')) or v is not None:
            epd.category = v
        if (v := d.get('description')) or v is not None:
            epd.description = v
        if (v := d.get('lastChange')) or v is not None:
            epd.last_change = v
        if (v := d.get('manufacturer')) or v is not None:
            epd.manufacturer = Ref.from_dict(v)
        if (v := d.get('modules')) or v is not None:
            epd.modules = [EpdModule.from_dict(e) for e in v]
        if (v := d.get('name')) or v is not None:
            epd.name = v
        if (v := d.get('pcr')) or v is not None:
            epd.pcr = Ref.from_dict(v)
        if (v := d.get('product')) or v is not None:
            epd.product = EpdProduct.from_dict(v)
        if (v := d.get('programOperator')) or v is not None:
            epd.program_operator = Ref.from_dict(v)
        if (v := d.get('tags')) or v is not None:
            epd.tags = v
        if (v := d.get('urn')) or v is not None:
            epd.urn = v
        if (v := d.get('verifier')) or v is not None:
            epd.verifier = Ref.from_dict(v)
        if (v := d.get('version')) or v is not None:
            epd.version = v
        return epd

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'Epd':
        return Epd.from_dict(json.loads(data))


@dataclass
class FlowMapRef:

    flow: Optional[Ref] = None
    flow_property: Optional[Ref] = None
    provider: Optional[Ref] = None
    unit: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.flow is not None:
            d['flow'] = self.flow.to_dict()
        if self.flow_property is not None:
            d['flowProperty'] = self.flow_property.to_dict()
        if self.provider is not None:
            d['provider'] = self.provider.to_dict()
        if self.unit is not None:
            d['unit'] = self.unit.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'FlowMapRef':
        flow_map_ref = FlowMapRef()
        if (v := d.get('flow')) or v is not None:
            flow_map_ref.flow = Ref.from_dict(v)
        if (v := d.get('flowProperty')) or v is not None:
            flow_map_ref.flow_property = Ref.from_dict(v)
        if (v := d.get('provider')) or v is not None:
            flow_map_ref.provider = Ref.from_dict(v)
        if (v := d.get('unit')) or v is not None:
            flow_map_ref.unit = Ref.from_dict(v)
        return flow_map_ref


@dataclass
class FlowMapEntry:

    conversion_factor: Optional[float] = None
    from_: Optional[FlowMapRef] = None
    to: Optional[FlowMapRef] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.conversion_factor is not None:
            d['conversionFactor'] = self.conversion_factor
        if self.from_ is not None:
            d['from'] = self.from_.to_dict()
        if self.to is not None:
            d['to'] = self.to.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'FlowMapEntry':
        flow_map_entry = FlowMapEntry()
        if (v := d.get('conversionFactor')) or v is not None:
            flow_map_entry.conversion_factor = v
        if (v := d.get('from')) or v is not None:
            flow_map_entry.from_ = FlowMapRef.from_dict(v)
        if (v := d.get('to')) or v is not None:
            flow_map_entry.to = FlowMapRef.from_dict(v)
        return flow_map_entry


@dataclass
class FlowMap:

    id: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    last_change: Optional[str] = None
    mappings: Optional[List[FlowMapEntry]] = None
    name: Optional[str] = None
    source: Optional[Ref] = None
    tags: Optional[List[str]] = None
    target: Optional[Ref] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'FlowMap'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.mappings is not None:
            d['mappings'] = [e.to_dict() for e in self.mappings]
        if self.name is not None:
            d['name'] = self.name
        if self.source is not None:
            d['source'] = self.source.to_dict()
        if self.tags is not None:
            d['tags'] = self.tags
        if self.target is not None:
            d['target'] = self.target.to_dict()
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('FlowMap')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'FlowMap':
        flow_map = FlowMap()
        if (v := d.get('@id')) or v is not None:
            flow_map.id = v
        if (v := d.get('category')) or v is not None:
            flow_map.category = v
        if (v := d.get('description')) or v is not None:
            flow_map.description = v
        if (v := d.get('lastChange')) or v is not None:
            flow_map.last_change = v
        if (v := d.get('mappings')) or v is not None:
            flow_map.mappings = [FlowMapEntry.from_dict(e) for e in v]
        if (v := d.get('name')) or v is not None:
            flow_map.name = v
        if (v := d.get('source')) or v is not None:
            flow_map.source = Ref.from_dict(v)
        if (v := d.get('tags')) or v is not None:
            flow_map.tags = v
        if (v := d.get('target')) or v is not None:
            flow_map.target = Ref.from_dict(v)
        if (v := d.get('version')) or v is not None:
            flow_map.version = v
        return flow_map

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'FlowMap':
        return FlowMap.from_dict(json.loads(data))


@dataclass
class FlowProperty:

    id: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    flow_property_type: Optional[FlowPropertyType] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    unit_group: Optional[Ref] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'FlowProperty'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.flow_property_type is not None:
            d['flowPropertyType'] = self.flow_property_type.value
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.tags is not None:
            d['tags'] = self.tags
        if self.unit_group is not None:
            d['unitGroup'] = self.unit_group.to_dict()
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('FlowProperty')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'FlowProperty':
        flow_property = FlowProperty()
        if (v := d.get('@id')) or v is not None:
            flow_property.id = v
        if (v := d.get('category')) or v is not None:
            flow_property.category = v
        if (v := d.get('description')) or v is not None:
            flow_property.description = v
        if (v := d.get('flowPropertyType')) or v is not None:
            flow_property.flow_property_type = FlowPropertyType.get(v)
        if (v := d.get('lastChange')) or v is not None:
            flow_property.last_change = v
        if (v := d.get('name')) or v is not None:
            flow_property.name = v
        if (v := d.get('tags')) or v is not None:
            flow_property.tags = v
        if (v := d.get('unitGroup')) or v is not None:
            flow_property.unit_group = Ref.from_dict(v)
        if (v := d.get('version')) or v is not None:
            flow_property.version = v
        return flow_property

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'FlowProperty':
        return FlowProperty.from_dict(json.loads(data))


@dataclass
class FlowPropertyFactor:

    conversion_factor: Optional[float] = None
    flow_property: Optional[Ref] = None
    is_ref_flow_property: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.conversion_factor is not None:
            d['conversionFactor'] = self.conversion_factor
        if self.flow_property is not None:
            d['flowProperty'] = self.flow_property.to_dict()
        if self.is_ref_flow_property is not None:
            d['isRefFlowProperty'] = self.is_ref_flow_property
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'FlowPropertyFactor':
        flow_property_factor = FlowPropertyFactor()
        if (v := d.get('conversionFactor')) or v is not None:
            flow_property_factor.conversion_factor = v
        if (v := d.get('flowProperty')) or v is not None:
            flow_property_factor.flow_property = Ref.from_dict(v)
        if (v := d.get('isRefFlowProperty')) or v is not None:
            flow_property_factor.is_ref_flow_property = v
        return flow_property_factor


@dataclass
class Flow:

    id: Optional[str] = None
    cas: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    flow_properties: Optional[List[FlowPropertyFactor]] = None
    flow_type: Optional[FlowType] = None
    formula: Optional[str] = None
    is_infrastructure_flow: Optional[bool] = None
    last_change: Optional[str] = None
    location: Optional[Ref] = None
    name: Optional[str] = None
    synonyms: Optional[str] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'Flow'
        if self.id is not None:
            d['@id'] = self.id
        if self.cas is not None:
            d['cas'] = self.cas
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.flow_properties is not None:
            d['flowProperties'] = [e.to_dict() for e in self.flow_properties]
        if self.flow_type is not None:
            d['flowType'] = self.flow_type.value
        if self.formula is not None:
            d['formula'] = self.formula
        if self.is_infrastructure_flow is not None:
            d['isInfrastructureFlow'] = self.is_infrastructure_flow
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.location is not None:
            d['location'] = self.location.to_dict()
        if self.name is not None:
            d['name'] = self.name
        if self.synonyms is not None:
            d['synonyms'] = self.synonyms
        if self.tags is not None:
            d['tags'] = self.tags
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('Flow')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Flow':
        flow = Flow()
        if (v := d.get('@id')) or v is not None:
            flow.id = v
        if (v := d.get('cas')) or v is not None:
            flow.cas = v
        if (v := d.get('category')) or v is not None:
            flow.category = v
        if (v := d.get('description')) or v is not None:
            flow.description = v
        if (v := d.get('flowProperties')) or v is not None:
            flow.flow_properties = [FlowPropertyFactor.from_dict(e) for e in v]
        if (v := d.get('flowType')) or v is not None:
            flow.flow_type = FlowType.get(v)
        if (v := d.get('formula')) or v is not None:
            flow.formula = v
        if (v := d.get('isInfrastructureFlow')) or v is not None:
            flow.is_infrastructure_flow = v
        if (v := d.get('lastChange')) or v is not None:
            flow.last_change = v
        if (v := d.get('location')) or v is not None:
            flow.location = Ref.from_dict(v)
        if (v := d.get('name')) or v is not None:
            flow.name = v
        if (v := d.get('synonyms')) or v is not None:
            flow.synonyms = v
        if (v := d.get('tags')) or v is not None:
            flow.tags = v
        if (v := d.get('version')) or v is not None:
            flow.version = v
        return flow

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'Flow':
        return Flow.from_dict(json.loads(data))


@dataclass
class FlowResult:

    amount: Optional[float] = None
    description: Optional[str] = None
    flow: Optional[Ref] = None
    flow_property: Optional[Ref] = None
    is_input: Optional[bool] = None
    is_ref_flow: Optional[bool] = None
    location: Optional[Ref] = None
    unit: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.amount is not None:
            d['amount'] = self.amount
        if self.description is not None:
            d['description'] = self.description
        if self.flow is not None:
            d['flow'] = self.flow.to_dict()
        if self.flow_property is not None:
            d['flowProperty'] = self.flow_property.to_dict()
        if self.is_input is not None:
            d['isInput'] = self.is_input
        if self.is_ref_flow is not None:
            d['isRefFlow'] = self.is_ref_flow
        if self.location is not None:
            d['location'] = self.location.to_dict()
        if self.unit is not None:
            d['unit'] = self.unit.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'FlowResult':
        flow_result = FlowResult()
        if (v := d.get('amount')) or v is not None:
            flow_result.amount = v
        if (v := d.get('description')) or v is not None:
            flow_result.description = v
        if (v := d.get('flow')) or v is not None:
            flow_result.flow = Ref.from_dict(v)
        if (v := d.get('flowProperty')) or v is not None:
            flow_result.flow_property = Ref.from_dict(v)
        if (v := d.get('isInput')) or v is not None:
            flow_result.is_input = v
        if (v := d.get('isRefFlow')) or v is not None:
            flow_result.is_ref_flow = v
        if (v := d.get('location')) or v is not None:
            flow_result.location = Ref.from_dict(v)
        if (v := d.get('unit')) or v is not None:
            flow_result.unit = Ref.from_dict(v)
        return flow_result


@dataclass
class ImpactResult:

    amount: Optional[float] = None
    description: Optional[str] = None
    indicator: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.amount is not None:
            d['amount'] = self.amount
        if self.description is not None:
            d['description'] = self.description
        if self.indicator is not None:
            d['indicator'] = self.indicator.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ImpactResult':
        impact_result = ImpactResult()
        if (v := d.get('amount')) or v is not None:
            impact_result.amount = v
        if (v := d.get('description')) or v is not None:
            impact_result.description = v
        if (v := d.get('indicator')) or v is not None:
            impact_result.indicator = Ref.from_dict(v)
        return impact_result


@dataclass
class ImpactValue:

    amount: Optional[float] = None
    impact_category: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.amount is not None:
            d['amount'] = self.amount
        if self.impact_category is not None:
            d['impactCategory'] = self.impact_category.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ImpactValue':
        impact_value = ImpactValue()
        if (v := d.get('amount')) or v is not None:
            impact_value.amount = v
        if (v := d.get('impactCategory')) or v is not None:
            impact_value.impact_category = Ref.from_dict(v)
        return impact_value


@dataclass
class Location:

    id: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    geometry: Optional[Dict[str, Any]] = None
    last_change: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'Location'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.code is not None:
            d['code'] = self.code
        if self.description is not None:
            d['description'] = self.description
        if self.geometry is not None:
            d['geometry'] = self.geometry
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.latitude is not None:
            d['latitude'] = self.latitude
        if self.longitude is not None:
            d['longitude'] = self.longitude
        if self.name is not None:
            d['name'] = self.name
        if self.tags is not None:
            d['tags'] = self.tags
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('Location')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Location':
        location = Location()
        if (v := d.get('@id')) or v is not None:
            location.id = v
        if (v := d.get('category')) or v is not None:
            location.category = v
        if (v := d.get('code')) or v is not None:
            location.code = v
        if (v := d.get('description')) or v is not None:
            location.description = v
        if (v := d.get('geometry')) or v is not None:
            location.geometry = v
        if (v := d.get('lastChange')) or v is not None:
            location.last_change = v
        if (v := d.get('latitude')) or v is not None:
            location.latitude = v
        if (v := d.get('longitude')) or v is not None:
            location.longitude = v
        if (v := d.get('name')) or v is not None:
            location.name = v
        if (v := d.get('tags')) or v is not None:
            location.tags = v
        if (v := d.get('version')) or v is not None:
            location.version = v
        return location

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'Location':
        return Location.from_dict(json.loads(data))


@dataclass
class NwFactor:

    impact_category: Optional[Ref] = None
    normalisation_factor: Optional[float] = None
    weighting_factor: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.impact_category is not None:
            d['impactCategory'] = self.impact_category.to_dict()
        if self.normalisation_factor is not None:
            d['normalisationFactor'] = self.normalisation_factor
        if self.weighting_factor is not None:
            d['weightingFactor'] = self.weighting_factor
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'NwFactor':
        nw_factor = NwFactor()
        if (v := d.get('impactCategory')) or v is not None:
            nw_factor.impact_category = Ref.from_dict(v)
        if (v := d.get('normalisationFactor')) or v is not None:
            nw_factor.normalisation_factor = v
        if (v := d.get('weightingFactor')) or v is not None:
            nw_factor.weighting_factor = v
        return nw_factor


@dataclass
class NwSet:

    id: Optional[str] = None
    description: Optional[str] = None
    factors: Optional[List[NwFactor]] = None
    name: Optional[str] = None
    weighted_score_unit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.id is not None:
            d['@id'] = self.id
        if self.description is not None:
            d['description'] = self.description
        if self.factors is not None:
            d['factors'] = [e.to_dict() for e in self.factors]
        if self.name is not None:
            d['name'] = self.name
        if self.weighted_score_unit is not None:
            d['weightedScoreUnit'] = self.weighted_score_unit
        return d

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.ref_type = RefType.get('NwSet')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'NwSet':
        nw_set = NwSet()
        if (v := d.get('@id')) or v is not None:
            nw_set.id = v
        if (v := d.get('description')) or v is not None:
            nw_set.description = v
        if (v := d.get('factors')) or v is not None:
            nw_set.factors = [NwFactor.from_dict(e) for e in v]
        if (v := d.get('name')) or v is not None:
            nw_set.name = v
        if (v := d.get('weightedScoreUnit')) or v is not None:
            nw_set.weighted_score_unit = v
        return nw_set


@dataclass
class ImpactMethod:

    id: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    impact_categories: Optional[List[Ref]] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    nw_sets: Optional[List[NwSet]] = None
    source: Optional[Ref] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'ImpactMethod'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.code is not None:
            d['code'] = self.code
        if self.description is not None:
            d['description'] = self.description
        if self.impact_categories is not None:
            d['impactCategories'] = [e.to_dict() for e in self.impact_categories]
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.nw_sets is not None:
            d['nwSets'] = [e.to_dict() for e in self.nw_sets]
        if self.source is not None:
            d['source'] = self.source.to_dict()
        if self.tags is not None:
            d['tags'] = self.tags
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('ImpactMethod')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ImpactMethod':
        impact_method = ImpactMethod()
        if (v := d.get('@id')) or v is not None:
            impact_method.id = v
        if (v := d.get('category')) or v is not None:
            impact_method.category = v
        if (v := d.get('code')) or v is not None:
            impact_method.code = v
        if (v := d.get('description')) or v is not None:
            impact_method.description = v
        if (v := d.get('impactCategories')) or v is not None:
            impact_method.impact_categories = [Ref.from_dict(e) for e in v]
        if (v := d.get('lastChange')) or v is not None:
            impact_method.last_change = v
        if (v := d.get('name')) or v is not None:
            impact_method.name = v
        if (v := d.get('nwSets')) or v is not None:
            impact_method.nw_sets = [NwSet.from_dict(e) for e in v]
        if (v := d.get('source')) or v is not None:
            impact_method.source = Ref.from_dict(v)
        if (v := d.get('tags')) or v is not None:
            impact_method.tags = v
        if (v := d.get('version')) or v is not None:
            impact_method.version = v
        return impact_method

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'ImpactMethod':
        return ImpactMethod.from_dict(json.loads(data))


@dataclass
class ProcessDocumentation:

    completeness_description: Optional[str] = None
    creation_date: Optional[str] = None
    data_collection_description: Optional[str] = None
    data_documentor: Optional[Ref] = None
    data_generator: Optional[Ref] = None
    data_selection_description: Optional[str] = None
    data_set_owner: Optional[Ref] = None
    data_treatment_description: Optional[str] = None
    geography_description: Optional[str] = None
    intended_application: Optional[str] = None
    inventory_method_description: Optional[str] = None
    is_copyright_protected: Optional[bool] = None
    modeling_constants_description: Optional[str] = None
    project_description: Optional[str] = None
    publication: Optional[Ref] = None
    restrictions_description: Optional[str] = None
    review_details: Optional[str] = None
    reviewer: Optional[Ref] = None
    sampling_description: Optional[str] = None
    sources: Optional[List[Ref]] = None
    technology_description: Optional[str] = None
    time_description: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.completeness_description is not None:
            d['completenessDescription'] = self.completeness_description
        if self.creation_date is not None:
            d['creationDate'] = self.creation_date
        if self.data_collection_description is not None:
            d['dataCollectionDescription'] = self.data_collection_description
        if self.data_documentor is not None:
            d['dataDocumentor'] = self.data_documentor.to_dict()
        if self.data_generator is not None:
            d['dataGenerator'] = self.data_generator.to_dict()
        if self.data_selection_description is not None:
            d['dataSelectionDescription'] = self.data_selection_description
        if self.data_set_owner is not None:
            d['dataSetOwner'] = self.data_set_owner.to_dict()
        if self.data_treatment_description is not None:
            d['dataTreatmentDescription'] = self.data_treatment_description
        if self.geography_description is not None:
            d['geographyDescription'] = self.geography_description
        if self.intended_application is not None:
            d['intendedApplication'] = self.intended_application
        if self.inventory_method_description is not None:
            d['inventoryMethodDescription'] = self.inventory_method_description
        if self.is_copyright_protected is not None:
            d['isCopyrightProtected'] = self.is_copyright_protected
        if self.modeling_constants_description is not None:
            d['modelingConstantsDescription'] = self.modeling_constants_description
        if self.project_description is not None:
            d['projectDescription'] = self.project_description
        if self.publication is not None:
            d['publication'] = self.publication.to_dict()
        if self.restrictions_description is not None:
            d['restrictionsDescription'] = self.restrictions_description
        if self.review_details is not None:
            d['reviewDetails'] = self.review_details
        if self.reviewer is not None:
            d['reviewer'] = self.reviewer.to_dict()
        if self.sampling_description is not None:
            d['samplingDescription'] = self.sampling_description
        if self.sources is not None:
            d['sources'] = [e.to_dict() for e in self.sources]
        if self.technology_description is not None:
            d['technologyDescription'] = self.technology_description
        if self.time_description is not None:
            d['timeDescription'] = self.time_description
        if self.valid_from is not None:
            d['validFrom'] = self.valid_from
        if self.valid_until is not None:
            d['validUntil'] = self.valid_until
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ProcessDocumentation':
        process_documentation = ProcessDocumentation()
        if (v := d.get('completenessDescription')) or v is not None:
            process_documentation.completeness_description = v
        if (v := d.get('creationDate')) or v is not None:
            process_documentation.creation_date = v
        if (v := d.get('dataCollectionDescription')) or v is not None:
            process_documentation.data_collection_description = v
        if (v := d.get('dataDocumentor')) or v is not None:
            process_documentation.data_documentor = Ref.from_dict(v)
        if (v := d.get('dataGenerator')) or v is not None:
            process_documentation.data_generator = Ref.from_dict(v)
        if (v := d.get('dataSelectionDescription')) or v is not None:
            process_documentation.data_selection_description = v
        if (v := d.get('dataSetOwner')) or v is not None:
            process_documentation.data_set_owner = Ref.from_dict(v)
        if (v := d.get('dataTreatmentDescription')) or v is not None:
            process_documentation.data_treatment_description = v
        if (v := d.get('geographyDescription')) or v is not None:
            process_documentation.geography_description = v
        if (v := d.get('intendedApplication')) or v is not None:
            process_documentation.intended_application = v
        if (v := d.get('inventoryMethodDescription')) or v is not None:
            process_documentation.inventory_method_description = v
        if (v := d.get('isCopyrightProtected')) or v is not None:
            process_documentation.is_copyright_protected = v
        if (v := d.get('modelingConstantsDescription')) or v is not None:
            process_documentation.modeling_constants_description = v
        if (v := d.get('projectDescription')) or v is not None:
            process_documentation.project_description = v
        if (v := d.get('publication')) or v is not None:
            process_documentation.publication = Ref.from_dict(v)
        if (v := d.get('restrictionsDescription')) or v is not None:
            process_documentation.restrictions_description = v
        if (v := d.get('reviewDetails')) or v is not None:
            process_documentation.review_details = v
        if (v := d.get('reviewer')) or v is not None:
            process_documentation.reviewer = Ref.from_dict(v)
        if (v := d.get('samplingDescription')) or v is not None:
            process_documentation.sampling_description = v
        if (v := d.get('sources')) or v is not None:
            process_documentation.sources = [Ref.from_dict(e) for e in v]
        if (v := d.get('technologyDescription')) or v is not None:
            process_documentation.technology_description = v
        if (v := d.get('timeDescription')) or v is not None:
            process_documentation.time_description = v
        if (v := d.get('validFrom')) or v is not None:
            process_documentation.valid_from = v
        if (v := d.get('validUntil')) or v is not None:
            process_documentation.valid_until = v
        return process_documentation


@dataclass
class ProcessLink:

    exchange: Optional[ExchangeRef] = None
    flow: Optional[Ref] = None
    process: Optional[Ref] = None
    provider: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.exchange is not None:
            d['exchange'] = self.exchange.to_dict()
        if self.flow is not None:
            d['flow'] = self.flow.to_dict()
        if self.process is not None:
            d['process'] = self.process.to_dict()
        if self.provider is not None:
            d['provider'] = self.provider.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ProcessLink':
        process_link = ProcessLink()
        if (v := d.get('exchange')) or v is not None:
            process_link.exchange = ExchangeRef.from_dict(v)
        if (v := d.get('flow')) or v is not None:
            process_link.flow = Ref.from_dict(v)
        if (v := d.get('process')) or v is not None:
            process_link.process = Ref.from_dict(v)
        if (v := d.get('provider')) or v is not None:
            process_link.provider = Ref.from_dict(v)
        return process_link


@dataclass
class Result:

    id: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    flow_results: Optional[List[FlowResult]] = None
    impact_method: Optional[Ref] = None
    impact_results: Optional[List[ImpactResult]] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    product_system: Optional[Ref] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'Result'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.flow_results is not None:
            d['flowResults'] = [e.to_dict() for e in self.flow_results]
        if self.impact_method is not None:
            d['impactMethod'] = self.impact_method.to_dict()
        if self.impact_results is not None:
            d['impactResults'] = [e.to_dict() for e in self.impact_results]
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.product_system is not None:
            d['productSystem'] = self.product_system.to_dict()
        if self.tags is not None:
            d['tags'] = self.tags
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('Result')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Result':
        result = Result()
        if (v := d.get('@id')) or v is not None:
            result.id = v
        if (v := d.get('category')) or v is not None:
            result.category = v
        if (v := d.get('description')) or v is not None:
            result.description = v
        if (v := d.get('flowResults')) or v is not None:
            result.flow_results = [FlowResult.from_dict(e) for e in v]
        if (v := d.get('impactMethod')) or v is not None:
            result.impact_method = Ref.from_dict(v)
        if (v := d.get('impactResults')) or v is not None:
            result.impact_results = [ImpactResult.from_dict(e) for e in v]
        if (v := d.get('lastChange')) or v is not None:
            result.last_change = v
        if (v := d.get('name')) or v is not None:
            result.name = v
        if (v := d.get('productSystem')) or v is not None:
            result.product_system = Ref.from_dict(v)
        if (v := d.get('tags')) or v is not None:
            result.tags = v
        if (v := d.get('version')) or v is not None:
            result.version = v
        return result

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'Result':
        return Result.from_dict(json.loads(data))


@dataclass
class ResultState:

    id: Optional[str] = None
    error: Optional[str] = None
    is_ready: Optional[bool] = None
    is_scheduled: Optional[bool] = None
    time: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.id is not None:
            d['@id'] = self.id
        if self.error is not None:
            d['error'] = self.error
        if self.is_ready is not None:
            d['isReady'] = self.is_ready
        if self.is_scheduled is not None:
            d['isScheduled'] = self.is_scheduled
        if self.time is not None:
            d['time'] = self.time
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ResultState':
        result_state = ResultState()
        if (v := d.get('@id')) or v is not None:
            result_state.id = v
        if (v := d.get('error')) or v is not None:
            result_state.error = v
        if (v := d.get('isReady')) or v is not None:
            result_state.is_ready = v
        if (v := d.get('isScheduled')) or v is not None:
            result_state.is_scheduled = v
        if (v := d.get('time')) or v is not None:
            result_state.time = v
        return result_state


@dataclass
class SankeyEdge:

    node_index: Optional[int] = None
    provider_index: Optional[int] = None
    upstream_share: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.node_index is not None:
            d['nodeIndex'] = self.node_index
        if self.provider_index is not None:
            d['providerIndex'] = self.provider_index
        if self.upstream_share is not None:
            d['upstreamShare'] = self.upstream_share
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'SankeyEdge':
        sankey_edge = SankeyEdge()
        if (v := d.get('nodeIndex')) or v is not None:
            sankey_edge.node_index = v
        if (v := d.get('providerIndex')) or v is not None:
            sankey_edge.provider_index = v
        if (v := d.get('upstreamShare')) or v is not None:
            sankey_edge.upstream_share = v
        return sankey_edge


@dataclass
class SankeyRequest:

    envi_flow: Optional[EnviFlow] = None
    for_costs: Optional[bool] = None
    impact_category: Optional[Ref] = None
    max_nodes: Optional[int] = None
    min_share: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.envi_flow is not None:
            d['enviFlow'] = self.envi_flow.to_dict()
        if self.for_costs is not None:
            d['forCosts'] = self.for_costs
        if self.impact_category is not None:
            d['impactCategory'] = self.impact_category.to_dict()
        if self.max_nodes is not None:
            d['maxNodes'] = self.max_nodes
        if self.min_share is not None:
            d['minShare'] = self.min_share
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'SankeyRequest':
        sankey_request = SankeyRequest()
        if (v := d.get('enviFlow')) or v is not None:
            sankey_request.envi_flow = EnviFlow.from_dict(v)
        if (v := d.get('forCosts')) or v is not None:
            sankey_request.for_costs = v
        if (v := d.get('impactCategory')) or v is not None:
            sankey_request.impact_category = Ref.from_dict(v)
        if (v := d.get('maxNodes')) or v is not None:
            sankey_request.max_nodes = v
        if (v := d.get('minShare')) or v is not None:
            sankey_request.min_share = v
        return sankey_request


@dataclass
class SocialAspect:

    activity_value: Optional[float] = None
    comment: Optional[str] = None
    quality: Optional[str] = None
    raw_amount: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    social_indicator: Optional[Ref] = None
    source: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.activity_value is not None:
            d['activityValue'] = self.activity_value
        if self.comment is not None:
            d['comment'] = self.comment
        if self.quality is not None:
            d['quality'] = self.quality
        if self.raw_amount is not None:
            d['rawAmount'] = self.raw_amount
        if self.risk_level is not None:
            d['riskLevel'] = self.risk_level.value
        if self.social_indicator is not None:
            d['socialIndicator'] = self.social_indicator.to_dict()
        if self.source is not None:
            d['source'] = self.source.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'SocialAspect':
        social_aspect = SocialAspect()
        if (v := d.get('activityValue')) or v is not None:
            social_aspect.activity_value = v
        if (v := d.get('comment')) or v is not None:
            social_aspect.comment = v
        if (v := d.get('quality')) or v is not None:
            social_aspect.quality = v
        if (v := d.get('rawAmount')) or v is not None:
            social_aspect.raw_amount = v
        if (v := d.get('riskLevel')) or v is not None:
            social_aspect.risk_level = RiskLevel.get(v)
        if (v := d.get('socialIndicator')) or v is not None:
            social_aspect.social_indicator = Ref.from_dict(v)
        if (v := d.get('source')) or v is not None:
            social_aspect.source = Ref.from_dict(v)
        return social_aspect


@dataclass
class SocialIndicator:

    id: Optional[str] = None
    activity_quantity: Optional[Ref] = None
    activity_unit: Optional[Ref] = None
    activity_variable: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    evaluation_scheme: Optional[str] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    unit_of_measurement: Optional[str] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'SocialIndicator'
        if self.id is not None:
            d['@id'] = self.id
        if self.activity_quantity is not None:
            d['activityQuantity'] = self.activity_quantity.to_dict()
        if self.activity_unit is not None:
            d['activityUnit'] = self.activity_unit.to_dict()
        if self.activity_variable is not None:
            d['activityVariable'] = self.activity_variable
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.evaluation_scheme is not None:
            d['evaluationScheme'] = self.evaluation_scheme
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.tags is not None:
            d['tags'] = self.tags
        if self.unit_of_measurement is not None:
            d['unitOfMeasurement'] = self.unit_of_measurement
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('SocialIndicator')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'SocialIndicator':
        social_indicator = SocialIndicator()
        if (v := d.get('@id')) or v is not None:
            social_indicator.id = v
        if (v := d.get('activityQuantity')) or v is not None:
            social_indicator.activity_quantity = Ref.from_dict(v)
        if (v := d.get('activityUnit')) or v is not None:
            social_indicator.activity_unit = Ref.from_dict(v)
        if (v := d.get('activityVariable')) or v is not None:
            social_indicator.activity_variable = v
        if (v := d.get('category')) or v is not None:
            social_indicator.category = v
        if (v := d.get('description')) or v is not None:
            social_indicator.description = v
        if (v := d.get('evaluationScheme')) or v is not None:
            social_indicator.evaluation_scheme = v
        if (v := d.get('lastChange')) or v is not None:
            social_indicator.last_change = v
        if (v := d.get('name')) or v is not None:
            social_indicator.name = v
        if (v := d.get('tags')) or v is not None:
            social_indicator.tags = v
        if (v := d.get('unitOfMeasurement')) or v is not None:
            social_indicator.unit_of_measurement = v
        if (v := d.get('version')) or v is not None:
            social_indicator.version = v
        return social_indicator

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'SocialIndicator':
        return SocialIndicator.from_dict(json.loads(data))


@dataclass
class Source:

    id: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    external_file: Optional[str] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    text_reference: Optional[str] = None
    url: Optional[str] = None
    version: Optional[str] = None
    year: Optional[int] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'Source'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.external_file is not None:
            d['externalFile'] = self.external_file
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.tags is not None:
            d['tags'] = self.tags
        if self.text_reference is not None:
            d['textReference'] = self.text_reference
        if self.url is not None:
            d['url'] = self.url
        if self.version is not None:
            d['version'] = self.version
        if self.year is not None:
            d['year'] = self.year
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('Source')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Source':
        source = Source()
        if (v := d.get('@id')) or v is not None:
            source.id = v
        if (v := d.get('category')) or v is not None:
            source.category = v
        if (v := d.get('description')) or v is not None:
            source.description = v
        if (v := d.get('externalFile')) or v is not None:
            source.external_file = v
        if (v := d.get('lastChange')) or v is not None:
            source.last_change = v
        if (v := d.get('name')) or v is not None:
            source.name = v
        if (v := d.get('tags')) or v is not None:
            source.tags = v
        if (v := d.get('textReference')) or v is not None:
            source.text_reference = v
        if (v := d.get('url')) or v is not None:
            source.url = v
        if (v := d.get('version')) or v is not None:
            source.version = v
        if (v := d.get('year')) or v is not None:
            source.year = v
        return source

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'Source':
        return Source.from_dict(json.loads(data))


@dataclass
class TechFlow:

    flow: Optional[Ref] = None
    provider: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.flow is not None:
            d['flow'] = self.flow.to_dict()
        if self.provider is not None:
            d['provider'] = self.provider.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'TechFlow':
        tech_flow = TechFlow()
        if (v := d.get('flow')) or v is not None:
            tech_flow.flow = Ref.from_dict(v)
        if (v := d.get('provider')) or v is not None:
            tech_flow.provider = Ref.from_dict(v)
        return tech_flow


@dataclass
class SankeyNode:

    direct_result: Optional[float] = None
    index: Optional[int] = None
    tech_flow: Optional[TechFlow] = None
    total_result: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.direct_result is not None:
            d['directResult'] = self.direct_result
        if self.index is not None:
            d['index'] = self.index
        if self.tech_flow is not None:
            d['techFlow'] = self.tech_flow.to_dict()
        if self.total_result is not None:
            d['totalResult'] = self.total_result
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'SankeyNode':
        sankey_node = SankeyNode()
        if (v := d.get('directResult')) or v is not None:
            sankey_node.direct_result = v
        if (v := d.get('index')) or v is not None:
            sankey_node.index = v
        if (v := d.get('techFlow')) or v is not None:
            sankey_node.tech_flow = TechFlow.from_dict(v)
        if (v := d.get('totalResult')) or v is not None:
            sankey_node.total_result = v
        return sankey_node


@dataclass
class SankeyGraph:

    edges: Optional[List[SankeyEdge]] = None
    nodes: Optional[List[SankeyNode]] = None
    root_index: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.edges is not None:
            d['edges'] = [e.to_dict() for e in self.edges]
        if self.nodes is not None:
            d['nodes'] = [e.to_dict() for e in self.nodes]
        if self.root_index is not None:
            d['rootIndex'] = self.root_index
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'SankeyGraph':
        sankey_graph = SankeyGraph()
        if (v := d.get('edges')) or v is not None:
            sankey_graph.edges = [SankeyEdge.from_dict(e) for e in v]
        if (v := d.get('nodes')) or v is not None:
            sankey_graph.nodes = [SankeyNode.from_dict(e) for e in v]
        if (v := d.get('rootIndex')) or v is not None:
            sankey_graph.root_index = v
        return sankey_graph


@dataclass
class TechFlowValue:

    amount: Optional[float] = None
    tech_flow: Optional[TechFlow] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.amount is not None:
            d['amount'] = self.amount
        if self.tech_flow is not None:
            d['techFlow'] = self.tech_flow.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'TechFlowValue':
        tech_flow_value = TechFlowValue()
        if (v := d.get('amount')) or v is not None:
            tech_flow_value.amount = v
        if (v := d.get('techFlow')) or v is not None:
            tech_flow_value.tech_flow = TechFlow.from_dict(v)
        return tech_flow_value


@dataclass
class Uncertainty:

    distribution_type: Optional[UncertaintyType] = None
    geom_mean: Optional[float] = None
    geom_sd: Optional[float] = None
    maximum: Optional[float] = None
    mean: Optional[float] = None
    minimum: Optional[float] = None
    mode: Optional[float] = None
    sd: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.distribution_type is not None:
            d['distributionType'] = self.distribution_type.value
        if self.geom_mean is not None:
            d['geomMean'] = self.geom_mean
        if self.geom_sd is not None:
            d['geomSd'] = self.geom_sd
        if self.maximum is not None:
            d['maximum'] = self.maximum
        if self.mean is not None:
            d['mean'] = self.mean
        if self.minimum is not None:
            d['minimum'] = self.minimum
        if self.mode is not None:
            d['mode'] = self.mode
        if self.sd is not None:
            d['sd'] = self.sd
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Uncertainty':
        uncertainty = Uncertainty()
        if (v := d.get('distributionType')) or v is not None:
            uncertainty.distribution_type = UncertaintyType.get(v)
        if (v := d.get('geomMean')) or v is not None:
            uncertainty.geom_mean = v
        if (v := d.get('geomSd')) or v is not None:
            uncertainty.geom_sd = v
        if (v := d.get('maximum')) or v is not None:
            uncertainty.maximum = v
        if (v := d.get('mean')) or v is not None:
            uncertainty.mean = v
        if (v := d.get('minimum')) or v is not None:
            uncertainty.minimum = v
        if (v := d.get('mode')) or v is not None:
            uncertainty.mode = v
        if (v := d.get('sd')) or v is not None:
            uncertainty.sd = v
        return uncertainty


@dataclass
class Exchange:

    amount: Optional[float] = None
    amount_formula: Optional[str] = None
    base_uncertainty: Optional[float] = None
    cost_formula: Optional[str] = None
    cost_value: Optional[float] = None
    currency: Optional[Ref] = None
    default_provider: Optional[Ref] = None
    description: Optional[str] = None
    dq_entry: Optional[str] = None
    flow: Optional[Ref] = None
    flow_property: Optional[Ref] = None
    internal_id: Optional[int] = None
    is_avoided_product: Optional[bool] = None
    is_input: Optional[bool] = None
    is_quantitative_reference: Optional[bool] = None
    location: Optional[Ref] = None
    uncertainty: Optional[Uncertainty] = None
    unit: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.amount is not None:
            d['amount'] = self.amount
        if self.amount_formula is not None:
            d['amountFormula'] = self.amount_formula
        if self.base_uncertainty is not None:
            d['baseUncertainty'] = self.base_uncertainty
        if self.cost_formula is not None:
            d['costFormula'] = self.cost_formula
        if self.cost_value is not None:
            d['costValue'] = self.cost_value
        if self.currency is not None:
            d['currency'] = self.currency.to_dict()
        if self.default_provider is not None:
            d['defaultProvider'] = self.default_provider.to_dict()
        if self.description is not None:
            d['description'] = self.description
        if self.dq_entry is not None:
            d['dqEntry'] = self.dq_entry
        if self.flow is not None:
            d['flow'] = self.flow.to_dict()
        if self.flow_property is not None:
            d['flowProperty'] = self.flow_property.to_dict()
        if self.internal_id is not None:
            d['internalId'] = self.internal_id
        if self.is_avoided_product is not None:
            d['isAvoidedProduct'] = self.is_avoided_product
        if self.is_input is not None:
            d['isInput'] = self.is_input
        if self.is_quantitative_reference is not None:
            d['isQuantitativeReference'] = self.is_quantitative_reference
        if self.location is not None:
            d['location'] = self.location.to_dict()
        if self.uncertainty is not None:
            d['uncertainty'] = self.uncertainty.to_dict()
        if self.unit is not None:
            d['unit'] = self.unit.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Exchange':
        exchange = Exchange()
        if (v := d.get('amount')) or v is not None:
            exchange.amount = v
        if (v := d.get('amountFormula')) or v is not None:
            exchange.amount_formula = v
        if (v := d.get('baseUncertainty')) or v is not None:
            exchange.base_uncertainty = v
        if (v := d.get('costFormula')) or v is not None:
            exchange.cost_formula = v
        if (v := d.get('costValue')) or v is not None:
            exchange.cost_value = v
        if (v := d.get('currency')) or v is not None:
            exchange.currency = Ref.from_dict(v)
        if (v := d.get('defaultProvider')) or v is not None:
            exchange.default_provider = Ref.from_dict(v)
        if (v := d.get('description')) or v is not None:
            exchange.description = v
        if (v := d.get('dqEntry')) or v is not None:
            exchange.dq_entry = v
        if (v := d.get('flow')) or v is not None:
            exchange.flow = Ref.from_dict(v)
        if (v := d.get('flowProperty')) or v is not None:
            exchange.flow_property = Ref.from_dict(v)
        if (v := d.get('internalId')) or v is not None:
            exchange.internal_id = v
        if (v := d.get('isAvoidedProduct')) or v is not None:
            exchange.is_avoided_product = v
        if (v := d.get('isInput')) or v is not None:
            exchange.is_input = v
        if (v := d.get('isQuantitativeReference')) or v is not None:
            exchange.is_quantitative_reference = v
        if (v := d.get('location')) or v is not None:
            exchange.location = Ref.from_dict(v)
        if (v := d.get('uncertainty')) or v is not None:
            exchange.uncertainty = Uncertainty.from_dict(v)
        if (v := d.get('unit')) or v is not None:
            exchange.unit = Ref.from_dict(v)
        return exchange


@dataclass
class ImpactFactor:

    flow: Optional[Ref] = None
    flow_property: Optional[Ref] = None
    formula: Optional[str] = None
    location: Optional[Ref] = None
    uncertainty: Optional[Uncertainty] = None
    unit: Optional[Ref] = None
    value: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.flow is not None:
            d['flow'] = self.flow.to_dict()
        if self.flow_property is not None:
            d['flowProperty'] = self.flow_property.to_dict()
        if self.formula is not None:
            d['formula'] = self.formula
        if self.location is not None:
            d['location'] = self.location.to_dict()
        if self.uncertainty is not None:
            d['uncertainty'] = self.uncertainty.to_dict()
        if self.unit is not None:
            d['unit'] = self.unit.to_dict()
        if self.value is not None:
            d['value'] = self.value
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ImpactFactor':
        impact_factor = ImpactFactor()
        if (v := d.get('flow')) or v is not None:
            impact_factor.flow = Ref.from_dict(v)
        if (v := d.get('flowProperty')) or v is not None:
            impact_factor.flow_property = Ref.from_dict(v)
        if (v := d.get('formula')) or v is not None:
            impact_factor.formula = v
        if (v := d.get('location')) or v is not None:
            impact_factor.location = Ref.from_dict(v)
        if (v := d.get('uncertainty')) or v is not None:
            impact_factor.uncertainty = Uncertainty.from_dict(v)
        if (v := d.get('unit')) or v is not None:
            impact_factor.unit = Ref.from_dict(v)
        if (v := d.get('value')) or v is not None:
            impact_factor.value = v
        return impact_factor


@dataclass
class Parameter:

    id: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    formula: Optional[str] = None
    is_input_parameter: Optional[bool] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    parameter_scope: Optional[ParameterScope] = None
    tags: Optional[List[str]] = None
    uncertainty: Optional[Uncertainty] = None
    value: Optional[float] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'Parameter'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.formula is not None:
            d['formula'] = self.formula
        if self.is_input_parameter is not None:
            d['isInputParameter'] = self.is_input_parameter
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.parameter_scope is not None:
            d['parameterScope'] = self.parameter_scope.value
        if self.tags is not None:
            d['tags'] = self.tags
        if self.uncertainty is not None:
            d['uncertainty'] = self.uncertainty.to_dict()
        if self.value is not None:
            d['value'] = self.value
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('Parameter')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Parameter':
        parameter = Parameter()
        if (v := d.get('@id')) or v is not None:
            parameter.id = v
        if (v := d.get('category')) or v is not None:
            parameter.category = v
        if (v := d.get('description')) or v is not None:
            parameter.description = v
        if (v := d.get('formula')) or v is not None:
            parameter.formula = v
        if (v := d.get('isInputParameter')) or v is not None:
            parameter.is_input_parameter = v
        if (v := d.get('lastChange')) or v is not None:
            parameter.last_change = v
        if (v := d.get('name')) or v is not None:
            parameter.name = v
        if (v := d.get('parameterScope')) or v is not None:
            parameter.parameter_scope = ParameterScope.get(v)
        if (v := d.get('tags')) or v is not None:
            parameter.tags = v
        if (v := d.get('uncertainty')) or v is not None:
            parameter.uncertainty = Uncertainty.from_dict(v)
        if (v := d.get('value')) or v is not None:
            parameter.value = v
        if (v := d.get('version')) or v is not None:
            parameter.version = v
        return parameter

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'Parameter':
        return Parameter.from_dict(json.loads(data))


@dataclass
class ImpactCategory:

    id: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    direction: Optional[Direction] = None
    impact_factors: Optional[List[ImpactFactor]] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    parameters: Optional[List[Parameter]] = None
    ref_unit: Optional[str] = None
    source: Optional[Ref] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'ImpactCategory'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.code is not None:
            d['code'] = self.code
        if self.description is not None:
            d['description'] = self.description
        if self.direction is not None:
            d['direction'] = self.direction.value
        if self.impact_factors is not None:
            d['impactFactors'] = [e.to_dict() for e in self.impact_factors]
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.parameters is not None:
            d['parameters'] = [e.to_dict() for e in self.parameters]
        if self.ref_unit is not None:
            d['refUnit'] = self.ref_unit
        if self.source is not None:
            d['source'] = self.source.to_dict()
        if self.tags is not None:
            d['tags'] = self.tags
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('ImpactCategory')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ImpactCategory':
        impact_category = ImpactCategory()
        if (v := d.get('@id')) or v is not None:
            impact_category.id = v
        if (v := d.get('category')) or v is not None:
            impact_category.category = v
        if (v := d.get('code')) or v is not None:
            impact_category.code = v
        if (v := d.get('description')) or v is not None:
            impact_category.description = v
        if (v := d.get('direction')) or v is not None:
            impact_category.direction = Direction.get(v)
        if (v := d.get('impactFactors')) or v is not None:
            impact_category.impact_factors = [ImpactFactor.from_dict(e) for e in v]
        if (v := d.get('lastChange')) or v is not None:
            impact_category.last_change = v
        if (v := d.get('name')) or v is not None:
            impact_category.name = v
        if (v := d.get('parameters')) or v is not None:
            impact_category.parameters = [Parameter.from_dict(e) for e in v]
        if (v := d.get('refUnit')) or v is not None:
            impact_category.ref_unit = v
        if (v := d.get('source')) or v is not None:
            impact_category.source = Ref.from_dict(v)
        if (v := d.get('tags')) or v is not None:
            impact_category.tags = v
        if (v := d.get('version')) or v is not None:
            impact_category.version = v
        return impact_category

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'ImpactCategory':
        return ImpactCategory.from_dict(json.loads(data))


@dataclass
class ParameterRedef:

    context: Optional[Ref] = None
    description: Optional[str] = None
    is_protected: Optional[bool] = None
    name: Optional[str] = None
    uncertainty: Optional[Uncertainty] = None
    value: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.context is not None:
            d['context'] = self.context.to_dict()
        if self.description is not None:
            d['description'] = self.description
        if self.is_protected is not None:
            d['isProtected'] = self.is_protected
        if self.name is not None:
            d['name'] = self.name
        if self.uncertainty is not None:
            d['uncertainty'] = self.uncertainty.to_dict()
        if self.value is not None:
            d['value'] = self.value
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ParameterRedef':
        parameter_redef = ParameterRedef()
        if (v := d.get('context')) or v is not None:
            parameter_redef.context = Ref.from_dict(v)
        if (v := d.get('description')) or v is not None:
            parameter_redef.description = v
        if (v := d.get('isProtected')) or v is not None:
            parameter_redef.is_protected = v
        if (v := d.get('name')) or v is not None:
            parameter_redef.name = v
        if (v := d.get('uncertainty')) or v is not None:
            parameter_redef.uncertainty = Uncertainty.from_dict(v)
        if (v := d.get('value')) or v is not None:
            parameter_redef.value = v
        return parameter_redef


@dataclass
class CalculationSetup:

    allocation: Optional[AllocationType] = None
    amount: Optional[float] = None
    flow_property: Optional[Ref] = None
    impact_method: Optional[Ref] = None
    nw_set: Optional[Ref] = None
    parameters: Optional[List[ParameterRedef]] = None
    target: Optional[Ref] = None
    unit: Optional[Ref] = None
    with_costs: Optional[bool] = None
    with_regionalization: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.allocation is not None:
            d['allocation'] = self.allocation.value
        if self.amount is not None:
            d['amount'] = self.amount
        if self.flow_property is not None:
            d['flowProperty'] = self.flow_property.to_dict()
        if self.impact_method is not None:
            d['impactMethod'] = self.impact_method.to_dict()
        if self.nw_set is not None:
            d['nwSet'] = self.nw_set.to_dict()
        if self.parameters is not None:
            d['parameters'] = [e.to_dict() for e in self.parameters]
        if self.target is not None:
            d['target'] = self.target.to_dict()
        if self.unit is not None:
            d['unit'] = self.unit.to_dict()
        if self.with_costs is not None:
            d['withCosts'] = self.with_costs
        if self.with_regionalization is not None:
            d['withRegionalization'] = self.with_regionalization
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'CalculationSetup':
        calculation_setup = CalculationSetup()
        if (v := d.get('allocation')) or v is not None:
            calculation_setup.allocation = AllocationType.get(v)
        if (v := d.get('amount')) or v is not None:
            calculation_setup.amount = v
        if (v := d.get('flowProperty')) or v is not None:
            calculation_setup.flow_property = Ref.from_dict(v)
        if (v := d.get('impactMethod')) or v is not None:
            calculation_setup.impact_method = Ref.from_dict(v)
        if (v := d.get('nwSet')) or v is not None:
            calculation_setup.nw_set = Ref.from_dict(v)
        if (v := d.get('parameters')) or v is not None:
            calculation_setup.parameters = [ParameterRedef.from_dict(e) for e in v]
        if (v := d.get('target')) or v is not None:
            calculation_setup.target = Ref.from_dict(v)
        if (v := d.get('unit')) or v is not None:
            calculation_setup.unit = Ref.from_dict(v)
        if (v := d.get('withCosts')) or v is not None:
            calculation_setup.with_costs = v
        if (v := d.get('withRegionalization')) or v is not None:
            calculation_setup.with_regionalization = v
        return calculation_setup


@dataclass
class ParameterRedefSet:

    description: Optional[str] = None
    is_baseline: Optional[bool] = None
    name: Optional[str] = None
    parameters: Optional[List[ParameterRedef]] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.description is not None:
            d['description'] = self.description
        if self.is_baseline is not None:
            d['isBaseline'] = self.is_baseline
        if self.name is not None:
            d['name'] = self.name
        if self.parameters is not None:
            d['parameters'] = [e.to_dict() for e in self.parameters]
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ParameterRedefSet':
        parameter_redef_set = ParameterRedefSet()
        if (v := d.get('description')) or v is not None:
            parameter_redef_set.description = v
        if (v := d.get('isBaseline')) or v is not None:
            parameter_redef_set.is_baseline = v
        if (v := d.get('name')) or v is not None:
            parameter_redef_set.name = v
        if (v := d.get('parameters')) or v is not None:
            parameter_redef_set.parameters = [ParameterRedef.from_dict(e) for e in v]
        return parameter_redef_set


@dataclass
class Process:

    id: Optional[str] = None
    allocation_factors: Optional[List[AllocationFactor]] = None
    category: Optional[str] = None
    default_allocation_method: Optional[AllocationType] = None
    description: Optional[str] = None
    dq_entry: Optional[str] = None
    dq_system: Optional[Ref] = None
    exchange_dq_system: Optional[Ref] = None
    exchanges: Optional[List[Exchange]] = None
    is_infrastructure_process: Optional[bool] = None
    last_change: Optional[str] = None
    last_internal_id: Optional[int] = None
    location: Optional[Ref] = None
    name: Optional[str] = None
    parameters: Optional[List[Parameter]] = None
    process_documentation: Optional[ProcessDocumentation] = None
    process_type: Optional[ProcessType] = None
    social_aspects: Optional[List[SocialAspect]] = None
    social_dq_system: Optional[Ref] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'Process'
        if self.id is not None:
            d['@id'] = self.id
        if self.allocation_factors is not None:
            d['allocationFactors'] = [e.to_dict() for e in self.allocation_factors]
        if self.category is not None:
            d['category'] = self.category
        if self.default_allocation_method is not None:
            d['defaultAllocationMethod'] = self.default_allocation_method.value
        if self.description is not None:
            d['description'] = self.description
        if self.dq_entry is not None:
            d['dqEntry'] = self.dq_entry
        if self.dq_system is not None:
            d['dqSystem'] = self.dq_system.to_dict()
        if self.exchange_dq_system is not None:
            d['exchangeDqSystem'] = self.exchange_dq_system.to_dict()
        if self.exchanges is not None:
            d['exchanges'] = [e.to_dict() for e in self.exchanges]
        if self.is_infrastructure_process is not None:
            d['isInfrastructureProcess'] = self.is_infrastructure_process
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.last_internal_id is not None:
            d['lastInternalId'] = self.last_internal_id
        if self.location is not None:
            d['location'] = self.location.to_dict()
        if self.name is not None:
            d['name'] = self.name
        if self.parameters is not None:
            d['parameters'] = [e.to_dict() for e in self.parameters]
        if self.process_documentation is not None:
            d['processDocumentation'] = self.process_documentation.to_dict()
        if self.process_type is not None:
            d['processType'] = self.process_type.value
        if self.social_aspects is not None:
            d['socialAspects'] = [e.to_dict() for e in self.social_aspects]
        if self.social_dq_system is not None:
            d['socialDqSystem'] = self.social_dq_system.to_dict()
        if self.tags is not None:
            d['tags'] = self.tags
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('Process')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Process':
        process = Process()
        if (v := d.get('@id')) or v is not None:
            process.id = v
        if (v := d.get('allocationFactors')) or v is not None:
            process.allocation_factors = [AllocationFactor.from_dict(e) for e in v]
        if (v := d.get('category')) or v is not None:
            process.category = v
        if (v := d.get('defaultAllocationMethod')) or v is not None:
            process.default_allocation_method = AllocationType.get(v)
        if (v := d.get('description')) or v is not None:
            process.description = v
        if (v := d.get('dqEntry')) or v is not None:
            process.dq_entry = v
        if (v := d.get('dqSystem')) or v is not None:
            process.dq_system = Ref.from_dict(v)
        if (v := d.get('exchangeDqSystem')) or v is not None:
            process.exchange_dq_system = Ref.from_dict(v)
        if (v := d.get('exchanges')) or v is not None:
            process.exchanges = [Exchange.from_dict(e) for e in v]
        if (v := d.get('isInfrastructureProcess')) or v is not None:
            process.is_infrastructure_process = v
        if (v := d.get('lastChange')) or v is not None:
            process.last_change = v
        if (v := d.get('lastInternalId')) or v is not None:
            process.last_internal_id = v
        if (v := d.get('location')) or v is not None:
            process.location = Ref.from_dict(v)
        if (v := d.get('name')) or v is not None:
            process.name = v
        if (v := d.get('parameters')) or v is not None:
            process.parameters = [Parameter.from_dict(e) for e in v]
        if (v := d.get('processDocumentation')) or v is not None:
            process.process_documentation = ProcessDocumentation.from_dict(v)
        if (v := d.get('processType')) or v is not None:
            process.process_type = ProcessType.get(v)
        if (v := d.get('socialAspects')) or v is not None:
            process.social_aspects = [SocialAspect.from_dict(e) for e in v]
        if (v := d.get('socialDqSystem')) or v is not None:
            process.social_dq_system = Ref.from_dict(v)
        if (v := d.get('tags')) or v is not None:
            process.tags = v
        if (v := d.get('version')) or v is not None:
            process.version = v
        return process

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'Process':
        return Process.from_dict(json.loads(data))


@dataclass
class ProductSystem:

    id: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    parameter_sets: Optional[List[ParameterRedefSet]] = None
    process_links: Optional[List[ProcessLink]] = None
    processes: Optional[List[Ref]] = None
    ref_exchange: Optional[ExchangeRef] = None
    ref_process: Optional[Ref] = None
    tags: Optional[List[str]] = None
    target_amount: Optional[float] = None
    target_flow_property: Optional[Ref] = None
    target_unit: Optional[Ref] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'ProductSystem'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.parameter_sets is not None:
            d['parameterSets'] = [e.to_dict() for e in self.parameter_sets]
        if self.process_links is not None:
            d['processLinks'] = [e.to_dict() for e in self.process_links]
        if self.processes is not None:
            d['processes'] = [e.to_dict() for e in self.processes]
        if self.ref_exchange is not None:
            d['refExchange'] = self.ref_exchange.to_dict()
        if self.ref_process is not None:
            d['refProcess'] = self.ref_process.to_dict()
        if self.tags is not None:
            d['tags'] = self.tags
        if self.target_amount is not None:
            d['targetAmount'] = self.target_amount
        if self.target_flow_property is not None:
            d['targetFlowProperty'] = self.target_flow_property.to_dict()
        if self.target_unit is not None:
            d['targetUnit'] = self.target_unit.to_dict()
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('ProductSystem')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ProductSystem':
        product_system = ProductSystem()
        if (v := d.get('@id')) or v is not None:
            product_system.id = v
        if (v := d.get('category')) or v is not None:
            product_system.category = v
        if (v := d.get('description')) or v is not None:
            product_system.description = v
        if (v := d.get('lastChange')) or v is not None:
            product_system.last_change = v
        if (v := d.get('name')) or v is not None:
            product_system.name = v
        if (v := d.get('parameterSets')) or v is not None:
            product_system.parameter_sets = [ParameterRedefSet.from_dict(e) for e in v]
        if (v := d.get('processLinks')) or v is not None:
            product_system.process_links = [ProcessLink.from_dict(e) for e in v]
        if (v := d.get('processes')) or v is not None:
            product_system.processes = [Ref.from_dict(e) for e in v]
        if (v := d.get('refExchange')) or v is not None:
            product_system.ref_exchange = ExchangeRef.from_dict(v)
        if (v := d.get('refProcess')) or v is not None:
            product_system.ref_process = Ref.from_dict(v)
        if (v := d.get('tags')) or v is not None:
            product_system.tags = v
        if (v := d.get('targetAmount')) or v is not None:
            product_system.target_amount = v
        if (v := d.get('targetFlowProperty')) or v is not None:
            product_system.target_flow_property = Ref.from_dict(v)
        if (v := d.get('targetUnit')) or v is not None:
            product_system.target_unit = Ref.from_dict(v)
        if (v := d.get('version')) or v is not None:
            product_system.version = v
        return product_system

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'ProductSystem':
        return ProductSystem.from_dict(json.loads(data))


@dataclass
class ProjectVariant:

    allocation_method: Optional[AllocationType] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    is_disabled: Optional[bool] = None
    name: Optional[str] = None
    parameter_redefs: Optional[List[ParameterRedef]] = None
    product_system: Optional[Ref] = None
    unit: Optional[Ref] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.allocation_method is not None:
            d['allocationMethod'] = self.allocation_method.value
        if self.amount is not None:
            d['amount'] = self.amount
        if self.description is not None:
            d['description'] = self.description
        if self.is_disabled is not None:
            d['isDisabled'] = self.is_disabled
        if self.name is not None:
            d['name'] = self.name
        if self.parameter_redefs is not None:
            d['parameterRedefs'] = [e.to_dict() for e in self.parameter_redefs]
        if self.product_system is not None:
            d['productSystem'] = self.product_system.to_dict()
        if self.unit is not None:
            d['unit'] = self.unit.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ProjectVariant':
        project_variant = ProjectVariant()
        if (v := d.get('allocationMethod')) or v is not None:
            project_variant.allocation_method = AllocationType.get(v)
        if (v := d.get('amount')) or v is not None:
            project_variant.amount = v
        if (v := d.get('description')) or v is not None:
            project_variant.description = v
        if (v := d.get('isDisabled')) or v is not None:
            project_variant.is_disabled = v
        if (v := d.get('name')) or v is not None:
            project_variant.name = v
        if (v := d.get('parameterRedefs')) or v is not None:
            project_variant.parameter_redefs = [ParameterRedef.from_dict(e) for e in v]
        if (v := d.get('productSystem')) or v is not None:
            project_variant.product_system = Ref.from_dict(v)
        if (v := d.get('unit')) or v is not None:
            project_variant.unit = Ref.from_dict(v)
        return project_variant


@dataclass
class Project:

    id: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    impact_method: Optional[Ref] = None
    is_with_costs: Optional[bool] = None
    is_with_regionalization: Optional[bool] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    nw_set: Optional[NwSet] = None
    tags: Optional[List[str]] = None
    variants: Optional[List[ProjectVariant]] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'Project'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.description is not None:
            d['description'] = self.description
        if self.impact_method is not None:
            d['impactMethod'] = self.impact_method.to_dict()
        if self.is_with_costs is not None:
            d['isWithCosts'] = self.is_with_costs
        if self.is_with_regionalization is not None:
            d['isWithRegionalization'] = self.is_with_regionalization
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.nw_set is not None:
            d['nwSet'] = self.nw_set.to_dict()
        if self.tags is not None:
            d['tags'] = self.tags
        if self.variants is not None:
            d['variants'] = [e.to_dict() for e in self.variants]
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('Project')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Project':
        project = Project()
        if (v := d.get('@id')) or v is not None:
            project.id = v
        if (v := d.get('category')) or v is not None:
            project.category = v
        if (v := d.get('description')) or v is not None:
            project.description = v
        if (v := d.get('impactMethod')) or v is not None:
            project.impact_method = Ref.from_dict(v)
        if (v := d.get('isWithCosts')) or v is not None:
            project.is_with_costs = v
        if (v := d.get('isWithRegionalization')) or v is not None:
            project.is_with_regionalization = v
        if (v := d.get('lastChange')) or v is not None:
            project.last_change = v
        if (v := d.get('name')) or v is not None:
            project.name = v
        if (v := d.get('nwSet')) or v is not None:
            project.nw_set = NwSet.from_dict(v)
        if (v := d.get('tags')) or v is not None:
            project.tags = v
        if (v := d.get('variants')) or v is not None:
            project.variants = [ProjectVariant.from_dict(e) for e in v]
        if (v := d.get('version')) or v is not None:
            project.version = v
        return project

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'Project':
        return Project.from_dict(json.loads(data))


@dataclass
class Unit:

    id: Optional[str] = None
    conversion_factor: Optional[float] = None
    description: Optional[str] = None
    is_ref_unit: Optional[bool] = None
    name: Optional[str] = None
    synonyms: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.id is not None:
            d['@id'] = self.id
        if self.conversion_factor is not None:
            d['conversionFactor'] = self.conversion_factor
        if self.description is not None:
            d['description'] = self.description
        if self.is_ref_unit is not None:
            d['isRefUnit'] = self.is_ref_unit
        if self.name is not None:
            d['name'] = self.name
        if self.synonyms is not None:
            d['synonyms'] = self.synonyms
        return d

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.ref_type = RefType.get('Unit')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Unit':
        unit = Unit()
        if (v := d.get('@id')) or v is not None:
            unit.id = v
        if (v := d.get('conversionFactor')) or v is not None:
            unit.conversion_factor = v
        if (v := d.get('description')) or v is not None:
            unit.description = v
        if (v := d.get('isRefUnit')) or v is not None:
            unit.is_ref_unit = v
        if (v := d.get('name')) or v is not None:
            unit.name = v
        if (v := d.get('synonyms')) or v is not None:
            unit.synonyms = v
        return unit


@dataclass
class UnitGroup:

    id: Optional[str] = None
    category: Optional[str] = None
    default_flow_property: Optional[Ref] = None
    description: Optional[str] = None
    last_change: Optional[str] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    units: Optional[List[Unit]] = None
    version: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.version is None:
            self.version = '01.00.000'
        if self.last_change is None:
            self.last_change = datetime.datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d['@type'] = 'UnitGroup'
        if self.id is not None:
            d['@id'] = self.id
        if self.category is not None:
            d['category'] = self.category
        if self.default_flow_property is not None:
            d['defaultFlowProperty'] = self.default_flow_property.to_dict()
        if self.description is not None:
            d['description'] = self.description
        if self.last_change is not None:
            d['lastChange'] = self.last_change
        if self.name is not None:
            d['name'] = self.name
        if self.tags is not None:
            d['tags'] = self.tags
        if self.units is not None:
            d['units'] = [e.to_dict() for e in self.units]
        if self.version is not None:
            d['version'] = self.version
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_ref(self) -> 'Ref':
        ref = Ref(id=self.id, name=self.name)
        ref.category = self.category
        ref.ref_type = RefType.get('UnitGroup')
        return ref

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'UnitGroup':
        unit_group = UnitGroup()
        if (v := d.get('@id')) or v is not None:
            unit_group.id = v
        if (v := d.get('category')) or v is not None:
            unit_group.category = v
        if (v := d.get('defaultFlowProperty')) or v is not None:
            unit_group.default_flow_property = Ref.from_dict(v)
        if (v := d.get('description')) or v is not None:
            unit_group.description = v
        if (v := d.get('lastChange')) or v is not None:
            unit_group.last_change = v
        if (v := d.get('name')) or v is not None:
            unit_group.name = v
        if (v := d.get('tags')) or v is not None:
            unit_group.tags = v
        if (v := d.get('units')) or v is not None:
            unit_group.units = [Unit.from_dict(e) for e in v]
        if (v := d.get('version')) or v is not None:
            unit_group.version = v
        return unit_group

    @staticmethod
    def from_json(data: Union[str, bytes]) -> 'UnitGroup':
        return UnitGroup.from_dict(json.loads(data))


@dataclass
class UpstreamNode:

    direct_contribution: Optional[float] = None
    required_amount: Optional[float] = None
    result: Optional[float] = None
    tech_flow: Optional[TechFlow] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.direct_contribution is not None:
            d['directContribution'] = self.direct_contribution
        if self.required_amount is not None:
            d['requiredAmount'] = self.required_amount
        if self.result is not None:
            d['result'] = self.result
        if self.tech_flow is not None:
            d['techFlow'] = self.tech_flow.to_dict()
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'UpstreamNode':
        upstream_node = UpstreamNode()
        if (v := d.get('directContribution')) or v is not None:
            upstream_node.direct_contribution = v
        if (v := d.get('requiredAmount')) or v is not None:
            upstream_node.required_amount = v
        if (v := d.get('result')) or v is not None:
            upstream_node.result = v
        if (v := d.get('techFlow')) or v is not None:
            upstream_node.tech_flow = TechFlow.from_dict(v)
        return upstream_node


RootEntity = Union[
    Actor,
    Currency,
    DQSystem,
    Epd,
    Flow,
    FlowMap,
    FlowProperty,
    ImpactCategory,
    ImpactMethod,
    Location,
    Parameter,
    Process,
    ProductSystem,
    Project,
    Result,
    SocialIndicator,
    Source,
    UnitGroup,
]


RefEntity = Union[RootEntity, Unit, NwSet]
