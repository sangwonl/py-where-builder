### Usage

##### Basic
```
from wherebuilder.qb import Q

where = Q('a.first_name = :first and a.age >= :age', first='eddy', age=34)
print where.clause()
>> a.first_name = 'eddy' and a.age >= 34
```

##### AND or OR
```
from wherebuilder.qb import Q, AND, OR

where = OR(
    Q('a.first_name = :first and a.last_name = :last', first='eddy', last='lee'),
    AND(Q('a.age >= 34'), Q('a.allowed_push = :allowed_push', allowed_push=1)))
print where.clause()
>> (a.first_name = 'eddy' and a.last_name = 'lee') or ((a.age >= 34) and (a.allowed_push = 1)) 
```

##### IF or SWITCH
```
from wherebuilder.qb import Q, AND, OR, SWITCH, IF

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

##### More Complex
```
from wherebuilder.qb import Q, AND, OR, SWITCH, IF

where = OR(
    Q('a.first_name = :first and a.last_name = :last', first='eddy', last='lee'),
    AND(Q('a.age >= 34'), Q('a.allowed_push = :allowed_push', allowed_push=1)),
    IF(True, Q('a.age > 30')),
    IF(True, SWITCH('inner_case1',
        ('inner_case1', Q('a.age >= 10')),
        ('inner_case2', Q('a.age >= 15')))
    ),
    SWITCH('case2',
        ('case1', AND(Q('a.age >= 34'), Q('a.age < :age', age=50))),
        ('case2', AND(Q('a.age >= 50'), Q('a.age < :age', age=60)))
    )
)
print where.clause()
>> (a.first_name = 'eddy' and a.last_name = 'lee') or ((a.age >= 34) and (a.allowed_push = 1)) or (a.age > 30) or (a.age >= 10) or ((a.age >= 50) and (a.age < 60))
```
