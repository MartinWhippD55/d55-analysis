# MealPlan — Screen Mockups

Low-fidelity wireframes for a meal-planning app: plan the week's meals,
discover recipes from connected recipe providers, and turn the plan into a
shopping list that maps ingredients to a connected supermarket's live catalogue
for one-click ordering. "Layout only" — not final visuals.

Generated with the `screen-mockups` skill.

## Screens

| # | Screen | File |
|---|--------|------|
| 1 | Weekly Meal Plan | [01-meal-plan.png](mockups/01-meal-plan.png) |
| 2 | Recipe Browser | [02-recipe-browser.png](mockups/02-recipe-browser.png) |
| 3 | Recipe Detail | [03-recipe-detail.png](mockups/03-recipe-detail.png) |
| 4 | Shopping List | [04-shopping-list.png](mockups/04-shopping-list.png) |
| 5 | Connections | [05-connections.png](mockups/05-connections.png) |

---

## Screen 1: Weekly Meal Plan

The home screen. A seven-day planner showing the meal slotted into each day.

**Layout**
- Header: "Meal Plan" + [+ Add Meal]
- Week navigator (‹ prev / next ›) with a summary of how many recipes are planned
- Seven day columns, each with a meal slot: filled slots show the recipe name, servings, and source provider; empty slots show a "+ add recipe" placeholder
- Footer actions: [Discover Recipes], [Build Shopping List]

**Key interactions**
- Drag a recipe between days to reschedule
- Click an empty slot to add a recipe (opens the Recipe Browser)
- "Build Shopping List" aggregates ingredients across the whole week into Screen 4

---

## Screen 2: Recipe Browser

Search recipes across the connected providers and add them to the plan.

**Layout**
- Header: "Discover Recipes" + [← Back to Plan]
- Search bar with query input + [Search]
- Left panel: filters (recipe provider, diet, max time)
- Right panel: result cards, each with thumbnail, title, time/servings, a provider badge, and [View] / [+ Add to plan]

**Key interactions**
- Filter pills narrow results by provider, diet, and cook time
- "View" opens the Recipe Detail modal (Screen 3)
- "+ Add to plan" drops the recipe into the next open day slot

---

## Screen 3: Recipe Detail (modal)

A single recipe pulled from its provider, with servings scaling.

**Layout**
- Modal over a dimmed backdrop; header shows recipe name + provider badge + Close
- Left: ingredient list with quantities
- Right: servings stepper, total time, calories, provider, link to the original source
- Footer: [+ Add to Meal Plan]

**Key interactions**
- Servings stepper rescales ingredient quantities
- "Add to Meal Plan" adds the recipe (at the chosen servings) to the week
- "View original" links out to the provider's page

---

## Screen 4: Shopping List

The week's recipes aggregated into a single, checkable list mapped to a
supermarket's catalogue — the todo-list heart of the app.

**Layout**
- Header: "Shopping List" + [Order via {store}]
- Sub-head: source summary + supermarket selector (Tesco / Sainsbury's / ASDA)
- Table: checkbox, ingredient, quantity, matched supermarket product, live price, stock status
- Footer note with the estimated total

**Key interactions**
- Tick items off as you shop (checked rows strike through); "in trolley" items are tagged
- Changing the supermarket re-matches products and refreshes prices/stock
- Out-of-stock items are flagged and offer a swap suggestion
- "Order via {store}" pushes the basket to the connected supermarket for checkout

---

## Screen 5: Connections

Link the supermarket and recipe-provider accounts that power the app.

**Layout**
- Header: "Connections" + [← Back to Plan]
- Left panel: Supermarkets, each row showing name, API description, and a
  Connected badge or [Connect] button (one marked as default store)
- Right panel: Recipe providers, each row showing name, catalogue size, and
  connection state ("Connected" or "Sign in required")

**Key interactions**
- Connect/disconnect a supermarket; the default store drives pricing on Screen 4
- Connect a recipe provider to include its catalogue in search (Screen 2)
- Providers needing a subscription prompt sign-in before use
