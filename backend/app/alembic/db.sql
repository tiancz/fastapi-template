
CREATE TABLE IF NOT EXISTS public."knowledge_base"
(
    description text COLLATE pg_catalog."default",
    created_by uuid NOT NULL,
    created_at timestamp DEFAULT current_timestamp,
    updated_by uuid NOT NULL,
    updated_at timestamp DEFAULT current_timestamp,
    name character varying(255) COLLATE pg_catalog."default",
    id uuid NOT NULL,
    CONSTRAINT knowledge_base_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."knowledge_base"
    OWNER to postgres;

CREATE UNIQUE INDEX IF NOT EXISTS ix_knowledge_base_name
    ON public."knowledge_base" USING btree
    (name COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;


CREATE TABLE IF NOT EXISTS public."knowledge_base_file"
(
    created_by uuid NOT NULL,
    created_at timestamp DEFAULT current_timestamp,
    updated_by uuid NOT NULL,
    updated_at timestamp DEFAULT current_timestamp,
    name character varying(255) COLLATE pg_catalog."default",
    type smallint,
    extension character varying(20) COLLATE pg_catalog."default",
    size int,
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


CREATE TABLE IF NOT EXISTS public."knowledge_base_permission"
(
    created_by uuid NOT NULL,
    created_at timestamp DEFAULT current_timestamp,
    updated_by uuid NOT NULL,
    updated_at timestamp DEFAULT current_timestamp,
    type smallint,
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
    user_id uuid NOT NULL,
    knowledge_base_file_id uuid NOT NULL,
    id uuid NOT NULL,
    CONSTRAINT knowledge_base_file_permission_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."knowledge_base_file_permission"
    OWNER to postgres;

CREATE INDEX IF NOT EXISTS ix_knowledge_base_permission_user
    ON public."knowledge_base_file_permission" USING btree
    (user_id ASC)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS ix_knowledge_base_permission_kbf
    ON public."knowledge_base_file_permission" USING btree
    (knowledge_base_file_id ASC)
    TABLESPACE pg_default;

