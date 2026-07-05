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
