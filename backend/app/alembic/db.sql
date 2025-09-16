
CREATE TABLE IF NOT EXISTS public."user"
(
    email character varying(255) COLLATE pg_catalog."default" NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    full_name character varying(255) COLLATE pg_catalog."default",
    hashed_password character varying COLLATE pg_catalog."default" NOT NULL,
    id uuid NOT NULL,
    CONSTRAINT user_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."user"
    OWNER to postgres;
-- Index: ix_user_email

-- DROP INDEX IF EXISTS public.ix_user_email;

CREATE UNIQUE INDEX IF NOT EXISTS ix_user_email
    ON public."user" USING btree
    (email COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;



-- Table: public.knowledge_base
-- DROP TABLE IF EXISTS public.knowledge_base;
CREATE TABLE IF NOT EXISTS public.knowledge_base
(
    description text COLLATE pg_catalog."default",
    created_by uuid NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_by uuid NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    name character varying(255) COLLATE pg_catalog."default",
    status smallint,
    id uuid NOT NULL,
    CONSTRAINT knowledge_base_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.knowledge_base
    OWNER to postgres;

CREATE INDEX IF NOT EXISTS ix_knowledge_base_name
    ON public.knowledge_base USING btree
    (name COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;



-- Table: public.knowledge_base_file
CREATE TABLE IF NOT EXISTS public."knowledge_base_file"
(
    created_by uuid NOT NULL,
    created_at timestamp DEFAULT current_timestamp,
    updated_by uuid NOT NULL,
    updated_at timestamp DEFAULT current_timestamp,
    name character varying(255) COLLATE pg_catalog."default",
    file_hash character varying(255) COLLATE pg_catalog."default",
    extension character varying(20) COLLATE pg_catalog."default",
    size int,
    status smallint,
    storage character varying(255) COLLATE pg_catalog."default",
    knowledge_base_id uuid NOT NULL,
    id uuid NOT NULL,
    CONSTRAINT knowledge_base_file_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."knowledge_base_file"
    OWNER to postgres;

CREATE INDEX IF NOT EXISTS ix_knowledge_base_file_name
    ON public."knowledge_base_file" USING btree
    (name COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
CREATE UNIQUE INDEX IF NOT EXISTS ix_knowledge_base_file_file_hash
    ON public.knowledge_base_file USING btree
    (file_hash COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.knowledge_base_permission
CREATE TABLE IF NOT EXISTS public."knowledge_base_permission"
(
    created_by uuid NOT NULL,
    created_at timestamp DEFAULT current_timestamp,
    updated_by uuid NOT NULL,
    updated_at timestamp DEFAULT current_timestamp,
    type smallint,
    status smallint,
    user_id uuid NOT NULL,
    knowledge_base_id uuid NOT NULL,
    id uuid NOT NULL,
    CONSTRAINT knowledge_base_permission_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."knowledge_base_permission"
    OWNER to postgres;

CREATE INDEX IF NOT EXISTS ix_knowledge_base_permission_user
    ON public."knowledge_base_permission" USING btree
    (user_id ASC)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS ix_knowledge_base_permission_kb
    ON public."knowledge_base_permission" USING btree
    (knowledge_base_id ASC)
    TABLESPACE pg_default;



CREATE TABLE IF NOT EXISTS public."knowledge_base_file_permission"
(
    created_by uuid NOT NULL,
    created_at timestamp DEFAULT current_timestamp,
    updated_by uuid NOT NULL,
    updated_at timestamp DEFAULT current_timestamp,
    type smallint,
    status smallint,
    user_id uuid NOT NULL,
    knowledge_base_file_id uuid NOT NULL,
    id uuid NOT NULL,
    CONSTRAINT knowledge_base_file_permission_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."knowledge_base_file_permission"
    OWNER to postgres;

CREATE INDEX IF NOT EXISTS ix_knowledge_base_file_permission_user
    ON public."knowledge_base_file_permission" USING btree
    (user_id ASC)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS ix_knowledge_base_file_permission_kbf
    ON public."knowledge_base_file_permission" USING btree
    (knowledge_base_file_id ASC)
    TABLESPACE pg_default;


