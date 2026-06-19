"""Build L_SakuraPath: dusk lighting rig + toon/bloom post + CineCamera + greybox blockout.

Greybox uses engine BasicShapes (replace with the CC0 kit later). Assigns MI_Sakura_*
materials if they exist (run setup_sakura_instances.py first).

Run (full path): py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_sakura_scene.py"
"""
import unreal

LEVEL = "/Game/EnvSandbox/Environments/Sakura/L_SakuraPath"
MIROOT = "/Game/EnvSandbox/Materials/Instances/Sakura"
CUBE = "/Engine/BasicShapes/Cube.Cube"
PLANE = "/Engine/BasicShapes/Plane.Plane"
CYL = "/Engine/BasicShapes/Cylinder.Cylinder"

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les.new_level(LEVEL)


def spawn(cls, loc=(0, 0, 0), rot=(0, 0, 0)):
    try:
        return eas.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator(*rot))
    except Exception as e:
        unreal.log_warning(f"spawn {cls}: {e}")
        return None


def mi(name):
    p = f"{MIROOT}/{name}"
    return unreal.load_asset(p) if unreal.EditorAssetLibrary.does_asset_exist(p) else None


def greybox(mesh_path, loc, scale, mat=None, label=""):
    a = spawn(unreal.StaticMeshActor, loc)
    if not a:
        return
    a.set_actor_scale3d(unreal.Vector(*scale))
    if label:
        a.set_actor_label(label)
    c = a.static_mesh_component
    c.set_static_mesh(unreal.load_asset(mesh_path))
    if mat:
        c.set_material(0, mat)
    return a


# ---- dusk lighting rig ----
sun = spawn(unreal.DirectionalLight, (0, 0, 900), (-11, 38, 0))
if sun:
    sc = sun.directional_light_component
    sc.set_editor_property("light_color", unreal.Color(255, 198, 162))
    sc.set_editor_property("intensity", 3.2)
spawn(unreal.SkyAtmosphere)
spawn(unreal.SkyLight, (0, 0, 500))
fog = spawn(unreal.ExponentialHeightFog, (0, 0, 60))
if fog:
    fc = fog.component
    fc.set_editor_property("fog_density", 0.012)
    fc.set_editor_property("volumetric_fog", True)

# ---- post: toon-friendly bloom + locked exposure ----
ppv = spawn(unreal.PostProcessVolume, (0, 0, 300))
if ppv:
    ppv.set_editor_property("unbound", True)
    s = ppv.get_editor_property("settings")
    s.set_editor_property("b_override_bloom_intensity", True)
    s.set_editor_property("bloom_intensity", 1.5)
    s.set_editor_property("b_override_auto_exposure_method", True)
    s.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    s.set_editor_property("b_override_auto_exposure_bias", True)
    s.set_editor_property("auto_exposure_bias", 11.0)
    ppv.set_editor_property("settings", s)

# ---- greybox blockout ----
greybox(PLANE, (0, 0, 0), (60, 60, 1), mi("MI_Sakura_Moss"), "Ground")
# stepping-stone path leading toward the torii
for i in range(7):
    greybox(CUBE, (-1400 + i * 230, -60 + (i % 2) * 50, 6), (1.4, 1.0, 0.12),
            mi("MI_Sakura_StonePath"), f"PathStone_{i}")
# torii focal point (2 pillars + 2 cross-beams)
red = mi("MI_Sakura_ToriiRed")
greybox(CUBE, (300, -260, 280), (0.4, 0.4, 5.6), red, "Torii_PillarL")
greybox(CUBE, (300, 260, 280), (0.4, 0.4, 5.6), red, "Torii_PillarR")
greybox(CUBE, (300, 0, 560), (0.5, 6.2, 0.4), red, "Torii_TopBeam")
greybox(CUBE, (300, 0, 470), (0.4, 5.6, 0.28), red, "Torii_Tie")
# stone lantern near the path
greybox(CYL, (-600, 360, 90), (0.5, 0.5, 1.8), mi("MI_Sakura_Lantern"), "Lantern")
# greybox sakura trunks (canopy goes on later)
bark = mi("MI_Sakura_Bark")
for x, y in ((-900, -520), (-300, 560), (600, -600), (1000, 500)):
    greybox(CYL, (x, y, 320), (0.7, 0.7, 6.4), bark, f"Trunk_{x}_{y}")

# ---- hero camera ----
spawn(unreal.CineCameraActor, (-1500, -260, 240), (0, -7, 14))

les.save_current_level()
unreal.log(f"[Sakura] scene built: {LEVEL}")
print(f"SAKURA_SCENE built {LEVEL}")
