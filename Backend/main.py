from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gtts import gTTS
from fastapi.responses import FileResponse
import os

# ----------------- App -----------------
app = FastAPI()

# Allow requests from your frontend (Live Server on port 5500)
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500"
]

# ----------------- CORS Middleware -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Serve frontend -----------------
app.mount("/", StaticFiles(directory="../Frontend", html=True), name="Frontend")

# Custom route for clean URL
@app.get("/forgot-password")
async def forgot_password():
    return FileResponse(os.path.join("Frontend", "forgotpassword.html"))

# ----------------- Data Models -----------------
class UserData(BaseModel):
    income: float
    expenses: float
    savings: float
    debt: float
    age: int
    dependents: int
    risk_profile: str  # 'low', 'medium', 'high'
    context: str       # e.g., 'spending', 'savings', etc.

# ----------------- Notebook Logic as Functions -----------------
def get_financial_advice_backend(income, expenses, savings, debt, risk_profile, age):
    disposable_income = income - expenses - debt
    advice = []

    if savings < 3 * expenses:
        advice.append("Build an emergency fund of at least three months of expenses.")
    if debt > 0:
        advice.append(f"Focus on reducing your debt of {debt}. Prioritize high-interest debts first.")
    if risk_profile == 'low':
        advice.append("Invest in low-risk assets like government bonds or fixed deposits.")
    elif risk_profile == 'medium':
        advice.append("Maintain a balanced portfolio with stocks, ETFs, bonds, and mutual funds.")
    else:
        advice.append("Consider aggressive investments such as stocks, ETFs, or real estate for higher returns.")
    if age < 30:
        advice.append("Start retirement savings early with long-term growth funds or retirement accounts.")
    elif age < 50:
        advice.append("Focus on building wealth and balancing retirement contributions with investments.")
    else:
        advice.append("Prioritize safe investments and ensure you are on track for retirement.")
    if disposable_income > 0:
        advice.append(f"Save or invest approximately {int(disposable_income * 0.3)} per month for your goals.")
    else:
        advice.append("Expenses and debt exceed income. Review your budget carefully.")
    advice.append("For short-term goals under three years, use safe, liquid options like savings accounts.")
    advice.append("For long-term goals over five years, diversify into stocks, ETFs, or index funds for growth.")
    return advice

def get_trust_advice_backend(age, savings, dependents):
    trust_advice = []
    if dependents > 0:
        trust_advice.append("Consider setting up a family trust to protect assets for your dependents.")
        trust_advice.append("Make sure you have a valid will to ensure smooth transfer of wealth.")
    if savings > 50000:
        trust_advice.append("Explore estate planning strategies to reduce tax burdens on inheritance.")
    if age > 40:
        trust_advice.append("Review life insurance and health insurance policies to safeguard your family.")
    return trust_advice

# ----------------- FastAPI Advice Functions -----------------
def get_financial_advice(user: UserData):
    return get_financial_advice_backend(
        user.income, user.expenses, user.savings, user.debt, user.risk_profile, user.age
    )

def get_trust_advice(user: UserData):
    return get_trust_advice_backend(
        user.age, user.savings, user.dependents
    )

# ----------------- Endpoints -----------------
@app.post("/get-advice")
def get_advice(user: UserData):
    financial_advice = get_financial_advice(user)
    trust_advice = get_trust_advice(user)
    return {"financial_advice": financial_advice, "trust_advice": trust_advice}

@app.post("/get-advice-audio")
def get_advice_audio(user: UserData):
    financial_advice = get_financial_advice(user)
    trust_advice = get_trust_advice(user)
    advice_text = "\n".join(financial_advice + trust_advice)

    filename = "voice.mp3"
    tts = gTTS(text=advice_text, lang='en')
    tts.save(filename)
    response = FileResponse(filename, media_type="audio/mpeg", filename=filename)
    # Optional: remove after sending
    # os.remove(filename)
    return response

# Request model
class FinanceInput(BaseModel):
    income: float
    expenses: float

@app.post("/recommend")
async def recommend(finance: FinanceInput):
    income = finance.income
    expenses = finance.expenses

    savings = max(0, income - expenses)
    savings_percent = round((savings / income) * 100, 2) if income > 0 else 0

    advice = []
    # Example advice logic
    if expenses > income:
        advice.append("Your expenses exceed your income! Consider reducing costs.")
    else:
        if savings_percent < 5:
            advice.append("Try to save at least 5% of your income.")
        if expenses / income > 0.7:
            advice.append("Expenses are over 70% of income. Consider budgeting.")
        if expenses / income < 0.5:
            advice.append("Good job! You are spending less than half your income.")

    return {
        "savings": round(savings, 2),
        "savings_percent": savings_percent,
        "expenses": round(expenses, 2),
        "advice": advice
    }
