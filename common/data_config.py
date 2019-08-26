import configparser
import os

# from commons.logger_utils import get_logging, init_logging
#
# init_logging()
# logger = get_logging(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONF_FILE = os.path.join(BASE_DIR, 'config.conf')

if not os.path.isfile(CONF_FILE):
    # logger.error("config file path is wrong")
    pass
cf = configparser.ConfigParser()

cf.read(CONF_FILE)
sections = cf.sections()

headers = {}
headers1 = {}
data = {}
store_id = 'e99d034135664536badbd93f778cfdb1'
params = {}
params['storeId'] = store_id
Host = cf.get("headers", "Host")
Content_Type = cf.get("headers", "Content-Type")
Authorization = cf.get("headers", "Authorization")
headers["Host"] = Host
headers["Content-Type"] = Content_Type
headers1["Host"] = Host
headers1["Content-Type"] = Content_Type
headers1["Authorization"] = Authorization

store_url = cf.get("urls", "access_token")
client_id = cf.get("params", "client_id")
client_secret = cf.get("params", "client_secret")
grant_type = cf.get("params", "grant_type")
scope = cf.get("params", "scope")

data["client_id"] = client_id
data["client_secret"] = client_secret
data["grant_type"] = grant_type
data["scope"] = scope
access_token = cf.get('urls', "access_token")
store_management = cf.get("urls", "store_management")
equipment_management = cf.get("urls", "equipment_management")
store_cameraList = cf.get("urls", "store_cameraList")
livevideoopen = cf.get("urls", "livevideoopen")
liveaddress = cf.get("urls", "liveaddress")
liveaddressbatch = cf.get("urls", "liveaddressbatch")
capture = cf.get("urls", "capture")
passenger_hour_flow = cf.get("urls", "passenger_hour_flow")
details = cf.get("urls", "details")
parking_record = cf.get("urls", "parking_record")
commentPictureList = cf.get("urls", "commentPictureList")
face_details = cf.get("urls", "face_details")
face_statistics = cf.get("urls", "face_statistics")
alarms_configs = cf.get("urls", "alarms_configs")
thief_list = cf.get("urls", "thief_list")
staff_list = cf.get("urls", "staff_list")
staff_info = cf.get("urls", "staff_info")
face_hour = cf.get("urls", "face_hour")
# vip_add = cf.get("urls", "vip_add")
signin_details = cf.get("urls", "signin_details")
heats_areas = cf.get("urls", "heats_areas")
stay_people_distributions = cf.get("urls", "stay_people_distributions")
heats_picture = cf.get("urls", "heats_picture")
generate_heat_map_picture = cf.get("urls", "generate_heat_map_picture")
vip_list = cf.get("urls", "vip_list")
messages = cf.get("urls", "messages")
print(messages)
