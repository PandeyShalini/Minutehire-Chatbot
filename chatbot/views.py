import time
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from .models import QA
import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY


def chatbot_page(request):
    return render(request, 'chatbot/index.html')


def chatbot_reply(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return JsonResponse({"reply": "", "suggestions": []})

    # ---------- 1️⃣ Suggestions while typing ----------
    if request.GET.get('suggest') == 'true':
        suggestions = list(
            QA.objects.filter(question__icontains=query)
            .values_list('question', flat=True)[:5]
        )
        return JsonResponse({"suggestions": suggestions})

    # ---------- 2️⃣ Check in database (case-insensitive) ----------
    match = QA.objects.filter(question__iexact=query).first()
    if match:
        # simulate human-like delay before showing saved answer
        time.sleep(2)
        return JsonResponse({"reply": match.answer, "suggestions": []})

    # ---------- 3️⃣ Fallback: Ask OpenAI only if not in DB ----------
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """
You are a MinuteHire assistant chatbot. 
Answer only questions related to the MinuteHire website and company.
Provide clear, concise answers about:
- who you are (e.g., “I am the official chatbot of MinuteHire”)
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

        # ---------- Save new Q&A only if not already present ----------
        if not QA.objects.filter(question__iexact=query).exists():
            QA.objects.create(question=query, answer=ai_answer)

        return JsonResponse({"reply": ai_answer, "suggestions": []})

    except Exception as e:
        print("ChatGPT error:", e)
        return JsonResponse({
            "reply": "⚠️ Sorry, I couldn't process your request right now.",
            "suggestions": []
        })
