INTERNAL_API_DESCRIPTION = """
# Core concepts

## Generic linked object serialization

Some models use GenericForeignKey fields to link to any other instance of an arbitrary model.
The target of such a field is designated as a "Generic linked object", or GLO.
The GenericForeignKey mechanism depends on the django ContentType infrastructure.

A GLO is represented by an object :
```
{
    'content_type_id': integer,
    'details': object,
    'model_name': string,
    'state': string,
}
```

##### state

The GLO may be in one of three state :
 - **active**: The instance is accessible
 - **soft_deleted**: The data are still in the db, but the user requested deletion, so the `hidden` flag is True and the instance is not accessible.
 - **terminated**: The data are not in the db anymore, the instance is inaccessible.
 
##### details
 
 The serialized representation of the GLO, which depends on the state and varies with each model.
 
 - Actives GLO
 ```
{
    'id': integer,
    'url': string,
    [other fields depends on the model ...]
}
```

 - Soft deleted GLO have the same representation than actives GLO, with all data visible, but the url is `null` because the instance is not accessible
```
{
    'id': integer,
    'url': null,
    [other fields depends on the state ...]
}
```

- Terminated GLO don't have any data, but a string representation from the past may be return on some endpoints :
```
{
    'repr': string,
}
```

## Diff

When an instance is updated, we record the changes in an array of Diff objects, 
one for each instance field affected :

```
[
    {
        'field_name': string,
        'field_type': string,
        'field_label': string,
        'before': any,
        'after': any
    },
    ...
]
```

The type of the `before` and `after` fields depends on the field_type

#### Field types

The field type is one of the django model fields type.
Those are the main field types and the corresponding type for the before/after fields : 

- **BooleanField**: boolean
- **CharField**: string
- **DateField**: string ( ISO 8601 datetime)
- **DateTimeField**: string ( ISO 8601 datetime)
- **DecimalField**: number
- **EmailField**: string
- **ForeignKey**: related ( see below )
- **IntegerField**: integer
- **JSONField**: object
- **ManyToManyField**: array of related ( see below )
- **PositiveIntegerField**: integer
- **TextField**: string
- **URLField**: string

#### Related fields

There are two field types for relations : `ForeignKey` and `ManyToManyField`.

A related instance is represented by

```
{
    'id': integer,
    'repr': string
}
```

For ForeignKeys, the before/after fields will hold a single related instance.

For ManyToManyField, the before/after fields will hold an array of related instances.

The absence of a related instance is represented by 

```
{
    'id': null,
    'repr': ''
}
```

#### Errors

A Diff object may be in error :

```
{
    'field_name': string,
    'error': string
}
```

#### Special-case for Item json content

The content field of an Item is a special beast, which has a dedicated diff infrastructure ( history of edit sessions ).
The item content diff won't be embedded as a Diff object, instead the user should be directed to the item history view.
When an update concerns an item content, the Diff object will simply be a marker :

```
{
    'field_name': 'json_content',
    'field_label': 'Content'
}
```

The url of the history view is available on the edit session object, for example in the activity API :
 `activity.action_object.details.url`
"""
