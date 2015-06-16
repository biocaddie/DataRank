-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2015-06-16 02:15:38.712



-- tables
-- Table: author
CREATE TABLE author (
    id integer NOT NULL  PRIMARY KEY,
    name text NOT NULL,
    family text NOT NULL
);

-- Table: citaion_network
CREATE TABLE citaion_network (
    id integer NOT NULL  PRIMARY KEY,
    cites_pmid integer NOT NULL,
    cited_pmid integer NOT NULL,
    FOREIGN KEY (cites_pmid) REFERENCES paper (pmid),
    FOREIGN KEY (cited_pmid) REFERENCES paper (pmid)
);

-- Table: collaboration
CREATE TABLE collaboration (
    id integer NOT NULL  PRIMARY KEY,
    author1 integer NOT NULL,
    author2 integer NOT NULL,
    times integer NOT NULL,
    FOREIGN KEY (author1) REFERENCES author (id),
    FOREIGN KEY (author2) REFERENCES author (id)
);

-- Table: concept
CREATE TABLE concept (
    id text NOT NULL  PRIMARY KEY,
    name text NOT NULL
);

-- Table: concept_term
CREATE TABLE concept_term (
    id integer NOT NULL  PRIMARY KEY,
    term_id text NOT NULL,
    concept_id text NOT NULL,
    FOREIGN KEY (term_id) REFERENCES term (id),
    FOREIGN KEY (concept_id) REFERENCES concept (id)
);

-- Table: dataset
CREATE TABLE dataset (
    id integer NOT NULL  PRIMARY KEY,
    accession text NOT NULL,
    repository_id integer NOT NULL,
    FOREIGN KEY (repository_id) REFERENCES repository (id)
);

-- Table: journal
CREATE TABLE journal (
    id integer NOT NULL  PRIMARY KEY,
    nlm_jid text NOT NULL,
    issn integer NOT NULL,
    name text NOT NULL,
    journal_type_id integer NOT NULL,
    journal_country_id integer NOT NULL,
    language_id integer NOT NULL,
    FOREIGN KEY (journal_type_id) REFERENCES journal_type (id),
    FOREIGN KEY (journal_country_id) REFERENCES journal_country (id),
    FOREIGN KEY (language_id) REFERENCES language (id)
);

-- Table: journal_country
CREATE TABLE journal_country (
    id integer NOT NULL  PRIMARY KEY,
    name text NOT NULL
);

-- Table: journal_type
CREATE TABLE journal_type (
    id integer NOT NULL  PRIMARY KEY,
    name text NOT NULL
);

-- Table: language
CREATE TABLE language (
    id integer NOT NULL  PRIMARY KEY,
    name text NOT NULL
);

-- Table: mehs_concept
CREATE TABLE mehs_concept (
    id integer NOT NULL  PRIMARY KEY,
    concept_id text NOT NULL,
    mesh_id text NOT NULL,
    FOREIGN KEY (concept_id) REFERENCES concept (id),
    FOREIGN KEY (mesh_id) REFERENCES mesh (id)
);

-- Table: mesh
CREATE TABLE mesh (
    id text NOT NULL  PRIMARY KEY,
    name text NOT NULL
);

-- Table: owner
CREATE TABLE owner (
    id integer NOT NULL  PRIMARY KEY,
    name text NOT NULL
);

-- Table: paper
CREATE TABLE paper (
    pmid integer NOT NULL  PRIMARY KEY,
    abstract text,
    title text,
    date date,
    journal_id integer NOT NULL,
    owner_id integer NOT NULL,
    status_id integer NOT NULL,
    FOREIGN KEY (journal_id) REFERENCES journal (id),
    FOREIGN KEY (owner_id) REFERENCES owner (id),
    FOREIGN KEY (status_id) REFERENCES status (id)
);

-- Table: paper_author
CREATE TABLE paper_author (
    id integer NOT NULL  PRIMARY KEY,
    author_id integer NOT NULL,
    paper_pmid integer NOT NULL,
    FOREIGN KEY (author_id) REFERENCES author (id),
    FOREIGN KEY (paper_pmid) REFERENCES paper (pmid)
);

-- Table: paper_dataset
CREATE TABLE paper_dataset (
    id integer NOT NULL  PRIMARY KEY,
    paper_pmid integer NOT NULL,
    dataset_id integer NOT NULL,
    FOREIGN KEY (paper_pmid) REFERENCES paper (pmid),
    FOREIGN KEY (dataset_id) REFERENCES dataset (id)
);

-- Table: paper_mesh
CREATE TABLE paper_mesh (
    id integer NOT NULL  PRIMARY KEY,
    paper_pmid integer NOT NULL,
    mesh_id integer NOT NULL,
    FOREIGN KEY (paper_pmid) REFERENCES paper (pmid),
    FOREIGN KEY (mesh_id) REFERENCES mesh (id)
);

-- Table: repository
CREATE TABLE repository (
    id integer NOT NULL  PRIMARY KEY,
    name text NOT NULL
);

-- Table: status
CREATE TABLE status (
    id integer NOT NULL  PRIMARY KEY,
    name text NOT NULL
);

-- Table: term
CREATE TABLE term (
    id text NOT NULL  PRIMARY KEY,
    name text NOT NULL
);





-- End of file.

