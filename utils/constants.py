"""
StackForge - Design Constants
"""

# Material
FY_IS2062 = 2548.0          # kg/cm²
E_STEEL = 2.1e6             # kg/cm² (can be adjusted)

# Density
STEEL_DENSITY = 7850.0      # kg/m³

# Default Corrosion
DEFAULT_INT_CORROSION = 3.0  # mm
DEFAULT_EXT_CORROSION = 0.0  # mm

# Flare Height Factors
FLARE_FACTOR_UNLINED = 20
FLARE_FACTOR_LINED = 25

# Minimum Thickness (IS 6533)
MIN_SHELL_THICKNESS = 6.0   # mm

# Bolt defaults
MIN_BOLT_SIZE = "M24"
MIN_BOLT_PITCH_FACTOR = 2.9
MAX_BOLT_PITCH_FACTOR = 5.0

# Allowable stresses (default)
ALLOW_FLANGE_PLATE = 1682.0   # kg/cm²
ALLOW_BOLT_TENSION = 1223.0   # kg/cm²
ALLOW_BASE_PLATE = 1500.0     # kg/cm²
