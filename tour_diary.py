import json

import numpy as np
import pandas as pd
import os
import zlib
import gzip
from fuzzywuzzy import fuzz
from queue import Queue
from skimage import io


def compress_string(string):
    compressed_data = zlib.compress(bytes(string, 'utf-8'))
    return compressed_data


def decompress_string(data):
    decompressed_data = zlib.decompress(data)
    return decompressed_data.decode('utf-8')


class TourDiary:
    def __init__(self, UserInfo):
        self.unusedId = Queue()  # 保存因删除日记而导致未使用的id
        self.UserInfo = UserInfo
        self.RecDiary = pd.DataFrame(
            columns=['recent_diary', 'next_pos', 'liked_diary'])  # 保存每个人最近浏览的日记，行索引为用户id，列索引为最近浏览的日记id和最久远的日记位置
        self.IdDir = pd.DataFrame(columns=['author_id', 'location', 'title', 'dir',
                                           'img_list', 'heat'])  # 日记信息，行索引为日记id，列索引包括作者id，地点，标题，所处文件夹，图片所处位置列表
        if not os.path.exists("./diary"):
            os.makedirs("./diary")
        if os.path.exists("./diary/IdDir.csv"):
            self.IdDir = pd.read_csv("./diary/IdDir.csv")
            self.IdDir['img_list'] = self.IdDir['img_list'].apply(json.loads)
        else:
            self.IdDir['img_list'] = self.IdDir['img_list'].apply(json.dumps)
            self.IdDir.to_csv("./diary/IdDir.csv", index=False)
            self.IdDir['img_list'] = self.IdDir['img_list'].apply(json.loads)
        if os.path.exists("./diary/RecDiary.csv"):
            self.RecDiary = pd.read_csv("./diary/RecDiary.csv")
            self.RecDiary['recent_diary'] = self.RecDiary['recent_diary'].apply(json.loads)
            self.RecDiary['liked_diary'] = self.RecDiary['liked_diary'].apply(json.loads)
        if os.path.exists("./diary/RecSize.npy"):
            self.RecSize = np.load("./diary/RecSize.npy")  # 存储可保存的最近浏览的日记最大数量，越大推荐得越精准，越小越节省空间
        else:
            self.SetRecSize(10)  # 默认初始值10
        self.UpdateRecDiary()

    def SaveRecDiary(self):
        self.RecDiary['recent_diary'] = self.RecDiary['recent_diary'].apply(json.dumps)
        self.RecDiary['liked_diary'] = self.RecDiary['liked_diary'].apply(json.dumps)
        self.RecDiary.to_csv("./diary/RecDiary.csv", index=False)
        self.RecDiary['recent_diary'] = self.RecDiary['recent_diary'].apply(json.loads)
        self.RecDiary['liked_diary'] = self.RecDiary['liked_diary'].apply(json.loads)

    def SaveIdDir(self):
        self.IdDir['img_list'] = self.IdDir['img_list'].apply(json.dumps)
        self.IdDir.to_csv("./diary/IdDir.csv", index=False)
        self.IdDir['img_list'] = self.IdDir['img_list'].apply(json.loads)

    def GetDiaryHeat(self, diaryId):
        return self.IdDir.loc[diaryId, 'heat']

    def LikeDiary(self, diaryId):
        UserId = self.UserInfo.GetCurrentUser()
        if UserId == -1:
            return False, "用户未登录。"
        print(self.RecDiary.loc[UserId, 'liked_diary'])
        print(type(self.RecDiary.loc[UserId, 'liked_diary']))
        # if np.isnan(self.RecDiary.loc[UserId, 'liked_diary']):
        #     self.RecDiary.loc[UserId, 'liked_diary'] = []
        if self.LikedDiary(diaryId):
            self.RecDiary.loc[UserId, 'liked_diary'].remove(int(diaryId))
            self.IdDir.loc[int(diaryId), 'heat'] = self.IdDir.loc[int(diaryId), 'heat'] - 5
        else:
            self.RecDiary.loc[UserId, 'liked_diary'].append(int(diaryId))
            self.IdDir.loc[int(diaryId), 'heat'] = self.IdDir.loc[int(diaryId), 'heat'] + 5
        print(self.RecDiary.loc[UserId, 'liked_diary'])
        self.SaveRecDiary()
        self.SaveIdDir()

    def UpdateRecDiary(self):  # 当创建新用户时需更新最近浏览
        if self.UserInfo.GetUserSize() > len(self.RecDiary):
            for i in range(len(self.RecDiary), self.UserInfo.GetUserSize()):
                recent_diary = []
                for j in range(self.RecSize):
                    recent_diary.append(-1)
                new_data = pd.DataFrame([[recent_diary, 0, []]], columns=['recent_diary', 'next_pos', 'liked_diary'])
                self.RecDiary = pd.concat([self.RecDiary, new_data], ignore_index=True)
        self.SaveRecDiary()

    def ReadDiary(self, diaryId):  # 当用户读日记时将其加入最近浏览
        self.IdDir.loc[diaryId, 'heat'] = self.IdDir.loc[diaryId, 'heat'] + 1
        self.SaveIdDir()
        UserId = self.UserInfo.GetCurrentUser()
        if UserId == -1:
            return False, "用户未登录。"
        self.RecDiary.loc[UserId, 'recent_diary'][self.RecDiary.iloc[UserId]['next_pos']] = int(
            diaryId)  # 删去最久远的记录并加入新的
        self.RecDiary.loc[UserId, 'next_pos'] += 1
        if self.RecDiary.iloc[UserId]['next_pos'] >= len(self.RecDiary.loc[UserId, 'recent_diary']):
            self.RecDiary.loc[UserId, 'next_pos'] = 0
        self.SaveRecDiary()

    def SetRecSize(self, size):  # 设置最近浏览的最大数量并相应更新最近浏览表
        self.RecSize = size
        np.save("./diary/RecSize.npy", self.RecSize)
        for i in range(len(self.RecDiary)):
            next_pos = self.RecDiary.iloc[i]['next_pos']
            recent_list = self.RecDiary.loc[i, 'recent_diary']
            length = len(recent_list)
            if length > size:  # 对最近浏览列表进行处理，保证其长度为新的size
                del recent_list[next_pos: length + min(next_pos - size, 0)]
                del recent_list[0: max(next_pos - size, 0)]
            else:
                for j in range(len(self.RecDiary.iloc[i]['recent_diary']), size):
                    recent_list.insert(next_pos + j, -1)
            self.RecDiary.loc[i, 'recent_diary'] = recent_list
        self.SaveRecDiary()

    def RecommendDiary(self):  # 根据用户最近浏览的日记推荐日记
        UserId = self.UserInfo.GetCurrentUser()
        if UserId == -1:
            return False, "用户未登录。"
        recommend_sim = pd.DataFrame(columns=['diary_id', 'ratio'])
        recommend_heat = pd.DataFrame(columns=['diary_id', 'ratio'])
        for i in self.RecDiary.iloc[UserId]['recent_diary']:
            result, diary = self.SearchDiary(i)
            if result:
                diary.drop(columns=['title', 'location', 'content'], inplace=True)
                for j in range(len(diary)):
                    if diary.iloc[j]['diary_id'] in recommend_sim['diary_id'].values:
                        recommend_sim.iloc[recommend_sim['diary_id'] == diary.iloc[j]['diary_id']]['ratio'] += diary.iloc[j][
                            'ratio']
                    else:
                        new_data = pd.DataFrame([[diary.iloc[j]['diary_id'], diary.iloc[j]['ratio']]],
                                                columns=['diary_id', 'ratio'])
                        recommend_sim = pd.concat([recommend_sim, new_data], ignore_index=True)
        recommend_sim.sort_values(by='ratio', ascending=False, inplace=True)
        for i in range(len(self.IdDir)):
            if i not in recommend_sim['diary_id'].values:
                new_data = pd.DataFrame([[i, self.IdDir.loc[i, 'heat']]], columns=['diary_id', 'ratio'])
                recommend_heat = pd.concat([recommend_heat, new_data], ignore_index=True)
        recommend_heat.sort_values(by='ratio', ascending=False, inplace=True)
        if recommend_sim.empty:
            return False, "没有推荐。"
        else:
            return True, pd.concat([recommend_sim, recommend_heat], ignore_index=True)  # 返回值为两列，一列是日记id，另一列是相关度，按相关度降序排列

    def CreateDiary(self, title, content, location=None, imgs=None):  # 创建日记，其中地点和图片是可选项，图片需传入一个列表，列表中是日记中的所有图片
        try:
            UserId = self.UserInfo.GetCurrentUser()
            if UserId == -1:
                return False, "用户未登录。"
            compressed_data = compress_string(content)  # 压缩日记内容
            if self.unusedId.empty():  # 如果没有可分配的id则为日记创建新id
                new_id = len(self.IdDir)
                new_data = pd.DataFrame([[None, None, None, None, None, 0]],
                                        columns=['author_id', 'location', 'title', 'dir', 'img_list', 'heat'])
                self.IdDir = pd.concat([self.IdDir, new_data], ignore_index=True)
            else:
                new_id = self.unusedId.get()
            path = "./diary/" + str(UserId) + "/" + str(new_id)
            if not os.path.exists(path):
                os.makedirs(path)
            if imgs is None:
                imgs = []
            imgdir = []
            for img in imgs:  # 按照图片的顺序保存图片，命名为编号
                num = str(len(imgdir))
                imgdir.append(path + "/" + num + ".jpg")
                io.imsave(path + "/" + num + ".jpg", img)
            self.IdDir['img_list'] = self.IdDir['img_list'].astype(object)
            self.IdDir.at[new_id, 'author_id'] = int(UserId)
            self.IdDir.at[new_id, 'location'] = location
            self.IdDir.at[new_id, 'title'] = title
            self.IdDir.at[new_id, 'dir'] = path + "/content.gz"
            self.IdDir.at[new_id, 'img_list'] = imgdir
            self.IdDir.at[new_id, 'heat'] = 0
            self.SaveIdDir()
            with gzip.open(path + "/content.gz", "wb") as file:  # 将压缩后的内容保存为.gz文件
                file.write(compressed_data)
            return True, "日记创建成功。"
        except FileNotFoundError:
            return False, "用户数据文件不存在。"
        except Exception as e:
            return False, f"保存文件时发生错误：{e}"

    def SearchDiary(self, key, SearchBy=None):  # 按照key来搜索，SearchBy为搜索方式，1为标题，2为内容，缺省表示三者相似度取最高值
        SearchByDict = {None: 'ratio', 1: 'title', 2: 'content'}
        result = pd.DataFrame(columns=['diary_id', 'ratio', 'title', 'content'])
        for i in range(len(self.IdDir)):
            if self.IdDir.iloc[i]['author_id'] == -1:
                continue
            ratio1 = fuzz.partial_ratio(self.IdDir.iloc[i]['title'], key)
            addr = self.IdDir.iloc[i]['dir']
            with gzip.open(addr, "rb") as f:
                data = f.read()
            ratio2 = fuzz.partial_ratio(decompress_string(data), key)
            ratio = max(ratio1, ratio2)
            if ratio > 0:  # 如果相似度不为0则将其加入结果
                new_data = {'diary_id': i, 'ratio': ratio, 'title': ratio1, 'content': ratio2}
                result = result._append(new_data, ignore_index=True)
        if result.empty:
            return False, "查找不到结果"
        else:
            result.sort_values(by=[SearchByDict[SearchBy]], ascending=False, inplace=True)
            return True, result

    def UserDiary(self, userId):  # 按照用户id来搜索，返回值为一个列表，列表中是这个用户的所有日记id
        result = []
        for i in range(len(self.IdDir)):
            if self.IdDir.iloc[i]['author_id'] == userId:
                result.append(i)
        if len(result) == 0:
            return False, "查找不到结果"
        return True, result

    def SelfDiary(self):  # 查找当前用户自己的所有日记
        return self.UserDiary(self.UserInfo.GetCurrentUser())

    def DeleteDiary(self, diaryId):  # 删除日记，将当前id改为-1，并删除文件，将此日记id加入可分配id列表
        try:
            diaryId = int(diaryId)
            addr = self.IdDir.iloc[diaryId]['dir']
            os.remove(addr)
            self.IdDir.loc[diaryId, 'author_id'] = -1
            self.IdDir.loc[diaryId, 'title'] = None
            self.IdDir.loc[diaryId, 'location'] = None
            self.IdDir.loc[diaryId, 'dir'] = None
            self.IdDir.loc[diaryId, 'img_list'] = []
            self.IdDir.loc[diaryId, 'heat'] = 0
            self.SaveIdDir()
            self.unusedId.put(diaryId)
            return True, "删除成功"
        except FileNotFoundError:
            return False, "日记文件不存在。"
        except Exception as e:
            return False, f"删除文件时发生错误：{e}"

    def AuthorName(self, diaryId):
        return self.UserInfo.GetUserName(self.IdDir.iloc[diaryId]['author_id'])

    def DiaryName(self, diaryId):  # 按照diaryid来获取日记标题
        return self.IdDir.iloc[int(diaryId)]['title']

    def ShowDiary(self, diaryId):  # 按照diaryid来获取日记内容
        try:
            diaryId = int(diaryId)
            if diaryId >= len(self.IdDir) or self.IdDir.iloc[diaryId]['author_id'] == -1:
                return False, "日记不存在。"
            addr = self.IdDir.iloc[diaryId]['dir']
            with gzip.open(addr, "rb") as f:
                data = f.read()
            return True, decompress_string(data)
        except FileNotFoundError:
            return False, "日记文件不存在。"
        except Exception as e:
            return False, f"读取文件时发生错误：{e}"

    def GetImageList(self, diaryId):
        return self.IdDir.iloc[diaryId]['img_list']

    def LikedDiary(self, diaryId):
        UserId = self.UserInfo.GetCurrentUser()
        if UserId == -1:
            return False
        return int(diaryId) in self.RecDiary.loc[self.UserInfo.GetCurrentUser(), 'liked_diary']
