from functools import wraps


def parametrize(arg_names, arg_values):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args):
            func(self, *args)
        wrapper._parametrized = (arg_names, arg_values)
        return wrapper
    return decorator


class ParametrizedTestCaseMeta(type):
    """
    Creates tested methods based on a parametrized method of the Testcase class. They have an index at the end,
      so you can easily track down errors.
    In general, this metaclass makes the testing process more reliable, clear and compact.
    """

    def __new__(cls, name, bases, attrs):
        new_attrs = {}
        for attr_name, attr_value in attrs.items():
            if hasattr(attr_value, '_parametrized'):
                arg_names, arg_values = attr_value._parametrized
                for index, values in enumerate(arg_values, 1):
                    test_method_name = f'{attr_name}_{index}'
                    new_attrs[test_method_name] = cls.create_test_method(attr_value, values)
            else:
                new_attrs[attr_name] = attr_value
        return super().__new__(cls, name, bases, new_attrs)

    @staticmethod
    def create_test_method(func, values):
        @wraps(func)
        def test_method(self):
            return func(self, *values)
        return test_method


