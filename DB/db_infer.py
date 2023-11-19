from sentence_transformers import SentenceTransformer, util
import pickle
import networkx as nx
import pandas as pd
from openpyxl import Workbook

def loadDB():
    return pickle.load(open('drug_db.pickle', 'rb'))

def getSimilarNode(drug_name, model):
    drug_vector = model.encode(drug_name)
    db = loadDB()
    maxSimilar = 0.0
    similarNode = db
    for node in db.nodes():
        if node == drug_name:
            return node
        else:
            sim = util.cos_sim(db.nodes[node]['vector'], drug_vector)
            if sim > maxSimilar:
                maxSimilar = sim
                similarNode = node
    return similarNode        

def getAllChild(db, node):
    if not node:
        return []
    children_set = set(node)
    children_list = [node]
    for i in range(len(children_list)):
        neighbor = list(db.neighbors(children_list[i]))
        for nei in neighbor:
            if nei not in children_set:
                children_set.add(nei)
                children_list.append(nei)
    return children_list

def read_xlsx_confict(file_name):
    df = pd.read_excel(io=file_name, dtype=str)
    return df[['冲突', '不冲突']]

if __name__ == '__main__':
    confict = read_xlsx_confict('../../drug/chatgpt/冲突测试.xlsx')
    db = loadDB()
    model = SentenceTransformer('../../model/biobert')
    workbook = Workbook()
    save_file = "无异名表_冲突对齐.xlsx"
    worksheet = workbook.active
        #每个workbook创建后，默认会存在一个worksheet，对默认的worksheet进行重命名
    worksheet.title = "Sheet1"
    for idx,data in confict.iterrows():
        res = []
        if not pd.isnull(data[0]):
            res = res + data[0].split('；')
        if not pd.isnull(data[1]):
            res = res  + data[1].split('；')
        for r in res:
            simiNode = getSimilarNode(r, model)
            childNode = getAllChild(db, simiNode)
            worksheet.append([r, simiNode, '；'.join(childNode)])
    workbook.save(filename=save_file)





