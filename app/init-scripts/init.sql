DROP TABLE IF EXISTS "TestCase" CASCADE;
DROP TABLE IF EXISTS "Solution" CASCADE;
DROP TABLE IF EXISTS "Task" CASCADE;
DROP TABLE IF EXISTS "Faculty" CASCADE;
DROP TABLE IF EXISTS "Group" CASCADE;
DROP TABLE IF EXISTS "User" CASCADE;
DROP TABLE IF EXISTS "Subject" CASCADE;
DROP TABLE IF EXISTS "TeacherHasGroups" CASCADE;
DROP TABLE IF EXISTS "Group_Subject" CASCADE;

CREATE TABLE "Faculty"
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE "Group"
(
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(32) UNIQUE NOT NULL,
    faculty INTEGER REFERENCES "Faculty" (id)
);

CREATE TABLE "User"
(
    id             SERIAL PRIMARY KEY,
    username       VARCHAR(64) UNIQUE NOT NULL,
    password       VARCHAR(255)       NOT NULL,
    "roleType"     VARCHAR(10)        NOT NULL DEFAULT 'student',
    "studyGroup"   INTEGER REFERENCES "Group" (id) ON DELETE CASCADE,
    form_education VARCHAR(255)       NOT NULL DEFAULT 'Не указано',
    first_name     VARCHAR(64)        NOT NULL DEFAULT 'Не указано',
    last_name      VARCHAR(64)        NOT NULL DEFAULT 'Не указано',
    middle_name    VARCHAR(64)                 DEFAULT 'Не указано'
);

CREATE TABLE "TeacherHasGroups"
(
    id         SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES "User" (id),
    group_id   INTEGER REFERENCES "Group" (id)
);

CREATE TABLE "Subject"
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL
);

CREATE TABLE "Group_Subject"
(
    group_id   integer NOT NULL
        REFERENCES "Group" (id) ON DELETE CASCADE,
    subject_id integer NOT NULL
        REFERENCES "Subject" (id) ON DELETE CASCADE,
    PRIMARY KEY (group_id, subject_id)
);

CREATE TABLE "Task"
(
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    description     VARCHAR(2048),
    teacher_formula VARCHAR,
    input_variables VARCHAR,
    status          VARCHAR CHECK ( status IN ('published', 'unpublished') ),
    "Subject_id"    INTEGER      NOT NULL REFERENCES "Subject" (id) ON DELETE CASCADE
);

CREATE TABLE "Solution"
(
    id                  SERIAL PRIMARY KEY,
    code                TEXT    NOT NULL,
    mark                INTEGER,
    "lengthTestResult"  BOOLEAN,
    "formulaTestResult" BOOLEAN,
    "autoTestResult"    INTEGER,
    status              VARCHAR,
    "User_id"           INTEGER NOT NULL REFERENCES "User" (id) ON DELETE CASCADE,
    "Task_id"           INTEGER REFERENCES "Task" (id) ON DELETE CASCADE
);

CREATE TABLE "TestCase"
(
    id        SERIAL PRIMARY KEY,
    inp       VARCHAR(512) NOT NULL,
    out       VARCHAR(512) NOT NULL,
    "Task_id" INTEGER REFERENCES "Task" (id) ON DELETE CASCADE
);

INSERT INTO "Faculty" (name)
VALUES ('Информационные системы и технологии'),
       ('Вычислительная техника и программное обеспечение');

INSERT INTO "Group" (name, faculty)
VALUES ('211-365', 1),
       ('211-366', 1),
       ('211-367', 2),
       ('211-368', 2),
       ('-', 1);

-- Добавление пользователей
INSERT INTO "User" (username, password, "roleType", "studyGroup", form_education, first_name, last_name,
                    middle_name)
VALUES ('teacher', 'teacher', 'teacher', 5, '', 'Иван',
        'Калмыков', 'Денисович'),
       ('student', 'student', 'student', 1, 'Платная',
        'Василий', 'Шубенок', 'Валерьевич');

INSERT INTO "TeacherHasGroups" (teacher_id, group_id)
VALUES (1, 1),
       (1, 2);

-- Добавление дисциплин
INSERT INTO "Subject" (name)
VALUES ('Python'),
       ('С++'),
       ('Java'),
       ('C#');

-- Привязка групп к дисциплинам
INSERT INTO "Group_Subject" (group_id, subject_id)
VALUES (1, 1),
       (1, 2),
       (1, 3),
       (1, 4),
       (2, 1),
       (2, 2),
       (2, 3),
       (2, 4),
       (3, 1),
       (3, 2),
       (3, 3),
       (3, 4),
       (4, 1),
       (4, 2),
       (4, 3),
       (4, 4);

-- Добавление заданий
INSERT INTO "Task" (name, "Subject_id", description, teacher_formula, input_variables, status)
VALUES ('Задание 1. Python - числовые типы', 1,
        'Задача на числовые типы\nПример входных данных: 1 2 3\nПример выходных данных: 0 2',
        'b1=a1+a2-a3\nb2=b1+a2', 'a1\na2\na3', 'published'),
       ('Задание 1. С++ - числовые типы', 2, 'Задача на числовые типы', 'c - d', 'a3, a4', 'published'),
       ('Задание 2. Python - строки', 1, 'Задача на строки', 'a + b', 'a1, a2', 'published'),
       ('Задание 2. С++ - строки', 2, 'Задача на строки', 'c - d', 'a3, a4', 'published'),
       ('Задание 3. Python - списки', 1, 'Задача на списки', 'a + b', 'a1, a2', 'unpublished'),
       ('Задание 3. С++ - списки', 2, 'Задача на списки', 'c - d', 'a3, a4', 'published'),
       ('Задание 1. Java - числовые типы', 3, 'Задача на числовые типы', 'a + b', 'a1, a2', 'published'),
       ('Задание 2. Java - строки', 3, 'Задача на строки', 'a + b', 'a1, a2', 'unpublished'),
       ('Задание 3. Java - списки', 3, 'Задача на списки', 'a + b', 'a1, a2', 'unpublished'),
       ('Задание 4. Java - массивы', 3, 'Задача на массивы', 'a + b', 'a1, a2', 'unpublished'),
       ('Задание 5. Java - классы', 3, 'Задача на классы', 'a + b', 'a1, a2', 'published'),
       ('Задание 1. C# - числовые типы', 4, 'Задача на числовые типы', 'a + b', 'a1, a2', 'published'),
       ('Задание 2. C# - строки', 4, 'Задача на строки', 'a + b', 'a1, a2', 'unpublished'),
       ('Задание 3. C# - списки', 4, 'Задача на списки', 'a + b', 'a1, a2', 'published'),
       ('Задание 4. C# - массивы', 4, 'Задача на массивы', 'a + b', 'a1, a2', 'unpublished'),
       ('Задание 5. C# - классы', 4, 'Задача на классы', 'a + b', 'a1, a2', 'published');

-- Добавление тестовых случаев
INSERT INTO "TestCase" (inp, out, "Task_id")
VALUES ('1 2 3', '0 2', 1),
       ('4 5 6', '3 8', 1),
       ('7 8 9', '6 14', 1),
       ('10 11 12', '9 20', 1),
       ('13 14 15', '12 26', 1),
       ('16 17 18', '15 32', 1),
       ('19 20 21', '18 38', 1),
       ('22 23 24', '21 44', 1),
       ('25 26 27', '24 50', 1),
       ('28 29 30', '27 56', 1),
       ('31 32 33', '30 62', 1),
       ('34 35 36', '33 68', 1),
       ('37 38 39', '36 74', 1),
       ('40 41 42', '39 80', 1),
       ('43 44 45', '42 86', 1),
       ('46 47 48', '45 92', 1),
       ('49 50 51', '48 98', 1),
       ('52 53 54', '51 104', 1),
       ('55 56 57', '54 110', 1),
       ('58 59 60', '57 116', 1);

-- Добавление решений
INSERT INTO "Solution" (code, "User_id", "Task_id")
VALUES ('print(''Hello, World!'')', 1, 1),
       ('print(''Hello, World!'')', 1, 3);