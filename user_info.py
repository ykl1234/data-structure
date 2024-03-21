import pandas as pd
import os


class UserInfo:
    existed = pd.DataFrame(columns=['name', 'password'])
    admin_password = "2022211154"
    current_user = -1

    def __init__(self):
        self.current_user = -1
        if os.path.exists("./accounts/user.csv"):
            self.existed = pd.read_csv("./accounts/user.csv")
        else:
            self.existed.to_csv("./accounts/user.csv", index=False)

    def SignUp(self):
        print("Welcome to sign up!")
        flag = True
        while flag:
            flag = False
            new_name = input("User name: ")
            if new_name == "-1":
                return
            for i in self.existed['name'].tolist():
                if i == new_name:
                    flag = True
                    print("Name already exists!")
                    break
            valid_name = False
            for i in range(26):
                if new_name.startswith((chr(ord('A') + i), chr(ord('a') + i))):
                    valid_name = True
                    break
            if not valid_name:
                flag = True
                print("Invalid name!")
        flag = True
        while flag:
            flag = False
            new_password = input("Password: ")
            if len(new_password) < 6:
                flag = True
                print("Too short!")
        self.existed = self.existed._append({"name": new_name, "password": new_password}, ignore_index=True)
        self.existed.to_csv("./accounts/user.csv", index=False)
        print("Sign up successfully!")

    def SignIn(self):
        if self.current_user != -1:
            print("Please log out first!")
            return
        print("Welcome to sign in!")
        name = input("User name: ")
        if name == "-1":
            return
        flag = True
        for i in self.existed.index:
            if self.existed.loc[i, 'name'] == name:
                user_id = i
                flag = False
                break
        if flag:
            print("User doesn't exist!")
            return
        for i in range(5):
            password = input("Password: ")
            if password == str(self.existed.loc[user_id, 'password']):
                print("Login successfully!")
                self.current_user = user_id
                return
            print("Wrong password! You have {} attempts left.".format(4 - i))
        print("Login failed!")

    def SignOut(self):
        self.current_user = -1
        print("Sign out successfully!")

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
