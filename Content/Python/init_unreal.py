import sys, os, importlib.util, unreal
pyc = os.path.join(os.path.dirname(__file__), "livelink_unreal.pyc")
spec = importlib.util.spec_from_file_location("livelink_unreal", pyc)
m = importlib.util.module_from_spec(spec)
sys.modules["livelink_unreal"] = m
spec.loader.exec_module(m)
def startup(): m.startup() if hasattr(m, 'startup') else None
def shutdown(): m.shutdown() if hasattr(m, 'shutdown') else None
