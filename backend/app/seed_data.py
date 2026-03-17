"""
Shelf Life Estimator — Seed Data
==================================
Pre-populates the database with 60+ food items,
each with shelf life data for 3 storage methods and storage tips.

Run on first startup if the food_items table is empty.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import FoodItem, User

# ============================================
# 60+ Food Items with Shelf Life Data
# ============================================
# Format: (name, category, room_temp_days, fridge_days, freezer_days, storage_tips)

FOOD_DATA = [
    # === FRUITS ===
    ("Apple", "fruits", 7, 28, 240,
     "Store loose in the fridge crisper drawer. Keep away from other fruits as apples produce ethylene gas."),
    ("Banana", "fruits", 5, 7, 180,
     "Store at room temperature until ripe. Refrigerate only when ripe — skin darkens but flesh stays fresh longer."),
    ("Orange", "fruits", 10, 21, 180,
     "Room temperature for a week, fridge for longer storage. Store in mesh bag for air circulation."),
    ("Strawberry", "fruits", 2, 7, 180,
     "Don't wash until ready to eat. Store in a single layer with paper towel to absorb moisture."),
    ("Grape", "fruits", 2, 10, 180,
     "Store unwashed in a perforated bag in the fridge. Remove spoiled grapes immediately."),
    ("Mango", "fruits", 5, 10, 180,
     "Ripen at room temperature. Once ripe, refrigerate to slow further ripening."),
    ("Pineapple", "fruits", 3, 7, 180,
     "Cut pineapple should be refrigerated in an airtight container. Whole pineapple keeps at room temp for a few days."),
    ("Avocado", "fruits", 4, 7, 120,
     "Ripen at room temperature. Once ripe, refrigerate to extend life. Sprinkle cut avocado with lemon juice."),
    ("Watermelon", "fruits", 7, 14, 180,
     "Whole watermelon keeps at room temperature. Once cut, wrap tightly and refrigerate."),
    ("Peach", "fruits", 3, 7, 180,
     "Ripen on counter, then refrigerate. Place in a paper bag to speed ripening."),
    ("Lemon", "fruits", 7, 28, 90,
     "Store whole lemons in the fridge in a sealed bag. Room temp is fine for a week."),
    ("Pear", "fruits", 4, 10, 180,
     "Ripen at room temperature. Check daily — pears ripen from the inside out. Refrigerate when slightly soft near stem."),
    ("Papaya", "fruits", 3, 7, 180,
     "Ripen at room temperature. Once yellow with slight give, refrigerate. Cut papaya lasts 2-3 days in fridge."),
    ("Blueberry", "fruits", 1, 10, 180,
     "Don't wash until ready to eat. Store in original container in the fridge. Discard any moldy berries immediately."),
    ("Kiwi", "fruits", 5, 14, 180,
     "Firm kiwis can ripen at room temp for a few days. Once ripe (slightly soft), refrigerate."),

    # === VEGETABLES ===
    ("Tomato", "vegetables", 5, 10, 60,
     "Store at room temperature stem-side down. Refrigeration dulls flavor. Only chill if very ripe."),
    ("Carrot", "vegetables", 4, 21, 240,
     "Remove green tops before storing. Wrap in damp paper towel in a sealed bag in the fridge."),
    ("Lettuce", "vegetables", 2, 7, 0,
     "Wrap in paper towels and store in a bag in the crisper. Don't freeze lettuce — it wilts badly."),
    ("Bell Pepper", "vegetables", 4, 14, 180,
     "Store whole in the crisper. Cut peppers should be in an airtight container. Green peppers last longer than red."),
    ("Cucumber", "vegetables", 3, 7, 0,
     "Store at room temp if using within 3 days. For longer, wrap individually in paper towels and refrigerate."),
    ("Onion", "vegetables", 30, 14, 180,
     "Store whole onions in a cool, dry, dark place. Once cut, wrap and refrigerate. Don't store near potatoes."),
    ("Potato", "vegetables", 21, 14, 180,
     "Store in a cool, dark, dry place. Don't refrigerate raw potatoes. Keep away from onions. Remove from plastic bags."),
    ("Spinach", "vegetables", 1, 7, 180,
     "Store in original container with a dry paper towel. Use within a week. Freezes well for smoothies and cooking."),
    ("Broccoli", "vegetables", 2, 7, 240,
     "Refrigerate unwashed in a loose or perforated bag. Use within a week for best flavor and nutrition."),
    ("Cauliflower", "vegetables", 2, 7, 240,
     "Wrap in a damp towel and store in fridge. Don't wash until ready to use."),
    ("Sweet Potato", "vegetables", 14, 7, 180,
     "Store in a cool, dry, dark place — NOT the fridge (it hardens the center). Cooked sweet potato goes in fridge."),
    ("Cabbage", "vegetables", 3, 14, 240,
     "Whole cabbage lasts weeks in the fridge. Cut cabbage should be wrapped tightly in plastic. Outer leaves protect inner."),
    ("Zucchini", "vegetables", 3, 7, 90,
     "Store in the crisper drawer in a perforated bag. Don't wash until ready to use."),
    ("Green Beans", "vegetables", 1, 7, 240,
     "Store unwashed in a reusable bag in the fridge. Blanch before freezing for best texture."),
    ("Garlic", "vegetables", 30, 14, 180,
     "Store whole bulbs in a cool, dry, dark place with good airflow. Don't refrigerate whole bulbs."),
    ("Corn", "vegetables", 1, 5, 240,
     "Use fresh corn as soon as possible — sugar converts to starch quickly. Refrigerate in husks."),

    # === DAIRY ===
    ("Milk", "dairy", 0.2, 7, 90,
     "Always refrigerate. Don't leave out for more than 2 hours. Keep in the back of the fridge, not the door."),
    ("Cheese (Hard)", "dairy", 1, 28, 180,
     "Wrap in wax paper then plastic wrap. Hard cheeses last longer than soft. Small mold spots can be cut off."),
    ("Cheese (Soft)", "dairy", 0.5, 7, 120,
     "Keep in original packaging. Use within a week of opening. Don't eat if moldy."),
    ("Yogurt", "dairy", 0.1, 14, 60,
     "Keep refrigerated and sealed. Use within 1-2 weeks of opening. Stir if liquid separates."),
    ("Butter", "dairy", 1, 30, 270,
     "Can be left at room temp for a day for spreading. Refrigerate for longer storage. Freezes exceptionally well."),
    ("Eggs", "dairy", 1, 28, 180,
     "Refrigerate in original carton. Don't store in door — temperature fluctuates. Fresh test: sink in water = fresh."),
    ("Cream", "dairy", 0.1, 7, 90,
     "Keep refrigerated. Don't freeze heavy cream for whipping — texture changes. UHT cream lasts longer."),

    # === MEAT ===
    ("Chicken Breast", "meat", 0.1, 2, 270,
     "Refrigerate immediately. Use within 2 days or freeze. Store on bottom shelf to prevent drips. Thaw in fridge."),
    ("Ground Beef", "meat", 0.1, 2, 120,
     "Use or freeze within 2 days of purchase. Store in the coldest part of the fridge. Cook to 160°F."),
    ("Pork Chop", "meat", 0.1, 3, 120,
     "Refrigerate in original packaging for 1-2 uses. For longer storage, wrap tightly and freeze."),
    ("Steak", "meat", 0.1, 4, 180,
     "Pat dry and store on a wire rack in the fridge for best results. Freeze in vacuum-sealed bags."),
    ("Turkey", "meat", 0.1, 2, 180,
     "Use within 2 days of purchase or freeze. Cooked turkey keeps 3-4 days in fridge."),
    ("Sausage", "meat", 0.1, 2, 60,
     "Fresh sausage is highly perishable. Freeze if not using within 2 days. Cooked sausage lasts longer."),
    ("Bacon", "meat", 0.1, 7, 30,
     "Opened bacon should be used within a week. Wrap tightly in foil or plastic. Freezes well."),

    # === SEAFOOD ===
    ("Salmon", "seafood", 0.1, 2, 90,
     "Use within 2 days of purchase. Store in coldest part of fridge on ice if possible. Freeze immediately if not using."),
    ("Shrimp", "seafood", 0.1, 2, 180,
     "Highly perishable. Refrigerate on ice. Use within 2 days or freeze. Thaw in fridge, not at room temp."),
    ("Tuna Steak", "seafood", 0.1, 1, 90,
     "Extremely perishable. Use the day of purchase or next day. Freeze immediately for longer storage."),
    ("Catfish", "seafood", 0.1, 2, 180,
     "Store on ice in the fridge. Use within 2 days. Pat dry before cooking for better searing."),
    ("Tilapia", "seafood", 0.1, 2, 180,
     "Refrigerate immediately. Should smell mild, not fishy. Freeze in meal-sized portions."),

    # === BAKERY ===
    ("Bread (White)", "bakery", 5, 10, 90,
     "Store at room temperature in original bag. Don't refrigerate — it dries out faster. Freeze sliced for quick toast."),
    ("Bread (Whole Wheat)", "bakery", 4, 10, 90,
     "Whole wheat spoils faster than white. Store in a cool, dry place. Freeze extra loaves immediately."),
    ("Tortilla", "bakery", 7, 21, 180,
     "Refrigerate after opening. Flour tortillas last longer than corn. Freeze with parchment between each."),
    ("Bagel", "bakery", 3, 7, 90,
     "Store at room temp for a few days. Slice before freezing for easy toasting."),

    # === GRAINS & LEGUMES ===
    ("Rice (Cooked)", "grains", 0.1, 5, 180,
     "Refrigerate within 1 hour of cooking. Spread in a thin layer to cool quickly. Reheat thoroughly."),
    ("Rice (Uncooked)", "grains", 365, 365, 365,
     "Store in an airtight container in a cool, dry place. White rice lasts almost indefinitely. Brown rice is shorter."),
    ("Pasta (Cooked)", "grains", 0.1, 5, 60,
     "Toss with a little oil to prevent sticking. Refrigerate in airtight container. Reheat with a splash of water."),
    ("Beans (Cooked)", "legumes", 0.1, 5, 180,
     "Refrigerate within 2 hours. Store in cooking liquid for moisture. Freeze in portions."),
    ("Lentils (Cooked)", "legumes", 0.1, 5, 180,
     "Cool quickly and refrigerate. Great for meal prep — freeze in individual portions."),

    # === HERBS ===
    ("Basil", "herbs", 3, 7, 120,
     "Trim stems and place in water on counter. Or wrap in damp paper towel and refrigerate in a bag."),
    ("Cilantro", "herbs", 2, 10, 120,
     "Trim stems, place in jar of water, cover loosely with plastic bag, refrigerate. Change water every few days."),
    ("Parsley", "herbs", 2, 14, 180,
     "Store like cilantro — stems in water in fridge. Flat-leaf parsley has more flavor than curly."),
    ("Mint", "herbs", 2, 7, 120,
     "Wrap loosely in damp paper towel, place in bag in fridge. Or freeze in ice cube trays with water."),
    ("Ginger", "herbs", 7, 21, 180,
     "Store unpeeled in the fridge in a bag. Freeze whole — grate frozen ginger directly into dishes."),
]


# Default user for single-user mode
DEFAULT_USER = {
    "username": "default",
    "email": "user@shelflife.local",
    "password_hash": "$2b$12$placeholder_hash_for_default_user",
}


async def seed_database(db: AsyncSession) -> None:
    """
    Populate the database with food items and a default user.
    Only runs if the tables are empty.
    """
    # Check if food items already exist
    result = await db.execute(select(func.count()).select_from(FoodItem))
    count = result.scalar()

    if count > 0:
        print(f"✅ Database already seeded with {count} food items. Skipping.")
        return

    print("🌱 Seeding database with food items...")

    # Seed food items
    food_items = [
        FoodItem(
            name=name,
            category=category,
            shelf_life_room_temp_days=room_temp,
            shelf_life_fridge_days=fridge,
            shelf_life_freezer_days=freezer,
            storage_tips=tips,
        )
        for name, category, room_temp, fridge, freezer, tips in FOOD_DATA
    ]

    db.add_all(food_items)

    # Seed default user
    result = await db.execute(select(func.count()).select_from(User))
    user_count = result.scalar()

    if user_count == 0:
        default_user = User(**DEFAULT_USER)
        db.add(default_user)
        print("👤 Created default user")

    await db.commit()
    print(f"✅ Seeded {len(food_items)} food items!")
