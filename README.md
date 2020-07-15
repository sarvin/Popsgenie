![Python application](https://github.com/sarvin/Popsgenie/workflows/Python%20application/badge.svg)
# Popsgenie
Python wrapper for [Opsgenie REST API](https://docs.opsgenie.com/docs/api-overview). Popsgenie objects represent queryable data in Opsgenie; schedules, teams, users etc. Each Popsgenie object has helper attributes to represent and query relationships. For example, a schedule has a relationship with rotations, rotations has a relationship with participants and participants has a relationship with (among others) users. Popsgenie sets up these relationships and allows you to query through objects: `schedule.rotations[0].participants[0].username`.

Querying Opsgenie's list end-points returns an iterable that automatically pages requests for you. See examples below.

## Getting Started
A popsgenie.Popsgenie object is used to make all the API calls. To instantiate a popsgenie.Popsgenie class the first positional argument is the [Opsgenie Web API URL](https://docs.opsgenie.com/docs/web-api). The second positional argument is your [Opsgenie API key](https://docs.opsgenie.com/docs/api-access-management).

```python
import popsgenie

genie = popsgenie.Popsgenie(
    'https://api.opsgenie.com/v2',
    'YOUR API KEY')
```

## Schedules
Listing schedules returns a Python iterable object that handles looping over the paged responses. In the example below `schedule_pages` is an iterable that does not hold any data and has not made a query. Looping over `schedule_pages` or calling `next(schedule_pages)` triggers a request against Opsgenie's API.

```python
schedule_pages = genie.schedules()
for page in schedule_pages:
    for schedule in page:
        print(schedule.name)

'Team 0 Schedule'
'Team 1 Schedule'
'Team 2 Schedule'
```

### Query a single schedule
`genie.schedules` can also be called with id and identifier_type to query a single schedule. A single PopsgenieSchedule object is returned in a lsit.

#### By id

```python
schedules = next(genie.schedules(identifier='m9r05hi3-limb-icj8-9mb3-051weib9plgh'))

schedules
[<class 'popsgenie.api_classes.PopsgenieSchedule'>('m9r05hi3-limb-icj8-9mb3-051weib9plgh')]

schedules[0].id
'm9r05hi3-limb-icj8-9mb3-051weib9plgh'
```

#### By name

```python
schedules = []
pages = genie.schedules(identifier='The Name of a team (doesn\'t have to be url safe)', identifier_type='name')

for page in pages:
    schedules.extend(page)

schedules
[<class 'popsgenie.api_classes.PopsgenieSchedule'>('m9r05hi3-limb-icj8-9mb3-051weib9plgh')]

schedules[0].name
'The Name of a team (doesn\'t have to be url safe)'
```

### Schedule
A PopsgenieSchedule object represents an individual [Opsgenie schedule](https://docs.opsgenie.com/docs/schedule-api#get-schedule).

```python
schedule.name
'Team 0 Schedule'
```

All JSON Body Fields are represented except for rotation and on_calls. The has attributes that represent the relationships between a schedule and [rotation](https://docs.opsgenie.com/docs/schedule-api#section-schedule-rotation-fields), [team](https://docs.opsgenie.com/docs/team-api#get-team) and [on_calls](https://docs.opsgenie.com/docs/user-api).

```python
rotations = schedule.rotations

schedule.team
<class 'popsgenie.api_classes.PopsgenieTeam'>('2a3456b7-c891-2de3-4fgh-i5j6k7891l23')

schedule.on_calls
[<class 'popsgenie.api_classes.PopsgenieUser'>('01a2bcd3-efgh-4i56-786j-9k0123456lm7')]
```
##### Rotation
A PopsgenieRotation represents rotations associated with a schedule.

```python
rotations = schedule.rotations

rotations
<class 'popsgenie.api_classes.PopsgenieRotation'>('abc1def2-g345-6hi7-jk89-123lm4no5p67')

rotations[0].name
'Rotation associated with Schedule'

rotations[0].id
'abc1def2-g345-6hi7-jk89-123lm4no5p67'
```

## Teams
Listing teams returns a Python iterable object that handles looping over the paged responses. In the example below `team_pages` is an iterable that does not hold any data and has not made a query. Looping over `team_pages` triggers a request against Opsgenie's API.

```python
team_pages = genie.teams()
teams = next(team_pages)

for team in teams:
    print(team.name)
'The first team'
'The second team'
```

### Query a single team
`genie.teams` can query by id or name for a single team. A single PopsgenieTeam object is returned in a lsit.

#### By id

```python
team = next(genie.teams(identifier='rungzd54-hc3l-t7i9-sqf5-4swjxnzkbejv'))

users
[<class 'popsgenie.api_classes.PopsgenieTeam'>('rungzd54-hc3l-t7i9-sqf5-4swjxnzkbejv')]

users[0].id
'rungzd54-hc3l-t7i9-sqf5-4swjxnzkbejv'
```

#### By name

```python
teams = []
pages = genie.teams(identifier='The Name of a team (doesn\'t have to be url safe)', identifier_type='name')

for page in pages:
    teams.extend(page)

teams
[<class 'popsgenie.api_classes.PopsgenieTeam'>('rungzd54-hc3l-t7i9-sqf5-4swjxnzkbejv')]

teams[0].name
'The Name of a team (doesn\'t have to be url safe)'
```

### Team
A PopsgenieTeam object represents an individual [Opsgenie team](https://docs.opsgenie.com/docs/team-api#get-team).

```python
team_pages = genie.teams()
teams = next(team_pages)
team = teams[0]

team.name
'Opsgenie - Team name'

team.description
'Opsgenie - Team description'
```

All JSON Body Fields are represented except for members.

`team.members` returns PopsgenieUser instances representing users associated with a team.

```python
team.members
[<class 'popsgenie.api_classes.PopsgenieUser'>('2a3456b7-c891-2de3-4fgh-i5j6k7891l23'),
 <class 'popsgenie.api_classes.PopsgenieUser'>('01a2bcd3-efgh-4i56-786j-9k0123456lm7'),
 <class 'popsgenie.api_classes.PopsgenieUser'>('abc1def2-g345-6hi7-jk89-123lm4no5p67')]
```

## Users
Listing users returns a Python iterable object that handles looping over the paged responses. In the example below `user_pages` is an iterable that does not hold any data and has not made a query. Looping over `user_pages` triggers a request against Opsgenie's API.

```python
user_pages = genie.users()
users = []

for user_page in user_pages:
    for user in user_page:
        users.append(user)

users
[<class 'popsgenie.api_classes.PopsgenieUser'>('abc1def2-g345-6hi7-jk89-123lm4no5p67'),
 <class 'popsgenie.api_classes.PopsgenieUser'>('01a2bcd3-efgh-4i56-786j-9k0123456lm7'),
 <class 'popsgenie.api_classes.PopsgenieUser'>('2a3456b7-c891-2de3-4fgh-i5j6k7891l23'),
 <class 'popsgenie.api_classes.PopsgenieUser'>('567ef8gh-9i01-2345-jk67-l89m0n12o34p'),
 #...
]

len(users)
134
```

### Query a single user
`genie.users` can query by id or username for a single user. A single PopsgenieUser object is returned in a lsit.

#### By id

```python
users = next(genie.users(identifier='7l3d9qrz-he0w-ucwu-206e-37kmawd1ucqc'))

users
[<class 'popsgenie.api_classes.PopsgenieUser'>('7l3d9qrz-he0w-ucwu-206e-37kmawd1ucqc')]

users[0].id
'7l3d9qrz-he0w-ucwu-206e-37kmawd1ucqc'
```

#### By username

```python
users = []
pages = genie.users(identifier='The Name of a user (doesn\'t have to be url safe)', identifier_type='username')

for page in pages:
    users.extend(page)

users
[<class 'popsgenie.api_classes.PopsgenieUser'>('m9r05hi3-limb-icj8-9mb3-051weib9plgh')]

users[0].name
'The Name of a user (doesn\'t have to be url safe)'
```

### User
A PopsgenieUser object represents an individual [Opsgenie user](https://docs.opsgenie.com/docs/user-api#get-user).

```python
user
<class 'popsgenie.api_classes.PopsgenieUser'>('2a3456b7-c891-2de3-4fgh-i5j6k7891l23')

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

In addition to the `user.createdAt` attribute PopsgenieUser instances also have the attribute `date_created`. `date_created` parses `createdAt` and returns a datetime.datetime object.

```python
user.createdAt
'2020-01-07T19:34:00.281Z'

user.date_created
datetime.datetime(2020, 1, 7, 19, 34, 0, 281000, tzinfo=datetime.timezone.utc)
```
