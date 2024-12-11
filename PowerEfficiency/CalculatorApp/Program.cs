



using System.Diagnostics;

namespace ConsoleApp1
{
    internal class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Reading");
            var items = FileAccessor.ReadItems();
            Console.WriteLine($"Loaded {items.Length} items");
            var recipes = FileAccessor.ReadRecipes();
            Console.WriteLine($"Loaded {recipes.Length} recipes");

            Iterate(items, recipes, 10000, defaultToZero: true);

            FileAccessor.WriteItems(items);
            FileAccessor.WriteRecipes(recipes);
            Console.WriteLine("Done!");
        }

        private static void Iterate(Item[] items, Recipe[] recipes, int repeats, bool defaultToZero)
        {
            //step one - update all item costs
            //step two - calculate all recipes cost
            //repeat until max iterations or no change

            if (!defaultToZero)
            {
                FixupRecipeStartingPosition(recipes);
            }


            for (int i = 0; i < repeats; i++)
            {
                foreach (Recipe recipe in recipes)
                {
                    if (!defaultToZero)
                    {
                        var newRecipeCost = CalculateRecipeCost(recipe, items);
                        if (newRecipeCost != null)
                        {
                            //Debug.Assert(!(recipe.TotalCost != null && newRecipeCost > recipe.TotalCost));
                            if (newRecipeCost < (recipe.TotalCost ?? 0) && newRecipeCost >= 0)
                            {
                                recipe.TotalCost = newRecipeCost;
                            }
                        }
                    }
                    else
                    {
                        recipe.TotalCost = CalculateRecipeCost2(recipe, items);
                    }
                }

                foreach (Item item in items)
                {
                    var newCost = CalculateCost(item, recipes);
                    if (newCost.cost != null)
                    {
                        item._previousCost = item.Cost;
                        (item.Cost, item.RecipeName) = newCost;
                    }
                }

                if (items.Any(i => i.Cost != i._previousCost))
                {
                    continue;
                }
                else
                {
                    Console.WriteLine($"Calculation stalled at {i}");
                    break;
                }
            }
        }

        private static void FixupRecipeStartingPosition(Recipe[] recipes)
        {
            //to prevent endless loops, initialize all ecipe totals to extremely large values - they will be pruned off when actual recipe costs are calculated
            foreach(Recipe recipe in recipes)
            {
                recipe.TotalCost = 999999;
            }
        }

        private static decimal? CalculateRecipeCost(Recipe recipe, Item[] items)
        {
            var cost = recipe.BuildingPower;

            foreach (var ingredient in recipe.Ingredients)
            {
                var itemCost = items.Single(i => i.Name == ingredient.name).Cost;
                if (itemCost == null)
                {
                    return null;
                }

                cost += ingredient.amount * itemCost.Value;
            }

            return cost / recipe.Amount;
        }

        private static decimal? CalculateRecipeCost2(Recipe recipe, Item[] items)
        {
            var cost = recipe.BuildingPower;

            foreach (var ingredient in recipe.Ingredients)
            {
                var itemCost = items.Single(i => i.Name == ingredient.name).Cost;
               
                cost += ingredient.amount * itemCost ?? 0;
            }

            return cost / recipe.Amount;
        }

        private static (decimal? cost, string recipe) CalculateCost(Item item, Recipe[] recipes)
        {
            var validRecipes = recipes.Where(r => r.Product == item.Name && r.TotalCost != null);
            var cheapest = validRecipes.OrderBy(vr => vr.TotalCost).FirstOrDefault();
            if (cheapest != null)
            {
                return (cheapest.TotalCost, cheapest.Name);
            }

            return (null, null);
        }

        public class Item
        {
            public string Name { get; set; }
            public int Points { get; set; }
            public string RecipeName { get; set; }

            public decimal? Cost { get; set; }   //in MW/unit/minute

            public decimal? _previousCost { get; set; }
        }

        public class Recipe
        {
            public string Name { get; set; }
            public string Product { get; internal set; }
            public decimal Amount { get; internal set; }
            public string ProducedIn { get; internal set; }
            public decimal BuildingPower { get; internal set; }
            public (string name, decimal amount)[] Ingredients { get; internal set; }
            public decimal? TotalCost { get; internal set; }
        }
    }
}
