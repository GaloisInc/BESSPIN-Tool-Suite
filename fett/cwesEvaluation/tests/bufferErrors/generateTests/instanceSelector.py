import collections
import math

from fett.base.utils.misc import *

# Access, Boundary, and Location all have 2 possible values, while Magnitude
# has 3 possible values.  Therefore, NUM_CONCEPTS == 2 * 2 * 2 * 3
NUM_CONCEPTS = 2**3 * 3

def instanceToConcept(instance):
    """
    Translates an instance to a concept consisting of a subset of the
    properties of the instance.  This subset has been selected to provide good
    coverage of the CWE clafer constraints.
    """
    return (instance.Access,
            instance.Boundary,
            instance.Location,
            instance.Magnitude)

def getQuota(instance):
    """
    Given an instance, returns the quota for the concept it belongs to.
    """
    baseQuota = (getSettingDict('bufferErrors', 'nTests') // NUM_CONCEPTS)
    if (instance.Boundary == "Boundary_Above" and
        instance.Access == "Access_Write" and
        instance.Excursion == "Excursion_Discrete"):
        # Increase representation of Excursion_Continuous when
        # Boundary_Above and Access_Write are selected to increase tests of
        # CWE-120, which is more constrained than the other CWE tests.
        # NOTE: Because Excursion is not an element of the concept tuple, this
        # places an upper bound on the number of tests that satisfy these
        # conditions.  It does not set a lower bound.  We only care that enough
        # Excursion_Continuous tests are generated to satisfy CWE-120.
        return baseQuota // 4
    return baseQuota

class InstanceSelector:
    """
    This class selects test instances from a list of instances to produce a
    set of generated tests with good coverage of the buffer errors concepts
    """
    def __init__(self, instancePairs, rnd):
        nTests = getSettingDict('bufferErrors', 'nTests')
        self.conceptCounts = collections.defaultdict(int)
        self.instancePairs = instancePairs
        self.rnd = rnd

    def chooseInstance(self):
        numSelected = sum(self.conceptCounts.values())
        (instance, tg) = self.rnd.choice(self.instancePairs)
        concept = instanceToConcept(instance)
        underQuota = numSelected < (getSettingDict('bufferErrors', 'nTests') //
                                    NUM_CONCEPTS *
                                    NUM_CONCEPTS)
        while ((underQuota and
                self.conceptCounts[concept] >= getQuota(instance)) or
               ((not underQuota) and
                self.conceptCounts[concept] >= (getQuota(instance) + 1))):
            # Sample until an instance is chosen that helps meet a quota.
            # If all quotas have been reached and nTests is not a multiple of
            # NUM_CONCEPTS, then select an instance that is at (but not
            # greater than) its quota.
            (instance, tg) = self.rnd.choice(self.instancePairs)
            concept = instanceToConcept(instance)
        self.conceptCounts[concept] += 1
        return tg

