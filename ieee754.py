## SOME FUNCTION FOR DECIMAL-BINARY CONVERSIONS ##
from fractions import Fraction

class FloatingPointFormat:
    def __init__(self, bias, exponent, fraction):
        self.bias = bias
        self.exponent = exponent
        self.fraction = fraction

float32 = FloatingPointFormat(127, 8, 23)
float64 = FloatingPointFormat(1023, 11, 52)
float128 = FloatingPointFormat(16383, 15, 112)

def dec_int_to_bin(number: int) -> str:
    bin = ""
    if number == 0:
        bin = "0"
    while number > 0:
        bin = str(number%2) + bin
        number //= 2
    return bin

def bin_to_dec_int(number: str) -> int:
    decimal = 0
    for index, bit in enumerate(number[::-1]):
        decimal += int(bit) * 2**index
    return decimal

def bin_ieee_754_to_dec(number: str, format: FloatingPointFormat = float32) -> float:
    sign = 1 if number[0] == '0' else -1
    exponent = number[1:format.exponent+1]
    fraction = number[format.exponent+1:]

    exponent_decimal = bin_to_dec_int(exponent) - format.bias
    if exponent_decimal > len(fraction):
        fraction = fraction + "0"*(exponent_decimal-len(fraction))
    fraction = "1." + fraction
    if exponent_decimal < 0:
        fraction = "0"*abs(exponent_decimal-1) + fraction
    for index, bit in enumerate(fraction):
        if bit == ".":
            point_index = index
    point_index = point_index + exponent_decimal
    fraction = fraction.replace(".", "")

    integer_part, fractional_part = fraction[:point_index], fraction[point_index:]
    integer_decimal = bin_to_dec_int(integer_part)
    fraction_decimal = 0
    for index, bit in enumerate(fractional_part):
        fraction_decimal += int(bit) * 2**(-index-1)
    return sign * (integer_decimal + fraction_decimal)

# this function needs some refactoring
def dec_to_bin_ieee_754(number: str, format: FloatingPointFormat = float32) -> str:
    sign_bit = '0' if not '-' in number else '1'
    
    if '-' in number:
        number = number.replace('-', '')

    number = Fraction(number)
    integer_part = number.numerator // number.denominator
    integer_binary = dec_int_to_bin(integer_part)

    fractional_part = number - integer_part
    fractional_binary = ''
    for _ in range(format.fraction+3):
        fractional_part *= 2
        bit = int(fractional_part)
        fractional_binary += str(bit)
        fractional_part -= bit

    binary_number = integer_binary + '.' + fractional_binary

    one_app, was_seen = 0, False
    point_app = 1
    for index, bit in enumerate(binary_number):
        if bit == '1' and not was_seen:
            one_app = index
            was_seen = True
        if bit == '.':
            point_app = index

    exponent = point_app - one_app
    if exponent > 0:
        exponent -= 1
    exponent += format.bias
    exponent_binary = dec_int_to_bin(exponent)

    binary_number = binary_number.replace('.', '')
    if exponent-format.bias >= 0:
        binary_number = binary_number[one_app+1:]
    else:
        binary_number = binary_number[one_app:]         # When point is removed indeces get shifted and one_app becomes index which is +1 from first 1 bit
    while len(binary_number) < format.fraction+3:
        fractional_part *= 2
        bit = int(fractional_part)
        binary_number += str(bit)
        fractional_part -= bit
    if len(binary_number) > format.fraction:
        # Rounding
        # If grs > 100 round up
        # If grs < 100 truncate
        # If grs = 100 take LSB if it is 1 round up, otherwise truncate (i.e. round ties to even) 
        grs = binary_number[format.fraction:format.fraction+3]
        binary_number = binary_number[:format.fraction]
        if int(grs) > 100 or binary_number[-1] == '1':
            binary_number = int(binary_number, base=2) + 1
            binary_number = dec_int_to_bin(binary_number)

    exponent_binary = '0'*(format.exponent-len(exponent_binary)) + exponent_binary
    binary_number = binary_number + '0'*(format.fraction-len(binary_number))

    return sign_bit + exponent_binary + binary_number

# Some numbers
# 123456789.0
bin = dec_to_bin_ieee_754("0.1", float64)
print(bin)
print(len(bin))
dec = bin_ieee_754_to_dec(bin, float64)
print(f"{dec:.17f}")

# Test this thing with numpy floating points
import numpy as np
val_64 = np.float64(0.1)
print(val_64)
