# Technical Specification: API Controller Implementation

## 1. Introduction

This document provides the technical specification for implementing the API controller functions for the Weather API. These controllers act as the interface between the HTTP requests (managed by Connexion based on the OpenAPI specification) and the application's business logic/data layer (represented by the in-memory repositories).

## 2. Objective

-   Implement the Python functions corresponding to the `operationId`s defined in `docs/openapi/paths/weather.yaml`.
-   Ensure controllers correctly handle request parameters (path, query, body) provided by Connexion.
-   Utilize the singleton in-memory repository instances (from `api.repositories.memory_repository`) to perform data operations (create, read, update, delete).
-   Perform necessary data validation and mapping between request/response formats and internal domain models.
-   Implement robust error handling, returning appropriate HTTP status codes and error responses defined in the OpenAPI specification.
-   Serialize domain model objects into JSON-compatible dictionaries for API responses using the `.to_dict()` methods.

## 3. Controller File Location

All controller functions specified below should be implemented within the following file:

-   `api/controllers/weather_controller.py`

## 4. Implementation Details

The following sections detail the implementation requirements for each controller function identified by its `operationId`.

### 4.1. `api.controllers.weather_controller.add_weather_report`

-   **OpenAPI Operation:** `POST /weather`
-   **Input:** `body` (dict): Parsed JSON request body conforming to the `WeatherReportCreate` schema. Connexion handles the basic schema validation if configured.
-   **Responsibilities:**
    1.  **Log Request:** Log the received request body (consider redacting sensitive info if applicable).
    2.  **Find Related Entities:**
        -   Extract the `city` name from the `body`.
        -   Use `city_repository.find_by_name(city_name)` to retrieve the `City` object.
        -   If the city is not found, return a 404 error (or potentially 400 if city creation isn't supported via this endpoint). Access the city's associated `Location` object (`city.location`).
    3.  **Data Validation/Parsing:**
        -   Parse the `timestamp` string from the `body` into a `datetime` object. Handle potential `ValueError` during parsing and return a 400 error if invalid.
        -   Validate `temperature` and `condition` against allowed values/types if not fully covered by the OpenAPI schema validation.
    4.  **Create Domain Object:** Instantiate a `Report` object from the `api.models.domain` module, passing the retrieved `Location` object and the validated/parsed data from the `body`.
    5.  **Persist Data:** Call `report_repository.add(new_report)`. Handle potential `ValueError` (e.g., duplicate ID, though unlikely with UUIDs) by returning a 400 or 409 error.
    6.  **Handle Conditions (Optional):** If the request body includes condition information, create `Condition` objects (if they don't exist) and `ReportCondition` link objects, adding them to their respective repositories.
    7.  **Serialize Response:** Call `created_report.to_dict()` on the report object returned by the repository.
    8.  **Return Response:** Return the serialized dictionary and the HTTP status code `201 Created`.
-   **Error Handling:**
    -   `400 Bad Request`: For invalid input data (e.g., bad timestamp format, missing required fields not caught by schema, validation errors). Use the `ValidationError` response schema.
    -   `404 Not Found`: If the specified city cannot be found in the `city_repository`. Use the `NotFoundError` response schema.
    -   `500 Internal Server Error`: For unexpected exceptions during processing.

### 4.2. `api.controllers.weather_controller.get_all_city_summaries`

-   **OpenAPI Operation:** `GET /weather`
-   **Input:** `page` (int, optional), `limit` (int, optional): Query parameters for pagination (currently commented out in `specification.yaml`, but implementation can anticipate them).
-   **Responsibilities:**
    1.  **Log Request:** Log the request (including pagination parameters if implemented).
    2.  **Retrieve Data:**
        -   Call `city_repository.get_all()` to get all `City` objects.
        -   For each `City`, retrieve its associated `Location` (this is already part of the `City` object in your model).
        -   For each `Location`, call `report_repository.find_by_location_id(location.id, latest_only=True)` to get the single latest `Report`.
    3.  **Format Summary:** Construct the list of city summaries conforming to the `WeatherSummary` schema's `cities` array structure. Each item in the array should contain the city name, and the temperature, condition, and timestamp from the latest report found for that city's location. Handle cases where a city might not have any reports yet.
    4.  **Pagination (Future):** If pagination parameters (`page`, `limit`) are added, implement logic to slice the list of city summaries accordingly before returning.
    5.  **Serialize Response:** The constructed summary list is already in the desired dictionary format.
    6.  **Return Response:** Return the summary dictionary (wrapping the list in `{"cities": [...]}`) and the HTTP status code `200 OK`.
-   **Error Handling:**
    -   `500 Internal Server Error`: For unexpected exceptions.

### 4.3. `api.controllers.weather_controller.get_city_weather`

-   **OpenAPI Operation:** `GET /weather/{city}`
-   **Input:** `city` (str): Path parameter representing the city name.
-   **Responsibilities:**
    1.  **Log Request:** Log the requested city name.
    2.  **Find City/Location:** Use `city_repository.find_by_name(city)` to find the `City` object. If not found, return `404 Not Found`. Get the `location.id`.
    3.  **Find Latest Report:** Call `report_repository.find_by_location_id(location_id, latest_only=True)`.
    4.  **Check Report Existence:** If the repository call returns an empty list, return `404 Not Found` (indicating no report exists for this city).
    5.  **Serialize Response:** Call `latest_report.to_dict()` on the retrieved report object (it will be the first element in the returned list).
    6.  **Return Response:** Return the serialized dictionary and the HTTP status code `200 OK`.
-   **Error Handling:**
    -   `404 Not Found`: If the city is not found or if no weather report exists for the city. Use the `NotFoundError` response schema.
    -   `500 Internal Server Error`: For unexpected exceptions.

### 4.4. `api.controllers.weather_controller.update_city_weather`

-   **OpenAPI Operation:** `PUT /weather/{city}`
-   **Input:**
    -   `city` (str): Path parameter for the city name.
    -   `body` (dict): Parsed JSON request body conforming to `WeatherReportCreate`.
-   **Responsibilities:**
    1.  **Log Request:** Log the city name and request body.
    2.  **Find City/Location:** Use `city_repository.find_by_name(city)` to find the `City` object. If not found, return `404 Not Found`. Get the `location.id`.
    3.  **Find Existing Report(s):** Decide on the update strategy:
        -   *Strategy A (Update Latest):* Call `report_repository.find_by_location_id(location_id, latest_only=True)`. If no report exists, return `404 Not Found`.
        -   *Strategy B (Create if Not Exists - like POST):* This might be closer to a typical PUT, but your OpenAPI spec uses `WeatherReportCreate` schema, implying creation/replacement semantics. If implementing replacement, you might skip finding the *latest* report.
    4.  **Data Validation/Parsing:** Validate/parse `body` content similar to `add_weather_report`. Return `400 Bad Request` on failure.
    5.  **Update/Create Domain Object:**
        -   *Strategy A:* Modify the fields of the existing `latest_report` object with data from the `body`.
        -   *Strategy B:* Create a *new* `Report` object using the `location` and data from the `body`. If replacing, you might first delete existing reports for the location or rely on the `update` method to overwrite based on ID (though IDs likely won't match). **Clarification needed on exact PUT semantics.** Assuming Strategy A (update latest) for now based on typical usage.
    6.  **Persist Data:** Call `report_repository.update(updated_report)`.
    7.  **Handle Conditions (Optional):** Update `ReportCondition` links if necessary.
    8.  **Serialize Response:** Call `updated_report.to_dict()` on the report object returned by the repository.
    9.  **Return Response:** Return the serialized dictionary and `200 OK`.
-   **Error Handling:**
    -   `400 Bad Request`: For invalid input data in the `body`. Use `ValidationError`.
    -   `404 Not Found`: If the city or the report to be updated doesn't exist. Use `NotFoundError`.
    -   `500 Internal Server Error`: For unexpected exceptions.

### 4.5. `api.controllers.weather_controller.delete_city_weather`

-   **OpenAPI Operation:** `DELETE /weather/{city}`
-   **Input:** `city` (str): Path parameter for the city name.
-   **Responsibilities:**
    1.  **Log Request:** Log the city name to be deleted.
    2.  **Find City/Location:** Use `city_repository.find_by_name(city)` to find the `City`. If not found, return `404 Not Found`. Get the `location.id`.
    3.  **Find Reports:** Call `report_repository.find_by_location_id(location_id)` to get *all* reports associated with the city's location.
    4.  **Check Report Existence:** If no reports are found, return `404 Not Found`.
    5.  **Delete Reports:** Iterate through the found reports and call `report_repository.delete(report.id)` for each one. Check the boolean return value if necessary.
    6.  **Delete Conditions (Optional):** Delete associated `ReportCondition` entries using `report_condition_repository`.
    7.  **Return Response:** Return an empty response body and the HTTP status code `204 No Content`.
-   **Error Handling:**
    -   `404 Not Found`: If the city or any reports for the city are not found. Use `NotFoundError`.
    -   `500 Internal Server Error`: For unexpected exceptions during deletion.

## 5. General Considerations

-   **Imports:** Ensure controllers import necessary domain models, repository instances, `logging`, and potentially `datetime`, `UUID`.
-   **Logging:** Implement consistent logging for request entry/exit, data retrieval, errors, etc.
-   **Data Mapping:** Carefully map data between the incoming request dictionaries (`body`) and the domain model object attributes. Handle potential type mismatches or missing keys.
-   **Serialization:** Consistently use the `.to_dict()` methods on domain models when preparing response data.
-   **Error Responses:** Adhere strictly to the error response schemas (`NotFoundError`, `ValidationError`) defined in the OpenAPI specification when returning 4xx errors.
-   **Dependencies:** Controllers should depend on repositories, not directly on the storage mechanism (in-memory dictionary).
-   **Thread Safety:** Be mindful that the in-memory repositories are not inherently thread-safe (as noted in the previous spec). This is acceptable for development but would need addressing for production if not using a database.

## 6. Expected Outcome

-   Fully implemented controller functions in `api/controllers/weather_controller.py`.
-   API endpoints behave according to the OpenAPI specification, interacting correctly with the in-memory data layer.
-   Appropriate HTTP status codes and response bodies (including errors) are returned for all operations.
