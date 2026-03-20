"""
Shelf Life Estimator — Seed Data
==================================
Pre-populates the database with 40+ fruit items,
each with shelf life data for 3 storage methods and storage tips.

Run on first startup if the food_items table is empty.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import FoodItem, User

# ============================================
# 40+ Fruit Items with Shelf Life Data
# ============================================
# Format: (name, category, room_temp_days, fridge_days, freezer_days, storage_tips)

FOOD_DATA = [
    # === COMMON FRUITS ===
    ("Apple", "fruits", 7, 28, 240,
     "Store loose in the fridge crisper drawer. Keep away from other fruits as apples produce ethylene gas that ripens others faster."),
    ("Banana", "fruits", 5, 7, 180,
     "Store at room temperature until ripe. Refrigerate only when ripe — skin darkens but flesh stays fresh longer. Freeze peeled for smoothies."),
    ("Orange", "fruits", 10, 21, 180,
     "Room temperature for a week, fridge for longer storage. Store in mesh bag for air circulation. Don't stack too tightly."),
    ("Strawberry", "fruits", 2, 7, 180,
     "Don't wash until ready to eat. Store in a single layer with paper towel to absorb moisture. Remove any moldy ones immediately."),
    ("Grape", "fruits", 2, 10, 180,
     "Store unwashed in a perforated bag in the fridge. Remove spoiled grapes immediately to prevent spread."),
    ("Mango", "fruits", 5, 10, 180,
     "Ripen at room temperature. Once ripe (slightly soft, fragrant), refrigerate to slow further ripening. Peel and cube before freezing."),
    ("Pineapple", "fruits", 3, 7, 180,
     "Cut pineapple should be refrigerated in an airtight container. Whole pineapple keeps at room temp for a few days. Smell the base — sweet = ripe."),
    ("Avocado", "fruits", 4, 7, 120,
     "Ripen at room temperature. Once ripe, refrigerate to extend life by 2-3 days. Sprinkle cut avocado with lemon juice to prevent browning."),
    ("Watermelon", "fruits", 7, 14, 180,
     "Whole watermelon keeps at room temperature. Once cut, wrap tightly and refrigerate. Freeze cubes for smoothies and snacks."),
    ("Peach", "fruits", 3, 7, 180,
     "Ripen on counter in a paper bag. Refrigerate once slightly soft near the stem. Bruises easily — handle with care."),

    # === CITRUS FRUITS ===
    ("Lemon", "fruits", 7, 28, 90,
     "Store whole lemons in the fridge in a sealed bag for up to a month. Room temp is fine for a week. Roll before juicing for more juice."),
    ("Lime", "fruits", 7, 21, 90,
     "Similar to lemons. Keep in a sealed bag in the fridge. Limes dry out faster than lemons, so bag storage is key."),
    ("Grapefruit", "fruits", 7, 21, 180,
     "Store at room temp for a week or fridge for longer. Heavier grapefruits have more juice. Peel segments for easy snacking."),
    ("Tangerine", "fruits", 5, 14, 180,
     "Store loose in the fridge. Easy to peel and segment. Eat within a week for best flavor. Keep away from strong odors."),
    ("Clementine", "fruits", 5, 14, 180,
     "Refrigerate in a mesh bag or loose in the crisper. Don't store in sealed plastic — moisture causes mold."),

    # === BERRIES ===
    ("Blueberry", "fruits", 1, 10, 180,
     "Don't wash until ready to eat. Store in original container in the fridge. Discard any moldy berries immediately — mold spreads fast."),
    ("Raspberry", "fruits", 1, 5, 180,
     "Extremely delicate. Don't wash until eating. Store in a single layer on paper towel. Use within 2-3 days of purchase."),
    ("Blackberry", "fruits", 1, 5, 180,
     "Similar to raspberries — very perishable. Store unwashed in a single layer. A vinegar rinse (1:3 vinegar to water) before storing extends life."),
    ("Cranberry", "fruits", 3, 28, 270,
     "Fresh cranberries last surprisingly long in the fridge. Freeze in original bag. Bounce test: fresh cranberries bounce!"),

    # === TROPICAL FRUITS ===
    ("Papaya", "fruits", 3, 7, 180,
     "Ripen at room temperature until skin is mostly yellow. Once ripe, refrigerate. Cut papaya lasts 2-3 days in the fridge."),
    ("Kiwi", "fruits", 5, 14, 180,
     "Firm kiwis ripen at room temp in 3-5 days. Place near bananas or apples to speed ripening. Refrigerate once ripe."),
    ("Passion Fruit", "fruits", 5, 14, 180,
     "Ripe when skin is wrinkled and dark purple. Store at room temp until wrinkled, then refrigerate. Scoop out pulp and freeze."),
    ("Dragon Fruit", "fruits", 3, 7, 120,
     "Store at room temperature for a few days. Refrigerate in a bag once cut. Bright pink skin should give slightly when ripe."),
    ("Guava", "fruits", 3, 7, 180,
     "Ripen at room temperature. Once fragrant and slightly soft, refrigerate. Green guavas are unripe but still edible."),
    ("Lychee", "fruits", 2, 7, 180,
     "Highly perishable. Refrigerate immediately in a perforated bag. Skin turns brown in the fridge but flesh stays good."),
    ("Coconut", "fruits", 14, 7, 180,
     "Whole unopened coconut lasts 2 weeks at room temp. Once opened, refrigerate the meat and use within a week. Freeze shredded."),
    ("Pomegranate", "fruits", 7, 30, 180,
     "Whole pomegranates last weeks in the fridge. Seeds (arils) in a container last about a week refrigerated. Freeze arils flat on a tray."),
    ("Star Fruit", "fruits", 3, 7, 120,
     "Ripen at room temperature until edges turn brown. Store ripe fruit in the fridge. Slice crosswise for decorative star shapes."),

    # === STONE FRUITS ===
    ("Pear", "fruits", 4, 10, 180,
     "Ripen at room temperature. Check daily — pears ripen from the inside out. Refrigerate when slightly soft near the stem."),
    ("Plum", "fruits", 3, 7, 180,
     "Ripen at room temperature. Once they give slightly to pressure, move to fridge. Great for baking and preserves."),
    ("Cherry", "fruits", 1, 7, 180,
     "Highly perishable. Refrigerate immediately in a bag with a paper towel. Don't wash until ready to eat. Leave stems on for longer life."),
    ("Apricot", "fruits", 3, 7, 180,
     "Ripen at room temperature. Very soft apricots should be eaten immediately. Store in a single layer to prevent bruising."),
    ("Nectarine", "fruits", 3, 7, 180,
     "Similar to peaches but with smooth skin. Ripen on counter, refrigerate when ripe. Don't stack — they bruise easily."),

    # === MELONS ===
    ("Cantaloupe", "fruits", 5, 10, 180,
     "Whole cantaloupe at room temp until ripe (fragrant, yields to pressure at stem end). Once cut, refrigerate and use within 3 days."),
    ("Honeydew", "fruits", 5, 10, 180,
     "Store at room temp until ripe. Ripe honeydew has creamy yellow skin and a sweet smell. Refrigerate once cut."),

    # === OTHER FRUITS ===
    ("Fig", "fruits", 2, 5, 180,
     "Very perishable. Refrigerate immediately. Handle gently — figs bruise at the slightest touch. Store in a single layer."),
    ("Date", "fruits", 30, 180, 365,
     "Dried dates last months at room temp. Fresh dates should be refrigerated. Store in an airtight container. Freeze for years."),
    ("Persimmon", "fruits", 5, 14, 180,
     "Fuyu (firm) type can be eaten crisp. Hachiya type must be fully soft/ripe. Ripen at room temp, refrigerate when ready."),
    ("Jackfruit", "fruits", 3, 7, 60,
     "Whole jackfruit keeps at room temp for a few days. Cut sections should be refrigerated in airtight containers."),
    ("Plantain", "fruits", 7, 10, 180,
     "Cook before eating (unlike bananas). Green = starchy, Yellow = sweeter, Black = very sweet. Ripen at room temperature."),
    ("Soursop", "fruits", 2, 5, 180,
     "Ripen at room temperature until soft. Once ripe, eat immediately or scoop out pulp and freeze. Very perishable when ripe."),
]


# Default user for single-user mode
DEFAULT_USER = {
    "username": "default",
    "email": "user@shelflife.local",
    "password_hash": "$2b$12$placeholder_hash_for_default_user",
}


async def seed_database(db: AsyncSession) -> None:
    """
    Populate the database with fruit items and a default user.
    Only runs if the tables are empty.
    """
    # Check if food items already exist
    result = await db.execute(select(func.count()).select_from(FoodItem))
    count = result.scalar()

    if count > 0:
        print(f"✅ Database already seeded with {count} fruit items. Skipping.")
        return

    print("🌱 Seeding database with fruit items...")

    # Seed fruit items
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
    print(f"✅ Seeded {len(food_items)} fruit items!")
