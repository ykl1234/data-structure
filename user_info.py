import pandas as pd
import os
from queue import Queue


class UserInfo:
    def __init__(self):
        self.unusedId = Queue()  # 存放因为用户注销而导致可分配的id
        self.existed = pd.DataFrame(columns=['name', 'password'])
        # 确保accounts目录存在
        if not os.path.exists("./accounts"):
            os.makedirs("./accounts")
        # 读取现有的用户数据
        if os.path.exists("./accounts/user.csv"):
            self.existed = pd.read_csv("./accounts/user.csv")
        else:
            self.existed.to_csv("./accounts/user.csv", index=False)

    def SignUp(self, new_name, new_password):  # 注册新用户
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
            if self.unusedId.empty():  # 如果有可分配id则优先使用可分配id
                new_data = pd.DataFrame([[new_name, new_password]], columns=['name', 'password'])
                self.existed = pd.concat([self.existed, new_data], ignore_index=True)
            else:
                new_id = self.unusedId.get()
                self.existed.iloc[new_id]['name'] = new_name
                self.existed.iloc[new_id]['password'] = new_password
            self.existed.to_csv("./accounts/user.csv", index=False)
        except Exception as e:
            print(f"保存用户数据时发生错误：{e}")
            return False, "保存用户数据失败。"

        return True, "注册成功！"

    def SignIn(self, name, password):  # 用户登录
        try:
            if not name[0].isalpha():
                return False, "用户名不合法"
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

    def GetCurrentUser(self):  # 获取当前用户编号，-1为未登录状态
        # if self.current_user == -1:
        #     print("Please sign in!")
        # else:
        #     print("User id: {}".format(self.current_user))
        #     print("User name: {}".format(self.existed.loc[self.current_user, 'name']))
        return self.current_user

    def GetUserName(self, uid):  # 根据uid获取用户名
        # if self.existed.iloc[uid]['name'] == "0":
        #     return
        return self.existed.iloc[int(uid)]['name']

    def CheckExist(self, uid):  # 检查用户是否存在
        if len(self.existed) > int(uid) and self.existed.iloc[int(uid)]['name'] != "0":
            return True
        return False

    def DeleteUserData(self, uid):  # 删除用户数据
        if self.CheckExist(uid):  # 如果用户存在则将其用户名置为非法用户名并将其id加入可分配id列表
            self.existed.iloc[int(uid)]['name'] = "0"
            self.existed.to_csv("./accounts/user.csv", index=False)
            self.unusedId.put(int(uid))
            return True, "删除成功！"
        else:
            return False, "用户不存在。"

    def GetUserSize(self):  # 获取用户数量
        return len(self.existed)

    def PrintUserData(self):  # 仅作测试用
        for i in range(5):
            password = input("Administrator password: ")
            if password == "2022211154":
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
