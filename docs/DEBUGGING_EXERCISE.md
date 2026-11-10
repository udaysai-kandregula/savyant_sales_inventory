# Debugging exercise: calculate_total

## Buggy implementation

```python
def calculate_total(items):
    total = 0
    for quantity, rate in items:
        total = quantity * rate  # BUG: overwrites the previous line total
    return total
```

## Correct implementation

```python
from decimal import Decimal

def calculate_total(items):
    total = Decimal("0.00")
    for quantity, rate in items:
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        amount = Decimal(str(rate))
        if not amount.is_finite() or amount < 0:
            raise ValueError("Rate must be a non-negative amount")
        total += quantity * amount
    return total.quantize(Decimal("0.01"))
```

## Explanation

The original loop assigns each line amount to `total`, so each new row replaces the previous result. Use `+=` to accumulate all line amounts. Decimal avoids binary floating-point errors in money calculations.

## Expected checks

- `[(2, 100), (3, 50)]` returns `350.00`.
- An empty list returns `0.00`.
- Zero/negative/non-integer quantities raise `ValueError`.
- Negative or non-finite rates raise `ValueError`.
