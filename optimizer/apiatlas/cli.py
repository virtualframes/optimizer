from optimizer.apiatlas.scanner import main as _map
from optimizer.apiatlas.health import main as _health
from optimizer.apiatlas.heal import main as _heal
from optimizer.apiatlas.debugger import main as _debug

def map_main(): _map()
def health_main(): _health()
def heal_main(): _heal()
def debug_main(): _debug()