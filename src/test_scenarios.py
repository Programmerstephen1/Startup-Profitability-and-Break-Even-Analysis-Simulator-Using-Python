import sys
sys.path.insert(0, '.')
from webapp import scenarios_list
try:
    result = scenarios_list()
    print("✓ scenarios_list() works")
    print(f"Result type: {type(result)}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
