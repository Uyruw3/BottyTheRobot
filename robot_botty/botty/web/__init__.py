try:
    from .dashboard import WebDashboard
except ImportError:
    class WebDashboard:
        def __init__(self, *a, **kw): pass
        def start(self): print("  [Web] Flask no instalado"); return False
        def stop(self): pass
