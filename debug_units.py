import json

from demyst.guards.unit_guard import UnitGuard

guard = UnitGuard()

print("--- Case 1: Incompatible Addition ---")
code1 = """
mass = 10  # unit: kg
time = 5   # unit: s
result = mass + time
"""
res1 = guard.analyze(code1)
print(json.dumps(res1, indent=2, default=str))

print("\n--- Case 2: Clean Multiplication ---")
code2 = """
mass = 10  # unit: kg
accel = 9.8 # unit: m/s^2
force = mass * accel
"""
res2 = guard.analyze(code2)
print(json.dumps(res2, indent=2, default=str))
