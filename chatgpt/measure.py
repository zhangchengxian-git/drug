import pandas as pd
def loadData(componentPath):
    df = pd.read_excel(io=componentPath, dtype=str)
    return df[['冲突药物', '家族存在相互作用但是个别不存在相互作用的特殊药物', '冲突', '不冲突']]

def get_matrix(df):
    TP, FN, FP = 0, 0, 0
    for index, row in df.iterrows():
        true_label, pred_label = set(), set()
        if isinstance(row['冲突药物'], str):
            true_label = set(row['冲突药物'].split('；'))
        if isinstance(row['冲突'], str):
            pred_label = set(row['冲突'].split('；'))
        TP += len(true_label&pred_label)
        FN += len(true_label-pred_label)
        FP += len(pred_label-true_label)
        true_label, pred_label = set(), set()
        if isinstance(row['家族存在相互作用但是个别不存在相互作用的特殊药物'], str):
            true_label = set(row['家族存在相互作用但是个别不存在相互作用的特殊药物'].split('；'))
        if isinstance(row['不冲突'], str):
            pred_label = set(row['不冲突'].split('；'))
        TP += len(true_label&pred_label)
        FN += len(true_label-pred_label)
        FP += len(pred_label-true_label)
    return TP, FN, FP

def cal(TP, FN, FP):
    pre = TP/(TP+FP)
    recall = TP/(TP+FN)
    f1 = 2*pre*recall/(pre+recall)
    return pre, recall, f1

if __name__ == "__main__":
    df = loadData('冲突测试.xlsx')
    TP, FN, FP = get_matrix(df)
    print(TP, FN, FP)
    pre, recall, f1 = cal(TP, FN, FP)
    print(pre, recall, f1)
