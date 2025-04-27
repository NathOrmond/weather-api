# Timezone-aware vs Timezone-naive Datetime Comparison Bug

## Issue

When attempting to delete weather reports for London through a `DELETE` request to `/weather/London`, the system would return a 500 Internal Server Error with the error message:

```
{
  "detail": "Internal error: can't compare offset-naive and offset-aware datetimes",
  "error": "Internal server error"
}
```

## Root Cause

The error stemmed from trying to compare timestamps with different timezone information:

1. The seed data in `api/repositories/seed.py` created reports with **timezone-naive** datetime objects:
   ```python
   # Example from seed data
   timestamp=datetime(2025, 4, 27, 10, 0, 0)  # No timezone info
   ```

2. When creating reports through the API, timestamps were converted to **timezone-aware** datetime objects:
   ```python
   # From weather_service.py
   timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))  # Has timezone info
   ```

3. The `InMemoryReportRepository.find_by_location_id` method sorted reports by timestamp, which attempted to compare timezone-aware and timezone-naive datetimes:
   ```python
   # Original code before fix
   reports.sort(key=lambda r: r.timestamp, reverse=True)
   ```

Python cannot directly compare datetime objects with different timezone information, leading to the error.

## Solution

The fix involved updating the `find_by_location_id` method to ensure all timestamps have consistent timezone information before comparison:

```python
def find_by_location_id(self, location_id: UUID, latest_only: bool = False) -> List[Report]:
    reports = [deepcopy(r) for r in self._data.values() if r.location_id == location_id]
    
    # Make sure timestamps are comparable by ensuring consistent timezone info
    def get_timestamp_safe(report):
        # If the timestamp is timezone-aware, use it as is
        # If it's timezone-naive, assume UTC
        try:
            if report.timestamp.tzinfo is None:
                return report.timestamp.replace(tzinfo=timezone.utc)
            return report.timestamp
        except Exception:
            # Fallback in case of any issues
            return report.timestamp
    
    # Sort using the safe timestamp access
    reports.sort(key=lambda r: get_timestamp_safe(r), reverse=True)
    return reports[:1] if latest_only and reports else reports
```

This helper function ensures that all timestamps are made comparable by converting timezone-naive datetimes to timezone-aware ones (assuming UTC) before comparison.

## Verification

After implementing the fix, the `DELETE /weather/London` endpoint now returns either:
- `204 No Content` when reports exist and are successfully deleted
- `404 Not Found` when no reports exist for the city

Both responses indicate that the datetime comparison issue has been resolved.

## Lessons Learned

1. When working with datetime objects in Python, always ensure consistent timezone handling, especially when comparing values.
2. Datetime objects from different sources (e.g., database seeding vs. API inputs) should use a consistent approach to timezone information.
3. When storing datetime values, it's usually preferable to use timezone-aware datetimes with UTC to avoid ambiguity.
4. Include defensive programming techniques in code that deals with datetime comparisons or sorting. 