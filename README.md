# PyTwistAPI
```python
from core import Connection
conn = Connection("127.0.0.1", port = 9265)
conn.connect()
conn.push_data(posx=0, posy=0, rot=90, turret_rot=180)
conn.disconnect()
```