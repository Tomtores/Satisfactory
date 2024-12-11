using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static ConsoleApp1.Program;

namespace ConsoleApp1
{
    internal class FileAccessor
    {
        public static Recipe[] ReadRecipes()
        {
            //headers:
            //Recipe Name	Product	Amount	ProducedIn	Power	Ing1	Am1	Ing2	Am2	Ing3	Am3	Ing4	Am4	Ing5	Am5

            var results = new List<Recipe>();
            //read from csv, file name items.csv, the columns are <Display Name><Points> 
            string filePath = "recipes.csv";
            try
            {
                using (var reader = new StreamReader(filePath))
                {
                    string? line;
                    _ = reader.ReadLine();  //skip header row
                    while ((line = reader.ReadLine()) != null)
                    {
                        var values = line.Split(','); // Split by comma
                        results.Add(new Recipe
                        {
                            Name = values[0],
                            Product = values[1],
                            Amount = decimal.Parse(values[2]),
                            ProducedIn = values[3],
                            BuildingPower = decimal.Parse(values[4]),
                            Ingredients = GetIngredients(values, 5),
                        });
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }

            return results.ToArray();
        }

        public static void WriteRecipes(Recipe[] recipes)
        {
            //headers:
            //Recipe Name	Product	Amount	ProducedIn	Power	Ing1	Am1	Ing2	Am2	Ing3	Am3	Ing4	Am4	Ing5	Am5

            string filePath = "recipes_out.csv";

            try
            {
                using (var writer = new StreamWriter(filePath))
                {
                    // Write header
                    writer.WriteLine("Total Cost,Recipe Name,Product,Amount,ProducedIn,Power,Ing1,Am1,Ing2,Am2,Ing3,Am3,Ing4,Am4,Ing5,Am5");

                    // Write each person
                    foreach (var recipe in recipes)
                    {
                        writer.WriteLine($"{recipe.TotalCost ?? 0},{recipe.Name},{recipe.Product},{recipe.Amount},{recipe.ProducedIn},{recipe.BuildingPower},{ListIngredients(recipe.Ingredients)}");
                    }
                }

                Console.WriteLine("CSV written successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }

        }

        private static string ListIngredients((string name, decimal amount)[] ingredients)
        {
            return string.Join(',', ingredients.Select(i => $"{i.name},{i.amount}"));
        }

        private static (string name, decimal amount)[] GetIngredients(string[] values, int startIndex)
        {
            var ingredientValues = values.Skip(startIndex).ToArray();
            var results = new List<(string, decimal)>();
            for (int i = 0; i < ingredientValues.Length; i = i + 2)
            {
                if (!string.IsNullOrWhiteSpace(ingredientValues[i]))
                {
                    results.Add((ingredientValues[i], decimal.Parse(ingredientValues[i + 1])));
                }
            }

            return results.ToArray();
        }

        public static Item[] ReadItems()
        {
            var results = new List<Item>();
            //read from csv, file name items.csv, the columns are <Display Name><Points> 
            string filePath = "items.csv";
            try
            {
                using (var reader = new StreamReader(filePath))
                {
                    string? line;
                    _ = reader.ReadLine();  //skip header row
                    while ((line = reader.ReadLine()) != null)
                    {
                        var values = line.Split(','); // Split by comma
                        results.Add(new Item { Name = values[0], Points = int.Parse(values[1]) });
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }

            return results.ToArray();
        }

        public static void WriteItems(Item[] items)
        {
            string filePath = "items_out.csv";

            try
            {
                using (var writer = new StreamWriter(filePath))
                {
                    // Write header
                    writer.WriteLine("MW,Item,Recipe,Points");

                    // Write each person
                    foreach (var item in items)
                    {
                        writer.WriteLine($"{item.Cost ?? 0},{item.Name},{item.RecipeName},{item.Points}");
                    }
                }

                Console.WriteLine("CSV written successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }
    }
}
