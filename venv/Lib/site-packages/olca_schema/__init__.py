from .schema import *
from typing import Optional, Union


def new_unit(name: str, conversion_factor=1.0) -> Unit:
    """Creates a new unit.

    Parameters
    ----------
    name:
        The name of the unit, e.g. 'kg'
    conversion_factor:
        An optional conversion factor to the reference unit of the unit group
        where this unit is defined. Defaults to 1.0.

    Example
    -------
    ```python
    unit = new_unit('kg')
    ```
    """
    return Unit(
        id=str(uuid.uuid4()),
        name=name,
        conversion_factor=1.0,
        is_ref_unit=conversion_factor == 1.0,
    )


def new_unit_group(name: str, ref_unit: Union[str, Unit]) -> UnitGroup:
    """Creates a new unit group.

    Parameters
    ----------
    name:
        The name of the new unit group.
    ref_unit:
        The reference unit of the new unit group.

    Example
    -------
    ```python
    group = new_unit_group('Mass units', 'kg')
    ```
    """
    unit: Unit = new_unit(ref_unit) if isinstance(ref_unit, str) else ref_unit
    group = UnitGroup(name=name, units=[unit])
    return group


def new_flow_property(
    name: str, unit_group: Union[Ref, UnitGroup]
) -> FlowProperty:
    """Creates a new flow property (quantity).

    Parameters
    ----------
    name:
        The name of the new flow property
    unit_group:
        The unit group or reference to the unit group if this flow property.

    Example
    -------
    ```python
    group = new_unit_group('Mass units', 'kg')
    mass = new_flow_property('Mass', group)
    ```
    """
    return FlowProperty(name=name, unit_group=as_ref(unit_group))


def new_flow(
    name: str, flow_type: FlowType, flow_property: Union[Ref, FlowProperty]
) -> Flow:
    """Creates a new flow.

    Parameters
    ----------
    name:
        The name of the new flow.
    flow_type:
        The type of the new flow (product, waste, or elementary flow).
    flow_property:
        The reference flow property of the flow.

    Example
    -------
    ```python
    group = new_unit_group('Mass units', 'kg')
    mass = new_flow_property('Mass', group)
    steel = new_flow('Steel', FlowType.PRODUCT_FLOW, mass)
    ```
    """
    factor = FlowPropertyFactor(
        flow_property=as_ref(flow_property),
        conversion_factor=1.0,
        is_ref_flow_property=True,
    )
    return Flow(name=name, flow_type=flow_type, flow_properties=[factor])


def new_product(name: str, flow_property: Union[Ref, FlowProperty]) -> Flow:
    """Creates a new product flow.

    Parameters
    ----------
    name:
        The name of the new flow.
    flow_property:
        The reference flow property of the flow.

    Example
    -------
    ```python
    group = new_unit_group('Mass units', 'kg')
    mass = new_flow_property('Mass', group)
    steel = new_product('Steel', FlowType.PRODUCT_FLOW, mass)
    ```
    """
    return new_flow(name, FlowType.PRODUCT_FLOW, flow_property)


def new_waste(name: str, flow_property: Union[Ref, FlowProperty]) -> Flow:
    """Creates a new waste flow.

    Parameters
    ----------
    name:
        The name of the new flow.
    flow_property:
        The reference flow property of the flow.

    Example
    -------
    ```python
    group = new_unit_group('Mass units', 'kg')
    mass = new_flow_property('Mass', group)
    scrap = new_waste('Scrap', FlowType.PRODUCT_FLOW, mass)
    ```
    """
    return new_flow(name, FlowType.WASTE_FLOW, flow_property)


def new_elementary_flow(
    name: str, flow_property: Union[Ref, FlowProperty]
) -> Flow:
    """Creates a new elementary flow.

    Parameters
    ----------
    name:
        The name of the new flow.
    flow_property:
        The reference flow property of the flow.

    Example
    -------
    ```python
    group = new_unit_group('Mass units', 'kg')
    mass = new_flow_property('Mass', group)
    co2 = new_elementary_flow('CO2', FlowType.PRODUCT_FLOW, mass)
    ```
    """
    return new_flow(name, FlowType.ELEMENTARY_FLOW, flow_property)


def new_process(name: str) -> Process:
    """Creates a new process.

    Parameters
    ----------
    name:
        The name of the new process.

    Example
    -------
    ```python
    process = new_process('Steel production')
    ```
    """
    return Process(name=name, process_type=ProcessType.UNIT_PROCESS)


def new_exchange(
    process: Process,
    flow: Union[Ref, Flow],
    amount: Union[str, float] = 1.0,
    unit: Optional[Union[Ref, Unit]] = None,
) -> Exchange:
    """Creates a new exchange.

    Parameters
    ----------
    process:
        The process of the new exchange.
    flow:
        The flow of this exchange.
    amount:
        The amount of the exchange; defaults to 1.0. Strings a floating point
        numbers are allowed. If a string is passed as amount, we assume that
        it is a valid formula.
    unit:
        The unit of the exchange. If not provided the exchange amount is given
        in the reference unit of the linked flow.

    Example
    -------
    ```python
    units = new_unit_group('Mass units', 'kg')
    mass = new_flow_property('Mass', units)
    steel = new_product('Steel', FlowType.PRODUCT_FLOW, mass)
    process = new_process('Steel production')
    exchange = new_exchange(process, steel, 1.0)
    exchange.quantitative_reference = True
    ```
    """
    if process.last_internal_id is None:
        internal_id = 1
    else:
        internal_id = process.last_internal_id + 1
    process.last_internal_id = internal_id
    exchange = Exchange(internal_id=internal_id, flow=as_ref(flow))
    if isinstance(amount, str):
        exchange.amount_formula = amount
    else:
        exchange.amount = amount
    if unit:
        exchange.unit = as_ref(unit)
    if process.exchanges is None:
        process.exchanges = [exchange]
    else:
        process.exchanges.append(exchange)
    return exchange


def new_input(
    process: Process,
    flow: Union[Ref, Flow],
    amount: Union[str, float] = 1.0,
    unit: Optional[Union[Ref, Unit]] = None,
) -> Exchange:
    """Creates a new input.

    Example
    -------
    ```python
    units = new_unit_group('Mass units', 'kg')
    mass = new_flow_property('Mass', units)
    process = new_process('Steel production')
    scrap = new_waste('Scrap', FlowType.PRODUCT_FLOW, mass)
    input = new_input(process, scrap, 0.1)
    ```
    """
    exchange = new_exchange(process, flow, amount, unit)
    exchange.is_input = True
    return exchange


def new_output(
    process: Process,
    flow: Union[Ref, Flow],
    amount: Union[str, float] = 1.0,
    unit: Optional[Union[Ref, Unit]] = None,
) -> Exchange:
    """Creates a new output.

    Example
    -------
    ```python
    units = new_unit_group('Mass units', 'kg')
    mass = new_flow_property('Mass', units)
    steel = new_product('Steel', FlowType.PRODUCT_FLOW, mass)
    process = new_process('Steel production')
    output = new_output(process, steel, 1.0)
    output.quantitative_reference = True
    ```
    """
    exchange = new_exchange(process, flow, amount, unit)
    exchange.is_input = False
    return exchange


def new_location(name: str, code: Optional[str] = None) -> Location:
    """Creates a new location.

    Parameters
    ----------
    name:
        The name of the new location.
    code:
        An optional location code.

    Example
    -------
    ```python
    location = new_location('Germany', 'DE')
    ```
    """
    return Location(name=name, code=code or name)


def new_parameter(
    name: str, value: Union[str, float], scope=ParameterScope.GLOBAL_SCOPE
) -> Parameter:
    """Creates a new parameter.

    Parameters
    ----------
    name:
        The name of the new parameter. Note that parameters can be used
        in formulas. So that the name of the parameter has to follow
        specific syntax rules, i.e. it cannot contain whitespaces or
        special characters.
    value:
        The parameter value. If a string is passed as value into this
        function we assume that this is a formula, and we will create
        a dependent, calculated parameter. Otherwise, we create an
        input parameter
    scope:
        The scope of the parameter. If not specified otherwise this
        defaults to global scope.
    Example
    -------
    ```python
    # create a global input parameter
    global_scrap_rate = new_parameter('global_scrap_rate', 1.0)
    # create a local calculated parameter of a process
    local_scrap_rate = new_parameter(
        'local_scrap_rate',
        'global_scrap_rate * 0.9',
        ParameterScope.PROCESS_SCOPE)
    process = new_process('Steel production')
    process.parameters = [local_scrap_rate]
    ```
    """
    param = Parameter(name=name, parameter_scope=scope)
    if isinstance(value, str):
        param.formula = value
        param.is_input_parameter = False
    else:
        param.value = value
        param.is_input_parameter = True
    return param


def new_physical_allocation_factor(
    process: Process, product: Union[Ref, Flow], amount: Union[str, float]
) -> AllocationFactor:
    f = _new_allocation_factor(process, product, amount)
    f.allocation_type = AllocationType.PHYSICAL_ALLOCATION
    return f


def new_economic_allocation_factor(
    process: Process, product: Union[Ref, Flow], amount: Union[str, float]
) -> AllocationFactor:
    f = _new_allocation_factor(process, product, amount)
    f.allocation_type = AllocationType.ECONOMIC_ALLOCATION
    return f


def new_causal_allocation_factor(
    process: Process,
    product: Union[Ref, Flow],
    amount: Union[str, float],
    exchange: Union[Exchange, ExchangeRef],
) -> AllocationFactor:
    f = _new_allocation_factor(process, product, amount)
    f.allocation_type = AllocationType.CAUSAL_ALLOCATION
    f.exchange = ExchangeRef(internal_id=exchange.internal_id)
    return f


def _new_allocation_factor(
    process: Process, product: Union[Ref, Flow], amount: Union[str, float]
) -> AllocationFactor:
    f = AllocationFactor()
    f.product = as_ref(product)
    if isinstance(amount, str):
        f.formula = amount
    else:
        f.value = amount
    if process.allocation_factors is None:
        process.allocation_factors = [f]
    else:
        process.allocation_factors.append(f)
    return f


def new_impact_category(name: str) -> ImpactCategory:
    return ImpactCategory(name=name)


def new_impact_factor(
    indicator: ImpactCategory,
    flow: Union[Ref, Flow],
    value: Union[str, float] = 1.0,
    unit: Optional[Union[Ref, Unit]] = None,
) -> ImpactFactor:
    factor = ImpactFactor(flow=as_ref(flow))
    if isinstance(value, str):
        factor.formula = value
    else:
        factor.value = value
    if unit:
        factor.unit = as_ref(unit)
    if indicator.impact_factors is None:
        indicator.impact_factors = [factor]
    else:
        indicator.impact_factors.append(factor)
    return factor


def new_impact_method(
    name: str, *indicators: Union[Ref, ImpactCategory]
) -> ImpactMethod:
    method = ImpactMethod(name=name)
    method.impact_categories = [as_ref(c) for c in indicators]
    return method


def as_ref(e: Union[RefEntity, Ref]) -> Ref:
    return e if isinstance(e, Ref) else e.to_ref()
