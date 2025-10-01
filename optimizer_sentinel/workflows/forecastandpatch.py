from .schemamigrationguard import SchemaMigrationGuard

schemamigrationguard = SchemaMigrationGuard()

def inject_isolation(target):
    print(f"Injecting SERIALIZABLE isolation level into {target}")

def addresourcelimits():
    print("Adding resource limits")

def forecastandpatch(forecast: dict) -> str:
    if forecast["bugtype"] == "racecondition":
        inject_isolation(forecast["target"])
    elif forecast["bugtype"] == "oom":
        addresourcelimits()
    elif forecast["bugtype"] == "migration":
        schemamigrationguard.validate(forecast["target"])
    return f"Patch applied to {forecast['target']}"
