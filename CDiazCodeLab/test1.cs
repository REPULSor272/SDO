using System;
using System.Linq;
class Program
{
    static void Main()
    {
        var input = Console.ReadLine();
        var numbers = input.Split(' ').Select(int.Parse).ToArray();
        var squares = numbers.Select(x => x * x).ToArray();
        var sumOfSquares = squares.Sum();
        
        Console.WriteLine(sumOfSquares);

        foreach (var sq in squares.OrderBy(x => x))
            Console.Write(sq + " ");
    }
}