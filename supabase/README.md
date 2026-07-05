# Supabase Setup for OcuCare

1. Create a Supabase project.
2. Open the Supabase SQL Editor.
3. Run `supabase/schema.sql`.
4. In Supabase Auth settings, enable email login or magic link login.
5. Copy `frontend/.env.example` to `frontend/.env`.
6. Fill in:

```powershell
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
```

7. Rebuild the frontend:

```powershell
cd frontend
npm.cmd run build
```

Anonymous users can still chat. Logged-in users can save and reload chat sessions.

## Automatic Eye Health Summary

If you already ran the original schema before the summary feature was added, run:

```sql
-- supabase/add_patient_summaries.sql
```

The app automatically updates `patient_summaries` after logged-in chat interactions. Users only click `Eye Health Summary` to view the latest generated summary; they do not need to manually update it.
