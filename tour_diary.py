import pandas as pd
import os
import zlib
import gzip
from fuzzywuzzy import fuzz


def compress_string(string):
    compressed_data = zlib.compress(bytes(string, 'utf-8'))
    return compressed_data


def decompress_string(data):
    decompressed_data = zlib.decompress(data)
    return decompressed_data.decode('utf-8')


class TourDiary:
    def __init__(self, UserInfo):
        self.UserInfo = UserInfo
        self.id_dir = pd.DataFrame(columns=['id', 'title', 'dir'])
        if not os.path.exists("./diary"):
            os.makedirs("./diary")
        if os.path.exists("./diary/id_dir.csv"):
            self.id_dir = pd.read_csv("./diary/id_dir.csv")
        else:
            self.id_dir.to_csv("./diary/id_dir.csv", index=False)

    def WriteDiary(self, title, index):
        try:
            UserId = self.UserInfo.GetCurrentUser()
            if UserId == -1:
                return False, "用户未登录。"
            compressed_data = compress_string(index)
            if not os.path.exists("./diary/" + str(UserId)):
                os.makedirs("./diary/" + str(UserId))
            new_data = pd.DataFrame([[UserId, title, "./diary/" + str(UserId) + "/" + title + ".gz"]],
                                    columns=['id', 'title', 'dir'])
            self.id_dir = pd.concat([self.id_dir, new_data], ignore_index=True)
            self.id_dir.to_csv("./diary/id_dir.csv", index=False)
            with gzip.open("./diary/" + str(UserId) + "/" + title + ".gz", "w") as file:
                file.write(compressed_data)
        except FileNotFoundError:
            return False, "用户数据文件不存在。"
        except Exception as e:
            print(f"保存文件时发生错误：{e}")
            return False, "保存文件时发生错误。"

    def ShowDiary(self, diaryId):
        try:
            addr = self.id_dir.loc[diaryId, 'dir']
            with gzip.open(addr, "r") as f:
                data = f.read()
            return True, decompress_string(data)
        except FileNotFoundError:
            return False, "用户数据文件不存在。"
        except Exception as e:
            print(f"读取文件时发生错误：{e}")
            return False, "读取文件时发生错误。"

    def SearchDiary(self, key):
        result = pd.DataFrame(columns=['id', 'ratio'])
        for i in range(len(self.id_dir)):
            if fuzz.ratio(self.id_dir.iloc[i]['title'], key) != 0:
                new_data = pd.DataFrame([[self.id_dir.iloc[i]['id']], fuzz.ratio(self.id_dir.iloc[i]['title'], key)], columns=['id', 'ratio'])
                result = pd.concat([result, new_data], ignore_index=True)
        if result.empty:
            return False, "查找不到结果"
        else:
            return True, result

