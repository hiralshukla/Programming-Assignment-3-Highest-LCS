# Highest Value Longest Common Sequence

## Student Info

- Emily Apel UFID: 34845199
- Hiral Shukla UFID: 42066733

## Compile / Build

This project is Python-based and does not require a compile step.

Environment used:
- Python 3.13+

Required package for plotting:
- matplotlib

Install dependency:

```bash
python -m pip install matplotlib
```

## How to Run

Run one input file:

```bash
python src/hvlcs.py <input_file.in> <output_file.out>
```

Example:

```bash
python src/hvlcs.py example.in example.out
```

Run all 10 test files:

```bash
python tests/run_all_tests.py
```

Run all tests and generate runtime plots:

```bash
python tests/run_all_tests.py --graph
```

Generate runtime plots directly (with repeated measurements):

```bash
python tests/graph.py --repeats 10
```

Generated runtime artifacts:
- tests/runtime_results.csv
- tests/runtime_graph.png
- tests/runtime_vs_size.png

## Assumptions

1. Input format is:
- First line: alphabet size `k`
- Next `k` lines: `<symbol> <value>`
- Next line: string `A`
- Next line: string `B`
2. Every character that appears in `A` or `B` has a value defined in the alphabet map.
3. All symbol values are integers.
4. Strings are case-sensitive.
5. The algorithm computes the maximum total value of a common subsequence using dynamic programming.
6. Runtime graphs in Question 1 measure the DP computation in-process (minimizing process startup overhead) and use repeated runs to reduce noise.

## Question 1: Emperical Comparsion

We used 10 nontrivial input files in data/test1.in through data/test10.in.
All test strings have length at least 25, and sizes were stepped to increase `|A| x |B|` from 625 to 13225.

Method:
1. For each test file, run the DP computation 10 times.
2. Record mean runtime, standard deviation, min, and max in tests/runtime_results.csv.
3. Plot:
- Runtime by test file with error bars (tests/runtime_graph.png)
- Runtime vs `|A| x |B|` with linear fit (tests/runtime_vs_size.png)

Runtime by test file (mean +/- standard deviation):

![HVLCS Runtime by Test File](tests/runtime_graph.png)

Runtime vs input size `|A| x |B|` with linear fit:

![HVLCS Runtime vs |A| x |B|](tests/runtime_vs_size.png)

Observation:
- Runtime generally increases as `|A| x |B|` increases.
- The runtime-vs-size plot is approximately linear, matching the expected `O(nm)` behavior of the DP algorithm.
- Some variance remains due to normal machine/runtime noise, but repeated runs and error bars show a consistent upward trend.

## Question 2: Reccurence Equation

Give a recurrence that is the basis of a dynamic programming algorithm to compute the HVLCS of strings *A* and *B*. You must provide the appropriate base cases, and explain why your recurrence is correct.

## Question 3: Big-Oh

Give pseudocode of an algorithm to compute the length of the HVLCS of given strings *A* and *B*. What is the runtime of your algorithm?
