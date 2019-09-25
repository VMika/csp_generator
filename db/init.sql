PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

DROP TABLE generator;
DROP TABLE csp;
DROP TABLE flag;
DROP TABLE flag_info;
DROP TABLE crawled_url;
DROP TABLE generator_progress;

CREATE TABLE flag_info (
    id TEXT NOT NULL,
    description TEXT NOT NULL,
    explanation TEXT NOT NULL,
    reco TEXT NOT NULL,

    PRIMARY KEY (id)
);

CREATE TABLE flag (
    csp_id INTEGER NOT NULL,
    flag_info_id TEXT NOT NULL,
    content TEXT,
    location INTEGER,

    FOREIGN KEY (flag_info_id) REFERENCES flag_info(id)
);

CREATE TABLE csp (
    gen_id INTEGER NOT NULL,
    flags_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    header TEXT NOT NULL,

    PRIMARY KEY (gen_id, flags_id),
    FOREIGN KEY (gen_id) REFERENCES generator(id)
);

CREATE TABLE generator (
    id INTEGER NOT NULL,
    start_url TEXT NOT NULL,
    allowed_domain TEXT NOT NULL,
    status INTEGER NOT NULL,

    PRIMARY KEY (id)
);

CREATE TABLE crawled_url (
    generator_id INTEGER NOT NULL,
    url TEXT NOT NULL,

    FOREIGN KEY (generator_id) REFERENCES generator(id)
);

CREATE TABLE generator_progress (
    generator_id INTEGER NOT NULL,
    total_url_number INTEGER NOT NULL,
    processed_url_number INTEGER NOT NULL,

    FOREIGN KEY (generator_id) REFERENCES generator(id)
);

COMMIT;

