from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

from .api.profile import router as profile_router
from .api.accounts import router as accounts_router
from .api.categories import router as categories_router
from .api.income_sources import router as income_sources_router
from .api.transactions import router as transactions_router
from .api.credit_cards import router as credit_cards_router
from .api.loans import router as loans_router
from .api.budgets import router as budgets_router
from .api.recurring_expenses import router as recurring_router
from .api.savings_goals import router as savings_goals_router
from .api.gold import router as gold_router
from .api.reports import router as reports_router
from .api.imports import router as imports_router

app = FastAPI(title="Personal Finance API", version="1.0.0")

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router, prefix="/api/v1")
app.include_router(accounts_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(income_sources_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(credit_cards_router, prefix="/api/v1")
app.include_router(loans_router, prefix="/api/v1")
app.include_router(budgets_router, prefix="/api/v1")
app.include_router(recurring_router, prefix="/api/v1")
app.include_router(savings_goals_router, prefix="/api/v1")
app.include_router(gold_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(imports_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"status": "ok", "service": "personal-finance-api"}


@app.get("/health")
def health():
    return {"status": "ok"}
