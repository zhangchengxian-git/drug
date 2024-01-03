import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pickle, csv
plt.rcParams['font.sans-serif'] = ['STFangsong']
from sentence_transformers import SentenceTransformer
import string
from db_infer import loadDB
from deep_translator import MyMemoryTranslator

def get_vector(model, sentence):
    vector = model.encode(sentence)
    '''
    with open('vector.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([sentence, vector])
    '''
    return vector

def read_csv(file_path):
    df = pd.read_csv(file_path, sep=',')
    return df

def add_atc_db(model, atc, db):
    for index, row in atc.iterrows():
        if not row['atc_name'] in db:
            vector = get_vector(model, row['atc_name'])
            db.add_node(row['atc_name'], vector=vector)
        if row['parent_atc_code'] == '0':
            continue
        father = atc[atc['atc_code'] == row['parent_atc_code']]
        if father.shape[0] > 0:
            father = father.iloc[0,2]
        else:
            continue
        if not father in db:
            father_vector = get_vector(model, father)
            db.add_node(father, vector=father_vector)
        if father != row['atc_name']:
            db.add_edge(father, row['atc_name'])
    return db

def add_atc_db_eng(model, atc, db):
    for index, row in atc.iterrows():
        eng_name = row['en_name']
        if pd.isnull(row['en_name']):
            eng_name = row['atc_name']
        if not eng_name in db:
            vector = get_vector(model, eng_name)
            db.add_node(eng_name, vector=vector)
        if row['parent_atc_code'] == '0':
            continue
        father = atc[atc['atc_code'] == row['parent_atc_code']]
        if len(father) == 0:
            continue
        father_eng = father.iloc[0,5]
        if pd.isnull(father_eng):
            father_eng = father.iloc[0, 2]
        print(father_eng)
        if not father_eng in db:
            father_vector = get_vector(model, father_eng)
            db.add_node(father_eng, vector=father_vector)
        if father_eng != eng_name:
            db.add_edge(father_eng, eng_name)
    return db

def add_family_db_eng(model, family, db):
    for index, row in family.iterrows():
        eng_name = row['drug_en_name']
        if not eng_name in db:
            vector = get_vector(model, eng_name)
            db.add_node(eng_name, vector=vector)
        if row['parent_id'] == '0':
            continue
        father = family[family['id'] == row['parent_id']]
        if father.shape[0] > 0:
            father_eng = father.iloc[0, 3]
            print(father_eng)
        else:
            continue
        if not father_eng in db:
            father_vector = get_vector(model, father_eng)
            db.add_node(father_eng, vector=father_vector)
        if father_eng != eng_name:
            db.add_edge(father_eng, eng_name)
    return db

def add_family_db(model, family, db):
    for index, row in family.iterrows():
        if not row['drug_name'] in db:
            vector = get_vector(model, row['drug_name'])
            db.add_node(row['drug_name'], vector=vector)
        if row['parent_id'] == 0:
            continue
        father = row['tmp_drug']
        if not father in db:
            father_vector = get_vector(model, father)
            db.add_node(father, vector=father_vector)
        if father != row['drug_name']:
            db.add_edge(father, row['drug_name'])
    return db

def db_save(db):
    pickle.dump(db, open('drug_db_eng_1228.pickle', 'wb'))

def read_xlsx_api(file_path):
    df = pd.read_excel(io=file_path, dtype=str, keep_default_na=False)
    return df[["drug_name", "一级目录", "二级目录", "三级目录", "四级目录", "基础库别名"]]  

def add_api(model, api, db):
    for idx,data in api.iterrows():
        res = []
        for i in range(6):
            if data[i] == '' or data[i] == '\\':
                res.append([])
            elif i != 5:
                res.append([data[i]])
            else:
                res.append(data[i].rstrip(',').split(','))
        data = res
        '''
        for node in db.nodes():
            if db.nodes[node] in data:
                print('add ' + node)
                for d in data:
                    if d != db.nodes[node]:
                        neighbor = list(db.neighbors(node))
                        db.add_node(d, vector=get_vector(model, d))
                        for nei in neighbor:
                            db.add_edge(d, nei)
        ''' 
        rem = ''
        for i in range(len(data)):
            if len(data[i]) != 0:
                if len(data[i]) == 1:
                    if data[i][0] not in db.nodes():
                        db.add_node(data[i][0], vector=get_vector(model, data[i][0]))
                    if i == 0:
                        rem = data[0][0]
                    else:
                        db.add_edge(data[i][0], rem)
                        rem = data[i][0]
                else:
                    for j in range(len(data[i])):
                        if data[i][j] not in db.nodes():
                            db.add_node(data[i][j], vector=get_vector(model, data[i][j]))
                        db.add_edge(data[i][j], rem)
                    rem = ''

    return db
    
                        
def main():
    
    atc = read_csv('../../../data/drug/data_base/gene_drug_atc.csv')
    family = read_csv('../../../data/drug/data_base/gene_drug_family.csv')
    db = nx.DiGraph()
    model = SentenceTransformer('../../../model/biobert-v1.1')
    #api = read_xlsx_api('../../../data/drug/data_base/待提取异名API20231117-1.xlsx')
    #db = add_atc_db(model, atc, db)
    #db = add_family_db(model, family, db)
    #db = add_api(model, api, db)
    # nx.draw(db,node_size = 30, with_labels=True)
    # plt.savefig("graph.png")
    # plt.show()
    db = add_atc_db_eng(model, atc, db)
    db = add_family_db_eng(model, family, db)
    db_save(db)
    


if __name__ == "__main__":
    main()

    

