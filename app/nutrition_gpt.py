import json
import logging
from openai import AsyncOpenAI
from app.config import settings
from app.models import NutritionResponse, Meal, Ingredient

logger = logging.getLogger(__name__)


class NutritionGPT:
    """
    🧠 Mini ChatGPT specialized for nutrition
    Understands: Arabic, Franco-Arabic, English, and any mix!
    """
    
    SYSTEM_PROMPT = """أنت مساعد تغذية ذكي متخصص في حساب السعرات الحرارية.
You are a smart nutrition assistant specialized in calorie calculation.

🌍 YOU UNDERSTAND ALL LANGUAGES:
- Arabic script: "اكلت شاورما بلا بطاطا"
- Franco-Arabic: "akalt sha2rma bala btata", "3melt salata"
- English: "I ate shawarma without fries"
- Mixed: "اكلت falafel with extra tahini"

🎯 YOUR JOB:
1. Understand EXACTLY what the user ate (any language, any style)
2. Identify ALL meals mentioned
3. Understand modifications (بلا/without, extra/زيادة, نص/half, etc.)
4. Calculate accurate calories for each meal
5. Respond in the SAME language the user used

📊 ALWAYS RESPOND WITH THIS JSON FORMAT:
{
    "meals": [
        {
            "name": "Meal name",
            "ingredients": [
                {"name": "ingredient1", "weight_g": 100, "calories": 150},
                {"name": "ingredient2", "weight_g": 50, "calories": 80}
            ],
            "total_calories": 230,
            "total_weight_g": 150,
            "modifications": ["without fries", "extra garlic"],
            "notes": "Optional notes"
        }
    ],
    "total_daily_calories": 230,
    "message": "Your friendly response in user's language",
    "language": "arabic/franco/english"
}

🔧 MODIFICATION UNDERSTANDING:
- "بلا", "بدون", "without", "no", "bala", "bidun" = REMOVE ingredient
- "extra", "زيادة", "double", "zyede", "ktir" = ADD more (1.5x-2x calories)
- "نص", "half", "nos", "شوي" = HALF portion (0.5x calories)
- "ع خبز عربي", "on arabic bread" = SUBSTITUTE bread type
- "مشوي", "grilled", "mashwi" = Lower calories than fried

🍽️ COMMON ARABIC DISHES (use accurate calories):
- شاورما/Shawarma: ~500-600 kcal (with bread and sauces)
- فلافل/Falafel sandwich: ~350-400 kcal
- منقوشة زعتر/Zaatar manouche: ~280-320 kcal
- حمص/Hummus (100g): ~170 kcal
- تبولة/Tabbouleh (100g): ~90 kcal
- كبسة/Kabsa: ~600-700 kcal
- كشري/Kushari: ~500-550 kcal

BE FRIENDLY AND HELPFUL! 😊
"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        logger.info(f"✅ NutritionGPT initialized with model: {self.model}")

    async def chat(self, user_message: str) -> dict:
        try:
            logger.info(f"📩 User message: {user_message}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            logger.info(f"🤖 GPT response: {content}")
            
            result = json.loads(content)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return {
                "meals": [],
                "total_daily_calories": 0,
                "message": "عذراً، حصل خطأ. حاول مرة تانية!",
                "language": "mixed"
            }
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                "meals": [],
                "total_daily_calories": 0,
                "message": f"Error: {str(e)}",
                "language": "english"
            }

    async def get_nutrition(self, user_message: str) -> NutritionResponse:
        result = await self.chat(user_message)
        
        meals = []
        for meal_data in result.get("meals", []):
            ingredients = [
                Ingredient(
                    name=ing.get("name", "Unknown"),
                    weight_g=ing.get("weight_g", 0),
                    calories=ing.get("calories", 0)
                )
                for ing in meal_data.get("ingredients", [])
            ]
            
            meal = Meal(
                name=meal_data.get("name", "Unknown"),
                ingredients=ingredients,
                total_calories=meal_data.get("total_calories", 0),
                total_weight_g=meal_data.get("total_weight_g", 0),
                modifications=meal_data.get("modifications", []),
                notes=meal_data.get("notes")
            )
            meals.append(meal)
        
        return NutritionResponse(
            meals=meals,
            total_daily_calories=result.get("total_daily_calories", 0),
            message=result.get("message", ""),
            language=result.get("language", "auto")
        )


nutrition_gpt = None

async def get_nutrition_gpt() -> NutritionGPT:
    global nutrition_gpt
    if nutrition_gpt is None:
        nutrition_gpt = NutritionGPT()
    return nutrition_gpt
