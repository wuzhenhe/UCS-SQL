zero_shot_v2_prompt = """
Given a 【Database schema】 description, an 【Evidence】 of knowledge, and the 【Question】, you need to use valid SQLite, understand the database and knowledge, extract 'content information' and 'structure information' based on the【Question】,【Evidence】, 【Database schema】, and 【Foreign keys】. Subsequently, generate the skeleton of SQL based on 'structure information'. Finally, fill the SQL skeleton based on 'structure information' and then generate SQL.
You can write final SQL in script blocks, and indicate script type in it, like this:
```sql
SELECT column_a
FROM table_b
```
When generating SQL, we should always consider constraints:
【Constraints】
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

### Useful information

#### Database schema 
{desc_str}

#### Foreign keys
{fk_str}

#### Question
{query}

#### Evidence
{evidence}

To generate SQL query, we extract 'content information' and 'structure information' based on the 【Question】,【Evidence】,【Database schema】and 【Foreign keys】.
"""

shot_example = """
### Useful information

#### Database schema 
{desc_str}

#### Foreign keys
{fk_str}

#### Question
{query}

#### Evidence
{evidence}

{sc}
"""

dynamic_shot_prompt_full = """
Given a 【Database schema】 description, an 【Evidence】 of knowledge, and the 【Question】, you need to use valid SQLite, understand the database and knowledge, extract 'content information' and 'structure information' based on the【Question】,【Evidence】, 【Database schema】, and 【Foreign keys】. Subsequently, generate the skeleton of SQL based on 'structure information'. Finally, fill the SQL skeleton based on 'structure information' and then generate SQL.
When generating SQL, we should always consider constraints:
【Constraints】
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

==========

{shot_examples}

==========

### Useful information

#### Database schema 
{desc_str}

#### Foreign keys
{fk_str}

#### Question
{query}

#### Evidence
{evidence}

{sc}

"""


fix_2shot_prompt_full = """
Given a 【Database schema】 description, an 【Evidence】 of knowledge, and the 【Question】, you need to use valid SQLite, understand the database and knowledge, extract 'content information' and 'structure information' based on the【Question】,【Evidence】, 【Database schema】, and 【Foreign keys】. Subsequently, generate the skeleton of SQL based on 'structure information'. Finally, fill the SQL skeleton based on 'content information' and then generate SQL.
When generating SQL, we should always consider constraints:
【Constraints】
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

==========

【Database schema】
# Table: frpm
[
  (CDSCode, CDSCode. Value examples: ['01100170109835', '01100170112607'].),
  (Charter School (Y/N), Charter School (Y/N). Value examples: [1, 0, None]. And 0: N;. 1: Y),
  (Enrollment (Ages 5-17), Enrollment (Ages 5-17). Value examples: [5271.0, 4734.0].),
  (Free Meal Count (Ages 5-17), Free Meal Count (Ages 5-17). Value examples: [3864.0, 2637.0]. And eligible free rate = Free Meal Count / Enrollment)
]
# Table: satscores
[
  (cds, California Department Schools. Value examples: ['10101080000000', '10101080109991'].),
  (sname, school name. Value examples: ['None', 'Middle College High', 'John F. Kennedy High', 'Independence High', 'Foothill High'].),
  (NumTstTakr, Number of Test Takers in this school. Value examples: [24305, 4942, 1, 0, 280]. And number of test takers in each school),
  (AvgScrMath, average scores in Math. Value examples: [699, 698, 289, None, 492]. And average scores in Math),
  (NumGE1500, Number of Test Takers Whose Total SAT Scores Are Greater or Equal to 1500. Value examples: [5837, 2125, 0, None, 191]. And Number of Test Takers Whose Total SAT Scores Are Greater or Equal to 1500. . commonsense evidence:. . Excellence Rate = NumGE1500 / NumTstTakr)
]
【Foreign keys】
frpm.`CDSCode` = satscores.`cds`
【Question】
List school names of charter schools with an SAT excellence rate over the average.
【Evidence】
Charter schools refers to `Charter School (Y/N)` = 1 in the table frpm; Excellence rate = NumGE1500 / NumTstTakr

To generate SQL query, we extract 'content information' and 'structure information' based on the 【Question】,【Evidence】,【Database schema】and 【Foreign keys】.

### Content Information

#### Step 1: Base on 【Question】, the following attribute values may be table or column names:
- [school names]
- [charter schools]
- [SAT excellence rate]

#### Step 2: Combined with 【Evidence】：
- [Charter schools] refers to [Charter School (Y/N)] = 1 in the table [frpm];
- [Excellence rate] = [NumGE1500 / NumTstTakr]

#### Step 3: The following attribute values may be table or column names:
- [school names]
- [Charter School (Y/N)]
- [frpm]
- [NumGE1500]
- [NumTstTakr]

#### Step 4: Further combined with 【Database schema】, the following attribute values may be table or column names:
- [Charter School (Y/N)]
- [NumGE1500]
- [NumTstTakr]
- [sname]
- [frpm]

#### Step 5: Further combined with 【Foreign keys】, the final 'content information' maybe:
- [Charter School (Y/N)]
- [NumGE1500]
- [NumTstTakr]
- [sname]
- [frpm]
- [CDSCode]
- [satscores]
- [cds]

### Structure Information

#### Step 1: The following words imply part of SQL structure:
- [over the average]

#### Step 2: SQL may involve functions, the final 'structure information' maybe: 
- [AVG]
- [>]

### Summary

#### Content Information:
- Tables: [satscores], [frpm]
- Columns: [cds], [CDSCode], [sname], [NumTstTakr], [NumGE1500], [Charter School (Y/N)]


#### Structure Information:
- Functions: [AVG], [>]

### SQL query

#### Step 1, considering 【Constraints】 and then generating the skeleton of SQL based on 'structure information':
```sql skeleton
SELECT T2.[column_name]
  FROM [table_name] AS T1
  INNER JOIN [table_name] AS T2
  ON T1.[column_name] = T2.[column_name]
  WHERE T2.[column_name] IS NOT NULL
  AND T1.[column_name] = 1
  AND CAST(T2.[column_name] AS REAL) / T2.[column_name] > (
    SELECT AVG(CAST(T4.[column_name] AS REAL) / T4.[column_name])
    FROM [table_name] AS T3
    INNER JOIN [table_name] AS T4
    ON T3.[column_name] = T4.[column_name]
    WHERE T3.[column_name] = 1
  )
```

#### Step 2, fill the SQL skeleton, replace [table_name] and [column_name] with exactly column and table names based on 'content information'. Understand the question and evidence, then generate the SQL step by step:
```sql
SELECT T2.`sname`
  FROM frpm AS T1
  INNER JOIN satscores AS T2
  ON T1.`CDSCode` = T2.`cds`
  WHERE T2.`sname` IS NOT NULL
  AND T1.`Charter School (Y/N)` = 1
  AND CAST(T2.`NumGE1500` AS REAL) / T2.`NumTstTakr` > (
    SELECT AVG(CAST(T4.`NumGE1500` AS REAL) / T4.`NumTstTakr`)
    FROM frpm AS T3
    INNER JOIN satscores AS T4
    ON T3.`CDSCode` = T4.`cds`
    WHERE T3.`Charter School (Y/N)` = 1
  )
```

Question Solved.

==========

【Database schema】
# Table: account
[
  (account_id, the id of the account. Value examples: [11382, 11362, 2, 1, 2367].),
  (district_id, location of branch. Value examples: [77, 76, 2, 1, 39].),
  (frequency, frequency of the acount. Value examples: ['POPLATEK MESICNE', 'POPLATEK TYDNE', 'POPLATEK PO OBRATU'].),
  (date, the creation date of the account. Value examples: ['1997-12-29', '1997-12-28'].)
]
# Table: client
[
  (client_id, the unique number. Value examples: [13998, 13971, 2, 1, 2839].),
  (gender, gender. Value examples: ['M', 'F']. And F：female . M：male ),
  (birth_date, birth date. Value examples: ['1987-09-27', '1986-08-13'].),
  (district_id, location of branch. Value examples: [77, 76, 2, 1, 39].)
]
# Table: district
[
  (district_id, location of branch. Value examples: [77, 76, 2, 1, 39].),
  (A4, number of inhabitants . Value examples: ['95907', '95616', '94812'].),
  (A11, average salary. Value examples: [12541, 11277, 8114].)
]
【Foreign keys】
account.`district_id` = district.`district_id`
client.`district_id` = district.`district_id`
【Question】
What is the gender of the youngest client who opened account in the lowest average salary branch?
【Evidence】
Later birthdate refers to younger age; A11 refers to average salary

To generate SQL query, we extract 'content information' and 'structure information' based on the 【Question】,【Evidence】,【Database schema】and 【Foreign keys】.

### Content Information

#### Step 1: Base on 【Question】, the following attribute values may be table or column names:
- [gender]
- [client]
- [average salary]

#### Step 2: Combined with 【Evidence】：
- [Later birthdate] refers to [younger age]
- [A11] refers to [average salary]

#### Step 3: The following attribute values may be table or column names:
- [gender]
- [client]
- [Later birthdate]
- [A11]

#### Step 4: Further combined with 【Database schema】, the following attribute values may be table or column names:
- [gender]
- [birth_date]
- [A11]
- [cilent]

#### Step 5: Further combined with 【Foreign keys】, the final 'content information' maybe:
- [gender]
- [birth_date]
- [A11]
- [cilent]
- [district]
- [district_id]

### Structure Information

#### Step 1: The following words imply part of SQL structure:
- [the youngest]
- [the lowest]
- [average]

#### Step 2: SQL may involve functions, the final 'structure information' maybe: 
- [ORDER BY]
- [ASC]
- [DECS]

### Summary

#### Content Information:
- Tables: [account], [cilent], [district]
- Columns: [gender], [birth_date], [A11], [district_id]

#### Structure Information:
- Functions: [ORDER BY], [ASC], [DECS]

### SQL query

#### Step 1, considering 【Constraints】 and then generating the skeleton of SQL based on 'structure information':
```sql skeleton
SELECT T1.[column_name]
  FROM [table_name] AS T1
  INNER JOIN [table_name] AS T2
  ON T1.[column_name] = T2.[column_name]
  ORDER BY T2.[column_name] ASC, T1.[column_name] DESC 
  LIMIT 1 
```

#### Step 2, fill the SQL skeleton, replace [table_name] and [column_name] with exactly column and table names based on 'content information'. Understand the question and evidence, then generate the SQL step by step:
```sql
SELECT T1.`gender`
  FROM client AS T1
  INNER JOIN district AS T2
  ON T1.`district_id` = T2.`district_id`
  ORDER BY T2.`A11` ASC, T1.`birth_date` DESC 
  LIMIT 1 
```
Question Solved.

==========

### Useful information

#### Database schema 
{desc_str}

#### Foreign keys
{fk_str}

#### Question
{query}

#### Evidence
{evidence}

"""