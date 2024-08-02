from enum import Enum

# Not used -> here as an example for future implementations
class LoggerType(Enum):
    CONSOLE = 'console'
    FILE = 'file'
    GCP = 'gcp'
    
class GCPProjects(Enum):
    NOTSET = 'nope'
    G1P = 'orbital-airfoil-393318'
    ANDROID = 'enhanced-cable-405820'
    PMI = 'pmi-data-infrastructure'
    GPRO = 'gpro-infra'