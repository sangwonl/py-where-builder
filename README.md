### Usage

##### Basic
```
from dumbsql.qb import Q

where = Q('a.first_name = :first and a.age >= :age', first='eddy', age=34)
print where.clause()
>> a.first_name = 'eddy' and a.age >= 34
```

##### AND or OR
```
from dumbsql.qb import Q, AND, OR

where = OR(
    Q('a.first_name = :first and a.last_name = :last', first='eddy', last='lee'),
    AND(Q('a.age >= 34'), Q('a.allowed_push = :allowed_push', allowed_push=1)))
print where.clause()
>> (a.first_name = 'eddy' and a.last_name = 'lee') or ((a.age >= 34) and (a.allowed_push = 1)) 
```

##### IF or SWITCH
```
from dumbsql.qb import Q, AND, OR, SWITCH, IF

case = 'case2'
where = SWITCH(case,
    ('case1', AND(Q('a.age >= 34'), Q('a.age < :age', age=50))),
    ('case2', AND(Q('a.age >= 50'), Q('a.age < :age', age=60))))
print where.clause()
>> (a.age >= 50) and (a.age < 60)"

cond = 30
where = IF(cond < 40, Q('a.age > 30'))
print where.clause()
>> a.age > 30

where = IF(cond > 30, Q('a.age > 30'))
print where.clause()
>>
```
