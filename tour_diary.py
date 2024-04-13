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

    def CreateDiary(self, title, content):
        # Here we reuse WriteDiary method, assuming content is the diary text
        return self.WriteDiary(title, content)

    def WriteDiary(self, title, content):
        try:
            UserId = self.UserInfo.GetCurrentUser()
            if UserId == -1:
                return False, "用户未登录。"
            compressed_data = compress_string(content) # content is the diary text
            if not os.path.exists("./diary/" + str(UserId)):
                os.makedirs("./diary/" + str(UserId))
            new_data = pd.DataFrame([[UserId, title, "./diary/" + str(UserId) + "/" + title + ".gz"]],
                                    columns=['id', 'title', 'dir'])
            self.id_dir = pd.concat([self.id_dir, new_data], ignore_index=True)
            self.id_dir.to_csv("./diary/id_dir.csv", index=False)
            with gzip.open("./diary/" + str(UserId) + "/" + title + ".gz", "wb") as file:
                file.write(compressed_data)
            return True, "日记创建成功。"
        except FileNotFoundError:
            return False, "用户数据文件不存在。"
        except Exception as e:
            return False, f"保存文件时发生错误：{e}"

    def SearchDiary(self, key):
        result = pd.DataFrame(columns=['id', 'title', 'ratio'])
        for i in range(len(self.id_dir)):
            ratio = fuzz.ratio(self.id_dir.iloc[i]['title'], key)
            if ratio > 0:  # Adding entries with a non-zero ratio
                new_data = {'id': self.id_dir.iloc[i]['id'], 'title': self.id_dir.iloc[i]['title'], 'ratio': ratio}
                result = result.append(new_data, ignore_index=True)
        if result.empty:
            return False, "查找不到结果"
        else:
            result.sort_values(by=['ratio'], ascending=False, inplace=True)
            return True, result

    def ShowDiary(self, diaryId):
        try:
            diary_entry = self.id_dir[self.id_dir['id'] == diaryId]
            if diary_entry.empty:
                return False, "日记不存在。"
            addr = diary_entry['dir'].iloc[0]
            with gzip.open(addr, "rb") as f:
                data = f.read()
            return True, decompress_string(data)
        except FileNotFoundError:
            return False, "日记文件不存在。"
        except Exception as e:
            return False, f"读取文件时发生错误：{e}"

