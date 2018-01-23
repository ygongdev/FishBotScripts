from datetime import datetime, timedelta
def increment_spreadsheet_column(column, increment):
	lastChar = column[-1]

	for i in range(increment):
		if lastChar < "Z":
			lastChar = chr(ord(lastChar) + 1)
			column = column[:-1] + lastChar
		else:
			length = len(column)
			column = ""
			for j in range(length + 1):
				column += "A"
			lastChar = "A"

	return column

print(increment_spreadsheet_column("AZ", 5))

def convert(time, duration):
	return (datetime.strptime(time, "%Y-%m-%d %H:%M:%S") - timedelta(seconds=int(duration)) - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")

print(convert("2018-01-22 21:48:05", 222))
