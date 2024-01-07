### Database

Password for `root` user: `password`

Initialization before running the django app:

```mysql
DROP DATABASE IF EXISTS LittleLemon;
CREATE DATABASE LittleLemon;
```

### Setup

Populating with fake data:

```shell
python manage.py init
```

Running tests:

```shell
python manage.py test 
```

### Endpoints

For endpoints that require authentication, set the header ```'Authorization': 'Token THE_TOKEN'```

Authentication requirements based on the available information (some of it doesn't make sense but is done based on the
instructions):

| Endpoint                   | Create | Patch | Put | Delete | List | Retrieve |
|----------------------------|--------|-------|-----|--------|------|----------|
| /restaurant/menu-items/    | Yes    | No    | No  | No     | Yes  | No       |
| /restaurant/booking/tables | Yes    | Yes   | Yes | Yes    | Yes  | Yes      |

Other endpoints:

| About                     | Endpoint                                         |
|---------------------------|--------------------------------------------------|
| Obtain token (i.e. login) | http://localhost:8000/restaurant/api-token-auth/ |
| Logout                    | http://localhost:8000/auth/token/logout          |
| Index page                | http://localhost:8000/restaurant/                |
| Create user               | http://localhost:8000/auth/users/                |