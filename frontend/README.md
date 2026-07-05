# OcuCare React Frontend

This folder contains the React/Vite frontend for the Flask backend.

## Development

Run Flask on port `5051` first:

```powershell
python app.py
```

Then run the React dev server:

```powershell
cd frontend
npm.cmd run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/get` and `/health` to Flask.

## Production Build

```powershell
cd frontend
npm.cmd run build
```

After the build, Flask serves the React app automatically from `frontend/dist`:

- `http://127.0.0.1:5051/`
- `http://127.0.0.1:5051/bot`

If `frontend/dist/index.html` is missing, Flask falls back to the older Jinja templates.
