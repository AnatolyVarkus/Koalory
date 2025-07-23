"""
AI Prompts Service for Koalory Story Generation
Содержит все промпты для генерации сказок и изображений
"""

from typing import Dict, Any, List
from app.models.stories import StoriesModel


class AIPrompts:
    """
    Centralized AI prompts for story and image generation
    Промпты для Leonardo AI и Claude API
    """

    @staticmethod
    def get_hero_avatar_prompt(story: StoriesModel, photo_description: str = "") -> str:
        """
        Промпт 1: Генерация аватара героя для Leonardo AI

        Args:
            story: Модель истории с данными пользователя
            photo_description: Описание загруженного фото (из GPT-4V анализа)

        Returns:
            str: Полный промпт для Leonardo AI
        """

        prompt = f"""Describe this person from this picture following these steps: 

Step 1: Character Name: {story.story_name} - Character Age: {story.story_age} - Character Gender: {story.story_gender} - Place of Residence: {story.story_location}

Step 2: Additional parameters (will be determined based on the uploaded image) - Hairstyle (examples: Bald, Pixie Cut, Bald, Buzz Cut, Crew Cut, Bob Cut, Lob, Layered Cut, Undercut, French Bob, V-Cut, U-Cut, Feathered Cut, Curly Bob, Beach Waves, Afro, Ringlets, Spiral Curls, Classic Bun, Top Knot, Chignon, Braided Bun, Messy Bun, Classic Braid, French Braid, Dutch Braid, Fishtail Braid, Cornrows, High Ponytail, Low Ponytail, Side Ponytail, Braided Ponytail, Bubble Ponytail, Pompadour, Quiff, Slick Back, Side Part, Mohawk, Dreadlocks, Man Bun, Emo Cut, Mullet, Straight Across Bangs, Side-Swept Bangs, Curtain Bangs, Wispy Bangs, Blunt Bangs, Caesar Cut, French Crop, Ivy League Cut, Buzz Cut Fade, High and Tight, Taper Fade Pixie, Textured Crop, Textured Crop with Fade, Wolf Cut, Hime Cut, Pageboy Cut, Asymmetrical Bob, Stacked Bob, Razor Cut, Wedge Cut, Long Layers with Curtain Bangs, Half-Up Half-Down, Finger Waves, Wet Look, Pineapple Updo, Bantu Knots, Braided Bantu Knots, Box Braids, Box Braids with Color Extensions, Chunky Braids, Statement Braids, Decorated Braids, High Braided Ponytail, Jumbo Braids, Braids with Accessories, Street Braids, Feed-in Braids, Two Statement Braids, Viking Braids (inspired), Senegalese Twists, Marley Twists, Flat Twists, Space Buns, Victory Rolls, Short Layered Pixie, Tapered Pixie): - Skin Tone (Fair, Light, Dark, Deep, Honey, Caramel, Chocolate, Ebony, etc.): - Eye Color (examples: dark brown, green, blue, etc.): - Accessories (examples: Glasses, Headband, etc.): - Facial Hair Details (Mustache, Beard, full beard, Goatee, Sideburns, Stubble, etc.): 

Instructions:
- Применяй только варианты hairstyle, представленные в списке.
- Для коротких hairstyle или лысин используй обозначения «Buzz Cut» или «Bald».
- Описывай только те элементы, которые явно видны на фотографии.
- Выделяй отдельно детали лица (усы, борода).

Step 3: Make prompt in English with character description creation Based on your information and the image, a character description will be created in this format: [Name], a [Age]-year-old [Gender] from [Place of Residence], with [Hairstyle], [Hair Color, if visible] hair, [Facial Hair Details, if visible], [Eye Color] eyes, a [Facial Expression] expression and [Skin Tone] skin tone, [wearing Accessories if applicable]. Dressed in a [Upper Clothing Color] [Upper Body Outfit] and [Lower Clothing Color] [Lower Body Outfit]. The character is [Action] against a whimsical background, in 3D Pixar Animation Style.

Instructions:
1. Don't write Step 1 and 2 in final answer
2. Don't mention anything if its not visible
3. Don't use word choker 
4. Keep [Name] and [Place of Residence] in original language

{f"Additional photo context: {photo_description}" if photo_description else ""}"""

        return prompt.strip()

    @staticmethod
    def get_story_generation_prompt(
            story: StoriesModel,
            hero_description: str
    ) -> str:
        """
        Промпт 2: Генерация сказки и промптов для иллюстраций для Claude API

        Args:
            story: Модель истории с пользовательскими данными
            hero_description: Результат первого промпта (описание героя)

        Returns:
            str: Полный промпт для Claude API
        """
        input_language = "english"
        prompt = f"""Используйте следующую информацию о персонаже: {hero_description}
## Жанр истории:
{story.story_theme}
## Интересы ребенка
{story.story_extra}
## Тема, которую нужно раскрыть в истории:
{story.story_message}
## Объем и сложность истории
Объем истории подбирается в соответствии с возрастом ребенка:
* 0–3 лет: 100–300 слов (короткие, простые истории с повторениями)
* 4–6 лет: 300–600 слов (сюжет чуть сложнее, но всё ещё с простой лексикой)
* 7–9 лет: 600–800 слов (более развитый сюжет, диалоги, мораль)
* 10 и больше лет: 800–1000 слов (сюжеты с развитием, завязкой и развязкой, психологией персонажей)
## Инструкция для генерации
Используя предоставленную информацию, создайте увлекательную историю в выбранном жанре на {input_language}, где главным героем будет описанный мультяшный персонаж. История должна:
1. Соответствовать возрасту ребенка по объему и сложности
2. Отражать интересы ребенка
3. Раскрывать заданную тему (если указана)
4. Содержать диалоги и\или яркие описания
5. Иметь четкую структуру с началом, серединой (где герой сталкивается с вызовом) и концом (где достигается разрешение)
6. Включать шесть специальных отметок для вставки иллюстраций в ключевых моментах рассказа: [ILLUSTRATION_1], [ILLUSTRATION_2], [ILLUSTRATION_3], [ILLUSTRATION_4], [ILLUSTRATION_5], [ILLUSTRATION_6]. Эти отметки должны быть размещены в тексте на отдельной строке в наиболее значимых и зрелищных моментах истории.
7. Для младших возрастов используйте больше повторений, простые предложения и понятные образы и меньше диалогов. Для старших возрастов добавляйте более сложные сюжетные линии, развитие персонажей и моральные уроки.
8. не пиши имена и внешность родственников и домашних животных (мам, пап, бабушек и тд), если они не указаны в запросе пользователя.
## Ограничение объема
Каждая ключевая часть рассказа (выделенная под изображение) должна содержать не более 3500 символов, не учитывая промты для генерации изображений.
## Структура ответа
1. Название истории (яркое и соответствующее сюжету) (story_title)
2. Сама история (с отметками для иллюстраций в ключевых моментах) (story_body)
3. Послесловие в одном предлложении о том, какие ценности или уроки представлены в истории
4. Промты для генерации иллюстраций - 6 детальных промтов на английском языке для генерации иллюстраций.  (illustration prompts, listed as n1, n2, n3, n4, n5, n6)
Инструкции для промтов изображений:
Промты должны:
 1. Всегда полностью прописывать информацию о внешности героя из информации в пункте 1 (кроме одежды)
 2. На иллюстрациях должна быть описана сцена
 3. Не должно быть повторяющихся второстепенных персонажей, за исключением главного героя.
 4. В начале должны указываться возраст персонажа и его пол, имя
 5. Стиль изображения должен указываться в конце
 6. Иллюстрации должны быть разных ракурсов и форматов, например: близкий кадр героя с размытым фоном, герой в полный рост на фоне детально описанной локации, герой издалека стоящий спиной и наблюдающий за локацией, средняя дистанция, эмоции героя, важные предметы близко и тд
 7. Don’t use words: ukraine, war, battle, religion, looking under, shooting, pot, mushroom, under, choker, below, low angle, thorny, needle, trip, portrait etc that is restricted to use with child content
 8. This prompt is intended for generating friendly, safe, and age-appropriate children’s illustrations. Avoid any references to nudity, suggestive clothing, body parts, chokers, shooting, below, low angle, or phrases like ‘looking under’. Do not use camera angles or poses that can be interpreted as voyeuristic. Use soft, imaginative, and wholesome descriptions suitable for children’s books or cartoons. The image must be safe for work (SFW) and child-appropriate
## ВАЖНО
Сначала проанализируй текст и если текст содержит запрещенные, нелегальные слова, останови генерацию и выведи сообщение об ошибке. Если все хорошо, сразу начинай генерацию"""
        return prompt.strip()

    @staticmethod
    def get_photo_analysis_prompt() -> str:
        """
        Промпт для анализа загруженного фото через GPT-4V (предварительный шаг)

        Returns:
            str: Промпт для извлечения деталей внешности из фото
        """

        prompt = """Analyze this photo and extract physical appearance details for character creation. Focus on:

1. Hair: style, color, length
2. Facial features: eye color, skin tone, facial hair
3. Accessories: glasses, headbands, etc.
4. Age estimation (if visible)
5. Expression and mood

Provide a detailed but child-friendly description suitable for 3D character modeling.
Avoid mentioning clothing details as they will be changed in the final character.
Format your response as natural descriptive text."""

        return prompt.strip()

    @staticmethod
    def parse_story_response(claude_response: str) -> Dict[str, Any]:
        """
        Парсинг ответа от Claude API для извлечения компонентов истории

        Args:
            claude_response: Сырой ответ от Claude API

        Returns:
            Dict с компонентами: title, story_text, moral, image_prompts
        """

        lines = claude_response.strip().split('\n')

        result = {
            'title': '',
            'story_text': '',
            'moral': '',
            'image_prompts': []
        }

        current_section = 'title'
        story_lines = []
        prompt_lines = []

        for line in lines:
            line = line.strip()

            # Определяем секции
            if line.startswith('1.') or 'название' in line.lower():
                current_section = 'title'
            elif line.startswith('2.') or 'история' in line.lower():
                current_section = 'story'
            elif line.startswith('3.') or 'послесловие' in line.lower():
                current_section = 'moral'
            elif line.startswith('4.') or 'промты' in line.lower():
                current_section = 'prompts'
            elif line:
                # Добавляем контент в соответствующую секцию
                if current_section == 'title' and not result['title']:
                    result['title'] = line
                elif current_section == 'story':
                    story_lines.append(line)
                elif current_section == 'moral' and not result['moral']:
                    result['moral'] = line
                elif current_section == 'prompts':
                    prompt_lines.append(line)

        # Собираем текст истории
        result['story_text'] = '\n'.join(story_lines)

        # Извлекаем промпты для изображений
        current_prompt = ""
        for line in prompt_lines:
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                if current_prompt:
                    result['image_prompts'].append(current_prompt.strip())
                current_prompt = line
            else:
                current_prompt += " " + line

        if current_prompt:
            result['image_prompts'].append(current_prompt.strip())

        return result

    @staticmethod
    def validate_content_safety(text: str) -> Dict[str, Any]:
        """
        Проверка контента на безопасность для детей

        Args:
            text: Текст для проверки

        Returns:
            Dict с результатом проверки: is_safe, warnings, blocked_words
        """

        # Список запрещенных слов
        blocked_words = {
            'ukraine', 'war', 'battle', 'religion', 'looking under',
            'shooting', 'pot', 'mushroom', 'under', 'choker',
            'below', 'low angle', 'thorny', 'needle', 'trip',
            'nude', 'naked', 'blood', 'violence', 'death',
            'kill', 'murder', 'weapon', 'gun', 'knife'
        }

        text_lower = text.lower()
        found_words = []

        for word in blocked_words:
            if word in text_lower:
                found_words.append(word)

        is_safe = len(found_words) == 0

        return {
            'is_safe': is_safe,
            'blocked_words': found_words,
            'warnings': [f"Found inappropriate word: {word}" for word in found_words]
        }

    @staticmethod
    def get_age_appropriate_guidelines(age: int) -> Dict[str, Any]:
        """
        Получение рекомендаций по возрасту для создания контента

        Args:
            age: Возраст ребенка

        Returns:
            Dict с рекомендациями: word_count, complexity, themes
        """

        if age <= 3:
            return {
                'word_count': (100, 300),
                'complexity': 'very_simple',
                'themes': ['family', 'animals', 'colors', 'sounds'],
                'features': ['repetition', 'simple sentences', 'familiar objects']
            }
        elif age <= 6:
            return {
                'word_count': (300, 600),
                'complexity': 'simple',
                'themes': ['friendship', 'adventure', 'helping others', 'learning'],
                'features': ['simple plot', 'clear moral', 'dialogue']
            }
        elif age <= 9:
            return {
                'word_count': (600, 800),
                'complexity': 'moderate',
                'themes': ['courage', 'problem solving', 'teamwork', 'creativity'],
                'features': ['character development', 'conflict resolution', 'humor']
            }
        else:
            return {
                'word_count': (800, 1000),
                'complexity': 'advanced',
                'themes': ['self-discovery', 'responsibility', 'complex emotions', 'ethics'],
                'features': ['complex plot', 'character psychology', 'multiple themes']
            }

    @staticmethod
    def create_illustration_prompts_from_story(
            story_text: str,
            hero_description: str,
            story_data: StoriesModel
    ) -> List[str]:
        """
        Создание промптов для иллюстраций на основе готового текста истории
        (используется если Claude не вернул промпты)

        Args:
            story_text: Текст истории с плейсхолдерами [ИЛЛЮСТРАЦИЯ X]
            hero_description: Описание героя
            story_data: Данные истории

        Returns:
            List[str]: 6 промптов для Leonardo AI
        """

        base_hero = f"{story_data.story_name}, a {story_data.story_age}-year-old {story_data.story_gender}"

        # Базовые промпты если не удалось извлечь из Claude
        fallback_prompts = [
            f"{base_hero} standing in a magical forest, {hero_description}, smiling and looking curious, in 3D Pixar Animation Style",
            f"{base_hero} meeting a friendly animal companion, {hero_description}, medium shot with beautiful background, in 3D Pixar Animation Style",
            f"{base_hero} facing a challenge or obstacle, {hero_description}, determined expression, dynamic composition, in 3D Pixar Animation Style",
            f"{base_hero} discovering something important, {hero_description}, surprised and happy expression, close-up shot, in 3D Pixar Animation Style",
            f"{base_hero} helping others or showing kindness, {hero_description}, warm and caring scene, in 3D Pixar Animation Style",
            f"{base_hero} celebrating success at the end, {hero_description}, joyful expression, full scene with celebration, in 3D Pixar Animation Style"
        ]

        return fallback_prompts


# Экземпляр сервиса для использования в других модулях
ai_prompts = AIPrompts()