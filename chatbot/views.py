# import time
# from django.http import JsonResponse
# from django.shortcuts import render
# from django.db.models import Q
# from .models import QA
# import openai
# from django.conf import settings

# openai.api_key = settings.OPENAI_API_KEY


# def chatbot_page(request):
#     return render(request, 'chatbot/index.html')


# def chatbot_reply(request):
#     query = request.GET.get('query', '').strip()
#     if not query:
#         return JsonResponse({"reply": "", "suggestions": []})

#     # ---------- 1️⃣ Suggestions while typing ----------
#     if request.GET.get('suggest') == 'true':
#         suggestions = list(
#             QA.objects.filter(question__icontains=query)
#             .values_list('question', flat=True)[:5]
#         )
#         return JsonResponse({"suggestions": suggestions})

#     # ---------- 2️⃣ Check in database (case-insensitive) ----------
#     match = QA.objects.filter(question__iexact=query).first()
#     if match:
#         # simulate human-like delay before showing saved answer
#         time.sleep(2)
#         return JsonResponse({"reply": match.answer, "suggestions": []})

#     # ---------- 3️⃣ Fallback: Ask OpenAI only if not in DB ----------
#     try:
#         response = openai.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": """
# You are a MinuteHire assistant chatbot. 
# Answer only questions related to the MinuteHire website and company.
# Provide clear, concise answers about:
# - who you are (e.g., “I am the official chatbot of MinuteHire”)
# - services offered by MinuteHire
# - profile updates
# - account creation / login / password reset
# - job posting / application
# - freelancer management / payments
# If the question is unrelated, reply exactly with:
# ❌ Sorry, I only answer MinuteHire-related questions.
# """}, 
#                 {"role": "user", "content": query}
#             ],
#             max_tokens=300
#         )

#         ai_answer = response.choices[0].message.content.strip()

#         # ---------- Save new Q&A only if not already present ----------
#         if not QA.objects.filter(question__iexact=query).exists():
#             QA.objects.create(question=query, answer=ai_answer)

#         return JsonResponse({"reply": ai_answer, "suggestions": []})

#     except Exception as e:
#         print("ChatGPT error:", e)
#         return JsonResponse({
#             "reply": "⚠️ Sorry, I couldn't process your request right now.",
#             "suggestions": []
#         })
import time
from django.http import JsonResponse
from django.shortcuts import render
import openai
from django.conf import settings
from pymongo import MongoClient

openai.api_key = settings.OPENAI_API_KEY

# ---------- MongoDB connection ----------
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]           # MongoDB database name
qa_collection = db["qa_collection"]    # MongoDB collection name

def chatbot_page(request):
    return render(request, 'chatbot/index.html')


def chatbot_reply(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return JsonResponse({"reply": "", "suggestions": []})

    # ---------- 1️⃣ Suggestions while typing ----------
    if request.GET.get('suggest') == 'true':
        suggestions = list(
            qa_collection.find(
                {"question": {"$regex": query, "$options": "i"}},
                {"question": 1, "_id": 0}
            ).limit(5)
        )
        suggestions = [s['question'] for s in suggestions]
        return JsonResponse({"suggestions": suggestions})

    # ---------- 2️⃣ Check in database (case-insensitive) ----------
    match = qa_collection.find_one({"question": {"$regex": f"^{query}$", "$options": "i"}})
    if match:
        time.sleep(2)  # simulate human typing
        return JsonResponse({"reply": match['answer'], "suggestions": []})

    # ---------- 3️⃣ Fallback: Ask OpenAI ----------
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """
You are a MinuteHire assistant chatbot. 
Answer only questions related to the MinuteHire website and company.
Provide clear, concise answers about:
- who you are
- services offered by MinuteHire
- profile updates
- account creation / login / password reset
- job posting / application
- freelancer management / payments
If the question is unrelated, reply exactly with:
❌ Sorry, I only answer MinuteHire-related questions.
"""}, 
                {"role": "user", "content": query}
            ],
            max_tokens=300
        )

        ai_answer = response.choices[0].message.content.strip()

        # Save new Q&A in MongoDB if not already present
        if not qa_collection.find_one({"question": {"$regex": f"^{query}$", "$options": "i"}}):
            qa_collection.insert_one({"question": query, "answer": ai_answer})

        return JsonResponse({"reply": ai_answer, "suggestions": []})

    except Exception as e:
        print("ChatGPT error:", e)
        return JsonResponse({
            "reply": "⚠️ Sorry, I couldn't process your request right now.",
            "suggestions": []
        })
