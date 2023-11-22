import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pickle, csv
plt.rcParams['font.sans-serif'] = ['STFangsong']
from sentence_transformers import SentenceTransformer
import string

def get_vector(model, sentence):
    vector = model.encode(sentence)
    with open('vector.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([sentence, vector])
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
    pickle.dump(db, open('drug_db_add_api_1117.pickle', 'wb'))

def read_xlsx_api(file_path):
    df = pd.read_excel(io=file_path, dtype=str)
    return df[['药物名称','API别名']]  

def add_api(model, api, db):
    for idx,data in api.iterrows():
        if pd.isnull(data[1]):
            continue
        data = [data[0]] + data[1].strip(string.punctuation).split(',')
        for node in db.nodes():
            if db.nodes[node] in data:
                print('add ' + node)
                for d in data:
                    if d != db.nodes[node]:
                        neighbor = list(db.neighbors(node))
                        db.add_node(d, vector=get_vector(model, d))
                        for nei in neighbor:
                            db.add_edge(d, nei)
    return db
    
                        
def main():
    atc = read_csv('../../../data/drug/data_base/gene_drug_atc.csv')
    family = read_csv('../../../data/drug/data_base/gene_drug_family.csv')
    db = nx.DiGraph()
    model = SentenceTransformer('../../../model/biobert-v1.1')
    api = read_xlsx_api('../../../data/drug/data_base/待提取异名API20231117-1.xlsx')
    db = add_atc_db(model, atc, db)
    db = add_family_db(model, family, db)
    db = add_api(model, api, db)
    # nx.draw(db,node_size = 30, with_labels=True)
    # plt.savefig("graph.png")
    # plt.show()
    db_save(db)

if __name__ == "__main__":
    main()

    

