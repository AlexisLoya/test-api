from fastapi import FastAPI
from routers import orders, nyt

app = FastAPI(title="Cometa Test API", version="1.0")

# Registrar los routers
app.include_router(orders.router, prefix="/beers", tags=["Beers Orders"])
app.include_router(nyt.router, prefix="/nyt", tags=["NYT Integration"])

@app.get("/")
def root():
    return {"message": "Welcome to Cometa Test API"}
