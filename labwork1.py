# 1. Calculate the area of a circle.
# radius = float(input("Enter circle radius? "))
# area = 3.14 * radius**2
# print(f"Circle area = {area:.1f}")

# 2. Convert Celsius into Fahrenheit.
# celsius = float(input("Enter the temperature in Celsius? "))
# fahrenheit = celsius * 9 / 5 + 32
# print(f"{celsius:g} (C) = {fahrenheit:g}(F)")

# 3. Check whether a number is prime.
# number = int(input("Enter a number? "))
# is_prime = number >= 2
#
# for divisor in range(2, int(number**0.5) + 1):
# 	if number % divisor == 0:
# 		is_prime = False
# 		break
#	
# if is_prime:
# 	print(f"{number} is a prime number")
# else:
# 	print(f"{number} is a NOT prime number")

# 4. Check whether a number is perfect.
# number = int(input("Enter a number? "))
# divisor_sum = 0
#
# for divisor in range(1, number):
# 	if number % divisor == 0:
# 		divisor_sum += divisor
#
# if divisor_sum == number:
# 	print(f"{number} is a perfect number")
# else:
# 	print(f"{number} is a NOT perfect number")

# 5. Find a favorite color in a list.
# colors = ["blue", "yellow", "black", "red"]
# favorite_color = input("What is your favorite color? ")
#
# if favorite_color in colors:
# 	color_index = colors.index(favorite_color)
# 	print(f"Your color is at index {color_index} in my list")
# else:
# 	print("Sorry, I could not find your color")

# 6. Create and print sequences using range().
# range1 = range(0, 7)
# range2 = range(1, 11, 3)
# range3 = range(5, 0, -1)
# range4 = range(6, -3, -2)
#
# print("range1", ", ".join(str(value) for value in range1))
# print("range2", ", ".join(str(value) for value in range2))
# print("range3", ", ".join(str(value) for value in range3))
# print("range4", ", ".join(str(value) for value in range4))

# 7. Remove dollar signs from a string.
# def remove_dollar_sign(s):
# 	return s.replace("$", "")
#
# money = input("Enter a money value: ")
# print(remove_dollar_sign(money))

# 8. Extract even numbers from an integer list.
# def extract_even(l):
# 	return [number for number in l if number % 2 == 0]
#
# numbers = [int(value) for value in input("Enter integers separated by spaces: ").split()]
# print(extract_even(numbers))

# 9. Calculate the factorial of a non-negative integer.
# def factorial(number):
# 	result = 1
# 	for value in range(2, number + 1):
# 		result *= value
# 	return result
#
# number = int(input("Enter a non-negative integer: "))
# print(factorial(number))

# 10. Get all divisors of a number.
# def get_divisors(number):
# 	return [divisor for divisor in range(1, number + 1) if number % divisor == 0]
#
# number = int(input("Enter a number: "))
# print(get_divisors(number))

# 11. Compute the distance between two points.
# import math
#
# x1 = float(input("Enter x1: "))
# y1 = float(input("Enter y1: "))
# x2 = float(input("Enter x2: "))
# y2 = float(input("Enter y2: "))
#
# distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
# print(f"Distance = {distance:.1f}")

# 12. Print a hollow rectangle with m rows and n columns.
def print_pattern(m, n):
	for row in range(m):
		if row == 0 or row == m - 1:
			print("*  " * (n - 1) + "*")
		elif n == 1:
			print("*")
		else:
			print("*" + " " * (3 * n - 4) + "*")


m = int(input("Enter the number of rows (m): "))
n = int(input("Enter the number of columns (n): "))
print_pattern(m, n)