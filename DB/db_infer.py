from sentence_transformers import SentenceTransformer, util
import pickle
import networkx as nx
import pandas as pd
from openpyxl import Workbook

def loadDB():
    return pickle.load(open('drug_db_add_api_1117.pickle', 'rb'))

def getSimilarNode(drug_name, model):
    drug_vector = model.encode(drug_name)
    db = loadDB()
    maxSimilar = 0.0
    similarNode = db
    for node in db.nodes():
        if node == drug_name:
            return node, '规则'
        elif node in drug_name:
            name = drug_name.replace(node, '')
            if '酸' in name or '盐' in name or '钠' in name or '酰' in name or '酮' in name or '醚' in name \
                or '葡萄糖' in name or '乳糖' in name or '次' == name[0] or '的浸膏' in name or '的流浸膏' in \
                name or '的提取物' in name or '艾司' in name or name.encode('utf-8').isalpha() or ('维生素' not in node and name.isdigit()):
                return node, '规则'
        elif drug_name in node:
            name = node.replace(drug_name, '')
            if '酸' in name or '盐' in name or '钠' in name or '酰' in name or '酮' in name \
                or '醚' in name or '葡萄糖' in name or '乳糖' in name or '次' == name[0] or \
                '的浸膏' in name or '的流浸膏' in name or '的提取物' in name or '艾司' in name or\
                name.encode('utf-8').isalpha() or '维生素' not in node and name.isdigit():
                    return node, '规则'
    
        sim = util.cos_sim(db.nodes[node]['vector'], drug_vector)
        if sim > maxSimilar:
            maxSimilar = sim
            similarNode = node
    return similarNode, '相似度'    

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
    confict = read_xlsx_confict('../chatgpt/冲突测试.xlsx')
    db = loadDB()
    model = SentenceTransformer('../../../model/biobert-v1.1')
    
    workbook = Workbook()
    save_file = "异名表1212_规则_冲突对齐.xlsx"
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
            simiNode, regular = getSimilarNode(r, model)
            childNode = getAllChild(db, simiNode)
            worksheet.append([r, simiNode, '；'.join(childNode), regular])
    workbook.save(filename=save_file)
    




