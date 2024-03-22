import pandas as pd
import os


class UserInfo:
    def __init__(self):
        self.existed = pd.DataFrame(columns=['name', 'password'])
        # 确保accounts目录存在
        if not os.path.exists("./accounts"):
            os.makedirs("./accounts")
        # 读取现有的用户数据
        if os.path.exists("./accounts/user.csv"):
            self.existed = pd.read_csv("./accounts/user.csv")
        else:
            self.existed.to_csv("./accounts/user.csv", index=False)

    def SignUp(self, new_name, new_password):
        # 检查用户名是否存在
        if new_name in self.existed['name'].values:
            return False, "用户名已存在！"
        # 检查用户名是否以字母开头
        if not new_name[0].isalpha():
            return False, "无效的用户名！必须以字母开头。"
        # 检查密码长度
        if len(new_password) < 6:
            return False, "密码太短！"

        # 尝试追加数据并保存到文件
        try:
            new_data = pd.DataFrame([[new_name, new_password]], columns=['name', 'password'])
            self.existed = pd.concat([self.existed, new_data], ignore_index=True)
            self.existed.to_csv("./accounts/user.csv", index=False)
        except Exception as e:
            print(f"保存用户数据时发生错误：{e}")
            return False, "保存用户数据失败。"

        return True, "注册成功！"

    def SignIn(self, name, password):
        try:
            # 确保用户数据是最新的
            self.existed = pd.read_csv("./accounts/user.csv")

            # 查找用户名是否存在
            user_row = self.existed[self.existed['name'] == name]
            if user_row.empty:
                return False, "用户不存在。"

            # 检查密码是否匹配
            if user_row.iloc[0]['password'] == password:
                self.current_user = user_row.index.item()  # 更新当前用户索引为登录用户的索引
                return True, "登录成功！"
            else:
                return False, "密码错误。"
        except FileNotFoundError:
            return False, "用户数据文件不存在。"
        except Exception as e:
            print(f"登录过程中发生错误：{e}")
            return False, "登录过程中发生错误。"

    def GetCurrentUser(self):
        if self.current_user == -1:
            print("Please sign in!")
        else:
            print("User id: {}".format(self.current_user))
            print("User name: {}".format(self.existed.loc[self.current_user, 'name']))

    def CheckExist(self, uid):
        for i in self.existed.index:
            if str(i) == uid:
                return True
        return False

    def DeleteUserData(self):
        uid = input("Please enter uid: ")
        if uid == "all":
            password = input("Please enter administrator password: ")
            if password == self.admin_password:
                confirmation = input("You are deleting all user data! Please enter \"confirm\" to confirm: ")
                if confirmation == "confirm":
                    self.existed = pd.DataFrame(columns=['name', 'password'])
                    print("Delete successfully!")
                else:
                    print("Operation cancelled!")
            else:
                print("Wrong password! Operation cancelled!")
        elif self.CheckExist(uid):
            password = input("Please enter your password: ")
            if password == str(self.existed.loc[int(uid), 'password']):
                confirmation = input("You are deleting user data of {}! Please enter \"confirm\" to confirm: ".format(self.existed.loc[int(uid), 'name']))
                if confirmation == "confirm":
                    self.existed = self.existed.drop(index=int(uid), axis=0)
                    print("Delete successfully!")
                else:
                    print("Operation cancelled!")
            else:
                print("Wrong password! Operation cancelled!")
        else:
            print("User doesn't exist!")
            return
        self.existed.to_csv("./accounts/user.csv", index=False)

    def PrintUserData(self):
        for i in range(5):
            password = input("Administrator password: ")
            if password == self.admin_password:
                uid = input("Uid: ")
                if uid == "all":
                    print(self.existed)
                elif self.CheckExist(uid):
                    print(self.existed[int(uid), ['name', 'password']])
                else:
                    print("User doesn't exist!")
                return
            print("Wrong password! You have {} attempts left.".format(4 - i))
        print("Operation failed!")


if __name__ == '__main__':
    user = UserInfo()
    while True:
        mode = input("Mode: ")
        if mode == "0":
            print("Thanks for using!")
            break
        elif mode == "-1":
            user.PrintUserData()
        elif mode == "1":
            user.SignUp()
        elif mode == "2":
            user.SignIn()
        elif mode == "3":
            user.SignOut()
        elif mode == "4":
            user.GetCurrentUser()
        elif mode == "5":
            user.DeleteUserData()
        else:
            print("Illegal operation!")