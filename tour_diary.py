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
        self.id_dir = pd.DataFrame(columns=['author_id', 'title', 'dir'])
        if not os.path.exists("./diary"):
            os.makedirs("./diary")
        if os.path.exists("./diary/id_dir.csv"):
            self.id_dir = pd.read_csv("./diary/id_dir.csv")
        else:
            self.id_dir.to_csv("./diary/id_dir.csv", index=False)

    # def CreateDiary(self, title, content):
    #     # Here we reuse WriteDiary method, assuming content is the diary text
    #     return self.WriteDiary(title, content)

    def CreateDiary(self, title, content):
        try:
            UserId = self.UserInfo.GetCurrentUser()
            if UserId == -1:
                return False, "用户未登录。"
            compressed_data = compress_string(content)  # content is the diary text
            if not os.path.exists("./diary/" + str(UserId)):
                os.makedirs("./diary/" + str(UserId))
            new_data = pd.DataFrame(
                [[int(UserId), title, "./diary/" + str(UserId) + "/" + str(len(self.id_dir)) + ".gz"]],
                columns=['author_id', 'title', 'dir'])
            if not os.path.exists("./diary/" + str(UserId)):
                os.makedirs("./diary/" + str(UserId))
            with gzip.open("./diary/" + str(UserId) + "/" + str(len(self.id_dir)) + ".gz", "wb") as file:
                file.write(compressed_data)
            self.id_dir = pd.concat([self.id_dir, new_data], ignore_index=True)
            self.id_dir.to_csv("./diary/id_dir.csv", index=False)
            return True, "日记创建成功。"
        except FileNotFoundError:
            return False, "用户数据文件不存在。"
        except Exception as e:
            return False, f"保存文件时发生错误：{e}"

    def SearchDiary(self, key, SearchBy=None):
        SearchByDict = {None: 'ratio', 1: 'title', 2: 'content'}
        result = pd.DataFrame(columns=['author_id', 'title', 'ratio'])
        for i in range(len(self.id_dir)):
            ratio1 = fuzz.partial_ratio(self.id_dir.iloc[i]['title'], key)
            # ratio2 = fuzz.partial_ratio(self.id_dir.iloc[i]['location'], key)
            addr = self.id_dir.iloc[int(i)]['dir']
            with gzip.open(addr, "rb") as f:
                data = f.read()
            ratio3 = fuzz.partial_ratio(decompress_string(data), key)
            ratio = max(ratio1, ratio3)
            if ratio > 0:  # Adding entries with a non-zero ratio
                new_data = {'diary_id': i, 'ratio': ratio, 'title': ratio1, 'content': ratio3}
                result = result._append(new_data, ignore_index=True)
        if result.empty:
            return False, "查找不到结果"
        else:
            result.sort_values(by=[SearchByDict[SearchBy]], ascending=False, inplace=True)
            return True, result

    def DeleteDiary(self, diaryId):
        try:
            addr = self.id_dir.iloc[int(diaryId)]['dir']
            os.remove(addr)
            self.id_dir.drop(diaryId, axis=0, inplace=True)
            return True, "删除成功"
        except FileNotFoundError:
            return False, "日记文件不存在。"
        except Exception as e:
            return False, f"删除文件时发生错误：{e}"

    def DiaryName(self, diaryId):
        return self.id_dir.iloc[diaryId]['title']

    def AuthorName(self, diaryId):
        return self.UserInfo.GetUserName(self.id_dir.iloc[diaryId]['author_id'])

    def ShowDiary(self, diaryId):
        try:
            # diary_entry = self.id_dir[self.id_dir['id'] == diaryId]
            # if diary_entry.empty:
            #     return False, "日记不存在。"
            # addr = diary_entry['dir'].iloc[0]
            addr = self.id_dir.iloc[int(diaryId)]['dir']
            with gzip.open(addr, "rb") as f:
                data = f.read()
            return True, decompress_string(data)
        except FileNotFoundError:
            return False, "日记文件不存在。"
        except Exception as e:
            return False, f"读取文件时发生错误：{e}"
