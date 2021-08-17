# Imports Database class from the project to provide basic functionality for database access
# Imports ObjectId to convert to the correct format before querying in the db
from bson.objectid import ObjectId

from database import Database


class AccessModel:
    USER_COLLECTION = 'users'
    USER_DEVICE_COLLECTION = 'users_device'

    def __init__(self, sess_user):
        self._db = Database()
        self._latest_error = ''
        self.sess_user = sess_user

    @property
    def latest_error(self):
        return self._latest_error

    def get_user_role(self):
        key = {'username': self.sess_user}
        result_data = self.__find(key)
        # logging.warning(result_data)
        if not result_data:
            self._latest_error = "invalid user!!!"
            # logging.warning(self._latest_error)
            return -1
        elif result_data['role'] == 'default':
            # logging.warning(result_data['role'])
            return result_data['role']
        elif result_data['role'] == 'admin':
            # logging.warning(result_data['role'])
            return result_data['role']

    def verify_read_prev(self, dev_id):
        res_doc = self.__find_usr_dev({'user_id': self.sess_user, 'device_access.device_id': dev_id}, {
            'device_access': {'$elemMatch': {'device_id': dev_id}}})
        if not res_doc:
            self._latest_error = "Dear %s, you do not have sufficient rights to perform this operation" % self.sess_user
            return -1

        acc_type = res_doc['device_access'][0]['access_type']
        if acc_type not in ['r', 'rw']:
            self._latest_error = "Dear %s, you do not have sufficient rights to perform this operation---" % self.sess_user
            return -1

    def verify_write_prev(self, dev_id):
        role_val = self.get_user_role()
        if role_val != 'admin':
            res_doc = self.__find_usr_dev({'user_id': self.sess_user, 'device_access.device_id': dev_id}, {
                'device_access': {'$elemMatch': {'device_id': dev_id}}})
            if not res_doc:
                self._latest_error = "Dear %s, you do not have sufficient rights to perform this operation" % self.sess_user
                return -1

            acc_type = res_doc['device_access'][0]['access_type']
            if acc_type != 'rw':
                self._latest_error = "Dear %s, you do not have sufficient rights to perform this operation---" % self.sess_user
                return -1

    def __find(self, key):
        device_document = self._db.get_single_data(AccessModel.USER_COLLECTION, key)
        return device_document

    def __find_usr_dev(self, key, *args):
        device_document = self._db.get_single_data(DeviceModel.USER_DEVICE_COLLECTION, key, *args)
        return device_document


# User document contains username (String), email (String), and role (String) fields
class UserModel:
    USER_COLLECTION = 'users'

    def __init__(self, sess_user):
        self._db = Database()
        self._latest_error = ''
        self.sess_user = sess_user

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    # Since username should be unique in users collection, this provides a way to fetch the user document based on the username
    def find_by_username(self, username):
        acc_mdl = AccessModel(self.sess_user)
        res_data = acc_mdl.get_user_role()
        if res_data == -1:
            self._latest_error = acc_mdl.latest_error
            return -1

        if res_data == 'default':
            self._latest_error = "Dear %s, you do not have sufficient rights to perform this operation" % self.sess_user
            return -1

        key = {'username': username}
        return self.__find(key)

    # Finds a document based on the unique auto-generated MongoDB object id 
    def find_by_object_id(self, obj_id):
        acc_mdl = AccessModel(self.sess_user)
        res_data = acc_mdl.get_user_role()
        if res_data == -1:
            self._latest_error = acc_mdl.latest_error
            return -1

        if res_data == 'default':
            self._latest_error = "Dear %s, you do not have sufficient rights to perform this operation" % self.sess_user
            return -1

        key = {'_id': ObjectId(obj_id)}
        return self.__find(key)

    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key):
        user_document = self._db.get_single_data(UserModel.USER_COLLECTION, key)
        return user_document

    # This first checks if a user already exists with that username. If it does, it populates latest_error and returns -1
    # If a user doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, username, email, role):
        self._latest_error = ''
        user_document = self.find_by_username(username)
        if user_document == -1:
            return -1

        if user_document:
            self._latest_error = f'Username {username} already exists'
            return -1

        user_data = {'username': username, 'email': email, 'role': role}
        user_obj_id = self._db.insert_single_data(UserModel.USER_COLLECTION, user_data)
        return self.find_by_object_id(user_obj_id)


# Device document contains device_id (String), desc (String), type (String - temperature/humidity) and manufacturer (String) fields
class DeviceModel:
    DEVICE_COLLECTION = 'devices'
    USER_DEVICE_COLLECTION = 'users_device'

    def __init__(self, sess_user):
        self._db = Database()
        self._latest_error = ''
        self.sess_user = sess_user

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    # Since device id should be unique in devices collection, this provides a way to fetch the device document based on the device id
    def find_by_device_id(self, device_id):
        acc_mdl = AccessModel(self.sess_user)
        res_data = acc_mdl.get_user_role()
        # logging.warning(res_data)
        if res_data == -1:
            self._latest_error = acc_mdl.latest_error
            return -1

        if res_data == 'default':
            res_doc = acc_mdl.verify_read_prev(device_id)
            # logging.warning(res_doc)
            if res_doc == -1:
                self._latest_error = acc_mdl.latest_error
                return -1

        key = {'device_id': device_id}
        return self.__find(key)

    # Finds a document based on the unique auto-generated MongoDB object id
    def find_by_object_id(self, obj_id):
        acc_mdl = AccessModel(self.sess_user)
        res_data = acc_mdl.get_user_role()
        if res_data == -1:
            self._latest_error = acc_mdl.latest_error
            return -1

        if res_data == 'default':
            dev_doc = self.__find({'_id': ObjectId(obj_id)})
            device_id = dev_doc['device_id']
            if device_id:
                res_doc = acc_mdl.verify_read_prev(device_id)
                # logging.warning(res_doc)
                if res_doc == -1:
                    self._latest_error = acc_mdl.latest_error
                    return -1

        key = {'_id': ObjectId(obj_id)}
        return self.__find(key)

    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key):
        device_document = self._db.get_single_data(DeviceModel.DEVICE_COLLECTION, key)
        return device_document

    # This first checks if a device already exists with that device id. If it does, it populates latest_error and returns -1
    # If a device doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, device_id, desc, type, manufacturer):
        self._latest_error = ''
        acc_mdl = AccessModel(self.sess_user)
        device_document = self.find_by_device_id(device_id)

        if device_document == -1:
            return -1

        res_doc = acc_mdl.verify_write_prev(device_id)
        # logging.warning(res_doc)
        if res_doc == -1:
            self._latest_error = acc_mdl.latest_error
            return -1

        if device_document:
            self._latest_error = f'Device id {device_id} already exists'
            return -1

        device_data = {'device_id': device_id, 'desc': desc, 'type': type, 'manufacturer': manufacturer}
        device_obj_id = self._db.insert_single_data(DeviceModel.DEVICE_COLLECTION, device_data)
        return self.find_by_object_id(device_obj_id)


# Weather data document contains device_id (String), value (Integer), and timestamp (Date) fields
class WeatherDataModel:
    WEATHER_DATA_COLLECTION = 'weather_data'

    def __init__(self, sess_user):
        self._db = Database()
        self._latest_error = ''
        self.sess_user = sess_user

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    # Since device id and timestamp should be unique in weather_data collection, this provides a way to fetch the data document based on the device id and timestamp
    def find_by_device_id_and_timestamp(self, device_id, timestamp):
        acc_mdl = AccessModel(self.sess_user)
        res_data = acc_mdl.get_user_role()
        if res_data == -1:
            self._latest_error = acc_mdl.latest_error
            return res_data

        if res_data == 'default':
            res_doc = acc_mdl.verify_read_prev(device_id)
            # logging.warning(res_doc)
            if res_doc == -1:
                self._latest_error = acc_mdl.latest_error
                return -1

        key = {'device_id': device_id, 'timestamp': timestamp}
        return self.__find(key)

    # Finds a document based on the unique auto-generated MongoDB object id 
    def find_by_object_id(self, obj_id):
        acc_mdl = AccessModel(self.sess_user)
        res_data = acc_mdl.get_user_role()
        if res_data == -1:
            self._latest_error = acc_mdl.latest_error
            return res_data

        if res_data == 'default':
            wdata_doc = self.__find({'_id': ObjectId(obj_id)})
            device_id = wdata_doc['device_id']

            if device_id:
                res_doc = acc_mdl.verify_read_prev(device_id)
                # logging.warning(res_doc)
                if res_doc == -1:
                    self._latest_error = acc_mdl.latest_error
                    return -1

        key = {'_id': ObjectId(obj_id)}
        return self.__find(key)

    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key):
        wdata_document = self._db.get_single_data(WeatherDataModel.WEATHER_DATA_COLLECTION, key)
        return wdata_document

    # This first checks if a data item already exists at a particular timestamp for a device id. If it does, it populates latest_error and returns -1.
    # If it doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, device_id, value, timestamp):
        self._latest_error = ''
        acc_mdl = AccessModel(self.sess_user)
        wdata_document = self.find_by_device_id_and_timestamp(device_id, timestamp)

        if wdata_document == -1:
            return -1

        res_doc = acc_mdl.verify_write_prev(device_id)
        if res_doc == -1:
            self._latest_error = acc_mdl.latest_error
            return -1

        if wdata_document:
            self._latest_error = f'Data for timestamp {timestamp} for device id {device_id} already exists'
            return -1

        weather_data = {'device_id': device_id, 'value': value, 'timestamp': timestamp}
        wdata_obj_id = self._db.insert_single_data(WeatherDataModel.WEATHER_DATA_COLLECTION, weather_data)
        return self.find_by_object_id(wdata_obj_id)
