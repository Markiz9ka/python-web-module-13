import fastapi
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import contacts.routes as contacts_routes
import auth.routes
import auth.exceptions
from dotenv import load_dotenv
import os
load_dotenv()

app = fastapi.FastAPI()

origins = ["http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(contacts_routes.router, prefix="/api")
app.include_router(auth.routes.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=os.environ.get('HOST'), port=int(os.environ.get('PORT'))
    )