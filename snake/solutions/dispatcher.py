"""
Dictionary to convert a string into a class.
"""

from decayingVortices import DecayingVortices
from movingVortices import MovingVortices


# dictionary that contains the plug-in classes
# key is a string that contains the name of the class
dispatcher = {'DecayingVortices': DecayingVortices,
              'MovingVortices': MovingVortices}
