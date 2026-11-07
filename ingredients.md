# Ingredient Index

Every ingredient a recipe uses must have a row here, and recipes must use the
**exact name** and **unit** from this table. That's what lets meal plans
combine recipes into one shopping list.

- **Ingredient** — lowercase, singular, what you'd buy (no prep words like
  "diced"). Keep words that change what you buy: `unsalted butter`,
  `canned black beans`, `fresh cilantro`.
- **Unit** — the one unit every recipe uses for this item.
- **Aisle** — one of: produce, meat & seafood, dairy & eggs, bakery, deli,
  frozen, canned & jarred, pasta & grains, baking, spices,
  condiments & sauces, oils & vinegars, snacks, beverages, international, other.
- **Staple** — `yes` if you normally keep it on hand (listed under "check
  before you shop" instead of the main list).
- **Aliases** — other names recipes use for it, comma-separated.
- **Conversions** — how other measurements map to the unit, used when
  adding recipes.

Run `python scripts/recipes.py validate` after editing.

| Ingredient | Unit | Aisle | Staple | Aliases | Conversions |
|---|---|---|---|---|---|
| all-purpose flour | cup | baking | yes | flour, ap flour, plain flour | 1 lb ≈ 3.6 cup; 125 g = 1 cup |
| bacon | lb | meat & seafood | no | bacon strips, sliced bacon | 1 slice ≈ 1 oz; 1 lb ≈ 16 slice |
| baking powder | tsp | baking | yes |  | 1 tbsp = 3 tsp |
| baking soda | tsp | baking | yes | bicarbonate of soda | 1 tbsp = 3 tsp |
| bay leaf | each | spices | yes | dried bay leaf, bay leaves |  |
| black pepper | tsp | spices | yes | pepper, ground black pepper | 1 tbsp = 3 tsp |
| boneless skinless chicken breast | lb | meat & seafood | no | chicken breast, chicken breasts | 1 breast ≈ 1/2 lb |
| canned black beans (15 oz) | can | canned & jarred | no | black beans, can black beans | 1 can ≈ 1.5 cup drained |
| canned kidney beans (15 oz) | can | canned & jarred | no | kidney beans, can kidney beans, red kidney beans | 1 can ≈ 1.5 cup drained |
| canned tomato sauce (15 oz) | can | canned & jarred | no | tomato sauce, can tomato sauce | 1 can ≈ 1.75 cup |
| carrot | each | produce | no | carrots | 1 medium ≈ 1/2 cup chopped; 1 lb ≈ 6 each |
| celery | bunch | produce | no | celery stalk, celery rib | 1 bunch ≈ 9 stalk; 1 stalk ≈ 1/2 cup chopped |
| chicken broth | cup | canned & jarred | no | chicken stock | 1 carton (32 oz) = 4 cup; 1 can (14.5 oz) ≈ 1.75 cup |
| chipotle chili powder | tsp | spices | yes | chipotle powder, ground chipotle | 1 tbsp = 3 tsp |
| dried oregano | tsp | spices | yes | oregano | 1 tbsp = 3 tsp |
| egg | each | dairy & eggs | no | eggs, large egg |  |
| fresh italian parsley | bunch | produce | no | italian parsley, flat-leaf parsley, parsley | 1 bunch ≈ 1 cup chopped |
| fresh rosemary | bunch | produce | no | rosemary, rosemary sprigs | 1 bunch ≈ 6 sprig; 1 sprig ≈ 1 tsp chopped |
| fresh thyme | bunch | produce | no | thyme, thyme sprigs | 1 bunch ≈ 12 sprig; 1 sprig ≈ 1/2 tsp leaves |
| garlic | clove | produce | no | garlic clove | 1 tsp minced ≈ 1 clove; 1 tbsp minced ≈ 3 clove; 1 head ≈ 10 clove |
| granulated sugar | cup | baking | yes | sugar, white sugar | 1 tbsp = 1/16 cup; 200 g = 1 cup |
| ground beef | lb | meat & seafood | no | hamburger, minced beef |  |
| ground cumin | tsp | spices | yes | cumin | 1 tbsp = 3 tsp |
| ground nutmeg | tsp | spices | yes | nutmeg | 1 tbsp = 3 tsp |
| heavy cream | cup | dairy & eggs | no | heavy whipping cream, whipping cream, cream | 8 oz = 1 cup; 1 pint = 2 cup; 1 tbsp = 1/16 cup |
| jalapeño | each | produce | no | jalapeno, jalepeno, jalapeño pepper |  |
| kosher salt | tsp | spices | yes | salt | 1 tbsp = 3 tsp |
| lemon | each | produce | no | lemons | 1 lemon ≈ 3 tbsp juice; 1 lemon ≈ 1 tbsp zest |
| lettuce | each | produce | no | head of lettuce, iceberg lettuce, romaine lettuce, green leaf lettuce | 1 head ≈ 8 cup shredded |
| mayonnaise | tbsp | condiments & sauces | yes | mayo | 1 cup = 16 tbsp |
| mild italian sausage | lb | meat & seafood | no | ground italian sausage, italian sausage, bulk italian sausage | 1 link ≈ 1/4 lb |
| olive oil | tbsp | oils & vinegars | yes | extra virgin olive oil, evoo | 1 cup = 16 tbsp; 1 tsp = 1/3 tbsp |
| parmesan cheese | oz | dairy & eggs | no | parmesan, parmigiano reggiano, grated parmesan | 1 cup grated ≈ 3 oz |
| sourdough bread | slice | bakery | no | sourdough, sourdough loaf | 1 loaf ≈ 16 slice |
| spaghetti | oz | pasta & grains | yes | spaghetti noodles, dried spaghetti | 1 box = 16 oz; 1 lb = 16 oz |
| tomato | each | produce | no | tomatoes, fresh tomato | 1 medium ≈ 1 cup chopped; 1 medium ≈ 4 slice |
| unsalted butter | tbsp | dairy & eggs | no | butter | 1 stick = 8 tbsp = 1/2 cup; 1 cup = 16 tbsp |
| whole chicken | each | meat & seafood | no | chicken, whole fryer, roaster | 1 each ≈ 4 lb; 1 each ≈ 4 cup cooked shredded meat |
| whole milk | cup | dairy & eggs | no | milk | 1 tbsp = 1/16 cup |
| yellow onion | each | produce | no | onion, brown onion | 1 medium ≈ 1 cup chopped |
