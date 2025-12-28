from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from app.graphql.schema import schema
from app.api.background_api import router as background_api_router
from app.api.chat_api import router as chat_api_router
from app.api.user_api import router as user_api_router

app = FastAPI()

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
app.include_router(background_api_router, prefix="/api")
app.include_router(chat_api_router, prefix="/api")
app.include_router(user_api_router, prefix="/api")