from Decoder import Decoder
from Corrector import Corrector
from Selector import Selector
import logging
import sys
import os
import json
import codecs
from datetime import datetime
from V2_prompt import *
from llm_request import *
current_time = datetime.now()
current_time_str = current_time.strftime("%Y%m%d-%H%M")
logging.basicConfig(filename=f"./log/{current_time_str}_main.log", level=logging.INFO)
logger = logging.getLogger()
import random
from utils import *

def check_tables_presence(fk_desc, schema_desc):
    if len(fk_desc)  <= 3:
        return False
    table_a, table_b = fk_desc.split('=')
    table_a, table_b = table_a.split('.')[0], table_b.split('.')[0]
    return ("Table: " + table_a).lower() in schema_desc.lower() and ("Table: " + table_b).lower() in schema_desc.lower()

def main(continue_question_id, end_question_id, db_root_path, read_path, output_root_path, tables_path, train_path = None, id2shot_path = None, mode='base', MAX_NUMS=3, shot_nums = 2):

    # selector = Selector(db_root_path, tables_path,'','spider')
    decoder = Decoder()
    corrector = Corrector(db_root_path)

    with open(train_path, 'r', encoding='utf8') as f:
        train_data = json.load(f)
    
    with open(id2shot_path, 'r', encoding='utf8') as f:
        id2shot = json.load(f)


    prompt_save_path = os.path.join(output_root_path, "input-" + continue_question_id +".txt")
    sql_save_path = os.path.join(output_root_path, "sql-" + continue_question_id +".txt")
    corre_prompt_save_path = os.path.join(output_root_path, "corre_input-" + continue_question_id +".txt")
    corre_sql_save_path = os.path.join(output_root_path, "corre_sql-" + continue_question_id +".txt")


    selected_data = json.load(open(read_path, 'r', encoding='utf-8'))
    n_data = len(selected_data)
    assert 0 <= int(continue_question_id) < n_data
    logger.info(f"continue to output, begin question_id ={continue_question_id}, all question nums is: {n_data}")

    with codecs.open(prompt_save_path, 'a+', encoding='utf8') as fout_prompt, \
        codecs.open(sql_save_path, 'a+', encoding='utf8') as fout_sql, \
        codecs.open(corre_prompt_save_path, 'a+', encoding='utf8') as fout_corre_prompt, \
        codecs.open(corre_sql_save_path, 'a+', encoding='utf8') as fout_corrt:
        for i in range(n_data):
            print('processing gpt4 {}/{} ({:.2f}%%)\r'.format(i, n_data, 100 * i / n_data), end='')
            data = selected_data[i]
            real_question_id = data.get("question_id", i)

            assert real_question_id == i, (real_question_id == i)
            if int(end_question_id) > real_question_id >= int(continue_question_id):

                logger.info(f"Begin question_id ={continue_question_id}, current question_id ={real_question_id}")
                db_id = data['db_id']
                query = data['question']
                evidence = data['evidence']


                # schema_list = list(data['pre_knowledge_schema'].values())
                # schema = "\n\n".join(schema_list)
                # fk = data['full_knowledge_fk']
                

                schema = data['llm_schema']
                fk = data['llm_fk']

                origin_schema_list =  list(data['full_origin_schema'].values())
                origin_schema = "\n\n".join(origin_schema_list)


                # target_sc = data["llm_SC"]
                # target_sc = ""
                # target_example = shot_example.format(query=query, evidence=evidence, desc_str=schema, fk_str=fk, sc = target_sc)


                prompt, prompt_token, response_token = fix_2shot_prompt_full.format(query=query, evidence=evidence, desc_str=schema, fk_str=fk)
                reply = request_llm(prompt)

                cleaned_sql = select_final_sql(reply, "```")
                cleaned_sql = clean_result(cleaned_sql)
                
                info = f"*******question_id {str(real_question_id)}: {query}\n{prompt}{reply}\n*******\n\n"
                fout_prompt.write(info)
                fout_prompt.flush()
                info = f"{str(real_question_id)} question_id:{cleaned_sql}\n"
                fout_sql.write(info)
                fout_sql.flush()


                exec_result = corrector.execute_model(db_id, cleaned_sql, topn=5)

                step1_corre = 0
                while step1_corre < MAX_NUMS:
                    data = exec_result.get('data', None)
                    if data is not None and len(data) == 0:

                        prompt = fix_2shot_prompt_full.format(query=query, evidence=evidence, desc_str=schema, fk_str=fk)
                        reply = request_llm(prompt)

                        cleaned_sql = select_final_sql(reply, "```")
                        cleaned_sql = clean_result(cleaned_sql)

                        exec_result = corrector.execute_model(db_id, cleaned_sql, topn=5)
                        step1_corre += 1
                    else:
                        break
                    

                data = exec_result.get('data', None)
                if data is not None and len(data) != 0 and step1_corre != 0:
                    corre_prompt, corre_reply, corr_sql =  prompt, '【correct SQL】【Round】' + str(step1_corre) + reply, cleaned_sql
                else:
                    corre_prompt, corre_reply, corr_sql = corrector.correction(db_id, cleaned_sql, query, evidence, schema, origin_schema, fk, MAX_NUMS=MAX_NUMS)

                
                info = f"*******question_id {str(real_question_id)}: {query}\n{corre_prompt}{corre_reply}\n*******\n\n"
                fout_corre_prompt.write(info)
                fout_corre_prompt.flush()
                info = f"{str(real_question_id)} question_id:{corr_sql}\n"
                fout_corrt.write(info)
                fout_corrt.flush()
            else:
                #Skip processed data
                logger.info(f"Skip processed data, question_id ={real_question_id}")
if __name__ == '__main__':

    continue_question_id = sys.argv[1]
    end_question_id = sys.argv[2]

    db_root_path = r'./dev_databases'
    read_path = r"./data/dev.json"
    output_root_path = r"./output"
    train_path = r'train_process.json'
    id2shot_path = r'./data/LLm-5shot_idx.json'


    MAX_NUMS = 3
    shot_nums = 3
    mode = 'base'
    
    if not os.path.exists(output_root_path):
        try:
            os.makedirs(output_root_path)
            print(f"Success: {output_root_path}")
        except OSError as e:
            print(f"Fail: {output_root_path}") 
    main(continue_question_id, end_question_id, db_root_path, read_path, output_root_path, '',train_path, id2shot_path, mode, MAX_NUMS, shot_nums)




    