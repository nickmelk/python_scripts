## SOME FUNCTION FOR DECIMAL-BINARY CONVERSIONS ##
class FloatingPointFormat:
    def __init__(self, bias, exponent, fraction):
        self.bias = bias
        self.exponent = exponent
        self.fraction = fraction

float32 = FloatingPointFormat(127, 8, 23)
float64 = FloatingPointFormat(1023, 11, 52)
float128 = FloatingPointFormat(16383, 15, 112)

def dec_to_bin(number):
    binary = ""
    if number == 0:
        binary = "0"
    while number > 0:
        binary = str(number%2) + binary
        number //= 2
    return binary

def bin_to_dec(number):
    decimal = 0
    for index, bit in enumerate(number[::-1]):
        decimal += int(bit) * 2**index
    return decimal

def dec_to_bin1(number: float, bits: int = 24):
    integer = int(number)
    fraction = number - integer
    integer_binary = ""
    if integer == 0:
        integer_binary = "0"
    while integer > 0:
        integer_binary = str(integer%2) + integer_binary
        integer //= 2
        bits -= 1
    fraction_binary = ""
    while bits > 0:
        fraction *= 2
        bit = int(fraction)
        fraction_binary += str(bit)
        fraction -= bit
        bits -= 1
    return integer_binary + "." + fraction_binary

def bin_ieee_754_to_dec(number: str, format: FloatingPointFormat = float32):
    sign = -int(number[0])
    exponent = number[1:format.exponent+1]
    fraction = number[format.exponent+1:]

    exponent_decimal = bin_to_dec(exponent) - format.bias
    if exponent_decimal < 0:
        fraction = "0"*abs(exponent_decimal-1) + fraction
    if exponent_decimal > len(fraction):
        fraction = fraction + "0"*(exponent_decimal-len(fraction))
    fraction = "1." + fraction
    for index, bit in enumerate(fraction):
        if bit == ".":
            point_index = index
    point_index = point_index+exponent_decimal
    fraction = fraction.replace(".", "")

    integer_part, fractional_part = fraction[:point_index], fraction[point_index:]
    integer_decimal = bin_to_dec(integer_part)
    fraction_decimal = 0
    for index, bit in enumerate(fractional_part):
        fraction_decimal += int(bit) * 2**(-index-1)
    return sign + (integer_decimal + fraction_decimal)

def dec_to_bin_ieee_754(number: float, format: FloatingPointFormat = float32):
    if number < 0:
        sign_bit = "1"
    else:
        sign_bit = "0"
    
    integer_part = int(abs(number))
    fractional_part = abs(number) - integer_part

    integer_binary = dec_to_bin(integer_part)

    fraction_binary = ""
    for _ in range(format.fraction):
        fractional_part *= 2
        bit = int(fractional_part)
        fraction_binary += str(bit)
        fractional_part -= bit

    binary_number = integer_binary + "." + fraction_binary

    one_app, was_seen = 0, False
    point_app = 1
    for index, bit in enumerate(binary_number):
        if bit == "1" and not was_seen:
            one_app = index
            was_seen = True
        if bit == ".":
            point_app = index

    binary_number = binary_number.replace(".", "")
    binary_number = binary_number[one_app+1:]
    if len(binary_number) > format.fraction:
        grs = binary_number[format.fraction:format.fraction+3]
        while len(grs) < 3:
            grs += "0"
        if int(grs) < 100:
            binary_number = binary_number[:format.fraction]
        if int(grs) > 100:
            binary_number = int(binary_number[:format.fraction], base=2) + 1
            binary_number = dec_to_bin(binary_number)
        # Other cases grs > 100, round up, grs == 100, round tie to even

    exponent = point_app - one_app
    if exponent > 0:
        exponent -= 1
    exponent += 127

    exponent_binary = dec_to_bin(exponent)

    exponent_binary = "0"*(format.exponent-len(exponent_binary)) + exponent_binary
    binary_number = binary_number + "0"*(format.fraction-len(binary_number))

    return sign_bit + exponent_binary + binary_number

bin = dec_to_bin_ieee_754(123456789.0)
print(bin)
print(bin_ieee_754_to_dec(bin))

# Test this thing with numpy floating points
import numpy as np
val_32 = np.float32(123456789.0)
print(val_32)
