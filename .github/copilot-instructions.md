# RailOpt AI project instructions

- This is a single-developer modular monolith for a 24-hour SIH prototype.
- Keep the existing root React/Vite app as the frontend until a deliberate migration is planned.
- Keep backend business logic in services, not FastAPI routes.
- Never claim the prototype authorizes railway blocks, signaling, traction isolation, or train movement.
- Label generated operational data as synthetic.
- Keep optimizer and risk logic deterministic and testable.
- Validate changes with the narrowest relevant test, then run `npm run build` and `npm run lint` for frontend changes.
