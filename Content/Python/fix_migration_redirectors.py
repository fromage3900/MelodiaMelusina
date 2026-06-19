"""Fix redirectors in /Game/EnvSandbox/Materials after Melodia migration.

Run: Tools -> Execute Python Script, or Output Log:
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/fix_migration_redirectors.py"
"""
import unreal

TARGET = "/Game/EnvSandbox/Materials"

def fix_redirectors(root: str = TARGET) -> bool:
    paths = unreal.EditorAssetLibrary.list_assets(root, recursive=True, include_folder=False)
    redirectors = [p for p in paths if unreal.EditorAssetLibrary.does_asset_exist(p)
                   and str(unreal.EditorAssetLibrary.find_asset_data(p).asset_class) == "ObjectRedirector"]
    unreal.log(f"[Redirectors] {root}: {len(redirectors)} redirector(s)")
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    for name in ("fix_up_redirectors", "fixup_referencers", "fix_up_referencers"):
        fn = getattr(asset_tools, name, None)
        if not callable(fn):
            continue
        try:
            fn(root) if fn.__code__.co_argcount >= 2 else fn(redirectors)
            unreal.EditorAssetLibrary.save_directory(root, only_if_is_dirty=False, recursive=True)
            unreal.log(f"[Redirectors] {name} OK — saved {root}")
            return True
        except Exception as exc:
            unreal.log_error(f"[Redirectors] {name} failed: {exc}")
    unreal.log_warning(
        "[Redirectors] No Python fix_up API — manual: Content Browser -> %s -> "
        "Fix Up Redirectors in Folder -> Save All. Found: %s" % (root, ", ".join(redirectors) or "none"))
    return False

if __name__ == "__main__":
    fix_redirectors()
