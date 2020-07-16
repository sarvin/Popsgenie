![Python application](https://github.com/sarvin/Popsgenie/workflows/Python%20application/badge.svg)
# Popsgenie
Python wrapper for [Opsgenie REST API](https://docs.opsgenie.com/docs/api-overview). Popsgenie objects represent resources in Opsgenie; schedules, teams, users etc. Each Popsgenie object has helper attributes to represent and query relationships. For example, a schedule has a relationship with rotations, rotations has a relationship with participants and participants has a relationship with (among others) users. Popsgenie sets up these relationships and allows you to query through objects: `schedule.rotations[0].participants[0].username`.

Querying Opsgenie's list end-points returns an iterable that pages requests for you. See examples below.

## Getting Started
A popsgenie.Popsgenie object is used to make all the API calls. To instantiate a popsgenie.Popsgenie class the first positional is your [Opsgenie API key](https://docs.opsgenie.com/docs/api-access-management).

```python
import popsgenie

genie = popsgenie.Popsgenie('YOUR API KEY')
```

## Schedules
Listing schedules returns a iterable that handles looping over the paged responses. In the example below `pages` is an iterable that does not hold any data and has not made a query. Looping over `pages` triggers a request against Opsgenie's API.

```python
pages = genie.schedules()
for page in pages:
    for schedule in page:
        print(schedule.name)

'Team 0 Schedule'
'Team 1 Schedule'
'Team 2 Schedule'
```

### Query a single schedule
`genie.schedules` is capable of querying for specific resources. A single schedule is returned in a list.

#### By id
Calling `genie.schedules` with the resource's id:

```python
schedules = next(genie.schedules(identifier='m9r05hi3-limb-icj8-9mb3-051weib9plgh'))

schedules
[<class 'popsgenie.resource.Schedule'>('m9r05hi3-limb-icj8-9mb3-051weib9plgh')]

schedules[0].id
'm9r05hi3-limb-icj8-9mb3-051weib9plgh'
```

#### By name
Calling `genie.schedules` by name requires two parameters; identifier set to the resource's name and identifier_type set to name:

```python
schedules = []
pages = genie.schedules(identifier='The Name of a team (doesn\'t have to be url safe)', identifier_type='name')

for page in pages:
    schedules.extend(page)

schedules
[<class 'popsgenie.resource.Schedule'>('m9r05hi3-limb-icj8-9mb3-051weib9plgh')]

schedules[0].name
"The Name of a team (doesn't have to be url safe)"
```

### Schedule
A PopsgenieSchedule object represents an individual [Opsgenie schedule](https://docs.opsgenie.com/docs/schedule-api#get-schedule).

```python
schedule.name
'Team 0 Schedule'
```

All JSON Body Fields are represented except for rotation and on_calls. Relationships between [rotation](https://docs.opsgenie.com/docs/schedule-api#section-schedule-rotation-fields), [team](https://docs.opsgenie.com/docs/team-api#get-team) and [on_calls](https://docs.opsgenie.com/docs/user-api) are represented by attributes that handle these relationships for you. When calling these methods additional resources are returned.

```python
schedule.rotations
[<class 'popsgenie.resource.Rotation'>('dxbby0qb-zrdu-v430-g7s4-w6i9pk7gvklz')]

schedule.team
<class 'popsgenie.resource.Team'>('2a3456b7-c891-2de3-4fgh-i5j6k7891l23')

schedule.on_calls
[<class 'popsgenie.resource.User'>('01a2bcd3-efgh-4i56-786j-9k0123456lm7')]
```
##### Rotation
A PopsgenieRotation represents rotations associated with a schedule.

```python
rotations = schedule.rotations

rotations
<class 'popsgenie.resource.Rotation'>('abc1def2-g345-6hi7-jk89-123lm4no5p67')

rotations[0].name
'Rotation associated with Schedule'

rotations[0].id
'abc1def2-g345-6hi7-jk89-123lm4no5p67'
```

## Teams
Like schedules, listing teams returns an iterable, `popsgenie.tool.Pages`, that handles looping over the paged responses.

```python
for page in genie.teams():
    for team in page:
        print(team.name)
'The first team'
'The second team'
```

### Query a single team
`genie.teams` is capable of querying for specific resources. A single `popsgenie.resource.Team` is returned in a list.

#### By id
Calling `genie.teams` with the resource's id:

```python
teams = next(genie.teams(identifier='rungzd54-hc3l-t7i9-sqf5-4swjxnzkbejv'))

teams
[<class 'popsgenie.resource.Team'>('rungzd54-hc3l-t7i9-sqf5-4swjxnzkbejv')]

teams[0].id
'rungzd54-hc3l-t7i9-sqf5-4swjxnzkbejv'
```

#### By name
Calling `genie.teams` by name requires two parameters; identifier set to the resource's name and identifier_type set to name:

```python
teams = []
pages = genie.teams(identifier='The Name of a team (doesn\'t have to be url safe)', identifier_type='name')

for page in pages:
    teams.extend(page)

teams
[<class 'popsgenie.resource.Team'>('rungzd54-hc3l-t7i9-sqf5-4swjxnzkbejv')]

teams[0].name
'The Name of a team (doesn\'t have to be url safe)'
```

### Team
A popsgenie.resource.Team represents an individual [Opsgenie team](https://docs.opsgenie.com/docs/team-api#get-team).

```python
team
<class 'popsgenie.resource.Team'>('068ecc2k-ifpa-tff8-i6nd-gedap0nzahai')

team.name
'Opsgenie - Team name'

team.description
'Opsgenie - Team description'
```

All JSON Body Fields are represented except for members.

`team.members` returns a list of User instances representing users associated with a team.

```python
team.members
[<class 'popsgenie.resource.User'>('2a3456b7-c891-2de3-4fgh-i5j6k7891l23'),
 <class 'popsgenie.resource.User'>('01a2bcd3-efgh-4i56-786j-9k0123456lm7'),
 <class 'popsgenie.resource.User'>('abc1def2-g345-6hi7-jk89-123lm4no5p67')]
```

## Users
Listing users returns a iterable that handles looping over the paged responses. In the example below `user_pages` is an iterable that does not hold any data and has not made a query. Looping over `user_pages` triggers a request against Opsgenie's API.

```python
user_pages = genie.users()
users = []

for user_page in user_pages:
    for user in user_page:
        users.append(user)

users
[<class 'popsgenie.resource.User'>('abc1def2-g345-6hi7-jk89-123lm4no5p67'),
 <class 'popsgenie.resource.User'>('01a2bcd3-efgh-4i56-786j-9k0123456lm7'),
 <class 'popsgenie.resource.User'>('2a3456b7-c891-2de3-4fgh-i5j6k7891l23'),
 <class 'popsgenie.resource.User'>('567ef8gh-9i01-2345-jk67-l89m0n12o34p'),
 #...
]

len(users)
134
```

### Query a single user
`genie.users` is capable of querying for specific resources. A single user is returned in a list.

#### By id
Calling `genie.users` with the resource's id:

```python
user = next(genie.users(identifier='7l3d9qrz-he0w-ucwu-206e-37kmawd1ucqc'))[0]

user
<class 'popsgenie.resource.User'>('7l3d9qrz-he0w-ucwu-206e-37kmawd1ucqc')

user.id
'7l3d9qrz-he0w-ucwu-206e-37kmawd1ucqc'
```

#### By username
Calling `genie.users` by name requires two parameters; identifier set to the resource's name and identifier_type set to username:

```python
users = []
pages = genie.users(
    identifier="The Name of a user (doesn't have to be url safe)", identifier_type='username')

for page in pages:
    users.extend(page)

users
[<class 'popsgenie.resource.User'>('m9r05hi3-limb-icj8-9mb3-051weib9plgh')]

users[0].name
"The Name of a user (doesn't have to be url safe)"
```

### User
A User object represents an individual [Opsgenie user](https://docs.opsgenie.com/docs/user-api#get-user).

```python
user
<class 'popsgenie.resource.User'>('2a3456b7-c891-2de3-4fgh-i5j6k7891l23')

user.username
'jherbewitz@notreal.net'
```

All JSON Body Fields are represented, through attributes, except for userContacts. userContacts is replaced by an attribute called `contacts`.

```python
user.contacts
[{'id': 'd30e40f8-ghi5-6070-8090-1j110k20lm3n',
  'method': 'email',
  'to': 'jherbewitz@notreal.net',
  'status': {'enabled': True},
  'applyOrder': 0},
 {'id': '2a3456b7-c891-2de3-4fgh-i5j6k7891l23',
  'method': 'voice',
  'to': '1-9148881173',
  'status': {'enabled': True},
  'applyOrder': 0},
 {'id': '01a2bcd3-efgh-4i56-786j-9k0123456lm7',
  'method': 'mobile',
  'to': 'some mobile thing',
  'status': {'enabled': True},
  'applyOrder': 0},
 {'id': 'abc1def2-g345-6hi7-jk89-123lm4no5p67',
  'method': 'sms',
  'to': '1-9148881173',
  'status': {'enabled': True},
  'applyOrder': 0}]
```

In addition, to the `user.createdAt` attribute, User also has the attribute `date_created`. `date_created` parses `createdAt` and returns a datetime.datetime object.

```python
user.createdAt
'2020-01-07T19:34:00.281Z'

user.date_created
datetime.datetime(2020, 1, 7, 19, 34, 0, 281000, tzinfo=datetime.timezone.utc)
```
