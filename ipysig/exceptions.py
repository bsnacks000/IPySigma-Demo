'''
custom exceptions for IPySigma application

'''

class IPySigmaBaseException(Exception):
    ''' 
    exception base class for IPySigmaPackage
    '''
    pass


class IPySigmaAddOnException(IPySigmaBaseException):
    '''
    exception base class for sigma_add_on module
    '''
    pass


class IPySigmaCoreException(IPySigmaBaseException):
    '''
    exception base class for SigmaCore module
    '''
    pass


class IPySigmaGraphNodeIndexError(IPySigmaAddOnException, IndexError):
    '''
    exception thrown when graphs are empty
    '''
    pass

class IPySigmaGraphEdgeIndexError(IPySigmaAddOnException, IndexError):
    '''
    exception thrown when graphs are empty
    '''
    pass


class IPySigmaGraphDataFrameValueError(IPySigmaAddOnException, ValueError):
    '''
    exception thrown when build_pandas_df method returns empty dfs
    '''
    pass

class IPySigmaGraphJSONValueError(IPySigmaAddOnException, ValueError):
    '''
    exception thrown if JSON dict is empty
    '''
    pass


class IPySigmaNodeTypeError(IPySigmaAddOnException):
    '''
    exception thrown if 'node_type' field has not been assigned by user to node attributes
    '''

class IPySigmaLabelError(IPySigmaAddOnException):
    '''
    exception thrown if 'label' field has not been assigned by the user to node attributes
    '''