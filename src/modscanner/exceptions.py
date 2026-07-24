'''exceptions raised by modscanne'''

class ModScannerError(Exception):
    '''base exception fpr all modscanner errors'''

class ModScannerConnectionError(Exception):
    '''raised when a Modbus connection cannot be establised'''