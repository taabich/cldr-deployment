DO $$
DECLARE
    r RECORD;
BEGIN
    -- Rename all tables (exclude views) to uppercase
    FOR r IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
          AND tablename <> lower(tablename)
          AND lower(tablename) NOT IN (
              SELECT lower(table_name) FROM information_schema.views WHERE table_schema = 'public'
          )
    LOOP
        EXECUTE format(
            'ALTER TABLE public.%I RENAME TO "%s"',
            r.tablename,
            lower(r.tablename)
        );
    END LOOP;

    -- Rename all columns to uppercase, for real tables only (exclude views)
    FOR r IN
        SELECT c.table_name, c.column_name
        FROM information_schema.columns c
        WHERE c.table_schema = 'public'
          AND lower(c.table_name) NOT IN (
              SELECT lower(table_name) FROM information_schema.views WHERE table_schema = 'public'
          )
    LOOP
        EXECUTE format(
            'ALTER TABLE public."%s" RENAME COLUMN %I TO "%s"',
            lower(r.table_name),
            r.column_name,
            lower(r.column_name)
        );
    END LOOP;
END $$;