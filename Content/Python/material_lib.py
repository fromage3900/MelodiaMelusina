"""Shared helpers for BS_GodFile material Python builders."""
from __future__ import annotations

import unreal

MATERIALS_ROOT = "/Game/EnvSandbox/Materials"
FUNCTION_DIR = f"{MATERIALS_ROOT}/Functions"
PROFILE_DIR = f"{MATERIALS_ROOT}/ToonProfiles"
MASTER_DIR = f"{MATERIALS_ROOT}/Masters"
SDF_INST_DIR = f"{MATERIALS_ROOT}/SDF/Instances"
ENV_INST_DIR = f"{MATERIALS_ROOT}/Instances/Environment"
POST_DIR = f"{MATERIALS_ROOT}/PostProcess"
MPC_DIR = f"{MATERIALS_ROOT}/Functions"


def ensure_directory(path: str) -> None:
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def asset_path(folder: str, name: str) -> str:
    return f"{folder}/{name}.{name}"


def save_package(asset) -> None:
    unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False)


def try_set_editor_property(obj, name: str, value) -> None:
    try:
        if hasattr(obj, "has_editor_property") and obj.has_editor_property(name):
            obj.set_editor_property(name, value)
    except Exception:
        pass


def create_expression(owner, expression_class, x: int, y: int):
    if isinstance(owner, unreal.MaterialFunction):
        return unreal.MaterialEditingLibrary.create_material_expression_in_function(
            owner, expression_class, x, y
        )
    return unreal.MaterialEditingLibrary.create_material_expression(
        owner, expression_class, x, y
    )


def connect(from_expr, from_output: str, to_expr, to_input: str) -> bool:
    try:
        unreal.MaterialEditingLibrary.connect_material_expressions(
            from_expr, from_output, to_expr, to_input
        )
        return True
    except Exception:
        return False


def connect_unary(from_expr, to_expr) -> bool:
    pin_names = list(
        unreal.MaterialEditingLibrary.get_material_expression_input_names(to_expr)
    )
    for pin in pin_names + ["", "None"]:
        if connect(from_expr, "", to_expr, pin):
            return True
    return False


def connect_front_material(material, from_expr, from_output: str = "") -> None:
    unreal.MaterialEditingLibrary.connect_material_property(
        from_expr,
        from_output,
        unreal.MaterialProperty.MP_FRONT_MATERIAL,
    )


def connect_toon_pin(toon_bsdf, expr, pin_names: tuple[str, ...]) -> bool:
    for pin in pin_names:
        if connect(expr, "", toon_bsdf, pin):
            return True
    return False


def scalar_param(owner, name: str, group: str, default: float, x: int, y: int):
    expr = create_expression(owner, unreal.MaterialExpressionScalarParameter, x, y)
    expr.set_editor_property("parameter_name", name)
    expr.set_editor_property("group", group)
    expr.set_editor_property("default_value", default)
    return expr


def vector_param(owner, name: str, group: str, default: tuple[float, float, float, float], x: int, y: int):
    expr = create_expression(owner, unreal.MaterialExpressionVectorParameter, x, y)
    expr.set_editor_property("parameter_name", name)
    expr.set_editor_property("group", group)
    expr.set_editor_property("default_value", unreal.LinearColor(*default))
    return expr


def texture_param(owner, name: str, group: str, x: int, y: int):
    expr = create_expression(owner, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
    expr.set_editor_property("parameter_name", name)
    expr.set_editor_property("group", group)
    return expr


def create_toon_profiles(names: list[str]) -> dict[str, unreal.ToonProfile]:
    ensure_directory(PROFILE_DIR)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.ToonProfileFactory()
    profiles: dict[str, unreal.ToonProfile] = {}
    for profile_name in names:
        path = asset_path(PROFILE_DIR, profile_name)
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            profiles[profile_name] = unreal.load_asset(path)
            continue
        profile = asset_tools.create_asset(
            profile_name, PROFILE_DIR, unreal.ToonProfile, factory
        )
        if not profile:
            raise RuntimeError(f"Failed to create ToonProfile {profile_name}")
        profiles[profile_name] = profile
        save_package(profile)
    return profiles


def set_instance_vector(instance, name: str, rgba: tuple[float, float, float, float]) -> None:
    color = unreal.LinearColor(*rgba)
    if hasattr(unreal.MaterialEditingLibrary, "set_material_instance_vector_parameter_value"):
        unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
            instance, name, color
        )
    else:
        instance.set_vector_parameter_value_editor_only(name, color)


def set_instance_scalar(instance, name: str, value: float) -> None:
    if hasattr(unreal.MaterialEditingLibrary, "set_material_instance_scalar_parameter_value"):
        unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
            instance, name, value
        )
    else:
        instance.set_scalar_parameter_value_editor_only(name, value)


def set_instance_static_switch(instance, name: str, value: bool) -> None:
    if hasattr(unreal.MaterialEditingLibrary, "set_material_instance_static_switch_parameter_value"):
        unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(
            instance, name, value
        )
    else:
        try_set_editor_property(instance, name, value)


def set_instance_toon_profile(instance, profile: unreal.ToonProfile) -> None:
    try_set_editor_property(instance, "toon_profile", profile)
    try_set_editor_property(instance, "override_toon_profile", True)


def create_material_instance(name: str, folder: str, parent_path: str) -> unreal.MaterialInstanceConstant:
    ensure_directory(folder)
    inst_path = asset_path(folder, name)
    if unreal.EditorAssetLibrary.does_asset_exist(inst_path):
        return unreal.load_asset(inst_path)
    factory = unreal.MaterialInstanceConstantFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    parent = unreal.load_asset(parent_path)
    instance = asset_tools.create_asset(
        name, folder, unreal.MaterialInstanceConstant, factory
    )
    if not instance:
        raise RuntimeError(f"Failed to create instance {name}")
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, parent)
    return instance
