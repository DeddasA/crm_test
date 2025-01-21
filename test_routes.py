from app import db, UserInfo
user = UserInfo.query.get(1)  # Replace 1 with the `user_id` you want to test
print(user)
