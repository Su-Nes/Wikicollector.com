import hashlib

password = "owowowo"

m = hashlib.sha256(password.encode('utf-8')).hexdigest()

print(m)

"""
result = sql(SELECT * FROM users WHERE email='email' and password = 'm')

if result > 0:
    good
else:
    something wrong


OR


result = sql(SELECT * FROM users WHERE email='email')

if result == hashed_password
    good
else:
    something wrong

"""