from typing import Union


def add(a: Union[float, int], b: Union[float, int]) -> float:
    """计算两个数的和.

    Examples:
        >>> add(4.0, 2.0)
        6.0
        >>> add(4, 2)
        6.0

    Args:
        a: A number representing the first addend in the addition.
        b: A number representing the second addend in the addition.

    Returns:
        A number representing the arithmetic sum of `a` and `b`.
    """
    return float(a + b)


def subtract(a: Union[float, int], b: Union[float, int]) -> float:
    """计算两个数的差.

    Examples:
        >>> subtract(3.0, 1.0)
        2.0
        >>> subtract(3, 1)
        2.0

    Args:
        a: A number representing the subtrahend in the subtraction.
        b: A number representing the minuend in the subtraction.

    Returns:
        A number representing the arithmetic remainder of `a` and `b`.
    """
    return float(a - b)


def multiply(a: Union[float, int], b: Union[float, int]) -> float:
    """计算两个数的积

    Examples:
        >>> multiply(2.0, 3.0)
        6.0
        >>> multiply(2, 3)
        6.0

    Args:
        a: A number representing the first multiplicator in the multiplication.
        b: A number representing the second multiplicator in the multiplication.

    Returns:
        A number representing the arithmetic product of `a` and `b`.
    """
    return float(a * b)


def divide(a: Union[float, int], b: Union[float, int]) -> float:
    """计算两个数的商

    Note:
        `0`不能做除数.

    Examples:
        >>> divide(3.0, 2.0)
        1.5
        >>> divide(3, 2)
        1.5

    Args:
        a: A number representing the divisor in the division.
        b: A number representing the dividend in the division.

    Returns:
        A number representing the arithmetic quotient of `a` and `b`.

    Exceptions:
        ZeroDivisionError: dividend cannot be zero number.
    """
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return float(a / b)
