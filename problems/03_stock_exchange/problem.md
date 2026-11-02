# Stock Exchange — Order Matching

Current attempt override (2026-11-02): learner explicitly replaced file/CLI input
with direct Order submission to OrderMatchingEngine. File handling below is the
original interview requirement, retained for reference, and is out of scope for
this attempt. Trade output interface remains to clarify. Matching rules remain.
The learner further narrowed this attempt to one stock; multi-stock support is
a future extension. Low latency is a goal, but O(1) complete order processing is
not an agreed guarantee; one order can generate multiple trades.

Source: learner's actual 90-minute machine-coding interview challenge, refined
on 2026-10-31; employer not specified. Execution rules are those of the challenge.
Planned session: 2026-11-01, as a 90-minute timed interview simulation.
Implementation language: Python, consistent with
this workspace; the Kotlin code fence in the request contained prose, not code.

## Objective

Build a command-line program that reads buy and sell limit orders from a text
file, processes them sequentially, and prints each executed trade to stdout.
Maintain independent order books for each stock. Unmatched quantities remain
available for subsequent orders until filled or the input ends.

## Input

Invocation: `python stock_exchange.py <input_file_path>`.

Each nonblank line contains six whitespace-separated fields:

```text
<order_id> <time> <stock> <buy|sell> <price> <quantity>
```

Example: `#1 09:45 BAC sell 240.12 100`.

- Order ID: globally unique, nonempty identifier. A leading `#` is part of the
  identifier, not a comment marker.
- Time: a valid 24-hour `HH:MM` timestamp within one trading day.
- Stock: a nonempty, case-sensitive symbol.
- Side: exactly `buy` or `sell`.
- Price: positive decimal amount with at most two fractional digits; monetary
  comparisons and output must be exact, without binary floating-point rounding.
- Quantity: a positive integer number of shares.

## Matching rules

1. Process orders in file order. After accepting each order, execute all matches
   it permits before processing the next input line.
2. Match only orders for the same stock and opposite sides.
3. A buy and sell cross when `buy_price >= sell_price`. Equality must match.
4. Price priority comes first: highest buy price and lowest sell price win.
5. Within a price level, earlier orders have priority. For equal timestamps,
   earlier input lines win.
6. Execute the smaller of the two remaining quantities. Reduce both quantities
   by the executed amount and remove completely filled orders.
7. A partially filled resting order retains its original time priority. The
   incoming order continues matching until filled or no compatible order remains.
   Any remainder then rests in its own book.
8. Every trade executes at the sell order's limit price, even if the sell order
   just arrived and the buy order was already resting. Preserve this explicit
   challenge rule; do not substitute a resting-order-price rule.

## Output

Print one line per individual match, in execution order:

```text
<buy_order_id> <sell_price> <executed_quantity> <sell_order_id>
```

Print prices with exactly two decimal places. Do not combine distinct matches.
Do not print unfilled orders, headers, prompts, or debug logs to stdout.
If no trades execute, stdout is empty.

## Sample

Input:

```text
#1 09:45 BAC sell 240.12 100
#2 09:46 BAC sell 237.45 90
#3 09:47 BAC buy 238.10 110
#4 09:48 BAC buy 237.80 10
#5 09:49 BAC buy 237.80 40
#6 09:50 BAC sell 236.00 50
```

Output:

```text
#3 237.45 90 #2
#3 236.00 20 #6
#4 236.00 10 #6
#5 236.00 20 #6
```

The last sell first fills #3's remaining 20 shares because its buy price is
higher. At buy price 237.80, #4 precedes #5. Order #5 retains 20 unfilled shares;
sell order #1 remains unmatched for 100 shares.

## Clarified defaults to confirm at the session

The original challenge does not specify these policies. The proposed baseline is:

- Input timestamps are globally nondecreasing; reject an out-of-order timestamp
  rather than sorting the file. This keeps arrival order and time priority aligned.
- Ignore blank lines. Reject malformed fields, invalid timestamps, duplicate
  IDs (including IDs already filled), invalid side, nonpositive price/quantity,
  and prices with more than two fractional digits.
- Stop at the first invalid record, report its line number and reason to stderr,
  and exit nonzero. Earlier trade output remains valid; no rollback is required.
- Missing/unreadable file or invalid command-line arguments: diagnostic on
  stderr, nonzero exit. An empty file succeeds with no output.
- Process one file in a single thread. No concurrent submission, cancellation,
  amendments, market orders, fees, persistence, or network APIs in the baseline.
- Explain complexity in terms of open orders and generated trades. No O(1)
  target is imposed; data structure selection belongs to the learner.

These defaults are refinements, not claims that they appeared in the source.
Begin tomorrow on the learner's start signal, with clarification included in the
90 minutes. Learner owns design, implementation, tests, and defense; no unsolicited
hints or mentor-written fixes during the mock. The timer has not started.
