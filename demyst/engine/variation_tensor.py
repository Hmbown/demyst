import numpy as np

class VariationTensor:
    """
    Replacement data structure that preserves variation metadata
    instead of collapsing it with operations like mean(), sum(), etc.
    """
    
    def __init__(self, data, axis=None, keepdims=False, metadata=None):
        self.data = data
        self.axis = axis
        self.keepdims = keepdims
        self.metadata = metadata or {}
        self._variation_history = []
        
    def collapse(self, operation='mean'):
        """
        Perform the collapse operation while preserving variation history
        """
        
        if operation == 'mean':
            result = np.mean(self.data, axis=self.axis, keepdims=self.keepdims)
            self._variation_history.append({
                'operation': 'mean',
                'input_shape': self.data.shape,
                'axis': self.axis,
                'std_before': np.std(self.data),
                'std_after': np.std(result) if hasattr(result, 'shape') else 0
            })
        elif operation == 'sum':
            result = np.sum(self.data, axis=self.axis, keepdims=self.keepdims)
            self._variation_history.append({
                'operation': 'sum',
                'input_shape': self.data.shape,
                'axis': self.axis,
                'total_variation': np.sum(np.abs(np.diff(self.data)))
            })
        else:
            raise ValueError(f"Unknown operation: {operation}")
            
        return result
    
    def ensemble_sum(self, axis=None):
        """
        Sum operation that preserves ensemble information
        """
        result = np.sum(self.data, axis=axis)
        self._variation_history.append({
            'operation': 'ensemble_sum',
            'preserved_variance': np.var(self.data, axis=axis) if axis is not None else np.var(self.data)
        })
        return result
