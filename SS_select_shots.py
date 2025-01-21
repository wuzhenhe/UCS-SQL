import json
import random
dev_path = r'D:\ChinaTele\Paper\SQL\CODE\LZQ-SQL\data\stage2_bird\dev_LLM_Tabels_Cols_clean-EV_AddKnowledge_FK_0722_shot_SKshot_QSK_SC.json'
train_path = r'D:\ChinaTele\Paper\SQL\CODE\LZQ-SQL\data\stage2_bird\train_bird_llm_SC_0721.json'
# save_path = r'D:\ChinaTele\Paper\SQL\CODE\LZQ-SQL\data\stage2_bird\SC_shots_from_bird_train.json'
save_path = r'D:\ChinaTele\Paper\SQL\CODE\LZQ-SQL\data\stage2_bird\规则5.json'

dev_train_shots = {}
with open(dev_path, 'r', encoding='utf-8') as f:
    dev_data = json.load(f)

with open(train_path, 'r', encoding='utf-8') as f:
    train_data = json.load(f)
MIN_ = 1000000000
MAX_ = 0
min10 = []
for item in dev_data:
    idx = item["question_id"]
    entity_funcs = set(item['entity_funcs']) 
    complexity_schema = item['complexity_schema']
    shot_list = []
    # 1. 函数完全一致（数量且种类一样），且实体数量在加减1的区间内的sample。
    for candidate in train_data:
        if candidate["pre_knowledge_schema"] == {}:
            print("跳过空schema")
            continue
        candidate_idx = candidate["question_id"]
        candidata_funs = set(candidate['entity_funcs'])
        candidate_complexity = candidate["complexity_schema"]
        if entity_funcs == candidata_funs and (-1 <= candidate_complexity - complexity_schema <= 1):
            shot_list.append(candidate_idx)
    # 2. 若1筛选出来的超过20条，则随便保留20条即可。
    if len(shot_list) > 20:
        shot_list = random.sample(shot_list, 20)

    # 3. 若1筛选出来的不足10条，则在上述的基础上增加：函数完全包含（train的包含test的）（若过多则随意保留10条即可）。
    train_cover_dev = []
    if len(shot_list) < 10:
        for candidate in train_data:
            if candidate["pre_knowledge_schema"] == {}:
                print("跳过空schema")
            candidate_idx = candidate["question_id"]
            candidata_funs = set(candidate['entity_funcs'])
            candidate_complexity = candidate["complexity_schema"]
            # if (candidate_idx not in shot_list) and (candidata_funs >= entity_funcs) and (candidate_complexity >= complexity_schema):
            if (candidate_idx not in shot_list) and (candidata_funs >= entity_funcs):
                train_cover_dev.append(candidate_idx)
        if len(train_cover_dev) >= (10 - len(shot_list)):
            train_cover_dev = random.sample(train_cover_dev, 10 - len(shot_list))

    shot_list = shot_list + train_cover_dev
    
    # 4. 如果3选出来还是不够10条，则函数取交集数的范围在2-5的区间内的数据, 或者字段复杂度误差在正负1范围内
    i = 5
    end_i = 4
    train_intersection_dev = []
    while i >= end_i and len(shot_list) + len(train_intersection_dev) < 10:
        for candidate in train_data:
            if candidate["pre_knowledge_schema"] == {}:
                print("跳过空schema")
            candidate_idx = candidate["question_id"]
            candidata_funs = set(candidate['entity_funcs'])
            candidate_complexity = candidate["complexity_schema"]
            intersection_set = candidata_funs & entity_funcs 
            if ((candidate_idx not in shot_list) and len(intersection_set) >= i):
                train_intersection_dev.append(candidate_idx)
        i -= 1
    if len(train_intersection_dev) >= (10 - len(shot_list)) and (10 - len(shot_list)) > 0:
        train_intersection_dev = random.sample(train_intersection_dev, 10 - len(shot_list))
    shot_list = shot_list + train_intersection_dev

    # 5. 如果4选出来还是不够10条，则字段复杂度误差在正负1范围内
    train_complexity_dev = []
    if len(shot_list) < 10:
        for candidate in train_data:
            if candidate["pre_knowledge_schema"] == {}:
                print("跳过空schema")
            candidate_idx = candidate["question_id"]
            candidata_funs = set(candidate['entity_funcs'])
            candidate_complexity = candidate["complexity_schema"]
            if (candidate_idx not in shot_list) and (-1 <= candidate_complexity - complexity_schema <= 1):
                train_complexity_dev.append(candidate_idx)
    if len(train_complexity_dev) >= (10 - len(train_complexity_dev)) and (10 - len(shot_list)) > 0:
        train_complexity_dev = random.sample(train_complexity_dev, 10 - len(shot_list))
    shot_list = shot_list + train_complexity_dev

    dev_train_shots[idx] = shot_list
    if len(shot_list) < 3:
        min10.append(idx)
    MIN_ = min(MIN_, len(shot_list))
    MAX_ = max(MAX_, len(shot_list))
        

print(MIN_)
print(MAX_)
print(set(min10))
print(len(min10))

# 将结果保存到文件中
with open(save_path, 'w', encoding='utf-8') as fout:
    json.dump(dev_train_shots, fout, indent=2, ensure_ascii=False)





# fun_entity_dict = {}

# count = 0
# for item in train_data:
#     idx = item["question_id"]
#     entity_funcs = sorted(item['entity_funcs']) # 将 entity_funcs 转换为元组并排序
#     entity_funcs = " ".join(entity_funcs)
#     complexity_schema = item['complexity_schema']

#     # 获取 entity_funcs 对应的字典
#     entity_dict = fun_entity_dict.get(entity_funcs, {})
    
#     # 获取 complexity_schema 对应的列表
#     shot_list = entity_dict.get(complexity_schema, [])
    
#     # 添加 idx 到列表中
#     shot_list.append(idx)
    
#     # 更新 entity_dict 中的列表
#     entity_dict[complexity_schema] = shot_list
#     count += 1
    
#     # 更新 fun_entity_dict 中的字典
#     fun_entity_dict[entity_funcs] = entity_dict







