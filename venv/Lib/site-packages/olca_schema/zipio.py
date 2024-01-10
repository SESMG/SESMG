import os
import zipfile
import olca_schema as schema

from typing import cast, Iterator, List, Optional, Type, TypeVar, Union

import olca_schema as schema


_E = TypeVar("_E", bound=schema.RootEntity)


class ZipWriter:
    def __init__(self, path: Union[str, os.PathLike]):
        self.__zip = zipfile.ZipFile(
            path, mode="a", compression=zipfile.ZIP_DEFLATED
        )
        if "olca-schema.json" not in self.__zip.namelist():
            self.__zip.writestr("olca-schema.json", '{"version": 2}')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.__zip.close()

    def write(self, entity: schema.RootEntity):
        if entity.id is None or entity.id == "":
            raise ValueError("entity must have an ID")
        folder = _folder_of_entity(entity)
        path = f"{folder}/{entity.id}.json"
        self.__zip.writestr(path, entity.to_json())


class ZipReader:
    def __init__(self, path: Union[str, os.PathLike]):
        self.__zip = zipfile.ZipFile(path, mode="r")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.__zip.close()

    def read(self, class_type: Type[_E], uid: str) -> Optional[_E]:
        folder = _folder_of_class(class_type)
        path = f"{folder}/{uid}.json"
        if path not in self.__zip.namelist():
            return None
        data = self.__zip.read(path)
        return cast(_E, class_type.from_json(data))

    def read_actor(self, uid: str) -> Optional[schema.Actor]:
        return self.read(schema.Actor, uid)

    def read_currency(self, uid: str) -> Optional[schema.Currency]:
        return self.read(schema.Currency, uid)

    def read_dq_system(self, uid: str) -> Optional[schema.DQSystem]:
        return self.read(schema.DQSystem, uid)

    def read_epd(self, uid: str) -> Optional[schema.Epd]:
        return self.read(schema.Epd, uid)

    def read_flow(self, uid: str) -> Optional[schema.Flow]:
        return self.read(schema.Flow, uid)

    def read_flow_property(self, uid: str) -> Optional[schema.FlowProperty]:
        return self.read(schema.FlowProperty, uid)

    def read_impact_category(self, uid: str) -> Optional[schema.ImpactCategory]:
        return self.read(schema.ImpactCategory, uid)

    def read_impact_method(self, uid: str) -> Optional[schema.ImpactMethod]:
        return self.read(schema.ImpactMethod, uid)

    def read_location(self, uid: str) -> Optional[schema.Location]:
        return self.read(schema.Location, uid)

    def read_parameter(self, uid: str) -> Optional[schema.Parameter]:
        return self.read(schema.Parameter, uid)

    def read_process(self, uid: str) -> Optional[schema.Process]:
        return self.read(schema.Process, uid)

    def read_product_system(self, uid: str) -> Optional[schema.ProductSystem]:
        return self.read(schema.ProductSystem, uid)

    def read_project(self, uid: str) -> Optional[schema.Project]:
        return self.read(schema.Project, uid)

    def read_result(self, uid: str) -> Optional[schema.Result]:
        return self.read(schema.Result, uid)

    def read_social_indicator(
        self, uid: str
    ) -> Optional[schema.SocialIndicator]:
        return self.read(schema.SocialIndicator, uid)

    def read_source(self, uid: str) -> Optional[schema.Source]:
        return self.read(schema.Source, uid)

    def read_unit_group(self, uid: str) -> Optional[schema.UnitGroup]:
        return self.read(schema.UnitGroup, uid)

    def read_each(self, type_: Type[_E]) -> Iterator[_E]:
        for uid in self.ids_of(type_):
            e = self.read(type_, uid)
            if e is not None:
                yield e

    def ids_of(self, type_: Type[_E]) -> List[str]:
        folder = _folder_of_class(type_)
        ids = []
        for info in self.__zip.filelist:
            if info.is_dir():
                continue
            name = info.filename
            if not name.endswith(".json"):
                continue
            parts = name.split("/")
            if len(parts) < 2:
                continue
            if parts[-2] != folder:
                continue
            ids.append(parts[-1][0:-5])
        return ids


def _folder_of_entity(entity: schema.RootEntity) -> str:
    if entity is None:
        raise ValueError("unknown root entity type")
    return _folder_of_class(type(entity))


def _folder_of_class(t: Type[_E]) -> str:
    if t == schema.Actor:
        return "actors"
    if t == schema.Currency:
        return "currencies"
    if t == schema.DQSystem:
        return "dq_systems"
    if t == schema.Epd:
        return "epds"
    if t == schema.Flow:
        return "flows"
    if t == schema.FlowProperty:
        return "flow_properties"
    if t == schema.ImpactCategory:
        return "lcia_categories"
    if t == schema.ImpactMethod:
        return "lcia_methods"
    if t == schema.Location:
        return "locations"
    if t == schema.Parameter:
        return "parameters"
    if t == schema.Process:
        return "processes"
    if t == schema.ProductSystem:
        return "product_systems"
    if t == schema.Project:
        return "projects"
    if t == schema.Result:
        return "results"
    if t == schema.SocialIndicator:
        return "social_indicators"
    if t == schema.Source:
        return "sources"
    if t == schema.UnitGroup:
        return "unit_groups"
    raise ValueError(f"not a known root entity type: {t}")
