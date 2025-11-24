import datetime
from utils import queueing

print(f"Current System Time: {datetime.datetime.now()}")
print(f"Current System Time (Time part): {datetime.datetime.now().time()}")
print(f"Start Time: {queueing.start_time}")
print(f"End Time: {queueing.end_time}")
print(f"Check Time Result: {queueing.check_time()}")
