<h1 align=center>Tracker</h1>

## About

**tracker** is lightweight lib created over pandas DataFrame concept to map code execution and provide insights/reports around it, especially computing [I/O](https://en.wikipedia.org/wiki/Input/output) operations, such as API calls, databases writting/reading actions, and so on.

## Creating a BaseTracker subclass and initializing it:

```python
import tracker as tk
import typing as t


class RequestTracker(tk.BaseTracker):

    def __init__(self) -> None:
        super().__init__(('user_id', 'status', 'payload', 'error'))

    def transform(self, **kwargs) -> t.Dict[str, t.Any]:
        """Update the received data when calling `add_snapshot` before writting a DataFrame row."""
        response = kwargs.pop('response')
        kwargs['status'] = response.status_code
        kwargs['success'] = True if 199 < response.status_code < 300 else False
        kwargs['payload'] = response.request.body
        if not kwargs['success']:
            kwargs['error'] = response.text
        return kwargs


tracker = RequestTracker()
```
When calling the superclass `__init__` an empty DataFrame is created with the passed columns. The columns are typically what you want to map. The `transform` method provides a way to apply several processing layers on data before effectively saving a row on the DataFrame each time, but nothing prevents ignoring this method and making the data processing outside the class scope.

## Use Case

Let's say you have received several requests to update your app customers' names, but rather than processing those requests immediately you've just saved those information (payloads) to process them later by an asynchronous approach.

```python
import requests


api_url = 'https://fictional-api/v1/customer/partial-update/'

customers = (
    {'name': 'Brand-new name 1', 'customer_pk': '9e642c11-ff62-48c9-828c-6a7ea45d99f3'},
    {'name': 'Brand-new name 2', 'customer_pk': 'b737b50c-0e90-4345-a8f3-272923493b58'},
    {'name': 'Brand-new name 3', 'customer_pk': 'f91aa8e3-2d03-4e6a-a021-ada6c33303a2'},
    {'name': 'Brand-new name 4', 'customer_pk': '8a479e98-336a-4f12-b930-0e36585bd654'},
    {'name': '', 'customer_pk': '58b2ca0d-edaa-4d56-ba90-54b4552fa9f0'},
)

for customer in customers:
    url = f"{api_url}{customer['customer_pk']}"
    payload = {'name': customer['name']}
    response = requests.patch(api_url, json=payload)
    tracker.add_snapshot(user_id=customer['customer_pk'], response=response)
````

After doing what must be done and populating your tracker, you may want to display a table holding all information appended into it:

```python
>>> tracker.df
```

<table>
  <tr>
    <th></th>
    <th>user_id</th>
    <th>status</th>
    <th>payload</th>
    <th>error</th>
    <th>success</th>
  </tr>
  <tr>
    <td>0</td>
    <td>2e642c11-ff62-48c9-828c-6a7ea45d99f3</td>
    <td>200</td>
    <td>{'name': 'Brand-new name 1'}</td>
    <td>NaN</td>
    <td>True</td>
  </tr>
  <tr>
    <td>1</td>
    <td>9e642c11-ff62-48c9-828c-6a7ea45d99f3</td>
    <td>200</td>
    <td>{'name': 'Brand-new name 2'}</td>
    <td>NaN</td>
    <td>True</td>
  </tr>
  <tr>
    <td>2</td>
    <td>4e642c11-ff62-48c9-828c-6a7ea45d99f3</td>
    <td>500</td>
    <td>{'name': 'Brand-new name 3'}</td>
    <td>"HTTP 500 ERROR"</td>
    <td>False</td>
  </tr>
  <tr>
    <td>3</td>
    <td>7e642c11-ff62-48c9-828c-6a7ea45d99f3</td>
    <td>200</td>
    <td>{'name': 'Brand-new name 4'}</td>
    <td>NaN</td>
    <td>True</td>
  </tr>
  <tr>
    <td>4</td>
    <td>8e642c11-ff62-48c9-828c-6a7ea45d9973</td>
    <td>400</td>
    <td>{'name': ''}</td>
    <td>"{'message': 'A `name` cannot be blank'}"</td>
    <td>False</td>
  </tr>
</table>


You might need only a piece of those information, like errors entries, successes entries or just a small insight around them:

<details>
    <summary>Checking only errors</summary>

```python
>>> tracker.errors_df
```

<table>
  <tr>
    <th></th>
    <th>user_id</th>
    <th>status</th>
    <th>payload</th>
    <th>error</th>
    <th>success</th>
  </tr>
  <tr>
    <td>2</td>
    <td>4e642c11-ff62-48c9-828c-6a7ea45d99f3</td>
    <td>500</td>
    <td>{'name': 'Brand-new name 3'}</td>
    <td>"HTTP 500 ERROR"</td>
    <td>False</td>
  </tr>
  <tr>
    <td>4</td>
    <td>8e642c11-ff62-48c9-828c-6a7ea45d9973</td>
    <td>400</td>
    <td>{'name': ''}</td>
    <td>"{'message': 'A `name` cannot be blank'}"</td>
    <td>False</td>
  </tr>
</table>

</details>

<details>
    <summary>Checking only successes</summary>

```python
>>> tracker.successes_df
```

<table>
  <tr>
    <th></th>
    <th>user_id</th>
    <th>status</th>
    <th>payload</th>
    <th>error</th>
    <th>success</th>
  </tr>
  <tr>
    <td>0</td>
    <td>2e642c11-ff62-48c9-828c-6a7ea45d99f3</td>
    <td>200</td>
    <td>{'name': 'Brand-new name 1'}</td>
    <td>NaN</td>
    <td>True</td>
  </tr>
  <tr>
    <td>1</td>
    <td>9e642c11-ff62-48c9-828c-6a7ea45d99f3</td>
    <td>200</td>
    <td>{'name': 'Brand-new name 2'}</td>
    <td>NaN</td>
    <td>True</td>
  </tr>
  <tr>
    <td>3</td>
    <td>7e642c11-ff62-48c9-828c-6a7ea45d99f3</td>
    <td>200</td>
    <td>{'name': 'Brand-new name 4'}</td>
    <td>NaN</td>
    <td>True</td>
  </tr>
</table>

</details>

<details>
    <summary>Errors/Successes count</summary>

```python
>>> tracker.errors
2
>>> tracker.successes
3
>>> tracker.status
(2, 3)
```

</details>

## Generating a JSON as a report

In order to generate a JSON from the entries both `errors_dict` and `successes_dict` methods must be overridden first aiming to select what information and how to display them fits better in each case:

```python
import pandas as pd


    class RequestTracker(tk.BaseTracker):

         def error_dict(self, entry: pd.Series) -> None:
            """Overridden."""
            error_dict = {
                'user_id': entry[0],
                'status': entry[1],
                'payload': entry[2],
                'error': entry[3],
            }
            self.append_dict(error_dict)


        def success_dict(self, entry: pd.Series) -> None:
            """Overridden."""
            success_dict = {'user_id': entry[0], 'message': 'All done!'}
            self.append_dict(success_dict)
```

```python
>>> tracker.summarize(summarize_successes=True)
```

```json
{
   "errors":2,
   "successes":3,
   "failed":[
      {
         "user_id":"4e642c11-ff62-48c9-828c-6a7ea45d99f3",
         "status":500,
         "payload":{
            "name":"Brand-new name 3"
         },
         "error":"HTTP 500 ERROR"
      },
      {
         "user_id":"8e642c11-ff62-48c9-828c-6a7ea45d9973",
         "status":400,
         "payload":{
            "name":""
         },
         "error":"{'message': 'A `name` cannot be blank'}"
      }
   ],
   "succeded":[
      {
         "user_id":"2e642c11-ff62-48c9-828c-6a7ea45d99f3",
         "message":"All done!"
      },
      {
         "user_id":"9e642c11-ff62-48c9-828c-6a7ea45d99f3",
         "message":"All done!"
      },
      {
         "user_id":"7e642c11-ff62-48c9-828c-6a7ea45d99f3",
         "message":"All done!"
      }
   ]
}
```

## Generating a CSV as a report

```python
import tracker as tk


class RequestTracker(tk.BaseTracker, tk.mixins.CSVMixin): ...
```

```python
>>> tracker.create_csv('errors.csv', flag=tk.flags.ONLY_ERRORS)
```
