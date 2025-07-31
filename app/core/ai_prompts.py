from app.models.stories import StoriesModel


class AIPrompts:
    @staticmethod
    def get_hero_avatar_prompt(story: StoriesModel, photo_description: str = "") -> str:
        if story.story_gender == "Boy":
            gender = "male"
        elif story.story_gender == "Girl":
            gender = "female"
        else:
            gender = "other"

        prompt = f"""Describe this person from this picture following these steps: 

Step 1: Character Name: {story.story_name} - Character Age: {story.story_age} - Character Gender: {gender} - Place of Residence: {story.story_location}

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
5. If you think the content is inappropriate for Leonardo, simply return [ERROR] and a concise reason after it

{f"Additional photo context: {photo_description}" if photo_description else ""}"""

        return prompt.strip()

    @staticmethod
    def get_story_generation_prompt(
            story: StoriesModel,
            hero_description: str
    ) -> str:
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
Используя предоставленную информацию, создайте увлекательную историю в выбранном жанре на {story.story_language}, где главным героем будет описанный мультяшный персонаж. История должна:
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
## Структура ответа (these should be in English everything else in {story.story_language}: [TITL], [STRY], [ILLUS], [N1], [N2], [N3], [N4], [N5], [N6])
1. Название истории (яркое и соответствующее сюжету) [TITL]
2. Сама история (с отметками для иллюстраций в ключевых моментах) [STRY]
3. Послесловие в одном предлложении о том, какие ценности или уроки представлены в истории
4. Промты для генерации иллюстраций - 6 детальных промтов на английском языке для генерации иллюстраций.  ([ILLUS], listed as [N1], [N2], [N3], [N4], [N5], [N6])
# Формат финального ответа (всегда на английском):

- [TITL] Название истории
- [STRY] Текст истории с тегами [ILLUSTRATION_1] … [ILLUSTRATION_6]
- [ILLUS]
  - [N1] (prompt for ILLUSTRATION_1)
  - [N2] ...
  - [N3] ...
  - [N4] ...
  - [N5] ...
  - [N6] ...

⚠️ Output must follow this exact format and field names, in English, regardless of story language.
Инструкции для промтов изображений:
Промты должны:
 1. Всегда полностью прописывать информацию о внешности героя из информации в пункте 1 (кроме одежды)
 2. На иллюстрациях должна быть описана сцена
 3. Не должно быть повторяющихся второстепенных персонажей, за исключением главного героя.
 4. В начале должны указываться возраст персонажа и его пол, имя
 5. Стиль изображения должен указываться в конце
 6. Иллюстрации должны быть разных ракурсов и форматов, например: близкий кадр героя с размытым фоном, герой в полный рост на фоне детально описанной локации, герой издалека стоящий спиной и наблюдающий за локацией, средняя дистанция, эмоции героя, важные предметы близко и тд
 7. Don’t use words: ukraine, war, battle, religion, looking under, shooting, pot, mushroom, under, choker, below, low angle, thorny, needle, lounge, trip, portrait etc that is restricted to use with toddler-child content
 8. This prompt is intended for generating friendly, safe, and age-appropriate children’s illustrations. Avoid any references to nudity, suggestive clothing, body parts, chokers, shooting, below, low angle, or phrases like ‘looking under’. Do not use camera angles or poses that can be interpreted as voyeuristic. Use soft, imaginative, and wholesome descriptions suitable for children’s books or cartoons. The image must be safe for work (SFW) and child-appropriate
## ВАЖНО
Сначала проанализируй текст и если текст содержит запрещенные, нелегальные слова, останови генерацию и выведи сообщение об ошибке. Если все хорошо, сразу начинай генерацию"""
        print(f"PROMPT: {prompt.strip()}")
        return prompt.strip()

ai_prompts = AIPrompts()